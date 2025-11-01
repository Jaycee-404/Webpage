# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("This dashboard shows **live fall detection** events from your BLE wearable.")

# ------------------ SESSION STATE INIT ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

# ------------------ SETTINGS ------------------
EVENT_FILE = "current_event.txt"
refresh_sec = st.sidebar.slider("Auto-refresh every (sec)", 1, 10, 2)

# Trigger a safe rerun every N seconds; returns an incrementing counter
_ = st.autorefresh(interval=refresh_sec * 1000, key="data_refresh")

# ------------------ UI PLACEHOLDERS ------------------
status_box = st.empty()
log_box = st.empty()

def show_event(event: str):
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

# ------------------ MAIN LOGIC ------------------
st.subheader("Live Status")

if os.path.exists(EVENT_FILE):
    try:
        with open(EVENT_FILE, "r") as f:
            event = f.read().strip() or "Waiting..."
    except Exception as e:
        event = "Waiting..."
        st.warning(f"Could not read event file: {e}")
else:
    event = "Waiting..."
    st.info("⚠️ Waiting for BLE listener to create `current_event.txt` ...")

show_event(event)

# Log only when the event changes
if event != "Waiting...":
    if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
        st.session_state.log.loc[len(st.session_state.log)] = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            event
        ]

st.subheader("📋 Event Log")
log_box.dataframe(st.session_state.log[::-1], use_container_width=True)

# Download button for the current session's log
if not st.session_state.log.empty:
    csv = st.session_state.log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Log (CSV)", csv, "fall_events_session.csv", "text/csv")
