from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    password_reset_tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="password_reset_tokens")

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
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    target_weight_kg = Column(Float, nullable=True)
    user = relationship("User", back_populates="profile")
