# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")
st.title("🩺 Real-Time IoT Fall Detection Dashboard")

st.markdown("""
This dashboard shows **live fall detection** data coming from your BLE wearable device.
""")

# ------------------ STATE INIT ------------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Event"])

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# ------------------ SETTINGS ------------------
EVENT_FILE = "current_event.txt"
refresh_sec = st.sidebar.slider("Refresh interval (seconds)", 1, 10, 2)

# ------------------ UI BUTTONS ------------------
col1, col2 = st.columns(2)
if col1.button("▶️ Start Auto-Refresh"):
    st.session_state.auto_refresh = True
if col2.button("⏸️ Pause Auto-Refresh"):
    st.session_state.auto_refresh = False

status_box = st.empty()
log_box = st.empty()

# ------------------ FUNCTION ------------------
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

# ------------------ MAIN READ FUNCTION ------------------
def read_event():
    if os.path.exists(EVENT_FILE):
        with open(EVENT_FILE, "r") as f:
            event = f.read().strip() or "Waiting..."
    else:
        event = "Waiting..."
    return event

# ------------------ DISPLAY ------------------
event = read_event()
show_event(event)

# log only new entries
if event != "Waiting...":
    if len(st.session_state.log) == 0 or st.session_state.log.iloc[-1]["Event"] != event:
        new_entry = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Event": event}
        st.session_state.log = pd.concat(
            [st.session_state.log, pd.DataFrame([new_entry])],
            ignore_index=True
        )

st.subheader("📋 Event Log")
log_box.dataframe(st.session_state.log[::-1], use_container_width=True)

if not st.session_state.log.empty:
    csv = st.session_state.log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Log (CSV)", csv, "fall_events.csv", "text/csv")

# ------------------ AUTO-REFRESH ------------------
# only refresh if toggle is ON
if st.session_state.auto_refresh:
    st.markdown(
        f"<p style='text-align:center;color:gray'>🔄 Auto-refreshing every {refresh_sec} seconds...</p>",
        unsafe_allow_html=True,
    )
    st.experimental_singleton.clear()  # optional cleanup
    st.toast("Refreshed!", icon="🔁")
    st.session_state._timer = st.session_state.get("_timer", 0) + 1
    st.experimental_set_query_params(refresh=st.session_state._timer)
else:
    st.caption("⏸️ Auto-refresh paused. Click ▶️ Start Auto-Refresh to continue.")
