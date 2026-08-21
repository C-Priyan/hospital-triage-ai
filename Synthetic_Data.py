import random
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

num_beds = 400
num_patients = 10000

# ==========================================
# 1. BEDS DATASET GENERATION
# ==========================================
ward_options = ["General Ward", "ICU", "NICU", "Maternity", "Pediatric", "Oncology", "Emergency"]
status_options = ["Available", "Occupied", "Under Maintenance"]
status_weights = [0.35, 0.60, 0.05]

beds_data = [
    {
        "Bed_ID": f"BED-{1000 + i}",
        "Ward_Type": random.choice(ward_options),
        "Status": random.choices(status_options, weights=status_weights)[0],
    }
    for i in range(num_beds)
]
pd.DataFrame(beds_data).to_csv("beds.csv", index=False)

# ==========================================
# 2. PATIENT DATASET GENERATION
# ==========================================
gender_pool = ["Male", "Female", "Non-binary"]
chronic_pool = [
    "No Chronic Conditions", "Hypertension", "Type 2 Diabetes", 
    "Asthma", "Chronic Kidney Disease", "COPD", "Cancer"
]
chronic_weights = [0.47, 0.15, 0.15, 0.08, 0.06, 0.06, 0.03]

surgery_pool = ["No Prior Surgeries", "Appendectomy", "Cholecystectomy", "Knee Replacement", "Hernia Repair"]
surgery_weights = [0.6, 0.15, 0.1, 0.08, 0.07]

patient_data = []

for i in range(num_patients):
    patient_gender = random.choices(gender_pool, weights=[0.49, 0.49, 0.02])[0]
    
    if patient_gender == "Male":
        patient_name = fake.name_male()
    elif patient_gender == "Female":
        patient_name = fake.name_female()
    else:
        patient_name = fake.name()
        
    patient_data.append({
        "Patient_ID": f"PT-{5000 + i}",
        "Name": patient_name,
        "Age": random.randint(1, 95),
        "Gender": patient_gender,
        "Chronic_Conditions": random.choices(chronic_pool, weights=chronic_weights)[0],
        "Past_Surgeries": random.choices(surgery_pool, weights=surgery_weights)[0],
    })

pd.DataFrame(patient_data).to_csv("patient_history.csv", index=False)
print("beds.csv and patient_history.csv created successfully!")
