import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from io import BytesIO

# ------------------------------
# PAGE CONFIG
# ------------------------------
st.set_page_config(page_title="CGM + Insulin Pump", layout="wide")

st.title("🩸 Continuous Glucose Monitoring + Insulin Pump Controller")
st.markdown(
    """
    This app simulates **real-time glucose monitoring** and **insulin control**
    using a PID controller. You can adjust parameters, start/stop simulation,
    and download readings as a CSV file.
    """
)

# ------------------------------
# SIDEBAR: CONTROL PANEL
# ------------------------------
st.sidebar.header("⚙️ Control Settings")
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

    start_sim = st.button("▶️ Start Simulation")
    stop_sim = st.button("⏹ Stop Simulation")

    graph_placeholder = st.empty()
    status_placeholder = st.empty()

    if start_sim:
        glucose = 120
        insulin = 0
        error_sum = 0
        last_error = 0
        glucose_history = []
        insulin_history = []
        time_history = []

        time_steps = 150
        run_simulation = True

        for t in range(time_steps):
            if stop_sim:
                status_placeholder.info("🛑 Simulation stopped.")
                run_simulation = False
                break

            # Simulate glucose variation
            glucose += np.random.randn() * 2

            # PID logic
            error = target_glucose - glucose
            error_sum += error
            d_error = error - last_error
            last_error = error

            insulin = kp * error + ki * error_sum + kd * d_error
            insulin = max(0, insulin)

            glucose += np.random.randn() - insulin * 0.1

            glucose_history.append(glucose)
            insulin_history.append(insulin)
            time_history.append(t)

            # Live graph
            fig, ax1 = plt.subplots()
            ax1.plot(time_history, glucose_history, color='r', label='Glucose (mg/dL)')
            ax1.axhline(y=target_glucose, color='r', linestyle='--', label='Target')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Glucose Level', color='r')
            ax2 = ax1.twinx()
            ax2.plot(time_history, insulin_history, color='b', label='Insulin Dose (units)')
            ax2.set_ylabel('Insulin Dose', color='b')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            graph_placeholder.pyplot(fig)
            plt.close(fig)

            # Status messages
            if glucose < 70:
                status_placeholder.warning("⚠️ Glucose too low! (Hypoglycemia risk)")
            elif glucose > 180:
                status_placeholder.error("🚨 Glucose too high! (Hyperglycemia risk)")
            else:
                status_placeholder.success("✅ Glucose is in the normal range.")

            time.sleep(0.2)

        # After simulation: download CSV
        if run_simulation:
            df = pd.DataFrame({
                "Time (s)": time_history,
                "Glucose (mg/dL)": glucose_history,
                "Insulin (units)": insulin_history
            })
            st.success("✅ Simulation complete!")

            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Glucose-Insulin Data (CSV)",
                data=csv_buffer.getvalue(),
                file_name="glucose_insulin_simulation.csv",
                mime="text/csv"
            )

# ------------------------------
# MODE 2: UPLOAD CSV
# ------------------------------
else:
    st.subheader("📁 Upload Glucose Data (CSV)")
    file = st.file_uploader("Upload a CSV file with a 'Glucose' column", type=["csv"])

    if file is not None:
        df = pd.read_csv(file)
        st.write("Preview of Uploaded Data:")
        st.dataframe(df.head())

        if 'Glucose' in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df['Glucose'], color='r', label='Glucose Level')
            ax.axhline(y=target_glucose, color='r', linestyle='--', label='Target')
            ax.set_xlabel('Time')
            ax.set_ylabel('Glucose (mg/dL)')
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("❌ CSV must include a 'Glucose' column.")

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("---")
st.markdown("👩‍⚕️ **Developed for educational demonstration of glucose-insulin feedback control using PID.**")
