from sqlalchemy.orm import Session
from typing import List
from .interfaces import MealPlannerInterface
from .. import models

class WeightLossPlanner(MealPlannerInterface):
    """A planner that recommends meals with lower calories."""
    def generate_plan(self, db: Session) -> List[models.Meal]:
        return db.query(models.Meal).order_by(models.Meal.total_calories.asc()).limit(3).all()

class MuscleGainPlanner(MealPlannerInterface):
    """A planner that recommends meals with higher protein."""
    def generate_plan(self, db: Session) -> List[models.Meal]:
        return db.query(models.Meal).order_by(models.Meal.protein_g.desc()).limit(3).all()

class MaintenancePlanner(MealPlannerInterface):
    """A default planner that recommends a variety of meals."""
    def generate_plan(self, db: Session) -> List[models.Meal]:
        return db.query(models.Meal).limit(3).all()