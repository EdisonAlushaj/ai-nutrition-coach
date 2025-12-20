import tensorflow as tf

class Model:
    """A Singleton class to ensure the ML model is loaded only once."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("---Loading MobileNetV2 model into memory...---")
            cls._instance = super(Model, cls).__new__(cls)
            cls._instance.model = tf.keras.applications.MobileNetV2(weights="imagenet")
            print("---Model loaded successfully---")
        return cls._instance

    def get_model(self):
        return self.model

model_singelton = Model()

def get_model():
    return model_singelton.get_model()