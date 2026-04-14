# 🎙️ DiagnoX-VitaScan

> **Continuous disease monitoring through non-invasive AI-powered vocal biomarker analysis.**

## 🌟 Overview
DiagnoX-VitaScan is an advanced full-stack AI healthcare application designed to detect the presence and risk level of diseases by analyzing human vocal biomarkers. By uploading or recording a short 10-15 second voice snippet, our hybrid architecture processes the audio waveform against a trained Random Forest classifier.

The platform allows users to view deep diagnostic feature maps, track their health trajectories over time, and gain continuous predictive health insights without invasive procedures.

---

## 🚀 Key Features
- **🎤 Real-time Audio Processing:** Record or upload `.wav`, `.mp3`, or `.ogg` files.
- **🧬 Deep Feature Extraction:** Parses audio streams to extract over 150 unique sound dimensions including MFCCs, spectral roll-off, chroma, and pitch contours.
- **🧠 Machine Learning Classification:** Utilizes a custom Random Forest model to instantly output predictive probabilities and risk severity levels.
- **📊 Longitudinal Dashboard:** Built with Recharts and Firebase Firestore, allowing patients and doctors to view historical trajectory charts.
- **🤖 Explainable GenAI:** Powered by the **Google Gemini SDK**, breaking down complex biomarker predictions into plain, easily digestible health summaries.
- **✨ Premium Experience:** Ultra-modern immersive UI engineered with Next.js 16, Framer Motion, Lenis Smooth Scroll, and rich Spline 3D graphics.

---

## 🏗️ Architecture Stack
### Web Application (Client)
- **Framework:** Next.js 16 (React 18)
- **Styling:** Tailwind CSS V4
- **Animations:** Framer Motion, Studio Freight Lenis
- **Auth & DB:** Firebase Identity Toolkit & Cloud Firestore

### Machine Learning Engine (Backend)
- **Language / Environment:** Python 3
- **Dev Interface:** Streamlit Engine (`backend/app.py`)
- **Audio Processing Engine:** Librosa, NumPy, Pandas
- **Classifier System:** Scikit-Learn (Random Forest `.pkl` pipeline)
- **Visualizations:** Plotly Express / Scatterpolar Radar charts

---

## 💻 Local Development Setup

### 1. Web Application (Next.js Frontend)
Install the dependencies and start the Turbopack development server:
```bash
npm install
npm run dev
```
Navigate to `http://localhost:3000` to interact with the dashboard.

### 2. Standalone ML Analytics Server (Python)
To dive strictly into the data science core and test the audio components manually:
```bash
cd backend
pip install -r requirements.txt
streamlit run app.py
```
This isolates the core ML engine and diagnostic tuning interface at `http://localhost:8501`.

---

## 🔒 Security & Privacy Notice
All vocal arrays processed by DiagnoX-VitaScan are routed through secured and authenticated Firebase routines. No raw audio is persistently stored on local instances unsupervised. Data integrity is enforced via strictly enforced Firestore Rules.
