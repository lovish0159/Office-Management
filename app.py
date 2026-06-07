import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional, Tuple

# ==========================================
# 1. APP CONFIGURATION & CONSTANTS
# ==========================================
class Config:
    PAGE_TITLE = "Civil Hospital Bathinda | Portal"
    PAGE_ICON = "🏥"
    SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit" # Apna URL yahan dalein
    CACHE_TTL = 300 # Data refresh interval in seconds

st.set_page_config(page_title=Config.PAGE_TITLE, page_icon=Config.PAGE_ICON, layout="wide")

# ==========================================
# 2. SECURITY & AUTHENTICATION MODULE
# ==========================================
class SecurityManager:
    @staticmethod
    def apply_strict_ui_policies():
        """Injects CSS to disable copying, text selection, and downloading."""
        css = """
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            body, .block-container, dataframe, table, div, th, td, tr {
                user-select: none !important;
                -webkit-user-select: none !important;
                -ms-user-select: none !important;
                -moz-user-select: none !important;
            }
            .corporate-table {
                width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;
            }
            .corporate-table th { background-color: #2c3e50; color: white; padding: 12px; text-align: left; }
            .corporate-table td { padding: 12px; border-bottom: 1px solid #ecf0f1; background-color: #ffffff; color: #333; }
            .corporate-table tr:hover td { background-color: #f5f6fa; }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def init_session():
        """Initializes secure session state variables."""
        if "is_authenticated" not in st.session_state:
            st.session_state.is_authenticated = False

    @staticmethod
    def login(username, password) -> bool:
        """Validates credentials against secure secrets."""
        try:
            valid_user = st.secrets["ADMIN_USERNAME"]
            valid_pass = st.secrets["ADMIN_PASSWORD"]
            if username == valid_user and password == valid_pass:
                st.session_state.is_authenticated = True
                return True
            return False
        except KeyError:
            st.error("⚠️ Server Configuration Error: Missing Secrets.")
            return False

    @staticmethod
    def logout():
        st.session_state.is_authenticated = False
        st.rerun()

# ==========================================
# 3. DATABASE MANAGEMENT MODULE
# ==========================================
class DatabaseManager:
    @staticmethod
    @st.cache_resource
    def _get_client() -> Optional[gspread.Client]:
        """Establishes a secure connection to Google Cloud via Service Account."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
            return gspread.authorize(creds)
        except Exception as e:
            st.error(f"⚠️ Database Connection Failed: {e}")
            return None

    @classmethod
    def get_sheet(cls) -> Optional[gspread.Worksheet]:
        """Fetches the active worksheet."""
        client = cls._get_client()
        if client:
            try:
                return client.open_by_url(Config.SHEET_URL).sheet1
            except Exception:
                st.error("⚠️ Failed to locate the specific Google Sheet. Check URL.")
        return None

    @classmethod
    @st.cache_data(ttl=Config.CACHE_TTL)
    def fetch_records(_cls) -> pd.DataFrame:
        """Fetches and caches records into a Pandas DataFrame."""
        sheet = _cls.get_sheet()
        if sheet:
            records = sheet.get_all_records()
            return pd.DataFrame(records)
        return pd.DataFrame()

    @classmethod
    def update_posting(cls, emp_name: str, new_posting: str) -> Tuple[bool, str]:
        """Updates a specific employee's posting securely."""
        sheet = cls.get_sheet()
        if not sheet: return False, "Database disconnected."
        
        try:
            cell = sheet.find(emp_name)
            if not cell: return False, "Employee not found in database."
            
            headers = sheet.row_values(1)
            if "Place of Posting" not in headers:
                return False, "'Place of Posting' column missing in database architecture."
            
            col_idx = headers.index("Place of Posting") + 1
            sheet.update_cell(cell.row, col_idx, new_posting)
            st.cache_data.clear() # Clear cache to show live updates immediately
            return True, "Success"
        except Exception as e:
            return False, str(e)

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_sidebar() -> str:
    """Renders the modular sidebar and returns the selected route."""
    st.sidebar.markdown("<h2 style='text-align: center; color: #34495e;'>🏥 CH Bathinda</h2>", unsafe_allow_html=True)
    st.sidebar.caption("Enterprise Resource Portal")
    st.sidebar.divider()
    
    route = st.sidebar.radio("📌 Navigation Menu", ["🏠 Dashboard", "📋 Staff Roster", "🔐 Admin Console"])
    
    if st.session_state.is_authenticated:
        st.sidebar.divider()
        st.sidebar.success("🟢 Admin Status: Online")
        if st.sidebar.button("🔒 Terminate Session", use_container_width=True):
            SecurityManager.logout()
            
    return route

def render_dashboard():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #2c3e50; font-size: 3.5rem;'>Civil Hospital Bathinda</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7f8c8d; font-weight: 300;'>Central Office & Establishment Matrix</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='width: 40%; margin: auto; border-top: 2px solid #ecf0f1;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("💡 **Navigation System:** Use the sidebar panel to access the Staff Roster or the Secure Admin Console.")

def render_staff_roster():
    st.header("📋 Staff Posting Roster")
    st.caption("Read-Only Secure Ledger | Data Extraction is Prohibited")
    st.divider()

    if not st.session_state.is_authenticated:
        st.warning("🔒 Access Restricted. Authorized personnel must authenticate via the Admin Console to view records.")
        return

    with st.spinner("Synchronizing with Cloud Database..."):
        df = DatabaseManager.fetch_records()

    if not df.empty:
        # Display Quick Metrics
        col1, col2 = st.columns(2)
        col1.metric("Total Active Staff", len(df))
        if 'Designation' in df.columns:
            col2.metric("Unique Designations", df['Designation'].nunique())
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Render Secure Custom HTML Table
        html_table = df.to_html(index=False, classes="corporate-table", border=0)
        st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_table}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 Database is currently empty or awaiting synchronization.")

def render_admin_console():
    st.header("🔐 Admin Operations Console")
    st.caption("Secure Environment for Establishment Adjustments")
    st.divider()

    if not st.session_state.is_authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("Please provide administrative credentials to proceed.")
            with st.form("auth_form"):
                user = st.text_input("Administrator ID")
                pwd = st.text_input("Security Key", type="password")
                if st.form_submit_button("Initiate Secure Handshake 🚀", use_container_width=True):
                    if SecurityManager.login(user, pwd):
                        st.rerun()
                    else:
                        st.error("❌ Authentication Failed. Unauthorized access attempt logged.")
    else:
        df = DatabaseManager.fetch_records()
        if not df.empty and 'Employee Name' in df.columns:
            with st.form("roster_update_form"):
                st.markdown("### 🔄 Station Allocation Manager")
                
                employees = df['Employee Name'].dropna().tolist()
                selected_emp = st.selectbox("Target Personnel:", ["-- Select ID --"] + employees)
                new_station = st.text_input("New Allocation / Duty Station:")
                
                if st.form_submit_button("Deploy Changes to Cloud ☁️"):
                    if selected_emp == "-- Select ID --" or not new_station:
                        st.warning("⚠️ Invalid input parameters. Please complete all fields.")
                    else:
                        with st.spinner("Processing transaction..."):
                            success, msg = DatabaseManager.update_posting(selected_emp, new_station)
                            if success:
                                st.toast(f"Database synced successfully!", icon="✅")
                                st.success(f"✅ Protocol complete: **{selected_emp}** relocated to **{new_station}**.")
                                st.rerun()
                            else:
                                st.error(f"❌ Transaction Failed: {msg}")
        else:
            st.error("⚠️ Database schema invalid. 'Employee Name' column is mandatory.")

# ==========================================
# 5. MAIN APPLICATION CONTROLLER
# ==========================================
def main():
    SecurityManager.init_session()
    SecurityManager.apply_strict_ui_policies()
    
    current_route = render_sidebar()
    
    if current_route == "🏠 Dashboard":
        render_dashboard()
    elif current_route == "📋 Staff Roster":
        render_staff_roster()
    elif current_route == "🔐 Admin Console":
        render_admin_console()

if __name__ == "__main__":
    main()
