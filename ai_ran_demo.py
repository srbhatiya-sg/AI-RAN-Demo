# Filename: ai_ran_demo.py
import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIGURATION
# -----------------------------
# Replace with your Zapier Webhook URL
WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/XXXXXXX/YYYYYYY"

# Optional: Google Sheet CSV export link (if using for dashboard)
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/your_sheet_id/export?format=csv"

st.set_page_config(
    page_title="AI RAN Simulator",
    layout="wide"
)

st.title("AI RAN Decision Simulator 🚀")
st.markdown(
    "Simulate mobile network/device scenarios and see AI recommendations in real-time."
)

# -----------------------------
# 1. INPUTS
# -----------------------------
st.sidebar.header("Input Parameters")

signal_strength = st.sidebar.selectbox(
    "Signal Strength", ["Strong", "Medium", "Weak"]
)

network_load = st.sidebar.selectbox(
    "Network Load", ["Low", "Medium", "High"]
)

user_type = st.sidebar.selectbox(
    "User Type", ["Video", "Gaming", "Browsing", "Idle"]
)

mobility = st.sidebar.selectbox(
    "Mobility", ["Stationary", "Moving"]
)

battery_level = st.sidebar.slider(
    "Battery Level (%)", 0, 100, 50
)

# Submit button
if st.sidebar.button("Run AI Decision"):

    st.info("Sending scenario to AI agent...")

    # -----------------------------
    # 2. POST to Zapier Webhook
    # -----------------------------
    payload = {
        "signal_strength": signal_strength,
        "network_load": network_load,
        "user_type": user_type,
        "mobility": mobility,
        "battery_level": battery_level
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            ai_output = response.json()
            st.success("AI Decision Received!")
        else:
            st.error(f"Error from Zapier: {response.status_code}")
            ai_output = None
    except Exception as e:
        st.error(f"Webhook error: {e}")
        ai_output = None

    # -----------------------------
    # 3. DISPLAY OUTPUT
    # -----------------------------
    if ai_output:
        st.subheader("AI Decision Outputs")
        st.write("**Network Decision:**", ai_output.get("network_decision", "N/A"))
        st.write("**Device Recommendation:**", ai_output.get("device_recommendation", "N/A"))
        st.write("**Reasoning:**", ai_output.get("reasoning", "N/A"))
        st.write("**Trade-Offs:**", ai_output.get("trade_offs", "N/A"))
        st.write("**Impact:**", ai_output.get("impact", "N/A"))

# -----------------------------
# 4. DASHBOARD / HISTORY (Optional)
# -----------------------------
st.markdown("---")
st.header("Historical Scenarios Dashboard")

try:
    df = pd.read_csv(GOOGLE_SHEET_CSV)
    st.dataframe(df)

    # Simple charts
    st.subheader("Battery vs Network Decision")
    if "Battery_Level" in df.columns and "Network_Decision" in df.columns:
        chart_data = df[["Battery_Level", "Network_Decision"]]
        st.bar_chart(chart_data["Battery_Level"])

except Exception as e:
    st.warning("Could not load Google Sheet history. Make sure CSV link is public.")
