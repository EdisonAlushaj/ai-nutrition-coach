from pydantic import BaseModel, EmailStr
from typing import Optional
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

class ActivityLevelEnum(str, enum.Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extra_active = "extra_active"

class GoalEnum(str, enum.Enum):
    lose_weight = "lose_weight"
    maintain = "maintain"
    gain_muscle = "gain_muscle"

class ProfileBase(BaseModel):
    age: int
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    profile: ProfileCreate

class User(UserBase):
    id: int
    is_active: bool
    profile: Optional[Profile] = None
    class Config:
        from_attributes = True