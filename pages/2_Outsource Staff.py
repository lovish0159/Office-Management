import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
# Apna Google Sheet URL yahan dalein
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"

st.set_page_config(page_title="Outsourced Staff Roster | CH Bathinda", page_icon="📝", layout="wide")

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
        .enterprise-table th { background-color: #0f766e; color: white; padding: 16px; text-align: left; }
        .enterprise-table td { padding: 14px 16px; border-bottom: 1px solid #e2e8f0; color: #334155; }
        .enterprise-table tr:hover td { background-color: #f1f5f9; }
    </style>
    """
    st.markdown(css_shield, unsafe_allow_html=True)

def initialize_session():
    if "outsource_verified" not in st.session_state:
        st.session_state.outsource_verified = False

def authenticate(user, pwd):
    try:
        if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.outsource_verified = True
            return True
        return False
    except Exception:
        st.error("⚠️ System Error: Authentication secrets are missing from the server.")
        return False

# ==========================================
# 3. CLOUD DATABASE CONTROLLER (WORKSHEET 2)
# ==========================================
@st.cache_data(ttl=300)
def fetch_outsource_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open_by_url(SHEET_URL)
        
        # 🎯 STRICT TARGET: 2nd Worksheet (Index 1)
        # Python mein counting 0 se shuru hoti hai (0 = Pehli sheet, 1 = Dusri sheet)
        worksheet = spreadsheet.get_worksheet(1) 
        
        if worksheet is None:
            st.error("⚠️ Error: 2nd Worksheet nahi mili. Check karein ki Google Sheet mein 2 tabs hain.")
            return pd.DataFrame()
            
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
        
    except Exception as e:
        st.error(f"⚠️ Database Connectivity Interrupted. Error: {e}")
        return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center; color: #0f766e;'>🔐 Outsource Staff Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Authorized Login Required</p>", unsafe_allow_html=True)
        
        with st.form("outsource_security_form"):
            username = st.text_input("Administrator ID").strip()
            password = st.text_input("Security Clearance Key", type="password").strip()
            
            if st.form_submit_button("Verify & Unlock Dashboard 🚀", use_container_width=True):
                if authenticate(username, password):
                    st.success("✅ Identity verified. Loading records...")
                    st.rerun()
                else:
                    st.error("❌ Authentication Failed: Invalid credentials.")

def render_outsource_dashboard():
    col_header, col_action = st.columns([4, 1])
    with col_header:
        st.title("📝 Outsourced Staff Roster")
        st.caption(f"Secure View-Only Environment | Sync Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    
    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Logout", type="primary", use_container_width=True):
            st.session_state.outsource_verified = False
            st.rerun()
            
    st.divider()

    with st.spinner("Decrypting Outsourced Data Matrix..."):
        df = fetch_outsource_data()

    if df.empty:
        st.warning("⚠️ Roster is empty or connection failed.")
        return

    st.markdown("#### 🔍 Filter Staff Records")
    f_col1, f_col2 = st.columns(2)
    
    processed_df = df.copy()
    
    with f_col1:
        if 'Designation' in df.columns:
            desig_options = ["All Designations"] + sorted(df['Designation'].dropna().unique().tolist())
            selected_desig = st.selectbox("Filter by Designation:", desig_options)
            if selected_desig != "All Designations":
                processed_df = processed_df[processed_df['Designation'] == selected_desig]
                
    with f_col2:
        if 'Place of Posting' in df.columns:
            posting_options = ["All Workstations"] + sorted(df['Place of Posting'].dropna().unique().tolist())
            selected_posting = st.selectbox("Filter by Location:", posting_options)
            if selected_posting != "All Workstations":
                processed_df = processed_df[processed_df['Place of Posting'] == selected_posting]

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("Total Outsourced Personnel Found", len(processed_df))

    # Rendering secure HTML table
    html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_grid}</div>", unsafe_allow_html=True)

# ==========================================
# 5. APPLICATION CORE EXECUTION
# ==========================================
enforce_anti_leak_ui()
initialize_session()

if not st.session_state.outsource_verified:
    render_auth_gateway()
else:
    render_outsource_dashboard()
