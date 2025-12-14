import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from . import schemas 

app = FastAPI(title="API Gateway")

services = {
    "users": "http://user-service:8000",
    "nutrition": "http://nutrition-service:8000",
    "logging": "http://logging-analytics-service:8000" 
}

@app.get("/")
async def root():
    """Redirect root path to Swagger documentation"""
    return RedirectResponse(url="/docs")

@app.post("/register", status_code=201)
async def register_user(user_data: schemas.UserCreate):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{services['users']}/users/",
                json=user_data.dict() 
            )
            
            response.raise_for_status()
        
            return response.json()
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"The User Service is currently unavailable: {str(e)}"
            )

@app.get("/meals")
async def get_meals():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(f"{services['nutrition']}/meals/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.json()
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"The Nutrition Service is currently unavailable: {str(e)}"
            )

@app.post("/users/{user_id}/logs")
async def log_food_for_user(user_id: int, log_data: schemas.FoodLogCreate):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{services['logging']}/users/{user_id}/logs/",
                json=log_data.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Logging Service is unavailable: {str(e)}")

@app.get("/users/{user_id}/meal-plan")
async def get_meal_plan(user_id: int):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(f"{services['nutrition']}/users/{user_id}/meal-plan")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Nutrition Service is unavailable: {str(e)}")