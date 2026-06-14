"""Motivation quote selection logic (US 4.1–4.3)."""

import hashlib
import random
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from ..users import crud as users_crud
from . import schemas
from .quotes import DEFAULT_FALLBACK_MESSAGE, DEFAULT_QUOTES, QUOTES_BY_GOAL


def _goal_category(profile) -> str:
    if profile and profile.goal:
        return profile.goal.value if hasattr(profile.goal, "value") else str(profile.goal)
    return "default"


def _quotes_for_category(category: str) -> list[str]:
    if category in QUOTES_BY_GOAL:
        return QUOTES_BY_GOAL[category]
    return DEFAULT_QUOTES


def get_daily_quote(
    user_id: int,
    category: str,
    query_date: Optional[date] = None,
) -> schemas.MotivationQuote:
    """Same quote all day for a user, rotated by goal category (AC 4.1.2)."""
    today = query_date or date.today()
    quotes = _quotes_for_category(category)
    if not quotes:
        return schemas.MotivationQuote(message=DEFAULT_FALLBACK_MESSAGE, category="default", is_daily=True)

    seed = int(
        hashlib.sha256(f"{user_id}:{today.isoformat()}:{category}".encode()).hexdigest(),
        16,
    )
    message = quotes[seed % len(quotes)]
    return schemas.MotivationQuote(message=message, category=category, is_daily=True)


def get_random_quote(
    category: str,
    exclude: Optional[str] = None,
) -> schemas.MotivationQuote:
    """Random quote from the user's goal category (AC 4.3.2)."""
    quotes = _quotes_for_category(category)
    pool = [quote for quote in quotes if quote != exclude] or quotes
    if not pool:
        return schemas.MotivationQuote(message=DEFAULT_FALLBACK_MESSAGE, category="default", is_daily=False)

    message = random.choice(pool)
    return schemas.MotivationQuote(message=message, category=category, is_daily=False)


def get_daily_quote_for_user(db: Session, user_id: int) -> schemas.MotivationQuote:
    user = users_crud.get_user(db, user_id=user_id)
    category = _goal_category(user.profile if user else None)
    return get_daily_quote(user_id=user_id, category=category)


def get_random_quote_for_user(
    db: Session,
    user_id: int,
    exclude: Optional[str] = None,
) -> schemas.MotivationQuote:
    user = users_crud.get_user(db, user_id=user_id)
    category = _goal_category(user.profile if user else None)
    return get_random_quote(category=category, exclude=exclude)
