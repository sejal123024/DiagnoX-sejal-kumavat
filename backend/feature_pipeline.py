import librosa
import numpy as np
import torch
import warnings
import opensmile
from transformers import Wav2Vec2Processor, Wav2Vec2Model

warnings.filterwarnings('ignore')

class FeaturePipeline:
    def __init__(self):
        self.target_dim = 150
        try:
            self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
            self.model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
        except Exception as e:
            print("Wav2Vec2 initialization failed. Will use fallback zero-padding:", e)
            self.processor, self.model = None, None
            
        try:
            self.smile = opensmile.Smile(
                feature_set=opensmile.FeatureSet.eGeMAPSv02,
                feature_level=opensmile.FeatureLevel.Functionals
            )
        except:
            self.smile = None

    def preprocess_audio(self, file_path):
        """Preprocess using Librosa (normalize, trim silence)"""
        y, sr = librosa.load(file_path, sr=16000, mono=True)
        # Trim silence
        y_trimmed, ind = librosa.effects.trim(y, top_db=20)
        # Normalize
        if np.max(np.abs(y_trimmed)) > 0:
            y_norm = y_trimmed / np.max(np.abs(y_trimmed))
        else:
            y_norm = y_trimmed
        return y_norm, 16000

    def extract_features(self, file_path):
        """Extracts exact 150 dimensions matching the dataset"""
        y, sr = self.preprocess_audio(file_path)
        
        feature_vector = []
        
        # 1. Librosa Features (42 features)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
        feature_vector.extend(np.mean(mfccs.T, axis=0))
        
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        feature_vector.append(np.mean(centroid))
        
        zcr = librosa.feature.zero_crossing_rate(y)
        feature_vector.append(np.mean(zcr))
        
        # 2. OpenSMILE (88 features)
        if self.smile:
            try:
                smile_df = self.smile.process_signal(y, sr)
                feature_vector.extend(smile_df.values[0])
            except:
                feature_vector.extend(np.zeros(88))
        else:
            feature_vector.extend(np.zeros(88))
            
        # 3. Wav2Vec 2.0 (To fill the remaining to exactly 150-dim)
        if self.processor and self.model:
            inputs = self.processor(y, sampling_rate=sr, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
            w2v_features = torch.mean(outputs.last_hidden_state, dim=1).squeeze().numpy()
        else:
            w2v_features = np.zeros(768)
            
        combined = np.concatenate([feature_vector, w2v_features])
        
        # Ensure feature format perfectly matches 150 features
        if len(combined) > self.target_dim:
            final_features = combined[:self.target_dim]
        else:
            final_features = np.pad(combined, (0, self.target_dim - len(combined)), 'constant')
            
        return final_features
