import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"

st.set_page_config(page_title="Secure Staff Roster | CH Bathinda", page_icon="🛡️", layout="wide")

# ==========================================
# 2. SECURITY & AUTHENTICATION MODULE
# ==========================================
def enforce_anti_leak_ui():
    css_shield = """
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        body, .block-container, table, div, th, td, tr, span, p {
            user-select: none !important;
            -webkit-user-select: none !important;
            -ms-user-select: none !important;
            -moz-user-select: none !important;
        }
        .enterprise-table {
            width: 100%; border-collapse: collapse; font-family: sans-serif;
            background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            border-radius: 8px; overflow: hidden; margin-top: 10px;
        }
        .enterprise-table th { background-color: #1e293b; color: white; padding: 16px; text-align: left; }
        .enterprise-table td { padding: 14px 16px; border-bottom: 1px solid #e2e8f0; color: #334155; }
    </style>
    """
    st.markdown(css_shield, unsafe_allow_html=True)

def initialize_session():
    if "is_verified" not in st.session_state:
        st.session_state.is_verified = False

def authenticate(user, pwd):
    try:
        if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.is_verified = True
            return True
        return False
    except Exception:
        st.error("⚠️ System Error: Authentication secrets are missing from the server.")
        return False

def terminate_session():
    st.session_state.is_verified = False
    st.rerun()

# ==========================================
# 3. CLOUD DATABASE CONTROLLER
# ==========================================
@st.cache_data(ttl=300)
def fetch_roster_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        worksheet = client.open_by_url(SHEET_URL).sheet1
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except Exception:
        st.error("⚠️ Database Connectivity Interrupted.")
        return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 Restricted Access</h2>", unsafe_allow_html=True)
        
        with st.form("security_clearance_form"):
            username = st.text_input("Administrator ID").strip()
            password = st.text_input("Security Clearance Key", type="password").strip()
            
            if st.form_submit_button("Authenticate & Initialize 🚀", use_container_width=True):
                if authenticate(username, password):
                    st.success("✅ Identity verified. Handshake successful.")
                    st.rerun()
                else:
                    st.error("❌ Authentication Failed: Invalid credentials.")

def render_main_dashboard():
    col_header, col_action = st.columns([4, 1])
    with col_header:
        st.title("📋 Operational Staff Ledger")
        st.caption(f"Secure Environment | Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    
    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Terminate Access", type="secondary", use_container_width=True):
            terminate_session()
            
    st.divider()

    with st.spinner("Decrypting data matrices..."):
        df = fetch_roster_data()

    if df.empty:
        st.warning("⚠️ Database schema is empty or connection is offline.")
        return

    st.markdown("#### ⚙️ Data Filter Parameters")
    f_col1, f_col2 = st.columns(2)
    
    processed_df = df.copy()
    
    with f_col1:
        if 'Designation' in df.columns:
            desig_options = ["All Designations"] + sorted(df['Designation'].dropna().unique().tolist())
            selected_desig = st.selectbox("Designation Target:", desig_options)
            if selected_desig != "All Designations":
                processed_df = processed_df[processed_df['Designation'] == selected_desig]
                
    with f_col2:
        if 'Place of Posting' in df.columns:
            posting_options = ["All Workstations"] + sorted(df['Place of Posting'].dropna().unique().tolist())
            selected_posting = st.selectbox("Deployment Location:", posting_options)
            if selected_posting != "All Workstations":
                processed_df = processed_df[processed_df['Place of Posting'] == selected_posting]

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("Total Personnel Located", len(processed_df))

    html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_grid}</div>", unsafe_allow_html=True)

# ==========================================
# 5. APPLICATION CORE EXECUTION
# ==========================================
enforce_anti_leak_ui()
initialize_session()

if not st.session_state.is_verified:
    render_auth_gateway()
else:
    render_main_dashboard()
