import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

sys.modules["tensorflow"] = MagicMock()
sys.modules["tensorflow.keras"] = MagicMock()
sys.modules["tensorflow.keras.applications"] = MagicMock()
sys.modules["PIL"] = MagicMock()
sys.modules["PIL.Image"] = MagicMock()
sys.modules["numpy"] = MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@patch("app.image_processor.predict")
def test_predict_image_success(mock_predict):
    """
    Test the happy path for image prediction.
    """
    mock_predict.return_value = [
        {"label": "pizza", "confidence": 0.98},
        {"label": "lasagna", "confidence": 0.01}
    ]
    
    files = {
        "file": ("pizza.jpg", b"fake_image_bytes", "image/jpeg")
    }
    
    response = client.post("/predict", files=files)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["filename"] == "pizza.jpg"
    assert len(data["predictions"]) == 2
    assert data["predictions"][0]["label"] == "pizza"
    assert data["predictions"][0]["confidence"] == 0.98

def test_predict_invalid_file_type():
    """
    Test that uploading a non-image file returns 400.
    """
    files = {
        "file": ("notes.txt", b"just some text", "text/plain")
    }
    
    response = client.post("/predict", files=files)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "File is not an image."
