import streamlit as st
import pandas as pd
import datetime, random, time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Fall Detection Dashboard", page_icon="🩺", layout="wide")

st.title("🩺 Adaptive IoT Fall Detection and Risk Prediction Dashboard")
st.markdown("""
Real-time visualization of sensor-based fall detection events powered by **ESP32-C3 + TinyML**.
""")

# ---------- SESSION STATE ----------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Person_ID", "Event", "Confidence"])

# ---------- SIDEBAR CONTROLS ----------
st.sidebar.header("Simulation / Live Options")
person_id = st.sidebar.text_input("Person ID", "user_001")
mode = st.sidebar.radio("Mode", ["Simulated", "Serial / API (future integration)"])
refresh_rate = st.sidebar.slider("Update every (sec)", 0.5, 5.0, 1.0)

# ---------- STATUS PANEL ----------
placeholder_status = st.empty()
placeholder_chart = st.empty()
placeholder_log = st.empty()

def classify_event():
    """Simulate TinyML output (replace with serial/API input later)."""
    events = [("Normal", "🟢", 0.95),
              ("About to Fall", "🟠", 0.82),
              ("Fall Detected", "🔴", 0.99)]
    event, icon, conf = random.choice(events)
    return event, icon, conf

# ---------- MAIN LOOP ----------
run = st.checkbox("Start Monitoring", False)

while run:
    event, icon, conf = classify_event()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append to session log
    new_entry = pd.DataFrame([[timestamp, person_id, event, f"{conf*100:.1f}%"]],
                             columns=["Timestamp", "Person_ID", "Event", "Confidence"])
    st.session_state.log = pd.concat([st.session_state.log, new_entry], ignore_index=True)

    # ----- Display Current Status -----
    color_map = {
        "Normal": "green",
        "About to Fall": "orange",
        "Fall Detected": "red"
    }
    st.markdown(f"""
    <div style='background-color:{color_map[event]};padding:1.2em;border-radius:12px;text-align:center'>
        <h2 style='color:white'>{icon} {event}</h2>
        <p style='color:white;font-size:18px'>Confidence: {conf*100:.1f}%</p>
        <p style='color:white;font-size:14px'>{timestamp}</p>
    </div>
    """, unsafe_allow_html=True)

    # ----- Show Rolling Log -----
    st.markdown("### 📋 Event Log")
    placeholder_log.dataframe(st.session_state.log[::-1], use_container_width=True)

# ---------- MAIN LOOP ----------
run = st.checkbox("Start Monitoring", False)

if run:
    while True:
        event, icon, conf = classify_event()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append to session log
        new_entry = pd.DataFrame([[timestamp, person_id, event, f"{conf*100:.1f}%"]],
                                 columns=["Timestamp", "Person_ID", "Event", "Confidence"])
        st.session_state.log = pd.concat([st.session_state.log, new_entry], ignore_index=True)

        # ----- Display Current Status -----
        color_map = {"Normal":"green","About to Fall":"orange","Fall Detected":"red"}
        placeholder_status.markdown(f"""
        <div style='background-color:{color_map[event]};padding:1.2em;border-radius:12px;text-align:center'>
            <h2 style='color:white'>{icon} {event}</h2>
            <p style='color:white;font-size:18px'>Confidence: {conf*100:.1f}%</p>
            <p style='color:white;font-size:14px'>{timestamp}</p>
        </div>
        """, unsafe_allow_html=True)

        # ----- Show Rolling Log -----
        placeholder_log.dataframe(st.session_state.log[::-1], use_container_width=True)

        # ----- Basic Counts -----
        counts = st.session_state.log["Event"].value_counts()
        placeholder_chart.bar_chart(counts)

        time.sleep(refresh_rate)
else:
    st.info("✅ Click 'Start Monitoring' to begin real-time event logging.")

