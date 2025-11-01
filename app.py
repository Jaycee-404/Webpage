import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
import time

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("""
This dashboard shows **live fall detection** data from your BLE wearable device.
It reads automatically from `fall_data.csv` saved by your BLE listener script.
""")

# ------------------ SETTINGS ------------------
CSV_FILE = "fall_data.csv"
refresh_sec = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)

# ------------------ TIMEZONE ------------------
IST = pytz.timezone("Asia/Kolkata")

# ------------------ SESSION STATE INIT ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

# ------------------ UI PLACEHOLDERS ------------------
status_box = st.empty()
log_box = st.empty()

# ------------------ HELPER FUNCTION ------------------
def show_event(event: str):
    color_map = {
        "Normal": ("green", "🟢"),
        "About to Fall": ("orange", "🟠"),
        "Fall Detected": ("red", "🔴"),
    }
    color, emoji = color_map.get(event, ("gray", "⚪"))
    current_time = datetime.now(IST).strftime("%H:%M:%S")
    status_box.markdown(
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

# ------------------ MAIN LOOP ------------------
if os.path.exists(CSV_FILE):
    try:
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            event = df.iloc[-1]["Event"]
            timestamp = df.iloc[-1]["Timestamp"]
            show_event(event)

            # Add new rows to session log only if changed
            if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
                new_entry = {"Timestamp": timestamp, "Event": event}
                st.session_state.log = pd.concat(
                    [st.session_state.log, pd.DataFrame([new_entry])],
                    ignore_index=True
                )
        else:
            st.warning("⚠️ CSV exists but is empty. Waiting for BLE listener to write data.")
            event = "Waiting..."
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        event = "Waiting..."
else:
    st.warning("⚠️ `fall_data.csv` not found. Run BLE listener to start logging events.")
    event = "Waiting..."

# ------------------ DISPLAY ------------------
st.subheader("📋 Event Log")
if not st.session_state.log.empty:
    st.session_state.log["Timestamp"] = pd.to_datetime(st.session_state.log["Timestamp"])
    st.session_state.log = st.session_state.log.sort_values(by="Timestamp", ascending=False)
    log_box.dataframe(st.session_state.log, use_container_width=True)
else:
    st.info("No events logged yet.")

# ------------------ REFRESH ------------------
st.caption(f"🔄 Auto-refreshing every {refresh_sec} seconds (local IST time).")
time.sleep(refresh_sec)
st.experimental_rerun()
