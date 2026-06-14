from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
from typing import List, Optional

from . import models, schemas

DEFAULT_DAILY_CALORIE_GOAL = 2000
DEFAULT_PROTEIN_GOAL = 150
GOAL_MET_LOWER_RATIO = 0.95
GOAL_MET_UPPER_RATIO = 1.05
PROTEIN_LOW_RATIO = 0.5
CALORIES_UNDER_RATIO = 0.6
MIN_CALORIES_FOR_PROTEIN_CHECK = 300
MISSED_MEAL_HOUR = 12


def update_daily_analytics(db: Session, user_id: int, log: schemas.FoodLogCreate):
    """Finds or creates a daily analytics record for the user and updates it."""
    today = date.today()

    analytics = db.query(models.DailyAnalytics).filter(
        models.DailyAnalytics.user_id == user_id,
        models.DailyAnalytics.date == today
    ).first()

    if not analytics:
        analytics = models.DailyAnalytics(
            user_id=user_id,
            date=today,
            total_calories=log.calories_consumed,
            total_protein=log.protein_g,
            total_carbs=log.carbs_g,
            total_fat=log.fat_g
        )
        db.add(analytics)
    else:
        analytics.total_calories += log.calories_consumed
        analytics.total_protein += log.protein_g
        analytics.total_carbs += log.carbs_g
        analytics.total_fat += log.fat_g

    db.commit()


def create_food_log(db: Session, user_id: int, log: schemas.FoodLogCreate):
    log_data = log.model_dump()
    if log_data.get("is_manual"):
        log_data["meal_id"] = None

    db_log = models.FoodLog(**log_data, user_id=user_id)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    update_daily_analytics(db, user_id=user_id, log=log)

    return db_log


def get_logs_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.FoodLog).filter(models.FoodLog.user_id == user_id).offset(skip).limit(limit).all()


def get_analytics_for_user_date(db: Session, user_id: int, query_date: date):
    return db.query(models.DailyAnalytics).filter(
        models.DailyAnalytics.user_id == user_id,
        models.DailyAnalytics.date == query_date
    ).first()


def classify_goal_status(total_calories: float, daily_goal: float) -> schemas.GoalStatus:
    upper_bound = daily_goal * GOAL_MET_UPPER_RATIO
    lower_bound = daily_goal * GOAL_MET_LOWER_RATIO
    if total_calories > upper_bound:
        return "over"
    if total_calories < lower_bound:
        return "under"
    return "met"


def get_weekly_analytics(
    db: Session,
    user_id: int,
    daily_goal: float = DEFAULT_DAILY_CALORIE_GOAL,
    days: int = 7,
) -> schemas.WeeklyAnalytics:
    today = date.today()
    start_date = today - timedelta(days=days - 1)

    records = (
        db.query(models.DailyAnalytics)
        .filter(
            models.DailyAnalytics.user_id == user_id,
            models.DailyAnalytics.date >= start_date,
            models.DailyAnalytics.date <= today,
        )
        .all()
    )
    by_date = {record.date: record for record in records}

    summaries: List[schemas.WeeklyDaySummary] = []
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        record = by_date.get(current_date)
        total_calories = record.total_calories if record else 0.0
        total_protein = record.total_protein if record else 0.0
        total_carbs = record.total_carbs if record else 0.0
        total_fat = record.total_fat if record else 0.0

        summaries.append(
            schemas.WeeklyDaySummary(
                date=current_date,
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fat=total_fat,
                goal_status=classify_goal_status(total_calories, daily_goal),
                daily_calorie_goal=daily_goal,
            )
        )

    return schemas.WeeklyAnalytics(daily_calorie_goal=daily_goal, days=summaries)


def get_nutrition_alerts(
    db: Session,
    user_id: int,
    daily_goal: float = DEFAULT_DAILY_CALORIE_GOAL,
    protein_goal: float = DEFAULT_PROTEIN_GOAL,
    now: Optional[datetime] = None,
) -> schemas.NutritionAlertsResponse:
    """Build today's nutrition alerts from current daily totals (US 2.6)."""
    current_time = now or datetime.now()
    today = current_time.date()
    analytics = get_analytics_for_user_date(db, user_id, today)

    total_calories = analytics.total_calories if analytics else 0.0
    total_protein = analytics.total_protein if analytics else 0.0

    alerts: List[schemas.NutritionAlert] = []

    if total_calories == 0 and current_time.hour >= MISSED_MEAL_HOUR:
        alerts.append(
            schemas.NutritionAlert(
                type="no_meals_logged",
                severity="info",
                message="You have not logged any meals today. Log your intake to stay on track.",
            )
        )
        return schemas.NutritionAlertsResponse(alerts=alerts)

    if total_calories > daily_goal:
        over_by = round(total_calories - daily_goal)
        alerts.append(
            schemas.NutritionAlert(
                type="calories_over",
                severity="warning",
                message=f"Daily calorie limit exceeded by {over_by} kcal ({int(total_calories)}/{int(daily_goal)} kcal).",
            )
        )

    protein_threshold = protein_goal * PROTEIN_LOW_RATIO
    if total_calories >= MIN_CALORIES_FOR_PROTEIN_CHECK and total_protein < protein_threshold:
        alerts.append(
            schemas.NutritionAlert(
                type="protein_low",
                severity="warning",
                message=(
                    f"Low protein intake: {int(total_protein)}g logged "
                    f"(goal {int(protein_goal)}g, aim for at least {int(protein_threshold)}g so far)."
                ),
            )
        )

    if 0 < total_calories < daily_goal * CALORIES_UNDER_RATIO:
        alerts.append(
            schemas.NutritionAlert(
                type="calories_under",
                severity="info",
                message=(
                    f"Calorie intake is well below your daily goal "
                    f"({int(total_calories)}/{int(daily_goal)} kcal)."
                ),
            )
        )

    return schemas.NutritionAlertsResponse(alerts=alerts)


def get_lifetime_progress(
    db: Session,
    user_id: int,
    daily_goal: float = DEFAULT_DAILY_CALORIE_GOAL,
) -> schemas.LifetimeProgress:
    """Lifetime goal adherence since the user first logged food (US 2.3)."""
    records = (
        db.query(models.DailyAnalytics)
        .filter(
            models.DailyAnalytics.user_id == user_id,
            models.DailyAnalytics.total_calories > 0,
        )
        .order_by(models.DailyAnalytics.date.asc())
        .all()
    )

    if not records:
        first_log_at = (
            db.query(func.min(models.FoodLog.timestamp))
            .filter(models.FoodLog.user_id == user_id)
            .scalar()
        )
        tracking_since = first_log_at.date() if first_log_at else None
        return schemas.LifetimeProgress(
            tracking_since=tracking_since,
            days_tracked=0,
            days_goal_met=0,
            days_over_goal=0,
            days_under_goal=0,
            success_rate=0.0,
            daily_calorie_goal=daily_goal,
            current_streak=0,
        )

    days_goal_met = 0
    days_over_goal = 0
    days_under_goal = 0
    met_dates: List[date] = []

    for record in records:
        status = classify_goal_status(record.total_calories, daily_goal)
        if status == "met":
            days_goal_met += 1
            met_dates.append(record.date)
        elif status == "over":
            days_over_goal += 1
        else:
            days_under_goal += 1

    days_tracked = len(records)
    success_rate = round((days_goal_met / days_tracked) * 100, 1)
    current_streak = _calculate_goal_met_streak(met_dates)

    return schemas.LifetimeProgress(
        tracking_since=records[0].date,
        days_tracked=days_tracked,
        days_goal_met=days_goal_met,
        days_over_goal=days_over_goal,
        days_under_goal=days_under_goal,
        success_rate=success_rate,
        daily_calorie_goal=daily_goal,
        current_streak=current_streak,
    )


def _calculate_goal_met_streak(met_dates: List[date]) -> int:
    """Count consecutive goal-met days ending on the most recent met day."""
    if not met_dates:
        return 0

    met_set = set(met_dates)
    streak = 0
    current = max(met_dates)
    while current in met_set:
        streak += 1
        current -= timedelta(days=1)
    return streak
