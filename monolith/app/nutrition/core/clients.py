"""In-process replacement for the old HTTP call to the User Service.

In the microservice version this module used httpx to call
``http://user-service:8000/users/{id}``. In the monolith the user data lives
in the same process and database, so we call the users CRUD layer directly.
"""
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas
from ...users import crud as users_crud


def get_user_profile(db: Session, user_id: int) -> Optional[schemas.UserProfile]:
    user = users_crud.get_user(db, user_id=user_id)
    if not user or not user.profile:
        return None
    # user.profile.goal is the users-domain GoalEnum; pass its value so Pydantic
    # coerces it into the nutrition-domain GoalEnum.
    return schemas.UserProfile(goal=user.profile.goal.value)
