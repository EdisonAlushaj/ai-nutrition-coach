from fastapi import APIRouter, UploadFile, File, HTTPException
from .model_loader import get_model
from . import image_processor

router = APIRouter(tags=["recognition"])


async def _predict(file: UploadFile):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")
    try:
        image_bytes = await file.read()
        model = get_model()  # lazy-loads ResNet50 on first call
        predictions = image_processor.predict(model, image_bytes)
        return {"filename": file.filename, "predictions": predictions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the image: {str(e)}")


@router.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """Receives an image file, processes it, and returns the top 3 predictions."""
    return await _predict(file)


@router.post("/recognize-food")
async def recognize_food(file: UploadFile = File(...)):
    """Gateway-facing alias of /predict."""
    return await _predict(file)
