import streamlit as st
import pandas as pd
import numpy as np
import time
import io

st.set_page_config(page_title="CGM + Insulin Pump", layout="wide")

st.sidebar.title("⚙️ Control Settings")
mode = st.sidebar.radio("Select Mode:", ["Live Simulation", "Upload CSV"])

target_glucose = st.sidebar.slider("🎯 Target Glucose (mg/dL)", 70, 180, 100)
kp = st.sidebar.slider("Kp (Proportional Gain)", 0.0, 1.0, 0.26, 0.01)
ki = st.sidebar.slider("Ki (Integral Gain)", 0.0, 1.0, 0.03, 0.01)
kd = st.sidebar.slider("Kd (Derivative Gain)", 0.0, 1.0, 0.10, 0.01)

st.title("💧 Continuous Glucose Monitoring + Insulin Pump Controller")
st.markdown("""
This app simulates **real-time glucose monitoring and insulin control** using a PID controller.
You can adjust parameters, start/stop simulation, and download readings as a CSV file.
""")

placeholder = st.empty()

if "running" not in st.session_state:
    st.session_state.running = False
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Time", "Glucose (mg/dL)", "Insulin (mU/L)"])

def simulate_glucose_control(kp, ki, kd, target_glucose):
    glucose = np.random.randint(100, 140)
    insulin = 0
    integral = 0
    prev_error = 0
    t = 0

    while st.session_state.running:
        t += 1
        error = glucose - target_glucose
        integral += error
        derivative = error - prev_error
        insulin = kp * error + ki * integral + kd * derivative
        glucose = glucose - insulin * 0.5 + np.random.normal(0, 1)
        prev_error = error
        yield [t, round(glucose, 2), round(insulin, 2)]
        time.sleep(0.5)

if mode == "Live Simulation":
    col1, col2 = st.columns(2)
    start = col1.button("▶️ Start Simulation")
    stop = col2.button("⏹️ Stop Simulation")

    if start:
        st.session_state.running = True
        st.session_state.data = pd.DataFrame(columns=["Time", "Glucose (mg/dL)", "Insulin (mU/L)"])
        placeholder.empty()
        with placeholder.container():
            st.subheader("📈 Live Glucose & Insulin Monitoring")
            chart_placeholder = st.empty()
            table_placeholder = st.empty()
            for reading in simulate_glucose_control(kp, ki, kd, target_glucose):
                new_row = pd.DataFrame([reading], columns=["Time", "Glucose (mg/dL)", "Insulin (mU/L)"])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                chart_placeholder.line_chart(st.session_state.data.set_index("Time"))
                table_placeholder.dataframe(st.session_state.data.tail(10))  # Show last 10 readings

    elif stop:
        st.session_state.running = False
        st.warning("⏹️ Simulation stopped by user.")
        if not st.session_state.data.empty:
            st.subheader("📊 Last Recorded Readings")
            st.dataframe(st.session_state.data.tail(10))

elif mode == "Upload CSV":
    st.subheader("📤 Upload your Glucose Data CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview of Uploaded Data")
        st.dataframe(df.head())
        st.line_chart(df.set_index(df.columns[0]))

# Download button (available if data exists)
if not st.session_state.data.empty:
    buffer = io.BytesIO()
    st.session_state.data.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="💾 Download Readings as CSV",
        data=buffer,
        file_name="glucose_readings.csv",
        mime="text/csv"
    )
