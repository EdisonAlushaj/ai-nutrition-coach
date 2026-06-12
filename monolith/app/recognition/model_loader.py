import tensorflow as tf

class Model:
    """A Singleton class to ensure the ML model is loaded only once."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("---Loading ResNet50 model into memory...---")
            cls._instance = super(Model, cls).__new__(cls)
            cls._instance.model = tf.keras.applications.ResNet50(weights="imagenet")
            print("---Model loaded successfully---")
        return cls._instance

    def get_model(self):
        return self.model


# Lazy load: the heavy ResNet50 weights are only loaded on the first /predict
# request, so importing this module (and booting the app) stays fast.
_model_singleton = None


def get_model():
    global _model_singleton
    if _model_singleton is None:
        _model_singleton = Model()
    return _model_singleton.get_model()
