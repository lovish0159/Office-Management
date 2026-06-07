import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. CONFIGURATION & DATABASE SERVICE ---
class GSheetLoader:
    @staticmethod
    def connect():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Streamlit Secrets se credentials uthana
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        return gspread.authorize(creds)

    @classmethod
    def get_df(cls, sheet_name: str):
        try:
            client = cls.connect()
            # Secrets se URL uthana
            ws = client.open_by_url(st.secrets["https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"]).worksheet(sheet_name)
            data = ws.get_all_values()
            
            # Smart Dataframe Creation
            df = pd.DataFrame(data[1:], columns=data[0])
            # Khaali columns ko drop karna (Error Prevention)
            df = df.loc[:, (df != '').any(axis=0)]
            return df
        except Exception as e:
            st.error(f"⚠️ Error loading '{sheet_name}': {e}")
            return pd.DataFrame()

# --- 2. SECURITY & AUTHENTICATION ---
def check_password():
    if "verified" not in st.session_state: st.session_state.verified = False
    if not st.session_state.verified:
        with st.form("login"):
            st.subheader("🔐 CH Bathinda Secure Portal")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                # Ye credentials Streamlit Secrets mein set hone chahiye
                if u == st.secrets["ADMIN_USERNAME"] and p == st.secrets["ADMIN_PASSWORD"]:
                    st.session_state.verified = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
        st.stop()

# --- 3. MAIN APPLICATION INTERFACE ---
def main():
    check_password()
    
    st.sidebar.title("🏥 CH Bathinda Portal")
    # Yahan apni Google Sheet ke tabs ke exact naam likhein
    module = st.sidebar.radio("Select Category:", [
        "Regular Staff", 
        "Outsource Staff", 
        "Deputation Staff"
    ])
    
    st.title(f"📋 {module}")
    st.divider()
    
    # Data Fetching
    df = GSheetLoader.get_df(module)
    
    if not df.empty:
        # Smart Search Feature
        search = st.text_input("🔎 Search by Name, Posting, or Designation:", placeholder="Type here to filter...")
        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        # Display Table
        st.dataframe(df, use_container_width=True)
        st.metric("Total Records", len(df))
    else:
        st.warning("Data load nahi ho pa raha. Sheet ka naam aur access permissions check karein.")

if __name__ == "__main__":
    main()
