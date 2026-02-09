
# B2B Agentic Lead Intelligence – Streamlit Demo



## Project Folder Structure
b2b_agentic_demo/
- app.py
- data_engineer.py
- lead_scoring.py
- insight_studio.py
- product_reco.py
- requirements.txt
- files/b2b_agentic_streamlit_demo_data.xlsx


### Prerequisites
- Python 3.9 or higher installed locally
- pip available


Verify Installation - Open Command Prompt or Terminal and run:
- python --version
- pip --version


## How to Run the Project (Step-by-Step)
Step 1: Open Command Prompt / Terminal

Windows:
- Press Windows + R
- Type cmd
- Press Enter

Mac:
- Open Spotlight
- Type Terminal
- Press Enter


Step 2: Navigate to Project Directory
Example (Windows):
- cd C:\Users\YourName\Documents\b2b_agentic_demo

Example (Mac):
- cd /Users/yourname/Documents/b2b_agentic_demo


Step 3: Install Dependencies:
- pip install -r requirements.txt


Step 4: Run Streamlit App
- streamlit run app.py


Step 5: Open Browser
- Open: http://localhost:8501


By default, Streamlit runs on port 8501, If you see an error like: Port 8501 is already in use, solve it with below step:
- streamlit run app.py --server.port 8502
- Then open: http://localhost:8502


# Login (Demo Mode)
- Login Page
    - Enter any username: Sarah Jones
    - Enter password: LeadGen#2025
- Data Enrichment Module:
    - enter company name = A Mark
- Lead Prioritization  Module:
    - select list = Q4 2025 — Expansion Accounts
- Insight Studio Module:
    - Questions to use in Insight Studio – Chat Agent
        - give me key insights on high priority accounts which i should target today
        - give me a deep dive on a-mark precious metals
    - Sales Intelligence Report
        - for scouting report: A Mark 
        - for Seller Pitch: A Mark 
        - for Marketing Email: A Mark 



# Agentic Lead Intelligence — Demo Guide

This document outlines the steps to run the application locally and walk through the core demo flows across Lead Management and Insight Studio.

---

## Login (Demo Mode)

1. Launch the application
2. On the Login page:
   - **Username: Sarah Jones
   - **Password: LeadGen#2025

---

## Data Enrichment Module (Lead Management)

1. Navigate to **Lead Management**
2. In the **Data Enrichment** flow:
   - Enter **Company Name:** A Mark
3. Click **Run Process**
4. Wait for the enrichment pipeline to complete (all steps will turn green)

---

## Lead Prioritization Module

1. Switch scope to **Lead Scoring & Prioritization**
2. Select **Lead List:**
   - Q4 2025 — Expansion Accounts
3. Review prioritized accounts and scoring outputs

---

## Insight Studio Module

### Chat Agent — Sample Questions

Use the following prompts in **Insight Studio → Chat**:

- Give me key insights on high priority accounts which I should target today
- Give me a deep dive on A-Mark Precious Metals

---

### Sales Intelligence Report

1. Navigate to **Insight Studio → Sales Intelligence Report**
2. Use **A Mark** as the target company for each report type:
   - **Scouting Report:** A Mark
   - **Seller Pitch:** A Mark
   - **Personalized Marketing Email:** A Mark
3. Click **Generate** to produce the report

---

## Running the App Locally (Mac)

1. Open Terminal
2. Navigate to the project directory:
   cd <your-project-directory>




## Notes
- product_reco.py is a placeholder
- Data is loaded locally from Excel
- Chat responses are static (demo-only)

