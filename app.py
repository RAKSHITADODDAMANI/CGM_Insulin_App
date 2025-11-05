import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="CGM + Insulin Pump", layout="wide")

st.title("🩸 Continuous Glucose Monitoring + Insulin Pump Controller")
st.markdown(
    """
    This app simulates **real-time glucose monitoring** and **insulin control**
    using a simple PID controller. You can adjust target glucose levels and PID parameters
    to observe how insulin dosage stabilizes blood sugar.
    """
)

# ------------------------------
# SIDEBAR: CONTROL PARAMETERS
# ------------------------------
st.sidebar.header("⚙️ Data & Control Options")
mode = st.sidebar.radio("Select Mode:", ["Live Simulation", "Upload CSV"])

target_glucose = st.sidebar.slider("🎯 Target Glucose (mg/dL)", 70, 180, 100)
kp = st.sidebar.slider("Kp (Proportional Gain)", 0.0, 1.0, 0.5, step=0.01)
ki = st.sidebar.slider("Ki (Integral Gain)", 0.0, 0.1, 0.01, step=0.001)
kd = st.sidebar.slider("Kd (Derivative Gain)", 0.0, 0.2, 0.1, step=0.01)

# ------------------------------
# MODE 1: LIVE SIMULATION
# ------------------------------
if mode == "Live Simulation":
    st.subheader("📡 Live Glucose & Insulin Monitoring")

    graph_placeholder = st.empty()
    status_placeholder = st.empty()

    # Simulation parameters
    time_steps = 100
    glucose = 120
    insulin = 0
    error_sum = 0
    last_error = 0

    glucose_history = []
    insulin_history = []

    # Real-time loop
    for t in range(time_steps):
        # Simulate natural body variation
        glucose += np.random.randn() * 2

        # PID control logic
        error = target_glucose - glucose
        error_sum += error
        d_error = error - last_error
        last_error = error

        insulin = kp * error + ki * error_sum + kd * d_error
        insulin = max(0, insulin)  # Insulin can't be negative

        # Glucose response (insulin lowers glucose)
        glucose += np.random.randn() - insulin * 0.1

        glucose_history.append(glucose)
        insulin_history.append(insulin)

        # Plot dynamic chart
        fig, ax1 = plt.subplots()
        ax1.plot(glucose_history, color='r', label='Glucose Level (mg/dL)')
        ax1.axhline(y=target_glucose, color='r', linestyle='--', label='Target')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Glucose Level', color='r')
        ax2 = ax1.twinx()
        ax2.plot(insulin_history, color='b', label='Insulin Dose (units)')
        ax2.set_ylabel('Insulin Dose', color='b')
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        graph_placeholder.pyplot(fig)
        plt.close(fig)

        # Update status
        if glucose < 70:
            status_placeholder.warning("⚠️ Glucose too low! (Hypoglycemia risk)")
        elif glucose > 180:
            status_placeholder.error("🚨 Glucose too high! (Hyperglycemia risk)")
        else:
            status_placeholder.success("✅ Glucose is in the normal range.")

        time.sleep(0.2)

# ------------------------------
# MODE 2: CSV UPLOAD
# ------------------------------
else:
    st.subheader("📁 Upload Glucose Data (CSV)")
    file = st.file_uploader("Upload a CSV file containing glucose readings", type=["csv"])
    if file is not None:
        import pandas as pd
        df = pd.read_csv(file)
        st.write("Preview of your data:")
        st.dataframe(df.head())

        if 'Glucose' in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df['Glucose'], color='r', label='Glucose Level')
            ax.axhline(y=target_glucose, color='r', linestyle='--', label='Target')
            ax.set_xlabel('Time')
            ax.set_ylabel('Glucose Level (mg/dL)')
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("❌ CSV must contain a 'Glucose' column.")

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("---")
st.markdown("👩‍⚕️ **Developed for educational demonstration of glucose-insulin feedback control using PID.**")
