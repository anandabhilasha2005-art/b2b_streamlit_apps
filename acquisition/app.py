import streamlit as st
from data_engineer import data_engineer_page
from lead_scoring import lead_scoring_page 

# --- Custom CSS for centered layout and component fixes ---

# --- Custom CSS for centered layout and component fixes ---
def load_custom_css():
    st.markdown(r"""
    <style>
    /* --- General page styling --- */
    .stApp { 
        background-color: #f0f2f6; 
    }

    /* Central Title Styling */
    h1 { 
        color:#6b00b8; 
        font-weight:900; 
        text-align:center; 
        font-size:3em; 
        letter-spacing:1px; 
    }

    .stMarkdown p { 
        text-align:center; 
        color:#555; 
        font-size:1.1em; 
        margin-bottom:20px; 
    }
    
    /* H3 for "Choose your role" inside the form */
    h3 { 
        text-align:center; 
        color:#444; 
        margin-top:10px; 
        font-size:1.4em; 
    } 

    /* --- Radio Button Centering --- */
    /* 1. Center the main stRadio container */
    div[data-testid="stRadio"] {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }

    /* 2. Center the inner radiogroup */
    div[role="radiogroup"] {
        display: flex !important; 
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important; 
        margin: 0 !important;
    }

    /* Radio option labels */
    div[role="radiogroup"] > label {
        display: inline-flex !important;
        align-items: center !important;
        gap: 8px;
        margin: 0 10px !important;
        padding: 8px 12px !important;
        border-radius: 10px;
        background: transparent !important;
        border: 1px solid transparent !important;
        cursor: pointer;
        font-weight: 600;
    }

    /* Selected radio */
    div[role="radiogroup"] > label[aria-checked="true"] {
        background: #fff !important;
        color: #6b00b8 !important;
        border: 1px solid rgba(107,0,184,0.12) !important;
        box-shadow: 0 4px 12px rgba(107,0,184,0.06);
        transform: translateY(-1px);
    }
    
    input[type="radio"] {
        margin-right: 6px !important;
    }

    /* --- Form/card styling --- */
    div[data-testid="stForm"] {
        padding: 30px;
        border-radius: 16px;
        border: 1px solid #e0e0e0;
        background-color: white;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin-top: 20px;
    }

    /* --- GLOBAL button styling (login + Run/Stop/etc.) --- */
    /* This styles:
       - Login button (st.form_submit_button with type="primary")
       - All st.button instances (Data Engineer, Lead Scoring, etc.)
    */
    button[kind="primary"], 
    .stButton > button {
        background-color: #6b00b8 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3em !important;
        padding: 0 1.4rem !important;
        border: none !important;
        transition: all 0.2s;
    }

    button[kind="primary"]:hover,
    .stButton > button:hover {
        background-color: #5a00a0 !important;
    }
    </style>
    """, unsafe_allow_html=True)




# -------------------------
# SESSION DEFAULTS
# -------------------------
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = "Data Intelligence Team"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None

# -------------------------
# PAGE CONFIG 
# -------------------------
st.set_page_config(page_title="B2B Lead Process", layout="wide")
load_custom_css() 

# -------------------------
# DEMO CREDENTIALS
# -------------------------
VALID_USERS = {
    "sarah jones": {"password": "LeadGen#2025", "role": "Data Intelligence Team"},
    "aaron miller": {"password": "LeadGen#2025", "role": "Sales Intelligence Team"},
}

# -------------------------
# HELPERS
# -------------------------
# NOTE: persona_changed() is no longer needed as the radio button is inside the form

def render_persona_radio():
    """Renders the horizontal radio button for persona selection (no on_change)."""
    st.radio(
        "Persona Selector", 
        ["Data Intelligence Team", "Sales Intelligence Team"],
        # Use st.session_state.selected_persona to set the initial index
        index=["Data Intelligence Team", "Sales Intelligence Team"].index(st.session_state.selected_persona),
        key="persona_radio",
        horizontal=True,
        label_visibility="collapsed" 
    )

def render_sidebar_logout():
    """Renders the user info and logout button in the sidebar at the bottom."""
    # Insert a spacer which grows to push content down
    st.sidebar.markdown("<div style='flex:1 1 auto; min-height:20px;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    if st.session_state.username:
        st.sidebar.markdown(f"**Signed in as:** {st.session_state.username}")
        st.sidebar.markdown(f"**Role:** {st.session_state.role}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()


# def render_sidebar_logout():
#     """Renders the user info and logout button in the sidebar."""
#     st.sidebar.markdown("---")
#     if st.session_state.username:
#         st.sidebar.markdown(f"**Signed in as:** {st.session_state.username}")
#         st.sidebar.markdown(f"**Role:** {st.session_state.role}")
#     if st.sidebar.button("Logout"):
#         st.session_state.logged_in = False
#         st.session_state.role = None
#         st.session_state.username = None
#         st.rerun()


# -------------------------
# LOGIN SCREEN (Centered via Columns)
# -------------------------
def show_login_screen():
    
    # Step 1: Center the main content column (5/7 width)
    col_left, col_center, col_right = st.columns([1, 5, 1])
    
    with col_center:
        # Title and Welcome Message
        st.markdown("<h1>🤖 B2B Agentic Lead Process</h1>", unsafe_allow_html=True)
        st.write("Welcome! Sign in to access the agentic lead management framework.")
        
        # Step 2: Further narrow the form for a smaller card (2/4 width within col_center)
        form_col_left, form_col_center, form_col_right = st.columns([1, 2, 1])

        with form_col_center:
            # Custom prompt for credentials
            st.markdown("<p style='color:#6b00b8; font-weight:600; text-align: center;'>Enter your credentials</p>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                
                # Role Selection is now inside the form
                # st.markdown("<h3>Choose your role</h3>", unsafe_allow_html=True)
                # render_persona_radio() # This updates st.session_state.persona_radio on submit

                # Credential Inputs
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                
                # Submit Button (This is what triggers the form submission)
                submitted = st.form_submit_button("🔑 Login", type="primary")

                if submitted:
                    
                    # Update selected_persona from the radio button state on submit
                    st.session_state.selected_persona = "Data Intelligence Team"
                    
                    u = (username or "").strip().lower()
                    
                    # --- Authentication Logic ---
                    if u in VALID_USERS and VALID_USERS[u]["password"] == password:
                        st.session_state.logged_in = True
                        # st.session_state.role = VALID_USERS[u]["role"] 
                        st.session_state.role = "Data Intelligence Team"
                        st.session_state.username = username.strip()
                        st.success(f"Welcome back, **{username.strip()}**!")
                        st.rerun()
                    else:
                        # --- Demo Fallback ---
                        st.session_state.logged_in = True
                        # Use the role from the radio button selected at the time of submission
                        st.session_state.role = "Data Intelligence Team" 
                        st.session_state.username = username.strip() or "Sarah Jones"
                        # st.info(f"Signed in as a demo user for **{st.session_state.selected_persona}**.")
                        st.rerun()

# -------------------------
# MAIN ROUTER
# -------------------------
def main():
    """Routes the user to the login screen or the appropriate dashboard."""
    if not st.session_state.logged_in:
        show_login_screen()
        return

    # show consistent sidebar logout
    # render_sidebar_logout()

    # Route pages based on the authenticated role.
    role = st.session_state.get("role")
    
    if role == "Data Intelligence Team":
        data_engineer_page()
    elif role == "Sales Intelligence Team":
        lead_scoring_page(df = None) 
    else:
        st.error("Access role not defined. Please log in.")

if __name__ == "__main__":
    main()