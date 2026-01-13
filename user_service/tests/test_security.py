from app.security import verify_password, get_password_hash, create_access_token, verify_token, create_refresh_token, verify_refresh_token
from app.models import RoleEnum
from datetime import timedelta

def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_access_token():
    data = {"sub": "test@example.com", "role": RoleEnum.user.value}
    token = create_access_token(data=data)
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"
    assert payload["role"] == "user"

def test_refresh_token():
    data = {"sub": "test@example.com"}
    token = create_refresh_token(data=data)
    # Assuming verify_refresh_token uses the same SECRET_KEY/ALGORITHM as verify_token for now based on security.py content
    payload = verify_refresh_token(token) 
    assert payload is not None
    assert payload["sub"] == "test@example.com"

def test_token_expiration():
    data = {"sub": "test@example.com", "role": "user"}
    # Create a token that expired 1 minute ago
    token = create_access_token(data=data, expires_delta=timedelta(minutes=-1))
    payload = verify_token(token)
    assert payload is None
