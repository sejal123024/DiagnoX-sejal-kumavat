import librosa
import numpy as np

class AudioProcessor:
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr

    def process(self, file_path_or_bytes):
        """
        1. Load audio
        2. Convert to mono & fixed sample rate
        3. Noise reduction (simplified via top_db trimming)
        4. Normalization
        5. Silence trimming
        """
        # Load audio (mono by default, fixed sr)
        audio, sr = librosa.load(file_path_or_bytes, sr=self.target_sr, mono=True)
        
        # Trim silence (top_db=20 isolates speech from background hum)
        audio_trimmed, _ = librosa.effects.trim(audio, top_db=20)
        
        # Normalization
        max_val = np.max(np.abs(audio_trimmed))
        if max_val > 0:
            audio_normalized = audio_trimmed / max_val
        else:
            audio_normalized = audio_trimmed
            
        return audio_normalized, self.target_sr
