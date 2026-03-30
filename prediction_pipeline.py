import joblib
import numpy as np
import os
import logging
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

logger = logging.getLogger(__name__)

class PhishingDetector:
    def __init__(self):
        try:
            self.lr_model = joblib.load('models/lr_model.pkl')
            self.rf_model = joblib.load('models/rf_model.pkl')
            self.tfidf_vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
            self.tokenizer = joblib.load('models/tokenizer.pkl')
            self.lstm_model = load_model('models/lstm_model.h5')
            logger.info("All models loaded successfully.")
            self.models_loaded = True
        except Exception as e:
            logger.warning(f"Models could not be loaded: {e}. System will require training.")
            self.models_loaded = False
            
        self.max_len = 100
        # Cascading Thresholds as per PHISHGUARD_COMPLETE_GUIDE.md
        self.lr_threshold = 0.70
        self.rf_threshold = 0.60
    
    def predict(self, email_text: str) -> dict:
        if not self.models_loaded:
            return {
                'prediction': 'Error',
                'confidence': 0.0,
                'model_stage': 'None (Models not trained)',
                'stage_number': 0
            }

        # --- Stage 1: Logistic Regression (Fast Filter) ---
        tfidf_features = self.tfidf_vectorizer.transform([email_text])
        lr_proba = self.lr_model.predict_proba(tfidf_features)[0][1]
        
        if lr_proba > self.lr_threshold or lr_proba < (1 - self.lr_threshold):
            prediction = 'Phishing' if lr_proba >= 0.5 else 'Legitimate'
            confidence = lr_proba if lr_proba >= 0.5 else 1 - lr_proba
            return {
                'prediction': prediction,
                'confidence': float(confidence),
                'model_stage': 'Logistic Regression (Stage 1)',
                'stage_number': 1
            }

        # --- Stage 2: Random Forest (Ambiguous Cases) ---
        rf_proba = self.rf_model.predict_proba(tfidf_features)[0][1]
        if rf_proba > self.rf_threshold or rf_proba < (1 - self.rf_threshold):
            prediction = 'Phishing' if rf_proba >= 0.5 else 'Legitimate'
            confidence = rf_proba if rf_proba >= 0.5 else 1 - rf_proba
            return {
                'prediction': prediction,
                'confidence': float(confidence),
                'model_stage': 'Random Forest (Stage 2)',
                'stage_number': 2
            }

        # --- Stage 3: LSTM Neural Network (Deep Analysis) ---
        seq = self.tokenizer.texts_to_sequences([email_text])
        padded = pad_sequences(seq, maxlen=self.max_len)
        lstm_proba = float(self.lstm_model.predict(padded, verbose=0)[0][0])

        prediction = 'Phishing' if lstm_proba >= 0.5 else 'Legitimate'
        confidence = lstm_proba if lstm_proba >= 0.5 else 1 - lstm_proba

        return {
            'prediction': prediction,
            'confidence': float(confidence),
            'model_stage': 'LSTM Neural Network (Stage 3)',
            'stage_number': 3
        }

detector = None

def get_detector() -> PhishingDetector:
    global detector
    if detector is None:
        logger.info("Initializing PhishingDetector with Cascading Pipeline...")
        detector = PhishingDetector()
    return detector
