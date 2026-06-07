import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"

st.set_page_config(page_title="Secure Roster | CH Bathinda", page_icon="🏥", layout="wide")

# ==========================================
# 2. SECURITY, AUTHENTICATION & RESPONSIVE UI
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
        .enterprise-table th { background-color: #1e293b; color: white; padding: 16px; text-align: left; white-space: nowrap; }
        .enterprise-table td { padding: 14px 16px; border-bottom: 1px solid #e2e8f0; color: #334155; white-space: nowrap; }
        
        div.row-widget.stRadio > div { 
            flex-direction: row; 
            flex-wrap: wrap; 
            gap: 8px; 
            background-color: #f1f5f9; 
            padding: 10px; 
            border-radius: 8px; 
            justify-content: center;
        }
        div.row-widget.stRadio > div > label { 
            background-color: #ffffff; 
            padding: 8px 14px; 
            border-radius: 6px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
            cursor: pointer;
            margin: 0;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
            h2 { font-size: 1.5rem !important; text-align: center; }
            div.row-widget.stRadio > div > label { padding: 6px 10px; font-size: 12px; flex: 1 1 auto; text-align: center; }
            .enterprise-table th, .enterprise-table td { padding: 10px 12px; font-size: 13px; }
        }
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
        st.error("⚠️ System Error: Authentication secrets are missing.")
        return False

def terminate_session():
    st.session_state.is_verified = False
    st.rerun()

# ==========================================
# 3. CLOUD DATABASE CONTROLLER
# ==========================================
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    return gspread.authorize(creds)

@st.cache_data(ttl=300)
def fetch_roster_data(sheet_index):
    try:
        client = get_gspread_client()
        worksheet = client.open_by_url(SHEET_URL).get_worksheet(sheet_index)
        if worksheet is not None:
            data = worksheet.get_all_values()
            if not data:
                return pd.DataFrame()
                
            df = pd.DataFrame(data[1:], columns=data[0])
            df = df.loc[:, (df.columns != '') & (~df.columns.isna())]
            return df
            
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ Data Sync Error: {e}")
        return pd.DataFrame()

def update_employee_posting(sheet_index, emp_name, new_posting):
    try:
        client = get_gspread_client()
        worksheet = client.open_by_url(SHEET_URL).get_worksheet(sheet_index)
        cell = worksheet.find(emp_name)
        
        headers = worksheet.row_values(1)
        if "Place of Posting" in headers:
            col_idx = headers.index("Place of Posting") + 1
            worksheet.update_cell(cell.row, col_idx, new_posting)
            st.cache_data.clear()
            return True, "Success"
        else:
            return False, "'Place of Posting' column not found."
    except Exception as e:
        return False, str(e)

# ==========================================
# 4. USER INTERFACE (UI) COMPONENTS
# ==========================================
def render_auth_gateway():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🔐 Restricted Access</h2>", unsafe_allow_html=True)
        with st.form("security_clearance_form"):
            username = st.text_input("Administrator ID").strip()
            password = st.text_input("Security Clearance Key", type="password").strip()
            if st.form_submit_button("Authenticate & Initialize 🚀", use_container_width=True):
                if authenticate(username, password):
                    st.success("✅ Identity verified. Handshake successful.")
                    st.rerun()
                else:
                    st.error("❌ Authentication Failed: Invalid credentials.")

def render_roster_dashboard(title, sheet_index):
    st.markdown(f"### {title}")
    st.caption(f"Secure Environment | Time: {datetime.now().strftime('%d-%m-%Y %H:%M')}")
    st.divider()

    with st.spinner("Decrypting data matrices..."):
        df = fetch_roster_data(sheet_index)

    if df.empty:
        st.warning("⚠️ Database schema is empty or connection is offline.")
        return

    st.markdown("#### 🔍 Search & Filter Records")
    
    # --- UNIVERSAL SEARCH BAR ADDED HERE ---
    search_term = st.text_input("🔎 Universal Search (Search by Name, Ward, or any detail):", placeholder="Type here to search...", key=f"search_{sheet_index}")
    
    f_col1, f_col2 = st.columns(2)
    processed_df = df.copy()
    
    with f_col1:
        if 'Designation' in df.columns:
            desig_options = ["All Designations"] + sorted(df['Designation'].dropna().unique().tolist())
            selected_desig = st.selectbox("By Designation:", desig_options, key=f"desig_{sheet_index}")
            if selected_desig != "All Designations":
                processed_df = processed_df[processed_df['Designation'] == selected_desig]
                
    with f_col2:
        if 'Place of Posting' in df.columns:
            posting_options = ["All Workstations"] + sorted(df['Place of Posting'].dropna().unique().tolist())
            selected_posting = st.selectbox("By Location:", posting_options, key=f"post_{sheet_index}")
            if selected_posting != "All Workstations":
                processed_df = processed_df[processed_df['Place of Posting'] == selected_posting]

    # --- SMART SEARCH LOGIC ---
    if search_term:
        mask = processed_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        processed_df = processed_df[mask]

    st.markdown("<br>", unsafe_allow_html=True)
    st.metric("Total Personnel Located", len(processed_df))

    if not processed_df.empty:
        html_grid = processed_df.to_html(index=False, classes="enterprise-table", border=0)
        st.markdown(f"<div style='width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch;'>{html_grid}</div>", unsafe_allow_html=True)
    else:
        st.info("⚠️ Koi record match nahi hua. Kripya apna search keyword check karein.")

def render_admin_console():
    st.markdown("### 🔐 Admin Operations Console")
    st.caption("Central Portal for Station Updates")
    st.divider()
    
    st.markdown("#### 🔄 Station Allocation Manager")
    staff_category = st.radio("Select Staff Category:", ["Regular Staff", "Outsource Staff"], horizontal=True)
    
    sheet_idx = 0 if staff_category == "Regular Staff" else 1
    df = fetch_roster_data(sheet_idx)
    
    if not df.empty and 'Employee Name' in df.columns:
        with st.form("roster_update_form"):
            employees = sorted(df['Employee Name'].dropna().unique().tolist())
            selected_emp = st.selectbox("Target Personnel:", ["-- Select ID --"] + employees)
            new_station = st.text_input("New Allocation / Duty Station:")
            
            if st.form_submit_button("Deploy Changes to Cloud ☁️", use_container_width=True):
                if selected_emp == "-- Select ID --" or not new_station:
                    st.warning("⚠️ Invalid input parameters. Please complete all fields.")
                else:
                    with st.spinner(f"Updating {staff_category}..."):
                        success, msg = update_employee_posting(sheet_idx, selected_emp, new_station)
                        if success:
                            st.success(f"✅ Protocol complete: **{selected_emp}** relocated to **{new_station}**.")
                        else:
                            st.error(f"❌ Transaction Failed: {msg}")
    else:
        st.warning(f"⚠️ Cannot load names for {staff_category}.")

# ==========================================
# 5. APPLICATION CORE EXECUTION
# ==========================================
enforce_anti_leak_ui()
initialize_session()

if not st.session_state.is_verified:
    render_auth_gateway()
else:
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown("<h2 style='margin-top: 0; padding-top: 0;'>🏥 CH Bathinda</h2>", unsafe_allow_html=True)
    with head_col2:
        if st.button("🔒 Logout", type="primary", use_container_width=True):
            terminate_session()
            
    app_page = st.radio(
        "Navigation",
        [
            "📋 Regular", "🤝 Outsource", "🏥 Reg Detail", "🏢 Out Detail", "🔐 Update"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1.5rem;'>", unsafe_allow_html=True)
    
    if app_page == "📋 Regular":
        render_roster_dashboard("📋 Regular Staff Ledger", sheet_index=0)
    elif app_page == "🤝 Outsource":
        render_roster_dashboard("🤝 Outsource Staff Ledger", sheet_index=1)
    elif app_page == "🏥 Reg Detail":
        render_roster_dashboard("🏥 Regular Staff Detail Ledger", sheet_index=2)
    elif app_page == "🏢 Out Detail":
        render_roster_dashboard("🏢 Outsource Staff Detail Ledger", sheet_index=3)
    elif app_page == "🔐 Update":
        render_admin_console()
