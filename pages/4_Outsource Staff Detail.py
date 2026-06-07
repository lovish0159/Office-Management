import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"

st.set_page_config(page_title="Outsource Staff Detail | CH Bathinda", page_icon="📝", layout="wide")

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
    if "outsource_detail_verified" not in st.session_state:
        st.session_state.outsource_detail_verified = False

def authenticate(user, pwd):
    try:
        if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
            st.session_state.outsource_detail_verified = True
            return True
        return False
    except Exception:
        st.error("⚠️ System Error: Authentication secrets are missing.")
        return False

# ==========================================
# 3. CLOUD DATABASE CONTROLLER (WORKSHEET 4)
# ==========================================
@st.cache_data(ttl=300)
def fetch_outsource_detail_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_url(SHEET_URL)
        
        # 🎯 STRICT TARGET: 4th Worksheet (Index 3)
        worksheet = spreadsheet.get_worksheet(3) 
        
        if worksheet is None:
            st.error("⚠️ Error: 4th Worksheet nahi mili. Check karein ki Google Sheet mein 4 tabs hain.")
            return pd.DataFrame()
            
        data = worksheet.get_all_values()
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data[1:], columns=data[0])
        df = df.loc[:, df.columns != ''] # Fix for empty columns
        return df
    except Exception as e:
        st.error(f"⚠️ Database Connectivity Interrupted. Error: {e}")
        return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE
# ==========================================
def render_auth_gateway():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #0f766e;'>🔐 Outsource Detail Portal</h2>", unsafe_allow_html=True)
        with st.form("security_form"):
            user = st.text_input("Administrator ID").strip()
            pwd = st.text_input("Security Key", type="password").strip()
            if st.form_submit_button("Verify & Unlock 🚀", use_container_width=True):
                if authenticate(user, pwd):
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials.")

def render_dashboard():
    st.title("📝 Outsource Staff Detail")
    st.caption(f"Sync Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    st.divider()

    with st.spinner("Fetching secure data..."):
        df = fetch_outsource_detail_data()

    if df.empty:
        st.warning("⚠️ Roster empty or connection issue.")
        return

    # Smart Search
    search_term = st.text_input("🔎 Search by Name, Company, or Designation:", placeholder="Type here...")
    
    processed_df = df.copy()
    if search_term:
        mask = processed_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        processed_df = processed_df[mask]

    st.metric("Total Records Found", len(processed_df))
    html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_grid}</div>", unsafe_allow_html=True)

# ==========================================
# 5. CORE EXECUTION
# ==========================================
enforce_anti_leak_ui()
initialize_session()

if not st.session_state.outsource_detail_verified:
    render_auth_gateway()
else:
    render_dashboard()
