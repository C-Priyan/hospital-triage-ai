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
