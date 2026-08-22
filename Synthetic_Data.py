import random
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

num_beds = 400
num_patients = 10000

# ==========================================
# 1. PATIENT DATASET (Generated First)
# ==========================================
gender_pool = ["Male", "Female", "Non-binary"]
chronic_pool = ["No Chronic Conditions", "Hypertension", "Type 2 Diabetes", "Asthma", "Chronic Kidney Disease", "COPD", "Cancer"]
surgery_pool = ["No Prior Surgeries", "Appendectomy", "Cholecystectomy", "Knee Replacement", "Hernia Repair"]

chronic_weights = [0.47, 0.15, 0.15, 0.08, 0.06, 0.06, 0.03]
surgery_weights = [0.6, 0.15, 0.1, 0.08, 0.07]

patient_data = []

for i in range(num_patients):
    # 1. Pick the gender FIRST
    patient_gender = random.choices(gender_pool, weights=[0.49, 0.49, 0.02])[0]
    
    # 2. Generate a matching name
    if patient_gender == "Male":
        patient_name = fake.name_male()
    elif patient_gender == "Female":
        patient_name = fake.name_female()
    else:
        patient_name = fake.name() 
        
    # 3. Append the record (Renamed to Recent_Surgeries)
    patient_data.append({
        "Patient_ID": f"PT-{5000 + i}",
        "Name": patient_name,
        "Age": random.randint(1, 95),
        "Gender": patient_gender,
        "Chronic_Conditions": random.choices(chronic_pool, weights=chronic_weights)[0],
        "Recent_Surgeries": random.choices(surgery_pool, weights=surgery_weights)[0], 
    })

pd.DataFrame(patient_data).to_csv("patient_history.csv", index=False, lineterminator='\n')
# ==========================================
# 2. BEDS DATASET (With Patient_ID linking)
# ==========================================
ward_options = ["General Ward", "ICU", "NICU", "Maternity", "Pediatric", "Oncology", "Emergency"]
status_options = ["Available", "Occupied", "Under Maintenance"]
status_weights = [0.35, 0.60, 0.05]

# Grab a list of unique patient IDs for the occupied beds
all_patient_ids = [p["Patient_ID"] for p in patient_data]
# Create an iterator to pull unique patients safely
occupants = iter(random.sample(all_patient_ids, num_beds)) 

beds_data = []
for i in range(num_beds):
    status = random.choices(status_options, weights=status_weights)[0]
    
    # If occupied, pull a patient ID. Otherwise, leave it as None.
    assigned_patient = next(occupants) if status == "Occupied" else None
    
    beds_data.append({
        "Bed_ID": f"BED-{1000 + i}",
        "Ward_Type": random.choice(ward_options),
        "Status": status,
        "Patient_ID": assigned_patient
    })

pd.DataFrame(beds_data).to_csv("beds.csv", index=False, lineterminator='\n')
print("Updated patient_history.csv and beds.csv generated successfully!")
