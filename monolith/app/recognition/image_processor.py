import numpy as np
from PIL import Image
import tensorflow as tf
from io import BytesIO

IMAGE_SIZE = 224

def preprocess_image(image_bytes: bytes) -> tf.Tensor:
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_batch = np.expand_dims(image_array, axis=0)
    return tf.keras.applications.resnet50.preprocess_input(image_batch)

def predict(model, image_bytes: bytes) -> list:
    processed_image = preprocess_image(image_bytes)
    predictions = model.predict(processed_image)

    decoded_predictions = tf.keras.applications.resnet50.decode_predictions(predictions, top=3)[0]

    results = []
    for _, label, confidence in decoded_predictions:
        # Clean up labels (e.g., pomegranate -> Pomegranate, Granny_Smith -> Granny Smith)
        clean_label = label.replace('_', ' ').capitalize()
        results.append({"label": clean_label, "confidence": float(confidence)})

    return results
