import streamlit as st
import librosa
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import io
from datetime import datetime

from core.audio_processor import AudioProcessor
from core.feature_extractor import FeatureExtractor
from core.model_manager import ModelManager
from core.alert_system import AlertSystem
from database import DatabaseManager, FirebaseAuth, FirebaseStorage

# Configuration
st.set_page_config(page_title="Voice Biomarker Analysis System", page_icon="🎙️", layout="wide")

# ─────────────────────────────────────
# PREMIUM DARK THEME STYLING
# ─────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #111827 50%, #0d1321 100%);
        font-family: 'Inter', -apple-system, system-ui, sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Main title */
    h1 {
        background: linear-gradient(135deg, #06b6d4, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* Section headers */
    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid rgba(56, 189, 248, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 500;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2)) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    /* Cards & containers */
    .css-1r6slb0, .css-12oz5g7, [data-testid="stVerticalBlock"] > div {
        border-radius: 12px;
    }

    /* Metric styling */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(10px);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0891b2, #0284c7) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(8, 145, 178, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 25px rgba(8, 145, 178, 0.5) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #06b6d4, #3b82f6) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(56, 189, 248, 0.3) !important;
        border-radius: 12px !important;
        background: rgba(15, 23, 42, 0.5) !important;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 10px !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border-color: rgba(56, 189, 248, 0.15) !important;
    }

    /* Custom classes */
    .glass-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(20px);
        margin-bottom: 16px;
    }
    .risk-badge-high {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
    }
    .risk-badge-medium {
        display: inline-block;
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
    }
    .risk-badge-low {
        display: inline-block;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
    }
    .stat-label {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .stat-value {
        color: #f1f5f9;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .insight-box {
        background: rgba(6, 182, 212, 0.08);
        border-left: 3px solid #06b6d4;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin: 16px 0;
        color: #cbd5e1;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .history-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.7));
        border: 1px solid rgba(56, 189, 248, 0.12);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .history-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateY(-1px);
    }
    .history-time {
        color: #64748b;
        font-size: 0.8rem;
    }
    .history-disease {
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: -10px;
        margin-bottom: 24px;
    }
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.5); }
    }
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #475569;
    }
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }
    .empty-state-text {
        font-size: 1rem;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_diagnostics" not in st.session_state:
    st.session_state.last_diagnostics = None
if "days_passed" not in st.session_state:
    st.session_state.days_passed = 1
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# ─────────────────────────────────────
# AUTHENTICATION SIDEBAR
# ─────────────────────────────────────
with st.sidebar:
    st.title("🔐 Authentication")
    st.markdown("Firebase Identity Toolkit")
    
    if not st.session_state.user_token:
        st.markdown("Sign in to save actual voice recordings to Cloud Storage and access personal history.")
        auth_mode = st.radio("Mode", ["Login", "Sign Up"])
        auth_email = st.text_input("Email", key="auth_email")
        auth_password = st.text_input("Password", type="password", key="auth_pass")
        
        if st.button("Submit", use_container_width=True):
            if auth_mode == "Sign Up":
                res = FirebaseAuth.sign_up(auth_email, auth_password)
                if "idToken" in res:
                    st.success("Account created!")
                    st.session_state.user_token = res["idToken"]
                    st.session_state.user_email = auth_email
                    st.rerun()
                else:
                    st.error(f"Error: {res.get('error', {}).get('message', 'Unknown')}")
            else:
                res = FirebaseAuth.sign_in(auth_email, auth_password)
                if "idToken" in res:
                    st.success("Logged in successfully!")
                    st.session_state.user_token = res["idToken"]
                    st.session_state.user_email = auth_email
                    st.rerun()
                else:
                    st.error(f"Error: {res.get('error', {}).get('message', 'Unknown')}")
    else:
        st.success(f"Logged in as: {st.session_state.user_email}")
        if st.button("Logout", use_container_width=True):
            st.session_state.user_token = None
            st.session_state.user_email = None
            st.session_state.firebase_history = []
            st.rerun()

# ─────────────────────────────────────
# LOAD COMPONENTS (cached)
# ─────────────────────────────────────
@st.cache_resource
def load_components():
    processor = AudioProcessor()
    extractor = FeatureExtractor()
    model_manager = ModelManager()
    alert_system = AlertSystem()
    return processor, extractor, model_manager, alert_system

processor, extractor, model_manager, alert_system = load_components()


def process_recording(uploaded_file):
    """Full analysis pipeline: Audio → Features → Model → Alert"""
    with st.spinner("🔬 Analyzing deep audio embeddings and extracting vocal biomarkers..."):
        time.sleep(1.0)

        # 1. Audio preprocessing
        audio_norm, sr = processor.process(uploaded_file)

        # 2. Extract 150-dim features (matching real trained model)
        features = extractor.extract_all(audio_norm, sr)

        # 3. Predict using real model
        result = model_manager.predict(features)

        # 4. Check alerts
        alerts = alert_system.check_alerts(result, st.session_state.history)
        result["alerts"] = alerts

        # 5. Extract diagnostic components for radar chart
        diagnostics = extractor.extract_diagnostic_components(audio_norm, sr)
        result["diagnostics"] = diagnostics

    return audio_norm, sr, result


# ─────────────────────────────────────
# UI HEADER
# ─────────────────────────────────────
st.title("🎙️ Voice Biomarker Health Tracker")
st.markdown('<p class="hero-subtitle"><span class="pulse-dot"></span>Continuous disease monitoring through non-invasive AI-powered vocal biomarker analysis</p>', unsafe_allow_html=True)

# Model status indicator
if model_manager.is_ready():
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:20px; padding:10px 16px; 
                background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:10px; width:fit-content;">
        <span class="pulse-dot"></span>
        <span style="color:#10b981; font-weight:500; font-size:0.85rem;">
            Model Active — Classes: {', '.join(model_manager.classes)}
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("⚠️ Model components not found. Please ensure `model.pkl`, `scaler.pkl`, `label_encoder.pkl` exist in the project root.")

# ─────────────────────────────────────
# TABS
# ─────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🎤 Record & Analyze", "📊 Progress Dashboard", "🔬 Diagnostics View", "📋 History"])

# ═══════════════════════════════════════
# TAB 1: RECORD & ANALYZE
# ═══════════════════════════════════════
with tab1:
    st.header("Voice Recording Module")
    st.markdown("Record or upload **10–15 seconds** of your voice reading the standard passage below:")
    st.info("📖 *\"A rainbow is a meteorological phenomenon that is caused by reflection, refraction and dispersion of light in water droplets resulting in a spectrum of light appearing in the sky…\"*")

    col_upload, col_record = st.columns(2)

    with col_upload:
        st.markdown("##### 📁 Upload Audio File")
        uploaded_audio = st.file_uploader("Upload Audio (WAV / MP3 / OGG)", type=['wav', 'mp3', 'ogg'], label_visibility="collapsed")

    with col_record:
        st.markdown("##### 🎙️ Live Recording")
        recorded_audio = None
        if hasattr(st, "audio_input"):
            recorded_audio = st.audio_input("Record Voice (10-15 seconds)")

    selected_audio = recorded_audio if recorded_audio else uploaded_audio

    if selected_audio is not None:
        if not recorded_audio:
            st.audio(selected_audio)

        if st.button("⚡ Analyze Recording", type="primary", use_container_width=True):
            if not model_manager.is_ready():
                st.error("Model is not loaded. Cannot analyze.")
            else:
                # Execute Pipeline
                audio_data, sr, results = process_recording(selected_audio)

                # Save into session history
                record_day = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_entry = {
                    "day": record_day,
                    "disease": results["predicted_disease"],
                    "probability": results["probability"],
                    "risk": results["risk_level"],
                    "alerts": results["alerts"],
                    "all_probs": results["all_probabilities"],
                    "explanation": results["explanation"]
                }
                st.session_state.history.append(history_entry)
                st.session_state.last_diagnostics = results.get("diagnostics", None)
                st.session_state.days_passed += 1

                # Extract Raw Audio Bytes for Firebase Cloud Storage
                selected_audio.seek(0)
                audio_bytes = selected_audio.read()
                file_name = f"recording_{int(time.time())}.wav"
                
                # If logged in, upload to Storage and associate with their DB
                user_id = st.session_state.user_email if st.session_state.user_email else "anonymous"
                user_token = st.session_state.user_token if st.session_state.user_token else None
                # Save metadata to Firestore Database
                # (Audio storage bypassed for external n8n workflow handling)
                DatabaseManager.save_prediction(
                    audio_url="pending_n8n_sync",
                    prediction=results["predicted_disease"],
                    probability=results["probability"] / 100.0,
                    risk_level=results["risk_level"],
                    user_id=user_id,
                    user_token=user_token
                )

                # ── Display Results ──
                st.markdown("---")
                st.subheader("🧬 Analysis Results")

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Primary Detection", results["predicted_disease"])
                with c2:
                    st.metric("Confidence Score", f"{results['probability']:.1f}%")
                with c3:
                    risk = results["risk_level"]
                    badge_class = f"risk-badge-{risk.lower()}"
                    st.markdown(f"""
                    <div style="padding-top:8px;">
                        <div class="stat-label">Risk Level</div>
                        <span class="{badge_class}">{risk}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Insight
                st.markdown(f"""
                <div class="insight-box">
                    💡 <strong>AI Insight:</strong> {results['explanation']}
                </div>
                """, unsafe_allow_html=True)

                # Probability breakdown
                st.markdown("##### Disease Probability Breakdown")
                prob_data = results["all_probabilities"]
                prob_df = pd.DataFrame(list(prob_data.items()), columns=["Disease", "Probability (%)"])
                prob_df = prob_df.sort_values("Probability (%)", ascending=True)

                fig_bar = px.bar(
                    prob_df, x="Probability (%)", y="Disease", orientation='h',
                    color="Probability (%)",
                    color_continuous_scale=["#0f172a", "#0891b2", "#06b6d4", "#f59e0b", "#ef4444"],
                    template="plotly_dark"
                )
                fig_bar.update_layout(
                    height=280,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#94a3b8"),
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=10, t=10, b=10)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # Alerts
                if results["alerts"]:
                    for alert in results["alerts"]:
                        st.error(alert, icon="🚨")
                else:
                    st.success("✅ No abnormal speech patterns detected. Biomarkers are within healthy ranges.", icon="🟢")

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎤</div>
            <div class="empty-state-text">Upload or record an audio sample to begin voice biomarker analysis</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# TAB 2: PROGRESS DASHBOARD
# ═══════════════════════════════════════
with tab2:
    st.header("📊 Progress Tracking Dashboard")
    st.markdown("Longitudinal tracking of vocal biomarker predictions over time.")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        # Summary metrics
        total_scans = len(df)
        high_risk_count = len(df[df["risk"] == "High"])
        latest = df.iloc[-1]

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Scans", total_scans)
        with m2:
            st.metric("High Risk Detections", high_risk_count)
        with m3:
            st.metric("Latest Detection", latest["disease"])
        with m4:
            st.metric("Latest Risk", latest["risk"])

        st.markdown("---")

        # ── Probability Trend Chart ──
        st.subheader("Risk Trends Over Time")
        probs_df = pd.json_normalize(df['all_probs'])
        df_combined = pd.concat([df[['day']], probs_df], axis=1)
        df_melt = df_combined.melt(id_vars=["day"], var_name="Disease", value_name="Probability")

        fig = px.line(
            df_melt, x="day", y="Probability", color="Disease",
            title="Disease Probability Trajectory",
            markers=True, template="plotly_dark"
        )
        fig.update_layout(
            yaxis_title="Probability (%)",
            xaxis_title="Timeline",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#94a3b8"),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Assessment Log Table ──
        st.subheader("Assessment History Log")
        display_df = df[["day", "disease", "probability", "risk"]].copy()
        display_df.columns = ["Timestamp", "Prediction", "Confidence (%)", "Risk Level"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-text">No data available yet. Complete a voice analysis to populate the dashboard.</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# TAB 3: DIAGNOSTICS VIEW
# ═══════════════════════════════════════
with tab3:
    st.header("🔬 Deep Diagnostics: Feature Map")
    st.markdown("Visualization of the extracted real audio features driving AI decisions.")

    if len(st.session_state.history) > 0 and st.session_state.last_diagnostics is not None:
        last_results = st.session_state.history[-1]
        diagnostics = st.session_state.last_diagnostics

        st.subheader(f"Latest Analysis: {last_results['disease']}")

        # ── Radar Chart from REAL audio features ──
        categories = list(diagnostics.keys())
        r_vals = list(diagnostics.values())

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals + [r_vals[0]],  # close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(6, 182, 212, 0.15)',
            line=dict(color='#06b6d4', width=2),
            name='Current Status'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], color="#475569"),
                angularaxis=dict(color="#94a3b8"),
                bgcolor='rgba(0,0,0,0)',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#94a3b8"),
            showlegend=False,
            height=400,
            margin=dict(l=60, r=60, t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Feature breakdown table
        st.markdown("##### Feature Component Scores")
        diag_df = pd.DataFrame({
            "Component": categories,
            "Score": r_vals,
            "Level": ["🔴 Elevated" if v > 0.6 else "🟡 Moderate" if v > 0.3 else "🟢 Normal" for v in r_vals]
        })
        st.dataframe(diag_df, use_container_width=True, hide_index=True)

        # Insight
        st.markdown(f"""
        <div class="insight-box">
            💡 <strong>Diagnostic Insight:</strong> {last_results['explanation']}
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🔬</div>
            <div class="empty-state-text">Perform an analysis to unlock real diagnostic feature insights.</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# TAB 4: HISTORY (Firebase Persistent)
# ═══════════════════════════════════════
with tab4:
    st.header("📋 Patient Report History")
    st.markdown("Persistent history of all past analyses stored in the cloud database.")

    col_refresh, col_spacer = st.columns([1, 4])
    with col_refresh:
        refresh_clicked = st.button("🔄 Refresh from Database", use_container_width=True)

    if refresh_clicked or "firebase_history" not in st.session_state:
        with st.spinner("Fetching personal records from Cloud Firestore..."):
            user_id = st.session_state.user_email if st.session_state.user_email else "anonymous"
            user_token = st.session_state.user_token if st.session_state.user_token else None
            st.session_state.firebase_history = DatabaseManager.get_past_reports(user_id=user_id, user_token=user_token)

    reports = st.session_state.get("firebase_history", [])

    if reports and len(reports) > 0:
        # Summary stats
        total = len(reports)
        high_risk = sum(1 for r in reports if r.get("risk_level") == "High")
        medium_risk = sum(1 for r in reports if r.get("risk_level") == "Medium")
        low_risk = sum(1 for r in reports if r.get("risk_level") == "Low")

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Total Records", total)
        with s2:
            st.metric("🔴 High Risk", high_risk)
        with s3:
            st.metric("🟡 Medium Risk", medium_risk)
        with s4:
            st.metric("🟢 Low Risk", low_risk)

        st.markdown("---")

        # Report cards
        for i, rep in enumerate(reports):
            ts = rep.get("timestamp", "Unknown")
            try:
                display_time = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%B %d, %Y  •  %I:%M %p UTC")
            except Exception:
                display_time = ts

            prediction = rep.get("prediction", "Unknown")
            probability = rep.get("probability", 0.0)
            risk_level = rep.get("risk_level", "Unknown")

            risk_color = "#ef4444" if risk_level == "High" else "#f59e0b" if risk_level == "Medium" else "#10b981"
            risk_icon = "🔴" if risk_level == "High" else "🟡" if risk_level == "Medium" else "🟢"
            prob_display = f"{probability * 100:.0f}%" if probability <= 1.0 else f"{probability:.0f}%"

            st.markdown(f"""
            <div class="history-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div class="history-time">{display_time}</div>
                        <div class="history-disease">{prediction}</div>
                        <div style="margin-top: 6px;">
                            <a href="{rep.get('audio_url', '#')}" target="_blank" style="color: #38bdf8; text-decoration: none; font-size: 0.85rem;">🎵 Listen to Original Audio from Cloud Storage</a>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:{risk_color}; font-weight:600; font-size:0.9rem;">
                            {risk_icon} {risk_level} Risk
                        </div>
                        <div style="color:#94a3b8; font-size:0.85rem;">
                            Confidence: {prob_display}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-text">No history records found in database. Complete an analysis to start building your health timeline.</div>
        </div>
        """, unsafe_allow_html=True)
