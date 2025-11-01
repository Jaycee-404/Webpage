import streamlit as st
import time
import os
from datetime import datetime
import pandas as pd

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("""
This dashboard displays **live fall detection and prediction** data from your wearable device via BLE.
""")

# ------------------ SESSION STATE INIT ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

# ------------------ UI PLACEHOLDERS ------------------
status_box = st.empty()
log_box = st.empty()

# ------------------ HELPER FUNCTION ------------------
def show_event(event):
    """Render event box with color and emoji."""
    color_map = {
        "Normal": ("green", "🟢"),
        "About to Fall": ("orange", "🟠"),
        "Fall Detected": ("red", "🔴")
    }
    color, emoji = color_map.get(event, ("gray", "⚪"))
    status_box.markdown(
        f"""
        <div style='background-color:{color};
                    padding:1em;
                    border-radius:10px;
                    text-align:center'>
            <h2 style='color:white'>{emoji} {event}</h2>
            <p style='color:white'>Updated at {datetime.now().strftime("%H:%M:%S")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------ MAIN LOOP ------------------
st.markdown("### Live Status")
st.info("⏳ Waiting for updates from BLE device...")

EVENT_FILE = "current_event.txt"
refresh_rate = 1  # seconds

while True:
    if os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "r") as f:
            event = f.read().strip()

        # Only log new events
        if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
            new_row = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Event": event}
            st.session_state.log = pd.concat(
                [st.session_state.log, pd.DataFrame([new_row])],
                ignore_index=True
            )

        show_event(event)

        # Display Event Log
        st.markdown("### 📋 Event Log")
        log_box.dataframe(st.session_state.log[::-1], use_container_width=True)
    else:
        st.warning("⚠️ Waiting for BLE listener to create `current_event.txt`...")

    time.sleep(refresh_rate)
    st.experimental_rerun()
