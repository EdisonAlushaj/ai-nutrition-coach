from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List
from .. import models

class MealPlannerInterface(ABC):
    @abstractmethod
    def generate_plan(self, db: Session) -> List[models.Meal]:
        pass