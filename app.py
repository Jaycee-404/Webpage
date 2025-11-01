# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("""
This dashboard displays **live fall detection** updates from your BLE wearable.
""")

# ------------------ USER LOGIN ------------------
st.sidebar.header("Login")

# Registered users (example mapping; replace with your own IDs)
registered_users = {
    "USER_001": "Ramesh",
    "USER_002": "Priya",
    "USER_003": "Sundar",
}

user_id = st.sidebar.text_input("Enter your ID (e.g., USER_001)")
login_btn = st.sidebar.button("🔓 Login")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if login_btn:
    if user_id in registered_users:
        st.session_state.logged_in = True
        st.sidebar.success(f"Welcome, {registered_users[user_id]} 👋")
    else:
        st.sidebar.error("❌ Invalid ID. Contact admin to register your device.")

if not st.session_state.logged_in:
    st.warning("Please log in with your user ID to view the dashboard.")
    st.stop()

# ------------------ INITIALIZE SESSION LOG ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# ------------------ SETTINGS ------------------
EVENT_FILE = "current_event.txt"
refresh_sec = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)

# ------------------ CONTROLS ------------------
col1, col2 = st.columns(2)
if col1.button("▶️ Start Auto-Refresh"):
    st.session_state.auto_refresh = True
if col2.button("⏸️ Pause Auto-Refresh"):
    st.session_state.auto_refresh = False

status_box = st.empty()
log_box = st.empty()

def show_event(event: str):
    """Show event with color coding."""
    color_map = {
        "Normal": ("green", "🟢"),
        "About to Fall": ("orange", "🟠"),
        "Fall Detected": ("red", "🔴"),
    }
    color, emoji = color_map.get(event, ("gray", "⚪"))
    status_box.markdown(
        f"""
        <div style='background-color:{color};
                    padding:1em;
                    border-radius:12px;
                    text-align:center'>
            <h2 style='color:white'>{emoji} {event}</h2>
            <p style='color:white'>Updated at {datetime.now().strftime("%H:%M:%S")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def read_event():
    if os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "r") as f:
            event = f.read().strip() or "Waiting..."
    else:
        event = "Waiting..."
    return event

event = read_event()
show_event(event)

# Log events for this user only
if event != "Waiting...":
    if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
        new_entry = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Event": event}
        st.session_state.log = pd.concat(
            [st.session_state.log, pd.DataFrame([new_entry])],
            ignore_index=True
        )

st.subheader(f"📋 Event Log for {registered_users[user_id]}")
log_box.dataframe(st.session_state.log[::-1], use_container_width=True)

if not st.session_state.log.empty:
    csv = st.session_state.log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download My Log (CSV)", csv, f"{user_id}_fall_log.csv", "text/csv")

if st.session_state.auto_refresh:
    st.caption(f"🔄 Auto-refresh every {refresh_sec} seconds...")
else:
    st.caption("⏸️ Auto-refresh paused. Click ▶️ to continue.")
