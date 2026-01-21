from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import os

# --- Configuration ---
# This SECRET_KEY and ALGORITHM MUST be the exact same as in the user_service.
# We will get them from environment variables for good practice.
SECRET_KEY = os.getenv("SECRET_KEY", "a-silly-default-secret-key-for-dev")
ALGORITHM = "HS256"

# This creates the "Authorize" button in the Swagger UI docs
security = HTTPBearer()

# --- Pydantic Schema for the data we expect inside the token ---
class TokenPayload(BaseModel):
    sub: str      # The user's email
    user_id: int  # The user's unique ID
    role: str     # The user's role ('user' or 'admin')

# --- The Security Guard Dependency ---
def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    """
    A dependency to validate a JWT and return its payload.
    This trusts the token's content without needing a database call,
    which is fast and efficient for microservices.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate that the necessary fields are in the token
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        
        # Use our Pydantic model to parse and validate the payload
        token_data = TokenPayload(**payload)

    except (JWTError, ValueError, TypeError):
        # This will catch any errors during decoding or validation
        raise credentials_exception
    
    return token_data