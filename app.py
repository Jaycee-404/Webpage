import streamlit as st
import pandas as pd
import datetime, time, random

st.set_page_config(page_title="Fall Detection Dashboard", layout="wide")
st.title("🩺 Fall Detection and Prediction Dashboard")

# ----------------- INIT -----------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Person_ID", "Event", "Confidence"])
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# ----------------- SIDEBAR -----------------
st.sidebar.header("Control Panel")
person_id = st.sidebar.text_input("Person ID", "user_001")
refresh_rate = st.sidebar.slider("Update every (sec)", 0.5, 5.0, 1.0)

# ----------------- BUTTONS -----------------
col1, col2 = st.columns(2)
if col1.button("▶️ Start Monitoring"):
    st.session_state.monitoring = True
if col2.button("🛑 Stop Monitoring"):
    st.session_state.monitoring = False

# ----------------- PLACEHOLDERS -----------------
status_box = st.empty()
table_box = st.empty()
chart_box = st.empty()

def classify_event():
    """Simulate model output. Replace with live serial/MQTT later."""
    events = [("Normal", "🟢", 0.95),
              ("About to Fall", "🟠", 0.82),
              ("Fall Detected", "🔴", 0.99)]
    return random.choice(events)

# ----------------- MAIN LOOP -----------------
if st.session_state.monitoring:
    # One loop cycle per render
    event, icon, conf = classify_event()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = pd.DataFrame([[timestamp, person_id, event, f"{conf*100:.1f}%"]],
                             columns=["Timestamp", "Person_ID", "Event", "Confidence"])
    st.session_state.log = pd.concat([st.session_state.log, new_entry], ignore_index=True)

    # Display current status
    color = {"Normal": "green", "About to Fall": "orange", "Fall Detected": "red"}[event]
    status_box.markdown(
        f"<div style='background-color:{color};padding:1em;border-radius:10px;text-align:center'>"
        f"<h2 style='color:white'>{icon} {event}</h2>"
        f"<p style='color:white'>Confidence {conf*100:.1f}% | {timestamp}</p></div>",
        unsafe_allow_html=True,
    )

    table_box.dataframe(st.session_state.log[::-1], use_container_width=True)
    chart_box.bar_chart(st.session_state.log["Event"].value_counts())

    # Auto-refresh page gently
    st.sidebar.write("Monitoring... auto-refreshing every few seconds.")
    time.sleep(refresh_rate)
    st.rerun()  # safe rerun after entire render completes

else:
    st.info("✅ Click 'Start Monitoring' to begin real-time event logging.")

# ----------------- DOWNLOAD -----------------
if not st.session_state.log.empty:
    csv = st.session_state.log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Event Log (CSV)", csv, "fall_events.csv", "text/csv")
