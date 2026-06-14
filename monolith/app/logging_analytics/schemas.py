from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, List, Literal
from datetime import datetime, date


class FoodLogBase(BaseModel):
    food_name: str
    calories_consumed: float
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    meal_id: Optional[int] = None
    is_manual: bool = False

    @field_validator("food_name")
    @classmethod
    def food_name_not_empty(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Food name must not be empty.")
        return trimmed

    @model_validator(mode="after")
    def validate_manual_macros(self):
        if not self.is_manual:
            return self

        for field_name in ("calories_consumed", "protein_g", "carbs_g", "fat_g"):
            if getattr(self, field_name) <= 0:
                raise ValueError("Manual entries require positive values for all nutrition fields.")
        return self


class FoodLogCreate(FoodLogBase):
    pass  # The user_id will come from the URL path


class FoodLog(FoodLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class DailyAnalytics(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float

    class Config:
        from_attributes = True


GoalStatus = Literal["met", "over", "under"]


class WeeklyDaySummary(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    goal_status: GoalStatus
    daily_calorie_goal: float


class WeeklyAnalytics(BaseModel):
    daily_calorie_goal: float
    days: List[WeeklyDaySummary]


AlertType = Literal["calories_over", "calories_under", "protein_low", "no_meals_logged"]
AlertSeverity = Literal["warning", "info"]


class NutritionAlert(BaseModel):
    type: AlertType
    severity: AlertSeverity
    message: str


class NutritionAlertsResponse(BaseModel):
    alerts: List[NutritionAlert]


class LifetimeProgress(BaseModel):
    tracking_since: Optional[date] = None
    days_tracked: int
    days_goal_met: int
    days_over_goal: int
    days_under_goal: int
    success_rate: float
    daily_calorie_goal: float
    current_streak: int
