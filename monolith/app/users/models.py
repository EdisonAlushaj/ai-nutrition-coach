from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.orm import relationship
from ..database import Base
# Note: We keep the enums here as they are specific to the Profile model
from .schemas import GenderEnum, ActivityLevelEnum, GoalEnum
import enum

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user, nullable=False)
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    gender = Column(Enum(GenderEnum))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    activity_level = Column(Enum(ActivityLevelEnum))
    goal = Column(Enum(GoalEnum))
    user = relationship("User", back_populates="profile")
