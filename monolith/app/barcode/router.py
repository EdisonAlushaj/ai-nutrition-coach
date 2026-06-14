from fastapi import APIRouter, HTTPException

from . import schemas, service

router = APIRouter(tags=["barcode"])


@router.get("/foods/barcode/{barcode}", response_model=schemas.BarcodeFood)
def read_food_by_barcode(barcode: str):
    """Look up food nutrition information by barcode (US 3.5.2)."""
    try:
        return service.lookup_barcode(barcode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
