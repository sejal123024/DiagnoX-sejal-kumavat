class AlertSystem:
    """
    Alert system for voice biomarker health tracking.
    Triggers alerts based on disease risk thresholds and trend analysis.
    """
    def __init__(self, risk_threshold=65.0):
        self.risk_threshold = risk_threshold

    def check_alerts(self, prediction_result, history=None):
        disease = prediction_result["predicted_disease"]
        prob = prediction_result["probability"]
        alerts = []

        # Trend & Anomaly Analysis against history
        if history and len(history) > 0:
            last_record = history[-1]

            # Rising trend: if same disease probability increased significantly
            if last_record["disease"] == disease:
                prob_diff = prob - last_record["probability"]
                if prob_diff >= 10.0:
                    alerts.append(f"📈 Increasing risk trend: {disease} probability increased by {prob_diff:.1f}%.")

            # Sudden biomarker change (transitioning from Low to Medium/High)
            if prob > 40.0 and last_record["risk"] == "Low":
                alerts.append("⚠️ Sudden change in voice biomarkers detected compared to previous session.")

        # Condition-specific high-risk alerts
        if disease != "Healthy" and prob >= self.risk_threshold:
            if "Asthma" in disease or "Respiratory" in disease:
                alerts.append("⚠️ Increased breathlessness detected (Respiratory risk)")
            elif "Parkinson" in disease:
                alerts.append("🚨 Voice tremor rising (Parkinson's risk)")
            elif "Depression" in disease:
                alerts.append("⚠️ Low energy speech (Depression indicator)")
            else:
                alerts.append(f"🚨 Elevated probability detected for {disease}. Immediate attention recommended.")

        return alerts
