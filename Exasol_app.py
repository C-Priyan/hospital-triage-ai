import pandas as pd
from google import genai
import streamlit as st

# 1. Setup the Google Gemini API Client securely
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# 2. Load the synthetic data
patients_df = pd.read_csv("patient_history.csv").fillna("None")

# 3. Build the Website Interface
st.title("🏥 Hospital Triage AI")
st.write("Track: Trust, Safety & Governance")

# ==========================================
# 4. PATIENT INTAKE TOGGLE
# ==========================================
patient_type = st.radio(
    "Select Patient Type:",
    options=["Existing Patient (EHR Lookup)", "New Patient (Walk-in)"],
    horizontal=True,
)

st.divider()

if patient_type == "Existing Patient (EHR Lookup)":
    # --- EXISTING PATIENT FLOW ---
    patient_ids = patients_df["Patient_ID"].tolist()
    selected_patient = st.selectbox("Search Patient ID:", patient_ids)

    # Fetch data from CSV
    patient_info = patients_df[
        patients_df["Patient_ID"] == selected_patient
    ].iloc[0]

    # Extract variables directly from the database
    patient_name = patient_info["Name"]
    patient_age = patient_info["Age"]
    patient_gender = patient_info["Gender"]
    patient_chronic = patient_info["Chronic_Conditions"]
    patient_surgeries = patient_info["Past_Surgeries"]

    # Display Demographics
    st.subheader("Patient Demographics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Patient Name", patient_name)
    col2.metric("Age", f"{patient_age} yrs")
    col3.metric("Gender", patient_gender)

    st.info(
        f"**Chronic Conditions:** {patient_chronic} | **Past Surgeries:** {patient_surgeries}"
    )

else:
    # --- NEW PATIENT FLOW ---
    st.subheader("New Patient Registration")

    col1, col2, col3 = st.columns(3)
    patient_name = col1.text_input("Full Name", value="Walk-in Patient")
    patient_age = col2.number_input("Age", min_value=0, max_value=120, value=30)
    patient_gender = col3.selectbox("Gender", ["Male", "Female", "Non-binary"])

    patient_chronic = st.text_input(
        "Chronic Conditions (e.g., Asthma, None)", value="None"
    )

# ==========================================
# 5. THE AI TRIAGE CHAT & BED ALLOCATION
# ==========================================
st.divider()
symptoms = st.chat_input("Enter the patient's symptoms here...")

if symptoms:
    with st.chat_message("user"):
        st.write(f"**Symptoms:** {symptoms}")

    ai_prompt = f"""
    You are a hospital triage AI. 
    Patient Name: {patient_name}
    Age: {patient_age}
    Gender: {patient_gender}
    Chronic Conditions: {patient_chronic}
    Current Symptoms: {symptoms}
    
    Based on this data, which hospital ward should they go to? 
    You MUST include one of these exact phrases in your response: 
    "General Ward", "ICU", "NICU", "Maternity", "Pediatric", "Oncology", or "Emergency".
    Be brief with your reasoning.
    """

    with st.spinner("AI is analyzing patient data..."):
        response = client.models.generate_content(
            model="gemini-3.5-flash", contents=ai_prompt
        )

        with st.chat_message("assistant"):
            st.write(response.text)

            # --- BED ALLOCATION ENGINE ---
            beds_df = pd.read_csv("beds.csv")
            ward_options = [
                "General Ward",
                "ICU",
                "NICU",
                "Maternity",
                "Pediatric",
                "Oncology",
                "Emergency",
            ]
            recommended_ward = None

            for ward in ward_options:
                if ward.lower() in response.text.lower():
                    recommended_ward = ward
                    break

            if recommended_ward:
                available_beds = beds_df[
                    (beds_df["Ward_Type"] == recommended_ward)
                    & (beds_df["Status"] == "Available")
                ]

                if not available_beds.empty:
                    assigned_bed = available_beds.iloc[0]["Bed_ID"]
                    st.success(
                        f"🛏️ **Bed Allocated:** {assigned_bed} in the {recommended_ward}"
                    )
                    st.info("Governance Check: Decision logged securely.")

                    # Update bed inventory
                    beds_df.loc[beds_df["Bed_ID"] == assigned_bed, "Status"] = "Occupied"
                    beds_df.to_csv("beds.csv", index=False)
                else:
                    st.error(
                        f"🚨 CAPACITY ALERT: No available beds in the {recommended_ward}!"
                    )
                    st.warning(
                        "Governance Protocol: Patient requires immediate hospital transfer or overflow triage."
                    )
            else:
                st.warning(
                    "Could not automatically detect the ward type from the AI response. Manual override required."
                )
