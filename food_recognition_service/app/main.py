from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from .model_loader import get_model
from . import image_processor

app = FastAPI(
    title="Food Recognition Service",
    description="An API that uses a pre-trained model to recognize food in images."
)

@app.get("/")
async def root():
    """Redirect root path to Swagger documentation"""
    return RedirectResponse(url="/docs")

model = get_model()

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Receives an image file, processes it, and returns the top 3 predictions.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")

    try:
        image_bytes = await file.read()
        predictions = image_processor.predict(model, image_bytes)
        return {"filename": file.filename, "predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the image: {str(e)}")