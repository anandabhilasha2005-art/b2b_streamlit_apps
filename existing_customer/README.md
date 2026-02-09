
# B2B Agentic Lead Intelligence – Streamlit Demo



## Project Folder Structure
b2b_agentic_demo/
- data_engineer.py
- lead_scoring.py

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


