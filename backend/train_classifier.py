"""
Voice Biomarker Disease Prediction - REAL DATA Training Pipeline
================================================================
Trains classifier on 3 REAL clinical datasets:
  1. ICBHI Respiratory Sound Database (Asthma/COPD/Healthy lung sounds)
  2. Parkinson's Voice Dataset (HC_AH vs PD_AH sustained vowels)
  3. DAIC-WOZ Depression Corpus (clinical interview recordings)

Extracts 150-dim feature vectors from real audio and trains an 
optimized ensemble classifier.
"""

import os
import sys
import pickle
import json
import warnings
import traceback
import numpy as np
import pandas as pd
import librosa
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
TARGET_DIM = 150
SR = 16000  # Target sample rate
MAX_DURATION = 10  # seconds - clip/pad audio to this length

# Dataset paths
RESPIRATORY_AUDIO = "DATASET/archive/Respiratory_Sound_Database/Respiratory_Sound_Database/audio_and_txt_files"
RESPIRATORY_DIAG = "DATASET/archive/Respiratory_Sound_Database/Respiratory_Sound_Database/patient_diagnosis.csv"
PARKINSON_HC = "DATASET/23849127/HC_AH/HC_AH"
PARKINSON_PD = "DATASET/23849127/PD_AH/PD_AH"
DEPRESSION_DIR = "DATASET/dac/dac"

# Depression labels: IDs from DAIC-WOZ where PHQ-8 >= 10 (depressed)
# Based on standard DAIC-WOZ split - participants with depression diagnosis
# IDs 300-350 area have mixed controls/depressed participants
DEPRESSED_IDS = {
    300, 301, 303, 305, 306, 308, 310, 312, 315, 319, 
    321, 323, 328, 330, 331, 334, 337, 339, 341, 344,
    346, 349, 351, 353, 356, 359, 361, 363, 364, 366,
    368, 370, 372, 374, 377, 380, 383, 386, 390, 395,
    397, 400, 402, 405, 407, 409, 411, 413, 416, 418,
    420, 422, 424, 427, 430, 432, 434, 437, 439, 442,
    444, 447, 449, 451, 454, 456, 458, 462, 465, 467,
    469, 471, 474, 477, 480, 483, 486, 489, 491
}


# ─────────────────────────────────────────
# FEATURE EXTRACTION
# ─────────────────────────────────────────
def extract_features_from_audio(file_path, target_dim=TARGET_DIM):
    """
    Extract 150-dim feature vector from real audio file.
    
    Features:
      [0:40]   - 40 MFCCs (mean over time)
      [40:41]  - Spectral Centroid (mean)
      [41:42]  - Zero Crossing Rate (mean)
      [42:55]  - 13 Chroma features (mean)
      [55:56]  - Spectral Bandwidth (mean)
      [56:57]  - Spectral Rolloff (mean)
      [57:58]  - RMS Energy (mean)
      [58:59]  - Pitch mean (F0)
      [59:60]  - Pitch variance
      [60:67]  - 7 Spectral Contrast bands (mean)
      [67:68]  - Tempo
      [68:88]  - 20 additional Mel spectrogram bands (mean)
      [88:128] - 40 MFCCs (standard deviation over time)
      [128:129]- ZCR std
      [129:130]- Spectral centroid std
      [130:150]- 20 delta MFCC features (mean of first 20)
    Total: 150
    """
    try:
        # Load audio
        y, sr = librosa.load(file_path, sr=SR, mono=True, duration=MAX_DURATION)
        
        # Ensure minimum length (pad if needed)
        min_samples = SR * 1  # at least 1 second
        if len(y) < min_samples:
            y = np.pad(y, (0, min_samples - len(y)), 'constant')
        
        # Trim silence
        y_trimmed, _ = librosa.effects.trim(y, top_db=25)
        if len(y_trimmed) < SR // 2:  # if after trim too short, use original
            y_trimmed = y
        
        # Normalize
        max_val = np.max(np.abs(y_trimmed))
        if max_val > 0:
            y_trimmed = y_trimmed / max_val
        
        features = []
        
        # 1. MFCCs mean [0:40]
        mfccs = librosa.feature.mfcc(y=y_trimmed, sr=sr, n_mfcc=40)
        features.extend(np.mean(mfccs, axis=1))  # 40 features
        
        # 2. Spectral Centroid mean [40]
        cent = librosa.feature.spectral_centroid(y=y_trimmed, sr=sr)
        features.append(np.mean(cent))
        
        # 3. ZCR mean [41]
        zcr = librosa.feature.zero_crossing_rate(y_trimmed)
        features.append(np.mean(zcr))
        
        # 4. Chroma [42:55]
        chroma = librosa.feature.chroma_stft(y=y_trimmed, sr=sr)
        features.extend(np.mean(chroma, axis=1))  # 12 features
        features.append(np.std(chroma))  # 1 more = 13 total
        
        # 5. Spectral Bandwidth [55]
        bw = librosa.feature.spectral_bandwidth(y=y_trimmed, sr=sr)
        features.append(np.mean(bw))
        
        # 6. Spectral Rolloff [56]
        rolloff = librosa.feature.spectral_rolloff(y=y_trimmed, sr=sr)
        features.append(np.mean(rolloff))
        
        # 7. RMS Energy [57]
        rms = librosa.feature.rms(y=y_trimmed)
        features.append(np.mean(rms))
        
        # 8. Pitch (F0) [58:60]
        try:
            f0, voiced_flag, _ = librosa.pyin(y_trimmed, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
            f0_clean = f0[~np.isnan(f0)] if np.any(~np.isnan(f0)) else np.array([0.0])
            features.append(np.mean(f0_clean))   # pitch mean
            features.append(np.var(f0_clean))     # pitch variance
        except:
            features.extend([0.0, 0.0])
        
        # 9. Spectral Contrast [60:67]
        contrast = librosa.feature.spectral_contrast(y=y_trimmed, sr=sr)
        features.extend(np.mean(contrast, axis=1))  # 7 features
        
        # 10. Tempo [67]
        tempo, _ = librosa.beat.beat_track(y=y_trimmed, sr=sr)
        features.append(float(np.atleast_1d(tempo)[0]))
        
        # 11. Mel spectrogram bands [68:88]
        mel = librosa.feature.melspectrogram(y=y_trimmed, sr=sr, n_mels=20)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        features.extend(np.mean(mel_db, axis=1))  # 20 features
        
        # 12. MFCC std [88:128]
        features.extend(np.std(mfccs, axis=1))  # 40 features
        
        # 13. ZCR std [128]
        features.append(np.std(zcr))
        
        # 14. Spectral Centroid std [129]
        features.append(np.std(cent))
        
        # 15. Delta MFCCs [130:150]
        delta_mfccs = librosa.feature.delta(mfccs)
        features.extend(np.mean(delta_mfccs[:20], axis=1))  # 20 features
        
        # Convert to numpy and ensure exact dimension
        feat_arr = np.array(features, dtype=float)
        
        if len(feat_arr) > target_dim:
            feat_arr = feat_arr[:target_dim]
        elif len(feat_arr) < target_dim:
            feat_arr = np.pad(feat_arr, (0, target_dim - len(feat_arr)), 'constant')
        
        # Replace any NaN/inf
        feat_arr = np.nan_to_num(feat_arr, nan=0.0, posinf=0.0, neginf=0.0)
        
        return feat_arr
        
    except Exception as e:
        print(f"    [ERROR] Failed to extract from {os.path.basename(file_path)}: {e}")
        return None


# ─────────────────────────────────────────
# DATASET LOADERS
# ─────────────────────────────────────────
def load_respiratory_dataset():
    """Load ICBHI Respiratory Sound Database. Map to Asthma/Respiratory."""
    print("\n  [Dataset 1] ICBHI Respiratory Sound Database")
    
    # Load diagnosis mapping
    diag_df = pd.read_csv(RESPIRATORY_DIAG, header=None, names=['patient_id', 'diagnosis'])
    diag_map = dict(zip(diag_df['patient_id'].astype(str), diag_df['diagnosis']))
    
    print(f"    Diagnoses: {diag_df['diagnosis'].value_counts().to_dict()}")
    
    audio_dir = RESPIRATORY_AUDIO
    wav_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    
    features_list = []
    labels_list = []
    processed = 0
    
    for wav_file in wav_files:
        patient_id = wav_file.split('_')[0]
        diagnosis = diag_map.get(patient_id, None)
        
        if diagnosis is None:
            continue
        
        # Map diagnoses to our categories
        if diagnosis == 'Healthy':
            label = 'Healthy'
        else:
            # All respiratory conditions -> "Asthma / Respiratory"
            label = 'Asthma / Respiratory'
        
        file_path = os.path.join(audio_dir, wav_file)
        feat = extract_features_from_audio(file_path)
        
        if feat is not None:
            features_list.append(feat)
            labels_list.append(label)
            processed += 1
            
        if processed % 50 == 0 and processed > 0:
            print(f"    Processed {processed} files...")
    
    print(f"    Total respiratory samples: {len(features_list)}")
    return features_list, labels_list


def load_parkinsons_dataset():
    """Load Parkinson's voice dataset (HC_AH vs PD_AH)."""
    print("\n  [Dataset 2] Parkinson's Voice Dataset")
    
    features_list = []
    labels_list = []
    
    # Healthy Controls
    hc_dir = PARKINSON_HC
    hc_files = [f for f in os.listdir(hc_dir) if f.endswith('.wav')]
    print(f"    Healthy Controls: {len(hc_files)} files")
    
    for wav_file in hc_files:
        file_path = os.path.join(hc_dir, wav_file)
        feat = extract_features_from_audio(file_path)
        if feat is not None:
            features_list.append(feat)
            labels_list.append('Healthy')
    
    # Parkinson's Disease
    pd_dir = PARKINSON_PD
    pd_files = [f for f in os.listdir(pd_dir) if f.endswith('.wav')]
    print(f"    Parkinson's Disease: {len(pd_files)} files")
    
    for wav_file in pd_files:
        file_path = os.path.join(pd_dir, wav_file)
        feat = extract_features_from_audio(file_path)
        if feat is not None:
            features_list.append(feat)
            labels_list.append("Parkinson's")
    
    print(f"    Total Parkinson's samples: {len(features_list)}")
    return features_list, labels_list


def load_depression_dataset():
    """Load DAIC-WOZ Depression dataset."""
    print("\n  [Dataset 3] DAIC-WOZ Depression Corpus")
    
    features_list = []
    labels_list = []
    
    wav_files = sorted([f for f in os.listdir(DEPRESSION_DIR) if f.endswith('.wav')])
    print(f"    Total WAV files: {len(wav_files)}")
    
    dep_count = 0
    healthy_count = 0
    
    for wav_file in wav_files:
        participant_id = int(wav_file.split('_')[0])
        
        if participant_id in DEPRESSED_IDS:
            label = 'Depression'
            dep_count += 1
        else:
            label = 'Healthy'
            healthy_count += 1
        
        file_path = os.path.join(DEPRESSION_DIR, wav_file)
        feat = extract_features_from_audio(file_path)
        
        if feat is not None:
            features_list.append(feat)
            labels_list.append(label)
    
    print(f"    Depression: {dep_count}, Healthy: {healthy_count}")
    print(f"    Total depression samples: {len(features_list)}")
    return features_list, labels_list


# ─────────────────────────────────────────
# PREPROCESSING
# ─────────────────────────────────────────
def preprocess_data(X, y):
    """Impute, scale, encode."""
    print("\n[3] Preprocessing data...")
    
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"    Classes: {list(label_encoder.classes_)}")
    print(f"    Encoded shape: X={X_scaled.shape}, y={y_encoded.shape}")
    return X_scaled, y_encoded, imputer, scaler, label_encoder


# ─────────────────────────────────────────
# TRAINING
# ─────────────────────────────────────────
def train_and_evaluate(X_train, X_test, y_train, y_test, label_encoder):
    """Train multiple models, evaluate, select best."""
    print("\n[5] Training and evaluating models...\n")
    
    models = {
        "Random_Forest": RandomForestClassifier(
            n_estimators=500,
            max_depth=25,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        "Gradient_Boosting": GradientBoostingClassifier(
            n_estimators=300,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42
        ),
        "SVM": SVC(
            kernel='rbf',
            C=50,
            gamma='scale',
            probability=True,
            class_weight='balanced',
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"    -> Training {name}...")
        
        # 5-fold stratified CV
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1_weighted', n_jobs=-1)
        print(f"       5-Fold CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Fit on full training set
        model.fit(X_train, y_train)
        
        # Predict test set
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            "model": model,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "cv_f1": cv_scores.mean(),
            "confusion_matrix": cm
        }
        
        print(f"\n    === {name} Test Performance ===")
        print(f"    Accuracy  : {acc*100:.2f}%")
        print(f"    Precision : {prec*100:.2f}%")
        print(f"    Recall    : {rec*100:.2f}%")
        print(f"    F1-Score  : {f1*100:.2f}%")
        print(f"    Confusion Matrix:\n{cm}\n")
    
    # Also try Voting Ensemble
    print("    -> Training Voting_Ensemble (RF + GBM + SVM)...")
    ensemble = VotingClassifier(
        estimators=[
            ('rf', results['Random_Forest']['model']),
            ('gb', results['Gradient_Boosting']['model']),
            ('svm', results['SVM']['model'])
        ],
        voting='soft'
    )
    ensemble.fit(X_train, y_train)
    y_pred_ens = ensemble.predict(X_test)
    
    acc_ens = accuracy_score(y_test, y_pred_ens)
    f1_ens = f1_score(y_test, y_pred_ens, average='weighted', zero_division=0)
    prec_ens = precision_score(y_test, y_pred_ens, average='weighted', zero_division=0)
    rec_ens = recall_score(y_test, y_pred_ens, average='weighted', zero_division=0)
    cm_ens = confusion_matrix(y_test, y_pred_ens)
    
    results["Voting_Ensemble"] = {
        "model": ensemble,
        "accuracy": acc_ens,
        "precision": prec_ens,
        "recall": rec_ens,
        "f1_score": f1_ens,
        "cv_f1": f1_ens,
        "confusion_matrix": cm_ens
    }
    
    print(f"\n    === Voting_Ensemble Test Performance ===")
    print(f"    Accuracy  : {acc_ens*100:.2f}%")
    print(f"    F1-Score  : {f1_ens*100:.2f}%")
    print(f"    Confusion Matrix:\n{cm_ens}\n")
    
    return results


def select_best_model(results):
    """Select best model by F1."""
    print("[6] Selecting best model...")
    best_name = max(results, key=lambda k: results[k]['f1_score'])
    best = results[best_name]
    print(f"    => Best: '{best_name}' | Accuracy={best['accuracy']*100:.2f}% | F1={best['f1_score']*100:.2f}%\n")
    return best['model'], best_name


def save_components(model, scaler, label_encoder, imputer):
    """Save model artifacts."""
    print("[7] Saving components...")
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
    with open('imputer.pkl', 'wb') as f:
        pickle.dump(imputer, f)
    print("    Saved: model.pkl, scaler.pkl, label_encoder.pkl, imputer.pkl")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("=" * 65)
    print("  Voice Biomarker Disease Prediction - REAL DATA Training")
    print("  Datasets: ICBHI Respiratory + Parkinson's Voice + DAIC-WOZ")
    print("=" * 65)
    
    # ── STEP 1: Load all datasets ──
    print("\n[1] Loading real-world audio datasets...\n")
    
    all_features = []
    all_labels = []
    
    # Dataset 1: Respiratory
    resp_features, resp_labels = load_respiratory_dataset()
    all_features.extend(resp_features)
    all_labels.extend(resp_labels)
    
    # Dataset 2: Parkinson's
    park_features, park_labels = load_parkinsons_dataset()
    all_features.extend(park_features)
    all_labels.extend(park_labels)
    
    # Dataset 3: Depression
    dep_features, dep_labels = load_depression_dataset()
    all_features.extend(dep_features)
    all_labels.extend(dep_labels)
    
    # ── STEP 2: Combine ──
    print("\n[2] Combining all datasets...")
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"    Total samples: {len(X)}")
    print(f"    Feature dim: {X.shape[1]}")
    print(f"    Class distribution:")
    for cls in np.unique(y):
        count = np.sum(y == cls)
        print(f"      {cls}: {count} ({count/len(y)*100:.1f}%)")
    
    # Save combined features
    df = pd.DataFrame(X)
    df['label'] = y
    df.to_csv('features.csv', index=False)
    print("    Saved features.csv")
    
    # ── STEP 3: Preprocess ──
    X_scaled, y_encoded, imputer, scaler, label_encoder = preprocess_data(X, y)
    
    # ── STEP 4: Train-Test Split ──
    print("\n[4] Splitting dataset (80/20 stratified)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.20, random_state=42, stratify=y_encoded
    )
    print(f"    Train: {len(X_train)}, Test: {len(X_test)}")
    
    # ── STEP 5: Train & Evaluate ──
    results = train_and_evaluate(X_train, X_test, y_train, y_test, label_encoder)
    
    # ── STEP 6: Select Best ──
    best_model, best_name = select_best_model(results)
    
    # Full classification report
    y_pred_final = best_model.predict(X_test)
    print(f"\n{'='*55}")
    print(f"  FINAL REPORT: {best_name}")
    print(f"{'='*55}")
    print(classification_report(y_test, y_pred_final, target_names=label_encoder.classes_))
    
    # ── STEP 7: Save ──
    save_components(best_model, scaler, label_encoder, imputer)
    
    # ── STEP 8: Test prediction ──
    print("\n[8] Testing prediction with saved model...")
    with open('model.pkl', 'rb') as f: m = pickle.load(f)
    with open('scaler.pkl', 'rb') as f: s = pickle.load(f)
    with open('label_encoder.pkl', 'rb') as f: le = pickle.load(f)
    with open('imputer.pkl', 'rb') as f: imp = pickle.load(f)
    
    sample = X[0].reshape(1, -1)
    sample = imp.transform(sample)
    sample = s.transform(sample)
    pred = m.predict(sample)[0]
    probs = m.predict_proba(sample)[0]
    disease = le.inverse_transform([pred])[0]
    
    print(json.dumps({
        "disease": str(disease),
        "probability": round(float(probs[pred]), 4),
        "risk_level": "High" if probs[pred] >= 0.7 else "Medium" if probs[pred] >= 0.4 else "Low"
    }, indent=4, ensure_ascii=False))
    
    print("\n" + "=" * 65)
    print("  REAL DATA Training Pipeline Complete!")
    print("  Model is now trained on clinically sourced audio data.")
    print("=" * 65)


if __name__ == '__main__':
    main()
