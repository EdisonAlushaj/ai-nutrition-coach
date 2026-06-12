from .interfaces import MealPlannerInterface
from .planners import WeightLossPlanner, MuscleGainPlanner, MaintenancePlanner
from ..schemas import GoalEnum

class MealPlanFactory:
    @staticmethod
    def create_planner(goal: GoalEnum) -> MealPlannerInterface:
        if goal == GoalEnum.lose_weight:
            return WeightLossPlanner()
        elif goal == GoalEnum.gain_muscle:
            return MuscleGainPlanner()
        elif goal == GoalEnum.maintain:
            return MaintenancePlanner()
        else:
            return MaintenancePlanner()
