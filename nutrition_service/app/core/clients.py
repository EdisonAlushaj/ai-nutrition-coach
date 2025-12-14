import httpx
from .. import schemas

USER_SERVICE_URL = "http://user-service:8000"

async def get_user_profile(user_id: int) -> schemas.UserProfile:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
            response.raise_for_status()
            
            full_user_data = response.json()
            profile_data = full_user_data.get("profile")

            if not profile_data:
                return None

            return schemas.UserProfile(**profile_data)
        except (httpx.RequestError, httpx.HTTPStatusError):
            return None