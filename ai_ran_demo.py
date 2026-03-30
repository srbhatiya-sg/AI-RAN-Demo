import streamlit as st
import pandas as pd
import json
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import datetime
import time

# -----------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI RAN Simulator", layout="wide")
st.title("📡 AI RAN Decision Simulator")

# -----------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------
SHEET_NAME = "RAN_Scenarios" 

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

try:
    # Load JSON secret from Streamlit TOML
    creds_dict = json.loads(st.secrets["google_creds"]["creds"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    st.error("Error connecting to Google Sheets. Make sure the secret is correct and the sheet is shared with the service account email.")
    st.stop()

# -----------------------------
# USER INPUT (SIDEBAR)
# -----------------------------
st.sidebar.header("Input Parameters")
signal_strength = st.sidebar.selectbox("Signal Strength", ["Strong", "Medium", "Weak"])
network_load = st.sidebar.selectbox("Network Load", ["Low", "Medium", "High"])
user_type = st.sidebar.selectbox("User Type", ["Video", "Gaming", "Browsing", "Idle"])
mobility = st.sidebar.selectbox("Mobility", ["Stationary", "Moving"])
battery_level = st.sidebar.slider("Battery Level (%)", 0, 100, 50)

# -----------------------------
# SUBMIT SCENARIO
# -----------------------------
if st.sidebar.button("Run AI Decision"):
    try:
        row = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            signal_strength,
            network_load,
            user_type,
            mobility,
            battery_level,
            "Pending",  # Status
            "", "", "", "", ""  # AI output columns: Network_Decision, Device_Recommendation, Reasoning, Trade_Offs, Impact
        ]
        sheet.append_row(row)
        st.info("Scenario submitted. Waiting for AI decision...")

        # Optional: short wait for Zapier processing
        time.sleep(5)

        df = pd.DataFrame(sheet.get_all_records())
        latest = df.iloc[-1]

        if latest["Status"] == "Completed":
            st.success("AI Decision Ready!")
            st.subheader("📊 AI Output")
            st.write("**Network Decision:**", latest["Network_Decision"])
            st.write("**Device Recommendation:**", latest["Device_Recommendation"])
            st.write("**Reasoning:**", latest["Reasoning"])
            st.write("**Trade-Offs:**", latest["Trade_Offs"])
            st.write("**Impact:**", latest["Impact"])
        else:
            st.warning("Still processing... refresh in a few seconds")

    except Exception as e:
        st.error(f"Error submitting scenario: {e}")

# -----------------------------
# DASHBOARD / HISTORICAL SCENARIOS
# -----------------------------
st.markdown("---")
st.header("📈 Last 10 Scenarios")
try:
    df = pd.DataFrame(sheet.get_all_records())
    st.dataframe(df.tail(10))
except Exception as e:
    st.warning("Unable to load historical data yet.")
