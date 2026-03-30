import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime
import time

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI RAN Dashboard", layout="wide")

st.title("📡 AI RAN Intelligent Network Dashboard")

# -----------------------------
# GOOGLE SHEETS CONNECTION
# -----------------------------
SHEET_NAME = "RAN_Scenarios"

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(st.secrets["google_creds"]["creds"])
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# -----------------------------
# PARSE AI RESPONSE
# -----------------------------
def parse_ai_response(response):
    sections = {
        "Network Decision": "",
        "Device Recommendation": "",
        "Reasoning": "",
        "Trade-Offs": "",
        "Impact": ""
    }

    for key in sections.keys():
        try:
            part = response.split(key + ":")[1]
            next_keys = [k for k in sections.keys() if k != key]
            for nk in next_keys:
                if nk + ":" in part:
                    part = part.split(nk + ":")[0]
            sections[key] = part.strip()
        except:
            sections[key] = "N/A"

    return sections

# -----------------------------
# SIDEBAR INPUT (SIMULATOR)
# -----------------------------
st.sidebar.header("📲 Scenario Simulator")

signal_strength = st.sidebar.selectbox("Signal Strength", ["Strong", "Medium", "Weak"])
network_load = st.sidebar.selectbox("Network Load", ["Low", "Medium", "High"])
user_type = st.sidebar.selectbox("User Type", ["Video", "Gaming", "Browsing", "Idle"])
mobility = st.sidebar.selectbox("Mobility", ["Stationary", "Moving"])
battery_level = st.sidebar.slider("Battery Level (%)", 0, 100, 50)

# -----------------------------
# SUBMIT BUTTON
# -----------------------------
if st.sidebar.button("🚀 Run AI Decision"):
    row = [
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        signal_strength,
        network_load,
        user_type,
        mobility,
        battery_level,
        "Pending",
        ""  # AI_Response
    ]

    sheet.append_row(row)
    st.sidebar.success("Scenario submitted!")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.DataFrame(sheet.get_all_records())

if len(df) == 0:
    st.warning("No data yet.")
    st.stop()

latest = df.iloc[-1]

# -----------------------------
# KPI METRICS (TOP DASHBOARD)
# -----------------------------
st.markdown("## 📊 Network KPIs")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📶 Signal", latest["signal_strength"])
col2.metric("📡 Load", latest["network_load"])
col3.metric("🔋 Battery", f"{latest['battery_level']}%")
col4.metric("🚶 Mobility", latest["mobility"])

# -----------------------------
# AI DECISION PANEL
# -----------------------------
st.markdown("---")
st.markdown("## 🤖 AI RAN Decision Engine")

if latest["Status"] == "Completed":

    parsed = parse_ai_response(latest["AI_Response"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📡 Network Decision")
        st.success(parsed["Network Decision"])

        st.markdown("### ⚙️ Device Recommendation")
        st.info(parsed["Device Recommendation"])

    with col2:
        st.markdown("### 🧠 Reasoning")
        st.write(parsed["Reasoning"])

        st.markdown("### ⚖️ Trade-Offs")
        st.write(parsed["Trade-Offs"])

        st.markdown("### 📊 Impact")
        st.write(parsed["Impact"])

else:
    st.warning("⏳ Waiting for AI processing... Refresh in a few seconds")

# -----------------------------
# AUTO REFRESH (LIVE FEEL)
# -----------------------------
time.sleep(5)
st.experimental_rerun()

# -----------------------------
# HISTORICAL DATA
# -----------------------------
st.markdown("---")
st.markdown("## 📈 Historical Scenarios")

st.dataframe(df.tail(10), use_container_width=True)
