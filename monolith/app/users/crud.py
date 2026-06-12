from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from .security import get_password_hash, verify_password
from .models import RoleEnum

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=getattr(user, 'role', RoleEnum.user)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    profile_data = user.profile.dict()
    db_profile = models.Profile(**profile_data, user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password"""
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def promote_user_to_admin(db: Session, user: models.User):
    user.role = RoleEnum.admin
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
