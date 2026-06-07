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
    SHEET_URL = "import streamlit as st
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
    SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit" # Apna URL yahan dalein
    CACHE_TTL = 300  # 5 minutes cache to optimize API calls

st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout="wide")

# ==========================================
# 2. SECURITY & AUTHENTICATION MODULE
# ==========================================
class SecurityProtocol:
    @staticmethod
    def enforce_anti_leak_ui():
        """Injects strict CSS to disable selection, copying, and default Streamlit menus."""
        css_shield = """
        <style>
            /* Hide default menus and footers */
            #MainMenu, footer, header {visibility: hidden;}
            
            /* Disable text selection globally */
            body, .block-container, table, div, th, td, tr, span, p {
                user-select: none !important;
                -webkit-user-select: none !important;
                -ms-user-select: none !important;
                -moz-user-select: none !important;
            }
            
            /* Corporate Data Table Styling */
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
        """Validates credentials securely against cloud secrets."""
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
        """Establishes secure connection and retrieves operational data."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            worksheet = client.open_by_url(AppConfig.SHEET_URL).sheet1
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            st.error(f"⚠️ Database Connectivity Interrupted: Ensure the Service Account is granted 'Editor' access.")
            return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    """Renders the secure login portal."""
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
    """Renders the core operational dashboard."""
    # Top Banner & Control Menu
    col_header, col_action = st.columns([4, 1])
    with col_header:
        st.title("📋 Operational Staff Ledger")
        st.caption(f"Secure Environment | System Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    
    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Terminate Access", type="secondary", use_container_width=True):
            SecurityProtocol.terminate_session()
            
    st.divider()

    # Data Extraction & Processing
    with st.spinner("Decrypting and assembling data matrices..."):
        df = DatabaseEngine.fetch_roster_data()

    if df.empty:
        st.warning("⚠️ Database schema is empty or connection is offline.")
        return

    # Advanced Dynamic Filtering
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

    # Metrics Overview
    st.markdown("<br>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Total Personnel Located", len(processed_df))
    m_col2.markdown("<div style='text-align: right; color: #ef4444; padding-top: 25px; font-size: 14px;'>⚠️ <b>Strict Compliance:</b> Data extraction or photography is prohibited.</div>", unsafe_allow_html=True)

    # Secure HTML Table Rendering (Bypassing Streamlit's native CSV download)
    html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_grid}</div>", unsafe_allow_html=True)

# ==========================================
# 5. APPLICATION CORE EXECUTION
# ==========================================
def main():
    SecurityProtocol.enforce_anti_leak_ui()
    SecurityProtocol.initialize_session()
    
    if not st.session_state.is_verified:
        render_auth_gateway()
    else:
        render_main_dashboard()

if __name__ == "__main__":
    main()" # Apna URL yahan dalein
    CACHE_TTL = 300  # 5 minutes cache to optimize API calls

st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout="wide")

# ==========================================
# 2. SECURITY & AUTHENTICATION MODULE
# ==========================================
class SecurityProtocol:
    @staticmethod
    def enforce_anti_leak_ui():
        """Injects strict CSS to disable selection, copying, and default Streamlit menus."""
        css_shield = """
        <style>
            /* Hide default menus and footers */
            #MainMenu, footer, header {visibility: hidden;}
            
            /* Disable text selection globally */
            body, .block-container, table, div, th, td, tr, span, p {
                user-select: none !important;
                -webkit-user-select: none !important;
                -ms-user-select: none !important;
                -moz-user-select: none !important;
            }
            
            /* Corporate Data Table Styling */
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
        """Validates credentials securely against cloud secrets."""
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
        """Establishes secure connection and retrieves operational data."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            client = gspread.authorize(creds)
            worksheet = client.open_by_url(AppConfig.SHEET_URL).sheet1
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            st.error(f"⚠️ Database Connectivity Interrupted: Ensure the Service Account is granted 'Editor' access.")
            return pd.DataFrame()

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    """Renders the secure login portal."""
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
    """Renders the core operational dashboard."""
    # Top Banner & Control Menu
    col_header, col_action = st.columns([4, 1])
    with col_header:
        st.title("📋 Operational Staff Ledger")
        st.caption(f"Secure Environment | System Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    
    with col_action:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Terminate Access", type="secondary", use_container_width=True):
            SecurityProtocol.terminate_session()
            
    st.divider()

    # Data Extraction & Processing
    with st.spinner("Decrypting and assembling data matrices..."):
        df = DatabaseEngine.fetch_roster_data()

    if df.empty:
        st.warning("⚠️ Database schema is empty or connection is offline.")
        return

    # Advanced Dynamic Filtering
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

    # Metrics Overview
    st.markdown("<br>", unsafe_allow_html=True)
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("Total Personnel Located", len(processed_df))
    m_col2.markdown("<div style='text-align: right; color: #ef4444; padding-top: 25px; font-size: 14px;'>⚠️ <b>Strict Compliance:</b> Data extraction or photography is prohibited.</div>", unsafe_allow_html=True)

    # Secure HTML Table Rendering (Bypassing Streamlit's native CSV download)
    html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_grid}</div>", unsafe_allow_html=True)

# ==========================================
# 5. APPLICATION CORE EXECUTION
# ==========================================
def main():
    SecurityProtocol.enforce_anti_leak_ui()
    SecurityProtocol.initialize_session()
    
    if not st.session_state.is_verified:
        render_auth_gateway()
    else:
        render_main_dashboard()

if __name__ == "__main__":
    main()
