import librosa
import numpy as np
import warnings

warnings.filterwarnings("ignore")

class FeatureExtractor:
    """
    Extracts exactly 150-dimensional feature vector from audio to match
    the REAL trained model (model.pkl) expectations.
    
    Features:
      [0:40]   - 40 MFCCs (mean over time)
      [40:41]  - Spectral Centroid (mean)
      [41:42]  - Zero Crossing Rate (mean)
      [42:55]  - 13 Chroma features (mean)
      [55:56]  - Spectral Bandwidth (mean)
      [56:57]  - Spectral Rolloff (mean)
      [57:58]  - RMS Energy (mean)
      [58:60]  - Pitch mean (F0) & variance
      [60:67]  - 7 Spectral Contrast bands (mean)
      [67:68]  - Tempo
      [68:88]  - 20 Mel spectrogram bands (mean)
      [88:128] - 40 MFCCs (std)
      [128:129]- ZCR (std)
      [129:130]- Spectral centroid (std)
      [130:150]- 20 delta MFCC features
    Total: 150
    """
    TARGET_DIM = 150

    def __init__(self):
        pass

    def extract_all(self, audio, sr):
        """
        Extract and fuse features into exactly 150-dimensional vector
        matching the trained model's expected input format.
        """
        try:
            # Ensure minimum length
            min_samples = sr * 1
            if len(audio) < min_samples:
                audio = np.pad(audio, (0, min_samples - len(audio)), 'constant')
            
            # Trim silence
            audio_trimmed, _ = librosa.effects.trim(audio, top_db=25)
            if len(audio_trimmed) < sr // 2:
                audio_trimmed = audio
                
            # Normalize
            max_val = np.max(np.abs(audio_trimmed))
            if max_val > 0:
                audio_trimmed = audio_trimmed / max_val
                
            features = []
            
            # 1. MFCCs mean [0:40]
            mfccs = librosa.feature.mfcc(y=audio_trimmed, sr=sr, n_mfcc=40)
            features.extend(np.mean(mfccs, axis=1))
            
            # 2. Spectral Centroid mean [40]
            cent = librosa.feature.spectral_centroid(y=audio_trimmed, sr=sr)
            features.append(np.mean(cent))
            
            # 3. ZCR mean [41]
            zcr = librosa.feature.zero_crossing_rate(audio_trimmed)
            features.append(np.mean(zcr))
            
            # 4. Chroma [42:55]
            chroma = librosa.feature.chroma_stft(y=audio_trimmed, sr=sr)
            features.extend(np.mean(chroma, axis=1))
            features.append(np.std(chroma))
            
            # 5. Spectral Bandwidth [55]
            bw = librosa.feature.spectral_bandwidth(y=audio_trimmed, sr=sr)
            features.append(np.mean(bw))
            
            # 6. Spectral Rolloff [56]
            rolloff = librosa.feature.spectral_rolloff(y=audio_trimmed, sr=sr)
            features.append(np.mean(rolloff))
            
            # 7. RMS Energy [57]
            rms = librosa.feature.rms(y=audio_trimmed)
            features.append(np.mean(rms))
            
            # 8. Pitch (F0) [58:60]
            try:
                f0, _, _ = librosa.pyin(audio_trimmed, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
                f0_clean = f0[~np.isnan(f0)] if np.any(~np.isnan(f0)) else np.array([0.0])
                features.append(np.mean(f0_clean))
                features.append(np.var(f0_clean))
            except:
                features.extend([0.0, 0.0])
                
            # 9. Spectral Contrast [60:67]
            contrast = librosa.feature.spectral_contrast(y=audio_trimmed, sr=sr)
            features.extend(np.mean(contrast, axis=1))
            
            # 10. Tempo [67]
            tempo, _ = librosa.beat.beat_track(y=audio_trimmed, sr=sr)
            features.append(float(np.atleast_1d(tempo)[0]))
            
            # 11. Mel spectrogram [68:88]
            mel = librosa.feature.melspectrogram(y=audio_trimmed, sr=sr, n_mels=20)
            mel_db = librosa.power_to_db(mel, ref=np.max)
            features.extend(np.mean(mel_db, axis=1))
            
            # 12. MFCC std [88:128]
            features.extend(np.std(mfccs, axis=1))
            
            # 13. ZCR std [128]
            features.append(np.std(zcr))
            
            # 14. Spectral Centroid std [129]
            features.append(np.std(cent))
            
            # 15. Delta MFCCs [130:150]
            delta_mfccs = librosa.feature.delta(mfccs)
            features.extend(np.mean(delta_mfccs[:20], axis=1))
            
            # Convert
            feat_arr = np.array(features, dtype=float)
            if len(feat_arr) > self.TARGET_DIM:
                feat_arr = feat_arr[:self.TARGET_DIM]
            elif len(feat_arr) < self.TARGET_DIM:
                feat_arr = np.pad(feat_arr, (0, self.TARGET_DIM - len(feat_arr)), 'constant')
                
            feat_arr = np.nan_to_num(feat_arr, nan=0.0, posinf=0.0, neginf=0.0)
            return feat_arr

        except Exception as e:
            print(f"[FeatureExtractor] Error: {e}")
            return np.zeros(self.TARGET_DIM)

    # ---- Additional Feature Insight Methods for Diagnostics ----

    def extract_diagnostic_components(self, audio, sr):
        """
        Returns interpretable feature components for the radar chart diagnostics.
        """
        try:
            # Vocal Tremor (pitch jitter)
            f0, _, _ = librosa.pyin(audio, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            f0_clean = f0[~np.isnan(f0)] if np.any(~np.isnan(f0)) else np.array([0.0])
            pitch_var = np.var(f0_clean)
            vocal_tremor = min(pitch_var / 500.0, 1.0)  # Normalize

            # Breathlessness (spectral rolloff indicates breathiness)
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)
            breathlessness = min(np.mean(rolloff) / 8000.0, 1.0)

            # Pacing / Pauses
            rms = librosa.feature.rms(y=audio)
            pauses = np.sum(rms[0] < 0.02) / len(rms[0])
            pacing = min(pauses * 3.0, 1.0)

            # Energy level
            energy = np.mean(rms)
            energy_low = max(1.0 - (energy * 5.0), 0.0)  # Inverted: low energy = high score

            # Pitch Variance
            pitch_range = (np.max(f0_clean) - np.min(f0_clean)) if len(f0_clean) > 1 else 0.0
            pitch_variance = min(pitch_range / 200.0, 1.0)

        except Exception:
            vocal_tremor = 0.2
            breathlessness = 0.2
            pacing = 0.2
            energy_low = 0.1
            pitch_variance = 0.1

        return {
            "Vocal Tremor": float(round(vocal_tremor, 3)),
            "Breathlessness": float(round(breathlessness, 3)),
            "Pacing/Pauses": float(round(pacing, 3)),
            "Energy Low": float(round(energy_low, 3)),
            "Pitch Variance": float(round(pitch_variance, 3))
        }
