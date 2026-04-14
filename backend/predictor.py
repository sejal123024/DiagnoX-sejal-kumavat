import numpy as np
from model_loader import ModelLoader
from feature_pipeline import FeaturePipeline

class Predictor:
    def __init__(self):
        self.loader = ModelLoader()
        self.pipeline = FeaturePipeline()
        
    def check_health(self):
        return self.loader.is_loaded()
        
    def predict(self, audio_path: str):
        if not self.loader.is_loaded():
            raise ValueError("Model components are missing!")
            
        # 1. Extract 150-dim feature vector
        features = self.pipeline.extract_features(audio_path)
        
        # Ensure 2D array
        features_np = np.array(features, dtype=float).reshape(1, -1)
        
        # 2. Impute & Scale (Preprocess)
        try:
            if self.loader.imputer:
                features_np = self.loader.imputer.transform(features_np)
            if self.loader.scaler:
                features_np = self.loader.scaler.transform(features_np)
        except Exception as e:
            print("Pre-processing scaling failed:", e)
            
        # 3. Model Prediction
        pred_idx = self.loader.model.predict(features_np)[0]
        disease = self.loader.label_encoder.inverse_transform([pred_idx])[0]
        
        probs = self.loader.model.predict_proba(features_np)[0]
        max_prob = probs[pred_idx]
        
        # 4. Risk Logic
        if max_prob >= 0.70:
            risk_level = "High"
        elif max_prob >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        # Optional: Basic Explainable Logic
        insights = f"Detected vocal biomarkers pointing towards {disease}."
        if disease == 'Parkinson’s':
            insights = "Abnormal tremor variations and pause ratios detected."
        elif disease == 'Asthma / Respiratory':
            insights = "High respiratory irregularity and breath variations found."
        elif disease == 'Depression':
            insights = "Flattened affect and pitch mono-tones detected."
            
        if disease == 'Healthy':
            risk_level = "Low"
            insights = "Vocal biomarkers appear smooth and rhythmic."
            
        return {
            "disease": str(disease),
            "probability": round(float(max_prob), 2),
            "risk_level": risk_level,
            "insights": insights
        }
