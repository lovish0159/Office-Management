import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Tuple

# ==========================================
# 1. CONFIGURATION & SECURITY
# ==========================================
class MasterConfig:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit?gid=0#gid=0"
    SHEET_MAP = {
        "Regular Staff": 0,
        "Outsource Staff": 1,
        "Staff Detail": 2,
        "Outsource Staff Detail": 3
    }

st.set_page_config(page_title="Master Admin Portal | CH Bathinda", layout="wide")

# ==========================================
# 2. DATABASE SERVICE LAYER
# ==========================================
class GSheetService:
    @staticmethod
    def get_client():
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        return gspread.authorize(creds)

    @classmethod
    def fetch_data(cls, index: int) -> pd.DataFrame:
        ws = cls.get_client().open_by_url(MasterConfig.SHEET_URL).get_worksheet(index)
        return pd.DataFrame(ws.get_all_records())

    @classmethod
    def update_data(cls, index: int, df: pd.DataFrame) -> Tuple[bool, str]:
        try:
            ws = cls.get_client().open_by_url(MasterConfig.SHEET_URL).get_worksheet(index)
            ws.clear()
            # Efficient update: Headers + Data
            data_to_write = [df.columns.tolist()] + df.values.tolist()
            ws.update(data_to_write)
            return True, "Success"
        except Exception as e:
            return False, str(e)

# ==========================================
# 3. CONTROLLER & UI
# ==========================================
def main():
    if "master_verified" not in st.session_state:
        st.session_state.master_verified = False

    if not st.session_state.master_verified:
        render_login()
    else:
        render_admin_panel()

def render_login():
    st.markdown("## 🛡️ Master Admin Authentication")
    with st.form("auth"):
        user = st.text_input("Master ID")
        pwd = st.text_input("Master Key", type="password")
        if st.form_submit_button("Verify"):
            if user == st.secrets["MASTER_ADMIN_USER"] and pwd == st.secrets["MASTER_ADMIN_PASS"]:
                st.session_state.master_verified = True
                st.rerun()
            else:
                st.error("Invalid Credentials.")

def render_admin_panel():
    st.title("🎛️ Enterprise Management Console")
    
    tab1, tab2 = st.tabs(["📊 Data Management", "📥 Reporting"])
    
    with tab1:
        selected = st.selectbox("Select Target Module:", list(MasterConfig.SHEET_MAP.keys()))
        idx = MasterConfig.SHEET_MAP[selected]
        
        df = GSheetService.fetch_data(idx)
        st.info("Direct cell editing enabled. Rows can be added/deleted.")
        
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("💾 Apply Batch Changes"):
            with st.spinner("Syncing to Cloud..."):
                success, msg = GSheetService.update_data(idx, edited_df)
                if success:
                    st.success("Changes committed successfully.")
                else:
                    st.error(f"Sync Failure: {msg}")

    with tab2:
        st.subheader("Export Data")
        st.download_button("Export as CSV", data=df.to_csv(index=False), file_name="export.csv")

if __name__ == "__main__":
    main()
