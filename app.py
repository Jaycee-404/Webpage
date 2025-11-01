import streamlit as st
import pandas as pd
import datetime, time, random

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Fall Detection Dashboard", layout="wide")
st.title("🩺 Adaptive IoT Fall Detection and Prediction Dashboard")

# ---------------- INITIALIZE STATE ----------------
if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Person_ID", "Event", "Confidence"])

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

# ---------------- SIDEBAR ----------------
st.sidebar.header("Login Panel")

# Simulated registered user list (replace with database later)
registered_users = {"USER_001": "Ramesh", "USER_002": "Priya", "USER_003": "Sundar"}

user_id = st.sidebar.text_input("Enter your ID (e.g., USER_001)")
if user_id and user_id not in registered_users:
    st.sidebar.error("❌ Invalid ID. Contact admin to register your device.")
    st.stop()

if user_id:
    st.sidebar.success(f"✅ Welcome, {registered_users[user_id]}")
else:
    st.warning("Please enter your ID to access logs.")
    st.stop()

refresh_rate = st.sidebar.slider("Auto-refresh every (sec)", 1.0, 10.0, 3.0)

# ---------------- CONTROL BUTTONS ----------------
col1, col2 = st.columns(2)
if col1.button("▶️ Start Monitoring"):
    st.session_state.monitoring = True
if col2.button("🛑 Stop Monitoring"):
    st.session_state.monitoring = False

# ---------------- PLACEHOLDERS ----------------
status_box = st.empty()
table_box = st.empty()
chart_box = st.empty()

# ---------------- EVENT GENERATOR (SIMULATED) ----------------
def classify_event():
    """Simulate TinyML output — replace with serial/MQTT input later."""
    events = [("Normal", "🟢", 0.95),
              ("About to Fall", "🟠", 0.82),
              ("Fall Detected", "🔴", 0.99)]
    return random.choice(events)

# ---------------- MAIN LOOP ----------------
if st.session_state.monitoring:
    # Simulate new event
    event, icon, conf = classify_event()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log event for this user only
    new_entry = pd.DataFrame([[timestamp, user_id, event, f"{conf*100:.1f}%"]],
                             columns=["Timestamp", "Person_ID", "Event", "Confidence"])
    st.session_state.log = pd.concat([st.session_state.log, new_entry], ignore_index=True)

    # Filter this user's data
    user_data = st.session_state.log[st.session_state.log["Person_ID"] == user_id]

    # Display current status
    color = {"Normal": "green", "About to Fall": "orange", "Fall Detected": "red"}[event]
    status_box.markdown(
        f"<div style='background-color:{color};padding:1em;border-radius:10px;text-align:center'>"
        f"<h2 style='color:white'>{icon} {event}</h2>"
        f"<p style='color:white'>Confidence {conf*100:.1f}% | {timestamp}</p></div>",
        unsafe_allow_html=True,
    )

    # Live log & chart
    table_box.dataframe(user_data[::-1], use_container_width=True)
    chart_box.bar_chart(user_data["Event"].value_counts())

    # Gentle refresh
    st.sidebar.write("Monitoring active... auto-refreshing.")
    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("✅ Click 'Start Monitoring' to begin real-time event logging.")

# ---------------- DOWNLOAD ----------------
if not st.session_state.log.empty:
    user_data = st.session_state.log[st.session_state.log["Person_ID"] == user_id]
    if not user_data.empty:
        csv = user_data.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download My Event Log (CSV)", csv, f"{user_id}_fall_events.csv", "text/csv")
