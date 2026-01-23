import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.responses import RedirectResponse
from . import schemas 
from typing import List
from datetime import date

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Gateway")

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post("/login")
async def login_user(credentials: schemas.UserLogin):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{services['users']}/login",
                json=credentials.dict()
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

@app.get("/users/me")
async def get_current_user_profile(authorization: str = Header(None)):
    """
    Forward the get current user request to the User Service.
    Requires Authorization header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{services['users']}/users/me",
                headers={"Authorization": authorization}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The User Service is currently unavailable: {str(e)}")

@app.get("/users/{user_id}", response_model=schemas.User)
async def get_user_by_id(user_id: int):
    """
    Forward the request to get a specific user by ID to the User Service.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{services['users']}/users/{user_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The User Service is unavailable: {str(e)}")

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

@app.get("/ingredients", response_model=List[schemas.Ingredient])
async def get_all_ingredients():
    """Forward request to get all ingredients from Nutrition Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{services['nutrition']}/ingredients/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Nutrition Service is unavailable: {str(e)}")

# --- Admin Endpoints ---

@app.get("/admin/users", response_model=List[schemas.User])
async def admin_get_all_users(authorization: str = Header(None)):
    """Forward request to get all users from User Service"""
    async with httpx.AsyncClient() as client:
        try:
            # Pass the auth header to the underlying service
            headers = {"Authorization": authorization} if authorization else {}
            response = await client.get(f"{services['users']}/users/", headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The User Service is unavailable: {str(e)}")

@app.put("/admin/users/{user_id}/promote", response_model=schemas.User)
async def admin_promote_user(user_id: int, authorization: str = Header(None)):
    """Forward request to promote a user to admin"""
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": authorization} if authorization else {}
            response = await client.put(f"{services['users']}/users/{user_id}/promote", headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The User Service is unavailable: {str(e)}")

@app.post("/admin/ingredients")
async def admin_create_ingredient(ingredient: schemas.IngredientCreate):
    """Forward request to create an ingredient in Nutrition Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{services['nutrition']}/ingredients/",
                json=ingredient.dict()
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"The Nutrition Service is unavailable: {str(e)}")

@app.post("/admin/meals")
async def admin_create_meal(meal: schemas.MealCreate):
    """Forward request to create a meal in Nutrition Service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{services['nutrition']}/meals/",
                json=meal.dict()
            )
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

@app.get("/users/{user_id}/analytics/{query_date}", response_model=schemas.DailyAnalytics)
async def get_analytics_by_date(user_id: int, query_date: date):
    """
    Get nutritional summary for a specific date.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{services['logging']}/users/{user_id}/analytics/{query_date.isoformat()}"
            )
            response.raise_for_status()
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