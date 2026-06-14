from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets

from . import models, schemas
from .security import get_password_hash, verify_password, PASSWORD_RESET_EXPIRE_MINUTES
from .password_validation import validate_new_password
from .models import RoleEnum

FORGOT_PASSWORD_MESSAGE = "If that email exists, a reset link has been sent."


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def get_user_by_email(db: Session, email: str):
    normalized_email = email.strip().lower()
    return (
        db.query(models.User)
        .options(joinedload(models.User.profile))
        .filter(models.User.email == normalized_email)
        .first()
    )

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


def invalidate_reset_tokens_for_user(db: Session, user_id: int) -> None:
    now = datetime.now(timezone.utc)
    tokens = (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.user_id == user_id,
            models.PasswordResetToken.used_at.is_(None),
        )
        .all()
    )
    for token in tokens:
        token.used_at = now
        db.add(token)
    db.commit()


def create_password_reset_token(db: Session, user: models.User) -> str:
    invalidate_reset_tokens_for_user(db, user.id)
    plain_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
    db_token = models.PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_reset_token(plain_token),
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()
    return plain_token


def get_valid_reset_token(db: Session, plain_token: str) -> Optional[models.PasswordResetToken]:
    token_hash = _hash_reset_token(plain_token)
    now = datetime.now(timezone.utc)
    return (
        db.query(models.PasswordResetToken)
        .filter(
            models.PasswordResetToken.token_hash == token_hash,
            models.PasswordResetToken.used_at.is_(None),
            models.PasswordResetToken.expires_at > now,
        )
        .first()
    )


def reset_password_with_token(db: Session, plain_token: str, new_password: str) -> models.User:
    validate_new_password(new_password)
    db_token = get_valid_reset_token(db, plain_token)
    if db_token is None:
        raise ValueError("Invalid or expired reset token.")

    user = get_user(db, db_token.user_id)
    if user is None:
        raise ValueError("Invalid or expired reset token.")

    user.hashed_password = get_password_hash(new_password)
    db_token.used_at = datetime.now(timezone.utc)
    db.add(user)
    db.add(db_token)
    db.commit()
    db.refresh(user)
    return user


def change_user_password(
    db: Session,
    user: models.User,
    current_password: str,
    new_password: str,
) -> models.User:
    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Current password is incorrect.")

    validate_new_password(new_password)

    if verify_password(new_password, user.hashed_password):
        raise ValueError("New password must be different from your current password.")

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session,
    user: models.User,
    profile_update: schemas.ProfileUpdate,
) -> models.Profile:
    if user.profile is None:
        raise ValueError("Profile not found.")

    for field, value in profile_update.model_dump().items():
        setattr(user.profile, field, value)

    db.add(user.profile)
    db.commit()
    db.refresh(user.profile)
    return user.profile
