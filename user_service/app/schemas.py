from pydantic import BaseModel, EmailStr
from typing import Optional
import enum

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

class Profile(ProfileBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    role: RoleEnum = RoleEnum.user

class UserCreate(UserBase):
    password: str
    profile: ProfileCreate
<<<<<<< HEAD
    role: RoleEnum = RoleEnum.user
=======
    # role field removed to hide it from Swagger input

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
>>>>>>> 60421828bf4efc6682c762e8abb64f1d9b2c8144

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
<<<<<<< HEAD
    password: str
=======
    password: str

class UserAuthenticated(User, Token):
    pass
>>>>>>> 60421828bf4efc6682c762e8abb64f1d9b2c8144
