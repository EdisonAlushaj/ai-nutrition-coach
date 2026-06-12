from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func
from ..database import Base

class FoodLog(Base):
    __tablename__ = "food_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)  # comes from the API path
    meal_id = Column(Integer, nullable=True)  # ID of a meal from the nutrition domain

    food_name = Column(String, nullable=False)  # Name of the meal/food eaten
    calories_consumed = Column(Float, nullable=False)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    date = Column(Date, nullable=False)

    total_calories = Column(Float, default=0.0)
    total_protein = Column(Float, default=0.0)
    total_carbs = Column(Float, default=0.0)
    total_fat = Column(Float, default=0.0)
