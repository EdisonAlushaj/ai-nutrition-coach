import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from . import schemas 
from typing import List
from datetime import date

app = FastAPI(title="API Gateway")

services = {
    "users": "http://user-service:8000",
    "nutrition": "http://nutrition-service:8000",
    "logging": "http://logging-analytics-service:8000",
    "recognition": "http://food-recognition-service:8000"
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

@app.get("/meals/{meal_id}")
async def get_meal_by_id(meal_id: int):
    """
    Forwards a request to get a single meal by its ID from the nutrition service.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{services['nutrition']}/meals/{meal_id}")
            
            # Forward the error if the meal was not found
            response.raise_for_status()
            
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Nutrition Service is unavailable: {str(e)}")

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

@app.get("/users/{user_id}/logs", response_model=List[schemas.FoodLog])
async def get_logs_for_user(user_id: int):
    """
    Forwards a request to get the food log history for a specific user.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request to the logging service
            response = await client.get(f"{services['logging']}/users/{user_id}/logs/")
            
            response.raise_for_status()
            
            return response.json()
        except httpx.HTTPStatusError as e:
            # Forward any errors from the downstream service
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            # Handle cases where the service is down
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

@app.get("/users/{user_id}/analytics/today", response_model=schemas.DailyAnalytics)
async def get_today_analytics_for_user(user_id: int):
    """
    A convenience endpoint to get the nutritional summary for the current day for a specific user.
    """
    # Step 1: Get today's date and format it as a string (YYYY-MM-DD)
    today_date = date.today().isoformat()
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 2: Call the more specific endpoint on the logging service, passing today's date
            response = await client.get(
                f"{services['logging']}/users/{user_id}/analytics/{today_date}"
            )
            
            response.raise_for_status()
            
            # Step 3: Return the response
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Logging Service is unavailable: {str(e)}")

@app.post("/recognize-food")
async def recognize_food(file: UploadFile = File(...)):
    """
    Receives a food image, forwards it to the recognition service,
    and returns the prediction results.
    """
    async with httpx.AsyncClient() as client:
        try:
            files = {'file': (file.filename, await file.read(), file.content_type)}
            
            response = await client.post(
                f"{services['recognition']}/predict",
                files=files
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Food Recognition Service is unavailable: {str(e)}")

@app.get("/search-food")
async def search_food(name: str):
    """
    Searches for a food item by name in the nutrition service.
    Example: /search-food?name=pizza
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{services['nutrition']}/meals/search",
                params={"name": name}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Nutrition Service is unavailable: {str(e)}")