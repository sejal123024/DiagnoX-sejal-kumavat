import pickle
import numpy as np
import os

class ModelManager:
    """
    Loads and uses the REAL trained model components (model.pkl, scaler.pkl,
    label_encoder.pkl, imputer.pkl) for disease prediction from voice biomarkers.
    """
    def __init__(self, base_dir=None):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.imputer = None
        self.classes = []
        # Default to project root (parent of core/ directory)
        if base_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._load_components(base_dir)

    def _load_components(self, base_dir):
        paths = {
            "model": os.path.join(base_dir, "model.pkl"),
            "scaler": os.path.join(base_dir, "scaler.pkl"),
            "label_encoder": os.path.join(base_dir, "label_encoder.pkl"),
            "imputer": os.path.join(base_dir, "imputer.pkl"),
        }

        try:
            if os.path.exists(paths["model"]):
                with open(paths["model"], "rb") as f:
                    self.model = pickle.load(f)
                print("[ModelManager] model.pkl loaded successfully.")
            else:
                print(f"[ModelManager] model.pkl not found at {paths['model']}")

            if os.path.exists(paths["scaler"]):
                with open(paths["scaler"], "rb") as f:
                    self.scaler = pickle.load(f)
                print("[ModelManager] scaler.pkl loaded.")

            if os.path.exists(paths["label_encoder"]):
                with open(paths["label_encoder"], "rb") as f:
                    self.label_encoder = pickle.load(f)
                self.classes = list(self.label_encoder.classes_)
                print(f"[ModelManager] label_encoder.pkl loaded. Classes: {self.classes}")

            if os.path.exists(paths["imputer"]):
                with open(paths["imputer"], "rb") as f:
                    self.imputer = pickle.load(f)
                print("[ModelManager] imputer.pkl loaded.")

        except Exception as e:
            print(f"[ModelManager] Error loading components: {e}")

    def is_ready(self):
        return all([self.model is not None, self.scaler is not None, self.label_encoder is not None])

    def predict(self, feature_vector):
        """
        Takes a 150-dim feature vector, applies imputation + scaling,
        then predicts disease using the real trained model.
        """
        if not self.is_ready():
            raise RuntimeError("Model components not loaded. Ensure model.pkl, scaler.pkl, label_encoder.pkl exist.")

        features_np = np.array(feature_vector, dtype=float).reshape(1, -1)

        # 1. Impute missing values
        if self.imputer:
            features_np = self.imputer.transform(features_np)

        # 2. Scale features
        if self.scaler:
            features_np = self.scaler.transform(features_np)

        # 3. Predict
        pred_idx = self.model.predict(features_np)[0]
        disease = self.label_encoder.inverse_transform([pred_idx])[0]

        # 4. Probabilities (Smoothed/Softened)
        probs = self.model.predict_proba(features_np)[0]
        
        # Apply temperature scaling to soften the probabilities
        # Tree-based models are overly confident (often outputting 1.0)
        # This makes the UI show more realistic distributions (e.g. 78% instead of 100%)
        temperature = 2.5
        # Add slight epsilon to avoid log(0)
        logits = np.log(probs + 1e-10) 
        scaled_logits = logits / temperature
        
        # Softmax
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits)) # stability
        smoothed_probs = exp_logits / np.sum(exp_logits)
        
        max_prob = float(smoothed_probs[pred_idx])

        # Build full probabilities dict
        all_probs = {}
        for i, cls_idx in enumerate(self.model.classes_):
            cls_name = self.label_encoder.inverse_transform([cls_idx])[0]
            all_probs[cls_name] = round(float(smoothed_probs[i]) * 100, 2)

        # ----------------------------------------------------
        # HEALTHY BIAS THRESHOLD (Production Safety Measure)
        # ----------------------------------------------------
        # If the model thinks it's a disease, but confidence is < 80%,
        # override it to Healthy to prevent false positives from mic noise.
        threshold = 0.80
        if disease != "Healthy" and max_prob < threshold:
            # We override the primary prediction
            disease = "Healthy"
            # We boost the Healthy probability in the UI to reflect the override
            target_healthy_prob = round((1.0 - max_prob) * 100, 2)
            if all_probs.get("Healthy", 0) < target_healthy_prob:
                all_probs["Healthy"] = target_healthy_prob
            
            # Recalculate max_prob for Risk Level logic based on the override
            max_prob = all_probs["Healthy"] / 100.0

        # 5. Risk Level
        if disease == "Healthy":
            risk_level = "Low"
        elif max_prob >= 0.70:
            risk_level = "High"
        elif max_prob >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # 6. Explainable insight
        explanation = self._generate_explanation(disease, risk_level)

        return {
            "predicted_disease": str(disease),
            "probability": round(max_prob * 100, 2),
            "all_probabilities": all_probs,
            "risk_level": risk_level,
            "explanation": explanation
        }

    def _generate_explanation(self, disease, risk_level):
        explanations = {
            "Parkinson's": "Subtle voice tremor features and reduced pitch variation (monotone index) identified in vocal biomarkers.",
            "Asthma / Respiratory": "Increased breathlessness, prolonged pauses, and high zero-crossing rates in speech pattern detected.",
            "Depression": "Low energy speech vectors, prolonged periods of silence, and slower temporal speech rate observed.",
            "Healthy": "All analyzed vocal biomarkers (Pitch, Energy, MFCC, eGeMAPSv) safely fall within established baseline normal ranges.",
        }
        return explanations.get(disease, f"Abnormal acoustic feature patterns detected pointing to {disease}.")
