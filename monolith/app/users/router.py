from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from fastapi.responses import JSONResponse, Response

from . import crud, models, schemas
from ..database import get_db
from .security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(tags=["users"])

security = HTTPBearer()


# --- Shared auth dependencies (importable by other domains) ---

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Get the current authenticated user from JWT token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
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

    # Set tokens as HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )

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
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )
    return response


@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user


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
