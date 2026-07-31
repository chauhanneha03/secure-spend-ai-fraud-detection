import os

class Config:
    SECRET_KEY = "creditcardfrauddetection2025"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DATABASE = os.path.join(BASE_DIR, "fraud_detection.db")

    MODELS_FOLDER = os.path.join(BASE_DIR, "models")

    SVM_MODEL = os.path.join(MODELS_FOLDER, "svm_model.pkl")
    KNN_MODEL = os.path.join(MODELS_FOLDER, "knn_model.pkl")
    ANN_MODEL = os.path.join(MODELS_FOLDER, "ann_model.keras")

    DATASET = os.path.join(BASE_DIR, "creditcard.csv")