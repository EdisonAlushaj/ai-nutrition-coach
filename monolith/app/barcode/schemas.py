from pydantic import BaseModel
from typing import Optional


class BarcodeFood(BaseModel):
    barcode: str
    food_name: str
    calories_consumed: float
    protein_g: float
    carbs_g: float
    fat_g: float
    brand: Optional[str] = None
    source: str
