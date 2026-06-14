"""Compute personalized daily nutrition targets from user profile (US 2.4)."""

from typing import Optional

from sqlalchemy.orm import Session

from . import crud, schemas
from .schemas import ActivityLevelEnum, GenderEnum, GoalEnum

DEFAULT_DAILY_CALORIES = 2000
DEFAULT_PROTEIN_G = 150
DEFAULT_CARBS_G = 250
DEFAULT_FAT_G = 70
MIN_DAILY_CALORIES = 1200

ACTIVITY_MULTIPLIERS = {
    ActivityLevelEnum.sedentary: 1.2,
    ActivityLevelEnum.lightly_active: 1.375,
    ActivityLevelEnum.moderately_active: 1.55,
    ActivityLevelEnum.very_active: 1.725,
    ActivityLevelEnum.extra_active: 1.9,
}

GOAL_CALORIE_ADJUSTMENTS = {
    GoalEnum.lose_weight: -500,
    GoalEnum.maintain: 0,
    GoalEnum.gain_muscle: 300,
}

PROTEIN_G_PER_KG = {
    GoalEnum.lose_weight: 2.0,
    GoalEnum.maintain: 1.6,
    GoalEnum.gain_muscle: 2.2,
}


def _bmr(weight_kg: float, height_cm: float, age: int, gender: GenderEnum) -> float:
    """Mifflin-St Jeor basal metabolic rate."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == GenderEnum.male:
        return base + 5
    return base - 161


def compute_nutrition_goals(profile) -> schemas.NutritionGoals:
    """Derive daily calorie and macro targets from a profile record."""
    gender = profile.gender if isinstance(profile.gender, GenderEnum) else GenderEnum(profile.gender)
    activity = (
        profile.activity_level
        if isinstance(profile.activity_level, ActivityLevelEnum)
        else ActivityLevelEnum(profile.activity_level)
    )
    goal = profile.goal if isinstance(profile.goal, GoalEnum) else GoalEnum(profile.goal)

    tdee = _bmr(profile.weight_kg, profile.height_cm, profile.age, gender) * ACTIVITY_MULTIPLIERS[activity]
    daily_calories = max(
        MIN_DAILY_CALORIES,
        round(tdee + GOAL_CALORIE_ADJUSTMENTS[goal]),
    )

    protein_g = round(profile.weight_kg * PROTEIN_G_PER_KG[goal])
    fat_g = round((daily_calories * 0.25) / 9)
    remaining_calories = daily_calories - (protein_g * 4) - (fat_g * 9)
    carbs_g = max(0, round(remaining_calories / 4))

    return schemas.NutritionGoals(
        daily_calories=float(daily_calories),
        protein_g=float(protein_g),
        carbs_g=float(carbs_g),
        fat_g=float(fat_g),
        fitness_goal=goal.value,
        current_weight_kg=float(profile.weight_kg),
        target_weight_kg=float(profile.target_weight_kg) if profile.target_weight_kg else None,
    )


def default_nutrition_goals() -> schemas.NutritionGoals:
    return schemas.NutritionGoals(
        daily_calories=float(DEFAULT_DAILY_CALORIES),
        protein_g=float(DEFAULT_PROTEIN_G),
        carbs_g=float(DEFAULT_CARBS_G),
        fat_g=float(DEFAULT_FAT_G),
    )


def resolve_nutrition_goals_for_user(
    db: Session,
    user_id: int,
    daily_calories_override: Optional[float] = None,
    protein_g_override: Optional[float] = None,
) -> schemas.NutritionGoals:
    """Load profile-based goals, allowing optional query-param overrides."""
    user = crud.get_user(db, user_id=user_id)
    if user and user.profile:
        goals = compute_nutrition_goals(user.profile)
    else:
        goals = default_nutrition_goals()

    if daily_calories_override is not None:
        goals = goals.model_copy(update={"daily_calories": daily_calories_override})
    if protein_g_override is not None:
        goals = goals.model_copy(update={"protein_g": protein_g_override})

    return goals
