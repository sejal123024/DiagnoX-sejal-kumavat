import requests
import json
import datetime
import os

from dotenv import load_dotenv

# Load secret environment variables from .env file
load_dotenv()

# ---------------------------------------------------------
# FIREBASE CREDENTIALS & CONFIGURATION
# ---------------------------------------------------------
FIREBASE_CONFIG = {
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") 
}

class FirebaseAuth:
    """Handles Firebase Email/Password Authentication via REST API"""
    
    @staticmethod
    def sign_up(email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_CONFIG['apiKey']}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        return response.json()

    @staticmethod
    def sign_in(email, password):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        return response.json()


class FirebaseStorage:
    """Handles audio file uploads to Firebase Cloud Storage"""
    
    @staticmethod
    def upload_audio(file_bytes, filename, user_id="anonymous", user_token=None):
        url = f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_CONFIG['storageBucket']}/o"
        params = {
            "name": f"audio_records/{user_id}/{filename}"
        }
        headers = {"Content-Type": "audio/wav"}
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        
        try:
            response = requests.post(url, params=params, data=file_bytes, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Construct public download URL
                token = data.get("downloadTokens")
                file_path = data.get("name").replace("/", "%2F")
                download_url = f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_CONFIG['storageBucket']}/o/{file_path}?alt=media&token={token}"
                return download_url
            print(f"Storage Upload Error: {response.text}")
            return None
        except Exception as e:
            print(f"Storage Exception: {e}")
            return None


class DatabaseManager:
    """Handles structured reporting and saving to Cloud Firestore database"""
    
    @staticmethod
    def save_prediction(audio_url: str, prediction: str, probability: float, risk_level: str, user_id: str = "anonymous", user_token=None):
        # Write to sub-collection: /users/{userId}/predictions
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents/users/{user_id}/predictions?key={FIREBASE_CONFIG['apiKey']}"
        
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        
        payload = {
            "fields": {
                "userId": {"stringValue": user_id},  # Rules require camelCase 'userId'
                "audio_url": {"stringValue": audio_url},
                "timestamp": {"timestampValue": timestamp},
                "prediction": {"stringValue": prediction},
                "probability": {"doubleValue": probability},
                "risk_level": {"stringValue": risk_level}
            }
        }
        
        headers = {}
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                print("Firestore Save: SUCCESS")
                return True
            else:
                print(f"Firestore Error: Status {response.status_code}")
                print(f"Firestore Error Body: {response.text}")
                return False
        except Exception as e:
            print(f"Firestore Exception: {e}")
            return False
            
    @staticmethod
    def get_past_reports(user_id: str = "anonymous", user_token=None):
        # Fetch directly from the user's specific sub-collection
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_CONFIG['projectId']}/databases/(default)/documents/users/{user_id}/predictions?key={FIREBASE_CONFIG['apiKey']}"
        
        headers = {}
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                docs = response.json().get("documents", [])
                reports = []
                for doc in docs:
                    fields = doc.get("fields", {})
                    ts = fields.get("timestamp", {}).get("timestampValue", "")
                    reports.append({
                        "timestamp": ts,
                        "audio_url": fields.get("audio_url", {}).get("stringValue", ""),
                        "prediction": fields.get("prediction", {}).get("stringValue", "Unknown"),
                        "probability": fields.get("probability", {}).get("doubleValue", 0.0),
                        "risk_level": fields.get("risk_level", {}).get("stringValue", "Unknown")
                    })
                # Sort descending by timestamp
                return sorted(reports, key=lambda x: x["timestamp"], reverse=True)
            else:
                print(f"Firestore Get Error: Status {response.status_code}")
                print(f"Firestore Get Error Body: {response.text}")
                return []
        except Exception as e:
            print(f"Firestore Get Exception: {e}")
            return []

