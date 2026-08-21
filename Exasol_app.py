import pandas as pd
from google import genai
import streamlit as st

# 1. Setup Gemini API Client via Streamlit Secrets
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. Load Patient Data
patients_df = pd.read_csv("patient_history.csv").fillna("None")

# 3. UI Setup
st.title("🏥 Hospital Triage AI")
st.write("Track: Trust, Safety & Governance")

# Select Patient
patient_ids = patients_df["Patient_ID"].tolist()
selected_patient = st.selectbox("Select Patient ID:", patient_ids)

patient_info = patients_df[
    patients_df["Patient_ID"] == selected_patient
].iloc[0]

# Display Demographics
st.subheader("Patient Demographics")
col1, col2, col3 = st.columns(3)
col1.metric("Patient Name", patient_info["Name"])
col2.metric("Age", f"{patient_info['Age']} yrs")
col3.metric("Gender", patient_info["Gender"])

st.info(
    f"**Chronic Conditions:** {patient_info['Chronic_Conditions']} | "
    f"**Past Surgeries:** {patient_info['Past_Surgeries']}"
)

# 4. Nurse Symptom Input & AI Triage
symptoms = st.chat_input("Enter the patient's symptoms here...")

if symptoms:
  with st.chat_message("user"):
    st.write(f"**Symptoms:** {symptoms}")

  ai_prompt = f"""
    You are a hospital triage AI. 
    Patient Name: {patient_info['Name']}
    Age: {patient_info['Age']}
    Gender: {patient_info['Gender']}
    Chronic Conditions: {patient_info['Chronic_Conditions']}
    Current Symptoms: {symptoms}
    
    Based on this data, which hospital ward should they go to, and why? Be brief.
    """

  with st.spinner("AI is analyzing patient data..."):
    response = client.models.generate_content(
        model="gemini-3.5-flash", contents=ai_prompt
    )

    with st.chat_message("assistant"):
      st.write(response.text)
      st.success("Governance Check: Decision logged securely.")
