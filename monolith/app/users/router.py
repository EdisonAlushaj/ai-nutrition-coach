from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from fastapi.responses import JSONResponse, Response

from . import crud, models, schemas
from ..database import get_db
from .email import send_password_reset_email
from .nutrition_goals import compute_nutrition_goals, default_nutrition_goals, resolve_nutrition_goals_for_user
from .password_validation import validate_new_password
from .security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(tags=["users"])

security = HTTPBearer(auto_error=False)

COOKIE_KWARGS = {
    "httponly": True,
    "samesite": "lax",
    "path": "/",
}


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **COOKIE_KWARGS,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        **COOKIE_KWARGS,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", **COOKIE_KWARGS)
    response.delete_cookie(key="refresh_token", **COOKIE_KWARGS)


def _extract_access_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials],
) -> Optional[str]:
    if credentials and credentials.credentials:
        return credentials.credentials
    return request.cookies.get("access_token")


# --- Shared auth dependencies (importable by other domains) ---

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user from Bearer header or HttpOnly cookie."""
    token = _extract_access_token(request, credentials)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """Dependency to check if current user is admin"""
    if current_user.role != models.RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# --- Registration (gateway exposed this as POST /register) ---

def _create_user(response: Response, user: schemas.UserCreate, db: Session):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = crud.create_user(db=db, user=user)

    # Auto-login logic
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role.value, "id": new_user.id},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": new_user.email})

    _set_auth_cookies(response, access_token, refresh_token)

    return schemas.UserAuthenticated(
        **schemas.User.from_orm(new_user).dict(),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/register", response_model=schemas.UserAuthenticated, status_code=201)
def register_user(response: Response, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return _create_user(response, user, db)


@router.post("/users/", response_model=schemas.UserAuthenticated, status_code=201)
def create_user_endpoint(response: Response, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return _create_user(response, user, db)


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin = Body(...), db: Session = Depends(get_db)):
    """Authenticate and get JWT tokens; also sets session cookies for web clients."""
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "id": user.id},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
    _set_auth_cookies(response, access_token, refresh_token)
    return response


@router.post("/auth/refresh", response_model=schemas.Token)
def refresh_session(request: Request, db: Session = Depends(get_db)):
    """Issue a new access token using the HttpOnly refresh cookie (US 1.3)."""
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_refresh_token(refresh_token)
    if payload is None or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = crud.get_user_by_email(db, email=payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "id": user.id},
        expires_delta=access_token_expires,
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **COOKIE_KWARGS,
    )
    return response


@router.post("/auth/logout", response_model=schemas.MessageResponse)
def logout(response: Response):
    """End the session by clearing auth cookies (US 1.2 / US 1.3)."""
    _clear_auth_cookies(response)
    return schemas.MessageResponse(message="Logged out successfully.")


# --- Password reset (US 1.4) ---

GENERIC_RESET_MESSAGE = schemas.MessageResponse(
    message="If that email exists, a reset link has been sent."
)


@router.post("/auth/forgot-password", response_model=schemas.MessageResponse)
def forgot_password(payload: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset link. Always returns the same message."""
    user = crud.get_user_by_email(db, email=payload.email)
    if user:
        plain_token = crud.create_password_reset_token(db, user)
        send_password_reset_email(user.email, plain_token)
    return GENERIC_RESET_MESSAGE


@router.get("/auth/reset-password/validate", response_model=schemas.MessageResponse)
def validate_reset_password_token(token: str, db: Session = Depends(get_db)):
    """Check whether a reset token is still valid before showing the reset form."""
    db_token = crud.get_valid_reset_token(db, token)
    if db_token is None:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    return schemas.MessageResponse(message="Token is valid.")


@router.post("/auth/reset-password", response_model=schemas.MessageResponse)
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    """Set a new password using a valid reset token."""
    try:
        validate_new_password(payload.new_password)
        crud.reset_password_with_token(db, payload.token, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return schemas.MessageResponse(message="Password updated successfully.")


@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


@router.get("/users/me/nutrition-goals", response_model=schemas.NutritionGoals)
def read_my_nutrition_goals(current_user: models.User = Depends(get_current_user)):
    """Personalized daily calorie and macro targets from profile (US 2.4)."""
    if current_user.profile:
        return compute_nutrition_goals(current_user.profile)
    return default_nutrition_goals()


@router.put("/users/me/profile", response_model=schemas.Profile)
def update_my_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update the authenticated user's fitness profile (US 5.1)."""
    try:
        return crud.update_user_profile(db, current_user, profile_update)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/users/me/change-password", response_model=schemas.MessageResponse)
def change_password(
    payload: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Change password for the authenticated user (US 5.2)."""
    try:
        crud.change_user_password(
            db,
            current_user,
            payload.current_password,
            payload.new_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return schemas.MessageResponse(message="Password updated successfully.")


# --- Admin: list users (gateway exposed GET /admin/users) ---

def _list_users(skip: int, limit: int, db: Session):
    return crud.get_users(db, skip=skip, limit=limit)


@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    return _list_users(skip, limit, db)


@router.get("/admin/users", response_model=List[schemas.User])
def admin_read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    return _list_users(skip, limit, db)


@router.get("/users/{user_id}/nutrition-goals", response_model=schemas.NutritionGoals)
def read_nutrition_goals_for_user(user_id: int, db: Session = Depends(get_db)):
    """Personalized daily calorie and macro targets from profile (US 2.4)."""
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return resolve_nutrition_goals_for_user(db, user_id)


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# --- Admin: promote user (gateway exposed PUT /admin/users/{id}/promote) ---

def _promote(user_id: int, db: Session):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.promote_user_to_admin(db, user=db_user)


@router.put("/users/{user_id}/promote", response_model=schemas.User)
def promote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Promote a user to admin role (Admin only)"""
    return _promote(user_id, db)


@router.put("/admin/users/{user_id}/promote", response_model=schemas.User)
def admin_promote_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user),
):
    """Promote a user to admin role (Admin only)"""
    return _promote(user_id, db)
