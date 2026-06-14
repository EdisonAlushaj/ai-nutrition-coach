from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
import enum


def _normalize_email(value: str) -> str:
    return value.strip().lower()

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"

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

class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: int
    gender: GenderEnum
    height_cm: float
    weight_kg: float
    activity_level: ActivityLevelEnum
    goal: GoalEnum
    target_weight_kg: Optional[float] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_names(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("age")
    @classmethod
    def age_positive(cls, value: int) -> int:
        if value < 1 or value > 120:
            raise ValueError("Age must be between 1 and 120.")
        return value

    @field_validator("height_cm", "weight_kg")
    @classmethod
    def measurements_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Height and weight must be greater than zero.")
        return value

    @field_validator("target_weight_kg")
    @classmethod
    def target_weight_positive(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value <= 0:
            raise ValueError("Target weight must be greater than zero.")
        return value

class Profile(ProfileBase):
    id: int
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    target_weight_kg: Optional[float] = None
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.user

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)

class UserCreate(UserBase):
    password: str
    profile: ProfileCreate
    role: RoleEnum = RoleEnum.user

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password",
                "profile": {
                    "age": 30,
                    "gender": "male",
                    "height_cm": 180,
                    "weight_kg": 75,
                    "activity_level": "moderately_active",
                    "goal": "maintain"
                }
            }
        }

class User(UserBase):
    id: int
    is_active: bool
    profile: Optional[Profile] = None
    role: RoleEnum
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "you@example.com",
                "password": "your-password-here",
            }
        }

class UserAuthenticated(User):
    access_token: str
    refresh_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str


class NutritionGoals(BaseModel):
    daily_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fitness_goal: Optional[str] = None
    current_weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self
