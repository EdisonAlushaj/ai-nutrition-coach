"""Barcode product lookup (US 3.5)."""

from typing import Optional

import httpx

from . import schemas

LOCAL_PRODUCTS = {
    "1234567890123": {
        "food_name": "Demo Protein Bar",
        "calories_consumed": 220.0,
        "protein_g": 20.0,
        "carbs_g": 25.0,
        "fat_g": 8.0,
        "brand": "Demo Foods",
    },
    "4001686341234": {
        "food_name": "Greek Yogurt Cup",
        "calories_consumed": 120.0,
        "protein_g": 15.0,
        "carbs_g": 9.0,
        "fat_g": 3.0,
        "brand": "Demo Dairy",
    },
}


def _normalize_barcode(barcode: str) -> str:
    return "".join(ch for ch in barcode.strip() if ch.isdigit())


def _lookup_local(barcode: str) -> Optional[schemas.BarcodeFood]:
    product = LOCAL_PRODUCTS.get(barcode)
    if not product:
        return None
    return schemas.BarcodeFood(barcode=barcode, source="local", **product)


def _parse_open_food_facts(barcode: str, payload: dict) -> Optional[schemas.BarcodeFood]:
    if payload.get("status") != 1:
        return None

    product = payload.get("product") or {}
    name = product.get("product_name") or product.get("generic_name")
    if not name:
        return None

    nutriments = product.get("nutriments") or {}

    def pick(*keys: str) -> Optional[float]:
        for key in keys:
            value = nutriments.get(key)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
        return None

    calories = pick("energy-kcal_serving", "energy-kcal_100g", "energy_serving", "energy_100g")
    protein = pick("proteins_serving", "proteins_100g")
    carbs = pick("carbohydrates_serving", "carbohydrates_100g")
    fat = pick("fat_serving", "fat_100g")

    if calories is None or protein is None or carbs is None or fat is None:
        return None

    brand = product.get("brands") or None
    if brand and "," in brand:
        brand = brand.split(",")[0].strip()

    return schemas.BarcodeFood(
        barcode=barcode,
        food_name=name.strip(),
        calories_consumed=round(calories, 1),
        protein_g=round(protein, 1),
        carbs_g=round(carbs, 1),
        fat_g=round(fat, 1),
        brand=brand,
        source="open_food_facts",
    )


def _lookup_open_food_facts(barcode: str) -> Optional[schemas.BarcodeFood]:
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return _parse_open_food_facts(barcode, response.json())


def lookup_barcode(barcode: str) -> schemas.BarcodeFood:
    """Resolve nutrition info for a product barcode."""
    normalized = _normalize_barcode(barcode)
    if not normalized:
        raise ValueError("Invalid barcode.")

    local = _lookup_local(normalized)
    if local:
        return local

    external = _lookup_open_food_facts(normalized)
    if external:
        return external

    raise LookupError(f"No product found for barcode {normalized}.")
