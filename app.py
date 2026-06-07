import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- PAGE CONFIGURATION & SECURITY ---
st.set_page_config(page_title="Civil Hospital Management", page_icon="🏥", layout="wide")

# 🛡️ Anti-Copy & Anti-Download CSS Shield
hide_and_secure_css = """
<style>
/* Hide Streamlit top menu and footer to prevent downloading/printing */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Disable text selection and copying across the entire app */
body, .block-container, dataframe, table, div {
    user-select: none !important;
    -webkit-user-select: none !important;
    -ms-user-select: none !important;
    -moz-user-select: none !important;
}
</style>
"""
st.markdown(hide_and_secure_css, unsafe_allow_html=True)

# --- CREDENTIALS & LOGIN SETUP ---
# Update your secure credentials here
ADMIN_USER = "admin"
ADMIN_PASS = "civil@123"

# Google Sheet URL (Aapki actual sheet ka link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        # Secrets se Google Cloud credentials read karna
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

# --- UI HEADER ---
st.title("🏥 Civil Hospital Office Management")
st.subheader("Regular Employee Posting & Attachment Ledger")
st.divider()

# --- DATA DISPLAY (READ-ONLY, NO COPY) ---
df, sheet_obj = load_data()

if not df.empty:
    st.markdown("### 📋 Active Staff Directory")
    st.markdown("*(Data copying and downloading is strictly restricted by system policies)*")
    
    # Render table in a secure HTML format instead of interactive dataframe to enforce anti-copy
    html_table = df.to_html(index=False, classes="table table-striped", border=0)
    st.markdown(f"<div style='width: 100%; overflow-x: auto;'>{html_table}</div>", unsafe_allow_html=True)
else:
    st.info("Loading data or sheet is currently empty.")

st.divider()

# --- SECURE UPDATE PORTAL (PASSWORD PROTECTED) ---
st.markdown("### 🔐 Admin Update Portal")

if not st.session_state.authenticated:
    with st.expander("Authorized Personnel Only - Click to Login", expanded=False):
        st.info("Posting position update karne ke liye credentials verify karein.")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Secure Login")
            
            if submitted:
                if username == ADMIN_USER and password == ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.success("Access Granted! Please wait...")
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials. Entry Denied.")
else:
    # --- ADMIN WORKSPACE ---
    st.success("✅ Secure connection established. You can now update employee postings.")
    if st.button("🔒 Logout"):
        st.session_state.authenticated = False
        st.rerun()

    if not df.empty and sheet_obj:
        with st.form("update_posting_form"):
            st.markdown("#### Update Regular Employee Station")
            
            # Select Employee Name (Assuming your sheet has a column named 'Employee Name')
            employee_list = df['Employee Name'].tolist()
            selected_emp = st.selectbox("Select Employee:", employee_list)
            
            # Input new posting position
            new_posting = st.text_input("Enter New Posting / Station / Ward:")
            
            update_btn = st.form_submit_button("Update Google Sheet")
            
            if update_btn and new_posting:
                try:
                    # Find the exact cell of the employee in Google Sheet
                    cell = sheet_obj.find(selected_emp)
                    # Find the column index for 'Place of Posting' (Assuming it exists in sheet)
                    header_row = sheet_obj.row_values(1)
                    posting_col_idx = header_row.index("Place of Posting") + 1
                    
                    # Update the specific cell
                    sheet_obj.update_cell(cell.row, posting_col_idx, new_posting)
                    st.success(f"✅ Posting for {selected_emp} successfully updated to '{new_posting}'!")
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Error updating sheet. Please ensure 'Employee Name' and 'Place of Posting' columns exist exactly as typed.")
