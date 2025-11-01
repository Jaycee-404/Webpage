import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("""
This dashboard shows **live fall detection** data from your BLE wearable device.
It reads from `fall_data.csv` saved by your BLE listener script.
""")

# ------------------ SETTINGS ------------------
CSV_FILE = "fall_data.csv"
IST = pytz.timezone("Asia/Kolkata")

# ------------------ LOGIN SECTION ------------------
st.sidebar.header("Login")

# Sample registered users
registered_users = {
    "USER_001": "Ramesh",
    "USER_002": "Priya",
    "USER_003": "Sundar",
}

# Input user ID
user_id = st.sidebar.text_input("Enter your ID (e.g., USER_001)")
login_btn = st.sidebar.button("🔓 Login")

# Initialize login session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if login_btn:
    if user_id in registered_users:
        st.session_state.logged_in = True
        st.sidebar.success(f"Welcome, {registered_users[user_id]} 👋")
    else:
        st.sidebar.error("❌ Invalid ID. Contact admin to register your device.")

# Stop the app until logged in
if not st.session_state.logged_in:
    st.warning("Please log in with your user ID to view the dashboard.")
    st.stop()

# ------------------ SESSION STATE FOR LOG ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

# ------------------ HELPER FUNCTION ------------------
def show_event(event: str):
    """Display the current event box with color coding."""
    color_map = {
        "Normal": ("green", "🟢"),
        "About to Fall": ("orange", "🟠"),
        "Fall Detected": ("red", "🔴"),
    }
    color, emoji = color_map.get(event, ("gray", "⚪"))
    current_time = datetime.now(IST).strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div style='background-color:{color};
                    padding:1em;
                    border-radius:12px;
                    text-align:center'>
            <h2 style='color:white'>{emoji} {event}</h2>
            <p style='color:white'>Updated at {current_time} (IST)</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------ FILE READER ------------------
def read_latest_event():
    """Read the most recent event from the CSV file."""
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            event = df.iloc[-1]["Event"]
            timestamp = df.iloc[-1]["Timestamp"]
            return event, timestamp
        else:
            return "Waiting...", None
    else:
        return "Waiting...", None

# ------------------ MAIN UI ------------------
st.sidebar.header("Controls")
if st.sidebar.button("🔄 Refresh Now"):
    st.session_state.refreshed = True

event, timestamp = read_latest_event()
show_event(event)

# ------------------ EVENT LOG ------------------
if event != "Waiting...":
    if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
        st.session_state.log.loc[len(st.session_state.log)] = [timestamp, event]

st.subheader(f"📋 Event Log for {registered_users[user_id]}")
if not st.session_state.log.empty:
    st.session_state.log["Timestamp"] = pd.to_datetime(st.session_state.log["Timestamp"])
    st.session_state.log = st.session_state.log.sort_values(by="Timestamp", ascending=False)
    st.dataframe(st.session_state.log, use_container_width=True)
else:
    st.info("No events logged yet.")

st.caption("Click **🔄 Refresh Now** in the sidebar to update manually.")
