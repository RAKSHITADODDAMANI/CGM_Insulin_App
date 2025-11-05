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

    readings = []

    for t in range(1, 31):  # 30 time steps
        error = glucose - target_glucose
        integral += error
        derivative = error - prev_error
        insulin = kp * error + ki * integral + kd * derivative
        glucose = glucose - insulin * 0.5 + np.random.normal(0, 1)
        prev_error = error
        readings.append([t, round(glucose, 2), round(insulin, 2)])
        time.sleep(0.3)
        yield readings

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
            for readings in simulate_glucose_control(kp, ki, kd, target_glucose):
                if not st.session_state.running:
                    break
                df = pd.DataFrame(readings, columns=["Time", "Glucose (mg/dL)", "Insulin (mU/L)"])
                st.session_state.data = df
                chart_placeholder.line_chart(df.set_index("Time"))
        st.success("✅ Simulation completed!")
    elif stop:
        st.session_state.running = False
        st.warning("⏹️ Simulation stopped by user.")

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

st.markdown("---")
st.markdown("🔬 **Developed for educational demonstration of glucose-insulin feedback control using PID.**")
