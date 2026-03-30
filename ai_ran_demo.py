iimport json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Load JSON string from Streamlit Secrets
creds_dict = json.loads(st.secrets["google_creds"]["creds"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("RAN_Scenarios").sheet1

# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="AI RAN Simulator", layout="wide")
st.title("📡 AI RAN Decision Simulator")

st.sidebar.header("Input Parameters")

signal_strength = st.sidebar.selectbox("Signal Strength", ["Strong", "Medium", "Weak"])
network_load = st.sidebar.selectbox("Network Load", ["Low", "Medium", "High"])
user_type = st.sidebar.selectbox("User Type", ["Video", "Gaming", "Browsing", "Idle"])
mobility = st.sidebar.selectbox("Mobility", ["Stationary", "Moving"])
battery_level = st.sidebar.slider("Battery Level (%)", 0, 100, 50)

# -----------------------------
# SUBMIT
# -----------------------------
if st.sidebar.button("Run AI Decision"):

    row = [
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        signal_strength,
        network_load,
        user_type,
        mobility,
        battery_level,
        "Pending", "", "", "", "", ""
    ]

    sheet.append_row(row)
    st.info("Scenario submitted. Waiting for AI decision...")

    # Wait for Zapier to process
    time.sleep(5)

    # Read latest data
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

# -----------------------------
# DASHBOARD
# -----------------------------
st.markdown("---")
st.header("📈 Historical Scenarios")

df = pd.DataFrame(sheet.get_all_records())
st.dataframe(df.tail(10))
