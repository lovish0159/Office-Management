import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIGURATION & SECURITY ---
st.set_page_config(page_title="Civil Hospital Bathinda", page_icon="🏥", layout="wide")

# 🛡️ Anti-Copy & Anti-Download CSS Shield
hide_and_secure_css = """
<style>
/* Hide Streamlit top menu and footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Disable text selection and copying */
body, .block-container, dataframe, table, div {
    user-select: none !important;
    -webkit-user-select: none !important;
    -ms-user-select: none !important;
    -moz-user-select: none !important;
}
</style>
"""
st.markdown(hide_and_secure_css, unsafe_allow_html=True)

# --- SECURE CREDENTIALS ---
# Streamlit secrets se secure login fetch karna
ADMIN_USER = st.secrets["ADMIN_USERNAME"]
ADMIN_PASS = st.secrets["ADMIN_PASSWORD"]

# Google Sheet URL (Aapki actual sheet ka link yahan dalein)
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL).sheet1
        return sheet
    except Exception as e:
        st.error(f"⚠️ Google Sheet Connection Error. Verify Streamlit Secrets.")
        return None

def load_data():
    sheet = get_google_sheet()
    if sheet:
        records = sheet.get_all_records()
        return pd.DataFrame(records), sheet
    return pd.DataFrame(), None

# ==========================================
# 📱 LEFT SIDEBAR NAVIGATION MENU
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #1f77b4;'>🏥 CH Bathinda</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation Options
app_page = st.sidebar.radio(
    "👉 Select Page:",
    ["🏠 Home", "📋 Posting Position of Staff", "🔐 Admin Update Portal"]
)

st.sidebar.markdown("---")

# Sidebar par logout button agar admin logged in hai
if st.session_state.authenticated:
    st.sidebar.success("👤 Admin Access Active")
    if st.sidebar.button("🔒 Logout Securely", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ==========================================
# 🖥️ PAGE 1: HOME PAGE
# ==========================================
if app_page == "🏠 Home":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #2c3e50; font-size: 50px;'>Welcome to Civil Hospital Bathinda</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Office Management & Establishment Portal</h3>", unsafe_allow_html=True)
    st.markdown("<hr style='width: 50%; margin: auto;'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("👈 Kripya left side menu se 'Posting Position of Staff' select karein employee records dekhne ke liye.")

# ==========================================
# 🖥️ PAGE 2: POSTING POSITION OF STAFF
# ==========================================
elif app_page == "📋 Posting Position of Staff":
    st.title("📋 Posting Position of Staff")
    st.caption("Regular Employee Attachment & Duty Ledger")
    st.divider()

    df, sheet_obj = load_data()

    if not df.empty:
        st.markdown("*(Data copying and downloading is strictly restricted by hospital system policies)*")
        # Secure HTML table rendering (Anti-copy enabled)
        html_table = df.to_html(index=False, classes="table table-striped", border=0)
        st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_table}</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Loading data or Google Sheet is currently empty.")

# ==========================================
# 🖥️ PAGE 3: ADMIN UPDATE PORTAL
# ==========================================
elif app_page == "🔐 Admin Update Portal":
    st.title("🔐 Admin Workspace")
    st.caption("Secure Portal for Establishment Updates")
    st.divider()

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("Data update karne ke liye Admin Login zaroori hai.")
            with st.form("login_form"):
                username = st.text_input("Admin Username")
                password = st.text_input("Secure Password", type="password")
                submitted = st.form_submit_button("Authenticate 🚀", use_container_width=True)
                
                if submitted:
                    if username == ADMIN_USER and password == ADMIN_PASS:
                        st.session_state.authenticated = True
                        st.success("Access Granted! Loading update panel...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials. Entry Denied.")
    else:
        # User is Logged In
        df, sheet_obj = load_data()
        
        if not df.empty and sheet_obj:
            with st.form("update_posting_form"):
                st.markdown("#### 🔄 Update Employee Station/Posting")
                
                # Fetching Employee Names for the dropdown
                if 'Employee Name' in df.columns:
                    employee_list = df['Employee Name'].dropna().tolist()
                    selected_emp = st.selectbox("Select Employee:", ["-- Select Staff Member --"] + employee_list)
                    new_posting = st.text_input("Enter New Posting / Station / Ward:")
                    
                    update_btn = st.form_submit_button("Update Records to Google Sheet")
                    
                    if update_btn:
                        if selected_emp == "-- Select Staff Member --":
                            st.error("⚠️ Please select a valid employee from the list.")
                        elif not new_posting:
                            st.error("⚠️ Please enter the new posting details.")
                        else:
                            try:
                                # Find row and update
                                cell = sheet_obj.find(selected_emp)
                                header_row = sheet_obj.row_values(1)
                                
                                if "Place of Posting" in header_row:
                                    posting_col_idx = header_row.index("Place of Posting") + 1
                                    sheet_obj.update_cell(cell.row, posting_col_idx, new_posting)
                                    st.success(f"✅ Posting for **{selected_emp}** successfully updated to **'{new_posting}'**!")
                                    st.rerun()
                                else:
                                    st.error("⚠️ 'Place of Posting' column not found in Google Sheet.")
                            except Exception as e:
                                st.error("⚠️ Error updating sheet. Verify your exact sheet structure.")
                else:
                    st.error("⚠️ 'Employee Name' column not found in the Google Sheet.")
