# hospital-triage-ai
# 🏥 Hospital Triage AI

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Gemini](https://img.shields.io/badge/Google_Gemini-3.5_Flash-orange)
![Exasol](https://img.shields.io/badge/Database-Exasol-green)

An AI-driven hospital triage system designed to optimize patient intake, automate ward allocation, and ensure strict clinical governance. Built for the *Exasol AI Building Challenge (AI for Safety, Governance & Healthcare)*.

## 🏆 Trust, Safety & Governance Features
In high-stakes medical environments, AI cannot be a black box, and database transactions cannot fail silently. This system is fortified with deterministic guardrails:
* **Deterministic Fail-Safe Fallback:** If cloud AI services experience latency or outages, the system automatically degrades to deterministic clinical rules (e.g., auto-routing emergencies to the Emergency Ward) to ensure zero downtime for patient care.
* **Double Admission Prevention:** Strict SQL governance constraints prevent an active patient from being admitted to multiple beds simultaneously.
* **Ghost Patient Guardrails:** Transaction logic ensures patient records are only committed to the database after physical bed availability is confirmed, preventing data corruption and "phantom" patient records.
* **Immutable Audit Trail:** Every admission and discharge is logged with exact, randomized-to-live timestamps (Admission_Time) for flawless historical auditing and compliance reporting.
* **Capacity Overflow Alerts:** Real-time bed tracking triggers UI alerts and blocks intake if a specialized ward (e.g., Oncology) reaches maximum capacity.

## 🛠️ Tech Stack
* **Frontend/UI:** Streamlit
* **AI/LLM:** Google Gemini 3.5 Flash
* **Database:** Exasol (Local / Docker Deployment)
* **Data Processing:** Pandas, Python
* **Synthetic Data Generation:** Faker

## 📂 Project Structure
* **Exasol_app.py:** The main Streamlit application containing the UI, AI integration, and live transaction logic.
* **Synthetic_Data.py:** A Python script that uses Faker to generate 10,000 realistic patient records and 400 hospital beds with weighted clinical distributions and historical audit timestamps.
* **beds.csv & patient_history.csv:** The generated datasets to be imported into Exasol.

## ⚙️ Setup & Installation

### 1. Database Setup (Exasol)
1. Ensure Exasol is running on your local machine (127.0.0.1:8563).
2. Create a schema named STARTER_KIT.
3. Create the required tables (PATIENT_HISTORY and BEDS) and import the provided .csv files.

### 2. Environment Setup
Clone this repository and install the required dependencies:
```bash
git clone [https://github.com/C-Priyan/hospital-triage-ai.git](https://github.com/C-Priyan/hospital-triage-ai.git)
cd hospital-triage-ai
pip install streamlit pandas pyexasol google-genai faker
