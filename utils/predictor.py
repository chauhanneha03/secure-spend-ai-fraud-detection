import os
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.preprocessing import StandardScaler
from config import Config


class FraudPredictor:

    def __init__(self):
        print("Loading AI Models...")

        self.svm_model = joblib.load(Config.SVM_MODEL)
        self.knn_model = joblib.load(Config.KNN_MODEL)
        self.ann_model = load_model(Config.ANN_MODEL)

        print("All Models Loaded Successfully!")

    def preprocess(self, data):

        df = pd.DataFrame([data])

        if "NormalizedAmount" in df.columns:
            scaler = StandardScaler()
            df["NormalizedAmount"] = scaler.fit_transform(
                df[["NormalizedAmount"]]
            )

        return df

    def predict(self, transaction):

        transaction = self.preprocess(transaction)

        svm_prediction = self.svm_model.predict(transaction)[0]
        knn_prediction = self.knn_model.predict(transaction)[0]

        ann_probability = float(self.ann_model.predict(transaction, verbose=0)[0][0])
        ann_prediction = 1 if ann_probability >= 0.5 else 0

        return {

            "SVM": {
                "prediction": "Fraud" if svm_prediction else "Legitimate"
            },

            "KNN": {
                "prediction": "Fraud" if knn_prediction else "Legitimate"
            },

            "ANN": {
                "prediction": "Fraud" if ann_prediction else "Legitimate",
                "confidence": round(ann_probability * 100, 2)
            }

        }


predictor = FraudPredictor()