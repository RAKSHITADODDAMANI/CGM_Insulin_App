import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="CGM + Insulin Pump", layout="wide")
st.title("💉 Continuous Glucose Monitoring with Insulin Pump Control")
st.markdown("""This demo simulates **real-time glucose monitoring** and **automatic insulin dosing** using a basic **PID controller**.""")

st.sidebar.header("📊 Data Options")
data_source = st.sidebar.radio("Select Data Source:", ["Simulated", "Upload CSV"])

if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload your glucose data CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.warning("Please upload a CSV file.")
        st.stop()
else:
    time = np.arange(0, 300, 1)
    glucose = 120 + 30*np.sin(time/30) + np.random.normal(0, 5, len(time))
    df = pd.DataFrame({"Time (min)": time, "Glucose (mg/dL)": glucose})

target = st.sidebar.slider("Target Glucose Level (mg/dL)", 80, 130, 100)
Kp = st.sidebar.slider("Kp (Proportional Gain)", 0.1, 1.0, 0.5)
Ki = st.sidebar.slider("Ki (Integral Gain)", 0.0, 0.1, 0.01)
Kd = st.sidebar.slider("Kd (Derivative Gain)", 0.0, 0.5, 0.1)

insulin_dose = []
integral, prev_error = 0, 0

for g in df["Glucose (mg/dL)"]:
    error = g - target
    integral += error
    derivative = error - prev_error
    insulin = Kp * error + Ki * integral + Kd * derivative
    insulin = max(0, round(insulin, 2))
    insulin_dose.append(insulin)
    prev_error = error

df["Insulin Dose (units)"] = insulin_dose

current_glucose = df["Glucose (mg/dL)"].iloc[-1]
if current_glucose > 180:
    st.error("⚠️ High glucose detected! Increase insulin dosage.")
elif current_glucose < 70:
    st.warning("⚠️ Low glucose! Intake glucose immediately.")
else:
    st.success("✅ Glucose is in the normal range.")

st.subheader("📈 Glucose and Insulin Trends")
fig, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df["Time (min)"], df["Glucose (mg/dL)"], label="Glucose Level", color='tab:red')
ax1.axhline(y=target, color='r', linestyle='--', label='Target')
ax1.set_xlabel("Time (min)")
ax1.set_ylabel("Glucose (mg/dL)")
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(df["Time (min)"], df["Insulin Dose (units)"], label="Insulin Dose", color='tab:blue')
ax2.set_ylabel("Insulin (units)")
ax2.legend(loc="upper right")

st.pyplot(fig)
st.subheader("📋 Recent Readings")
st.dataframe(df.tail(10))

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(label="⬇️ Download Results as CSV", data=csv, file_name='cgm_results.csv', mime='text/csv')

st.markdown("---")
st.caption("Developed by [Your Name] | Smart Insulin Control Project")
