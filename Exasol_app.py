import pandas as pd
from google import genai
import streamlit as st
import pyexasol
import ssl

# --- Page Config (Must be first) ---
st.set_page_config(page_title="Hospital Triage AI", layout="wide")

# --- 1. Database Connection Setup ---
@st.cache_resource 
def get_db_connection():
    db = pyexasol.connect(
        dsn='127.0.0.1:8563',
        user='sys',
        password='EXASSOL_PASSWORD',
        websocket_sslopt={'cert_reqs': ssl.CERT_NONE}
    )
    return db

def query_to_df(query: str) -> pd.DataFrame:
    """Execute a SQL query and return the result as a Pandas DataFrame."""
    db = get_db_connection()
    stmt = db.execute(query)
    rows = stmt.fetchall()
    cols = list(stmt.columns().keys())
    return pd.DataFrame(rows, columns=cols)

# --- 2. Setup the Google Gemini API Client ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# --- 3. Session State for Navigation ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

def go_home():
    st.session_state.current_page = "Home"

def go_admin():
    st.session_state.current_page = "Admin Operations"

# ==========================================
# 🏠 HOME PAGE (No Sidebar)
# ==========================================
if st.session_state.current_page == "Home":
    # CSS trick to hide sidebar and center-align headers
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
            .centered-header {
                text-align: center;
                margin-bottom: 2rem;
            }
        </style>
        <div class="centered-header">
            <h1>🏥 Hospital Triage AI</h1>
            <p style="font-size: 1.2rem; color: #a3a3a3;">Track: Trust, Safety & Governance</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacing
    if st.button("⚙️ Admin Operations", type="primary"):
        go_admin()
        st.rerun()

# ==========================================
# ⚙️ ADMIN OPERATIONS (Sidebar Active)
# ==========================================
elif st.session_state.current_page == "Admin Operations":
    
    # Top Corner Home Button
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("🏠 Home"):
            go_home()
            st.rerun()

    # Sidebar Navigation for Admin
    st.sidebar.title("⚙️ Admin Operations")
    admin_action = st.sidebar.radio(
        "Select Module:",
        ["📝 Patient Admission", "🏥 Discharge Patient"]
    )

    db = get_db_connection() # Grab connection for write operations

    # ------------------------------------------
    # MODULE A: PATIENT ADMISSION
    # ------------------------------------------
    if admin_action == "📝 Patient Admission":
        st.title("📝 Patient Admission & Triage")
        
        # Load the live synthetic data from Exasol
        patients_df = query_to_df("SELECT * FROM STARTER_KIT.PATIENT_HISTORY")
        patients_df = patients_df.fillna("None")

        # 1. TRIAGE LEVEL TOGGLE
        triage_level = st.radio(
            "Triage Category:",
            options=["🔴 Emergency (Immediate)", "🟢 Non-Emergency (Standard Intake)"],
            horizontal=True
        )

        # 2. PATIENT INTAKE TOGGLE
        patient_type = st.radio(
            "Select Patient Type:",
            options=["New Patient (Walk-in)", "Existing Patient (EHR Lookup)"],
            horizontal=True,
        )

        st.divider()
        
        # Initialize variables to avoid unbound errors
        active_patient_id = None

        if patient_type == "Existing Patient (EHR Lookup)":
            patient_ids = patients_df["Patient_ID"].tolist()
            selected_patient = st.selectbox("Search Patient ID:", patient_ids)
            active_patient_id = selected_patient

            patient_info = patients_df[patients_df["Patient_ID"] == selected_patient].iloc[0]
            patient_name = patient_info["Name"]
            patient_age = patient_info["Age"]
            patient_gender = patient_info["Gender"]
            patient_chronic = patient_info["Chronic_Conditions"]
            patient_surgeries = patient_info["Recent_Surgeries"]

            st.subheader("Patient Demographics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Patient Name", patient_name)
            col2.metric("Age", f"{patient_age} yrs")
            col3.metric("Gender", patient_gender)

            st.info(f"**Chronic Conditions:** {patient_chronic} | **Recent Surgeries:** {patient_surgeries}")

        else:
            st.subheader("New Patient Registration")
            
            # FAST-TRACK PROTOCOL LOGIC
            if triage_level == "🔴 Emergency (Immediate)":
                st.warning("⚠️ FAST-TRACK INTAKE ACTIVATED: Capturing vital details only.")
                col1, col2, col3 = st.columns(3)
                patient_name = col1.text_input("Full Name", value="Unknown Patient")
                patient_age = col2.number_input("Estimated Age", min_value=0, max_value=120, value=30)
                patient_gender = col3.selectbox("Gender", ["Male", "Female", "Non-binary", "Unknown"])
                
                # Automatically bypass forms for speed
                patient_chronic = "Unknown (Emergency Bypass)"
                patient_surgeries = "Unknown"
            else:
                col1, col2, col3 = st.columns(3)
                patient_name = col1.text_input("Full Name", value="Walk-in Patient")
                patient_age = col2.number_input("Age", min_value=0, max_value=120, value=30)
                patient_gender = col3.selectbox("Gender", ["Male", "Female", "Non-binary"])
                
                patient_chronic = st.text_input("Chronic Conditions (e.g., Asthma, Diabetes, Hypertension, or None)", value="None")
                patient_surgeries = "None"

        # AI TRIAGE CHAT
        st.divider()
        symptoms = st.chat_input("Enter the patient's symptoms here...")

        if symptoms:
            with st.chat_message("user"):
                st.write(f"**Symptoms:** {symptoms}")

            ai_prompt = f"""
            You are a hospital triage AI. 
            Triage Level: {triage_level}
            Patient Name: {patient_name}
            Age: {patient_age}
            Gender: {patient_gender}
            Chronic Conditions: {patient_chronic}
            Current Symptoms: {symptoms}
            
            Based on this data, which hospital ward should they go to? 
            You MUST include one of these exact phrases in your response: 
            "General Ward", "ICU", "NICU", "Maternity", "Pediatric", "Oncology", or "Emergency".
            If the Triage Level is 'Emergency', highly prioritize 'Emergency' or 'ICU'.
            Be brief with your reasoning.
            """

            with st.spinner("AI is analyzing patient data..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash", contents=ai_prompt
                    )

                    with st.chat_message("assistant"):
                        st.write(response.text)

                        # Get Live Bed Data
                        beds_df = query_to_df("SELECT * FROM STARTER_KIT.BEDS")
                        
                        # SAVE NEW PATIENT DIRECTLY TO EXASOL DB
                        if patient_type == "New Patient (Walk-in)":
                            active_patient_id = f"PT-{5000 + len(patients_df)}"
                            insert_sql = f"""
                                INSERT INTO STARTER_KIT.PATIENT_HISTORY 
                                ("Patient_ID", "Name", "Age", "Gender", "Chronic_Conditions", "Recent_Surgeries")
                                VALUES ('{active_patient_id}', '{patient_name}', {patient_age}, '{patient_gender}', '{patient_chronic}', 'None')
                            """
                            db.execute(insert_sql)
                            st.info(f"💾 Patient registered directly into Exasol DB as {active_patient_id}.")

                        # WARD MATCHING
                        ward_options = ["General Ward", "ICU", "NICU", "Maternity", "Pediatric", "Oncology", "Emergency"]
                        recommended_ward = next((ward for ward in ward_options if ward.lower() in response.text.lower()), None)

                        if recommended_ward:
                            available_beds = beds_df[
                                (beds_df["Ward_Type"] == recommended_ward) & 
                                (beds_df["Status"] == "Available")
                            ]

                            if not available_beds.empty:
                                assigned_bed = available_beds.iloc[0]["Bed_ID"]
                                st.success(f"🛏️ **Bed Allocated:** {assigned_bed} in the {recommended_ward}")
                                st.info("Governance Check: Decision logged securely.")

                                # UPDATE EXASOL BED INVENTORY AND LINK PATIENT
                                update_bed_sql = f"""
                                    UPDATE STARTER_KIT.BEDS 
                                    SET "Status" = 'Occupied', "Patient_ID" = '{active_patient_id}' 
                                    WHERE "Bed_ID" = '{assigned_bed}'
                                """
                                db.execute(update_bed_sql)
                            else:
                                st.error(f"🚨 CAPACITY ALERT: No available beds in the {recommended_ward}!")
                                st.warning("Governance Protocol: Patient requires immediate hospital transfer or overflow triage.")
                        else:
                            st.warning("Could not automatically detect the ward type from the AI response. Manual override required.")
                
                except Exception as e:
                    # If Google's servers crash, the app stays alive and shows this clean message
                    st.error("⚠️ The AI Triage system is currently experiencing high network traffic. Please wait a moment and try again.")

    # ------------------------------------------
    # MODULE B: DISCHARGE PATIENT
    # ------------------------------------------
    elif admin_action == "🏥 Discharge Patient":
        st.title("🏥 Discharge Patient & Manage Beds")
        
        # Only pull beds that are occupied
        occupied_beds_df = query_to_df("""SELECT * FROM STARTER_KIT.BEDS WHERE "Status" = 'Occupied'""")
        
        if not occupied_beds_df.empty:
            bed_ids = occupied_beds_df["Bed_ID"].tolist()
            bed_to_free = st.selectbox("Select Bed ID to Process Discharge:", bed_ids)
            
            # Look up the patient currently assigned to this bed
            bed_row = occupied_beds_df[occupied_beds_df["Bed_ID"] == bed_to_free].iloc[0]
            occupant_id = bed_row["Patient_ID"]
            ward_type = bed_row["Ward_Type"] # <-- Grab the ward type
            
            # Fetch that specific patient's details from the EHR table
            # We add pd.notna() to ensure pandas isn't feeding us a 'NaN' ghost value
            if pd.notna(occupant_id) and str(occupant_id).strip() != "" and str(occupant_id) != "nan":
                try:
                    # Run query WITHOUT .iloc[0] first so it doesn't crash if empty
                    patient_search_df = query_to_df(f"""SELECT * FROM STARTER_KIT.PATIENT_HISTORY WHERE "Patient_ID" = '{occupant_id}'""")
                    
                    if not patient_search_df.empty:
                        patient_data = patient_search_df.iloc[0]
                        
                        st.subheader("Patient Details")
                        # 4 Columns to display the Ward Type beautifully
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Name", patient_data["Name"])
                        col2.metric("Age", patient_data["Age"])
                        col3.metric("Gender", patient_data["Gender"])
                        col4.metric("Ward", ward_type)
                        
                        st.divider()
                        
                        # Surgery Checkbox & Text Input
                        had_surgery = st.checkbox("Was this admission for a surgery? (Check to update EHR)")
                        
                        if had_surgery:
                            # Show this text box ONLY if the box is checked
                            surgery_details = st.text_input("Enter specific surgery details:")
                        else:
                            # Default text if the box is left unchecked
                            surgery_details = "No Prior Surgeries"
                        
                        if st.button("Discharge Patient & Free Bed", type="primary"):
                            # 1. Update the patient's surgery record in Exasol with the new details
                            update_surgery_sql = f"""
                                UPDATE STARTER_KIT.PATIENT_HISTORY 
                                SET "Recent_Surgeries" = '{surgery_details}' 
                                WHERE "Patient_ID" = '{occupant_id}'
                            """
                            db.execute(update_surgery_sql)
                                
                            # 2. Free up the bed and remove the patient link in Exasol
                            free_bed_sql = f"""
                                UPDATE STARTER_KIT.BEDS 
                                SET "Status" = 'Available', "Patient_ID" = NULL 
                                WHERE "Bed_ID" = '{bed_to_free}'
                            """
                            db.execute(free_bed_sql)
                            
                            st.success(f"✅ {patient_data['Name']} discharged successfully. {bed_to_free} is now Available!")
                            st.rerun()
                            
                    else:
                        st.error(f"🚨 Data Error: Bed {bed_to_free} is occupied by ID '{occupant_id}', but they do not exist in the Patient table!")
                        
                except Exception as e:
                    st.error(f"Error fetching patient data: {e}")
            else:
                st.warning("This bed is marked as Occupied, but no valid Patient ID is linked to it in the database.")
                
        else:
            st.info("🟢 No beds are currently occupied. Hospital is at full capacity!")
