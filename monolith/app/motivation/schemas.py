from pydantic import BaseModel


class MotivationQuote(BaseModel):
    message: str
    category: str
    is_daily: bool = True
