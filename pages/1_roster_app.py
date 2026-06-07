import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
class AppConfig:
    PAGE_TITLE = "Secure Staff Roster | CH Bathinda"
    PAGE_ICON = "🛡️"
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"
    CACHE_TTL = 300

st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout="wide")

# ==========================================
# 2. SECURITY & AUTHENTICATION MODULE
# ==========================================
class SecurityProtocol:
    @staticmethod
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
                width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif;
                background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                border-radius: 8px; overflow: hidden; margin-top: 10px;
            }
            .enterprise-table th { background-color: #1e293b; color: #f8fafc; padding: 16px; text-align: left; font-size: 14px; font-weight: 600; }
            .enterprise-table td { padding: 14px 16px; border-bottom: 1px solid #e2e8f0; color: #334155; font-size: 14px; }
            .enterprise-table tr:last-child td { border-bottom: none; }
            .enterprise-table tr:hover td { background-color: #f1f5f9; transition: background-color 0.2s ease; }
        </style>
        """
        st.markdown(css_shield, unsafe_allow_html=True)

    @staticmethod
    def initialize_session():
        if "is_verified" not in st.session_state:
            st.session_state.is_verified = False

    @staticmethod
    def authenticate(user: str, pwd: str) -> bool:
        try:
            if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.is_verified = True
                return True
            return False
        except KeyError:
            st.error("⚠️ System Error: Authentication secrets are missing from the server configuration.")
            return False

    @staticmethod
    def terminate_session():
        st.session_state.is_verified = False
        st.rerun()

# ==========================================
# 3. CLOUD DATABASE CONTROLLER
# ==========================================
class DatabaseEngine:
    @staticmethod
    @st.cache_data(ttl=AppConfig.CACHE_TTL)
    def fetch_roster_data() -> pd.DataFrame:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            worksheet = client.open_by_url(AppConfig.SHEET_URL).sheet1
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            st.error("⚠️ Database Connectivity Interrupted: Ensure the Service Account is granted 'Editor' access.")
            return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 Restricted Access Area</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Establishment personnel authentication required.</p>", unsafe_allow_html=True)
        
        with st.form("security_clearance_form"):
            username = st.text_input("Administrator ID").strip()
            password = st.text_input("Security Clearance Key", type="password").strip()
            
            if st.form_submit_button("Authenticate & Initialize 🚀", use_container_width=True):
                if SecurityProtocol.authenticate(username, password):
                    st.success("✅ Identity verified. Handshake successful.")
                    st.rerun()
                else:
                    st.error("❌ Authentication Failed: Invalid credentials.")

def render_main_dashboard():
    col_header, col_action = st.columns([4, 1])
    with col_header:
        st.title("📋 Operational Staff Ledger
