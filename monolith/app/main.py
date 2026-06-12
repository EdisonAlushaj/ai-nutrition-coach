import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .database import Base, engine

# Import models from every domain so that their tables are registered on the
# shared Base.metadata BEFORE create_all() runs.
from .users import models as user_models  # noqa: F401
from .nutrition import models as nutrition_models  # noqa: F401
from .logging_analytics import models as logging_models  # noqa: F401

from .users.router import router as users_router
from .nutrition.router import router as nutrition_router
from .logging_analytics.router import router as logging_router

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="AI Nutrition Coach (Monolith)",
    description="Single-process version of the AI Nutrition Coach. "
    "Combines user, nutrition, logging/analytics and food-recognition into one app.",
)

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


@app.on_event("startup")
def on_startup():
    # Creates all tables (users, profiles, meals, ingredients, meal_ingredients,
    # food_logs, daily_analytics) in the single shared database.
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    """Redirect root path to Swagger documentation"""
    return RedirectResponse(url="/docs")


# --- Domain routers ---
app.include_router(users_router)
app.include_router(nutrition_router)
app.include_router(logging_router)

# Food recognition pulls in TensorFlow (heavy). Guard the import so a missing or
# broken TF install degrades gracefully — the rest of the API still boots.
try:
    from .recognition.router import router as recognition_router

    app.include_router(recognition_router)
except Exception as exc:  # pragma: no cover - depends on optional heavy deps
    logger.warning("Food recognition disabled (could not load TensorFlow): %s", exc)
