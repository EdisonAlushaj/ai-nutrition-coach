from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .security import create_access_token, create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
<<<<<<< HEAD
from fastapi.responses import JSONResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")

=======
from fastapi.responses import JSONResponse, Response

app = FastAPI(title="User Service")

@app.on_event("startup")
def startup_db_client():
    models.Base.metadata.create_all(bind=engine)


>>>>>>> 60421828bf4efc6682c762e8abb64f1d9b2c8144

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    """Get the current authenticated user from JWT token"""
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
            detail="The user doesn't have enough privileges"
        )
    return current_user

<<<<<<< HEAD
@app.post("/users/", response_model=schemas.User)
def create_user_endpoint(user: schemas.UserCreate, db: Session = Depends(get_db)):
=======
@app.post("/users/", response_model=schemas.UserAuthenticated)
def create_user_endpoint(response: Response, user: schemas.UserCreate, db: Session = Depends(get_db)):
>>>>>>> 60421828bf4efc6682c762e8abb64f1d9b2c8144
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(db=db, user=user)
    
    # Auto-login logic
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "role": new_user.role.value}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": new_user.email}
    )
    
    # Set tokens as HttpOnly cookies:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    
    # Combine user data and token data for the response
    return schemas.UserAuthenticated(
        **schemas.User.from_orm(new_user).dict(),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin = Body(...), db: Session = Depends(get_db)):
    """Login endpoint to authenticate and get JWT tokens and optionally set session cookies for web clients. Accepts application/json."""
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )
    # Set tokens as HttpOnly cookies:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    return response

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin = Body(...), db: Session = Depends(get_db)):
    """Login endpoint to authenticate and get JWT tokens and optionally set session cookies for web clients. Accepts application/json."""
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )
    # Set tokens as HttpOnly cookies:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=7*24*60*60,
        samesite="lax"
    )
    return response

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.put("/users/{user_id}/promote", response_model=schemas.User)
def promote_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_admin_user)
):
    """Promote a user to admin role (Admin only)"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.promote_user_to_admin(db, user=db_user)