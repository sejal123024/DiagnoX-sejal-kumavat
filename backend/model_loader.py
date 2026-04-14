import pickle
import os

class ModelLoader:
    def __init__(self, model_path='model.pkl', scaler_path='scaler.pkl', le_path='label_encoder.pkl', imputer_path='imputer.pkl'):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.imputer = None
        
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            if os.path.exists(le_path):
                with open(le_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
            if os.path.exists(imputer_path):
                with open(imputer_path, 'rb') as f:
                    self.imputer = pickle.load(f)
        except Exception as e:
            print(f"Error loading model components: {e}")

    def is_loaded(self):
        return all([self.model is not None, self.scaler is not None, self.label_encoder is not None])
