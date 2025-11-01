import streamlit as st
import pandas as pd
import datetime, time, random

st.set_page_config(page_title="Fall Detection Dashboard", layout="wide")
st.title("🩺 Fall Detection and Prediction Dashboard")

if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Timestamp", "Person_ID", "Event", "Confidence"])

person_id = st.sidebar.text_input("Person ID", "user_001")
refresh_rate = st.sidebar.slider("Update every (sec)", 0.5, 5.0, 1.0)

run = st.checkbox("Start Monitoring", key="run_monitoring")

status_box = st.empty()
table_box = st.empty()
chart_box = st.empty()

def classify_event():
    events = [("Normal", "🟢", 0.95),
              ("About to Fall", "🟠", 0.82),
              ("Fall Detected", "🔴", 0.99)]
    return random.choice(events)

if run:
    stop_button = st.button("🛑 Stop Monitoring")
    if stop_button:
        st.session_state["run_monitoring"] = False
        st.stop()

    event, icon, conf = classify_event()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.log.loc[len(st.session_state.log)] = [timestamp, person_id, event, f"{conf*100:.1f}%"]

    color = {"Normal": "green", "About to Fall": "orange", "Fall Detected": "red"}[event]
    status_box.markdown(
        f"<div style='background-color:{color};padding:1em;border-radius:10px;text-align:center'>"
        f"<h2 style='color:white'>{icon} {event}</h2>"
        f"<p style='color:white'>Confidence {conf*100:.1f}% | {timestamp}</p></div>",
        unsafe_allow_html=True,
    )

    table_box.dataframe(st.session_state.log[::-1], use_container_width=True)
    chart_box.bar_chart(st.session_state.log["Event"].value_counts())

    time.sleep(refresh_rate)
    st.experimental_rerun()
else:
    st.info("✅ Click 'Start Monitoring' to begin real-time event logging.")
