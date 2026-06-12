import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Smart Exception Attendance", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header { font-size: 2.2rem; color: #1e3a8a; text-align: center; font-weight: bold; margin-bottom: 5px; }
        .sub-header { text-align: center; color: #64748b; margin-bottom: 25px; }
        .section-title { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT & DATA INITIALIZATION
# ==========================================
# Setup dates order: 16 to 31, then 1 to 15
DAYS_ORDER = [str(i) for i in range(16, 32)] + [str(i) for i in range(1, 16)]
LEAVE_TYPES = ["CL", "D/O", "T", "CE", "JD", "CCL", "SL", "A", "Off", "-"]

def init_state():
    if "staff_list" not in st.session_state:
        # Default staff list
        st.session_state.staff_list = pd.DataFrame({
            "ਲੜੀ ਨੰ. (S.No)": [1, 2, 3, 4, 5],
            "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)": ["Dr. Gopi Mehra", "Dr. Navjot Singh", "Dr. Ramandeep Kaur", "Dr. Deepak Sharma", "Dr. Vishal Agarwal"],
            "ਅਹੁਦਾ (Designation)": ["Medical Officer", "Medical Officer", "Medical Officer", "Medical Officer", "Medical Officer"],
            "ਅਸਲ ਪੋਸਟਿੰਗ (Posting)": ["Emergency", "OPD", "Ward", "ICU", "Dispensary"]
        })
    
    if "leave_records" not in st.session_state:
        # The only table the user actually fills
        st.session_state.leave_records = pd.DataFrame(
            columns=["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Doctor Name)", "ਤਾਰੀਖ (Date 1-31)", "ਛੁੱਟੀ ਦੀ ਕਿਸਮ (Leave Type)"]
        )

# ==========================================
# 3. CORE LOGIC: AUTO-FILL ENGINE
# ==========================================
def generate_final_attendance():
    """Takes base staff, fills 'P' everywhere, then overwrites only the exceptions (Leaves)."""
    # Create base sheet
    df = st.session_state.staff_list.copy()
    
    # ⚡ AUTO-FILL ENGINE: Fill 'P' in all dates
    for day in DAYS_ORDER:
        df[day] = "P"
        
    # Apply exceptions (Leaves/DO/Off) from user input
    for index, row in st.session_state.leave_records.iterrows():
        doc_name = row["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Doctor Name)"]
        leave_date = str(row["ਤਾਰੀਖ (Date 1-31)"])
        leave_status = row["ਛੁੱਟੀ ਦੀ ਕਿਸਮ (Leave Type)"]
        
        # If valid entry, overwrite the 'P' with the specific leave
        if pd.notna(doc_name) and pd.notna(leave_date) and pd.notna(leave_status):
            if leave_date.endswith('.0'): # Clean decimal dates if any
                leave_date = leave_date[:-2]
                
            if doc_name in df["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"].values and leave_date in df.columns:
                df.loc[df["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"] == doc_name, leave_date] = leave_status

    df["ਵਿਸ਼ੇਸ਼ ਕਥਨ (Remarks)"] = ""
    return df

# ==========================================
# 4. USER INTERFACE
# ==========================================
def main():
    init_state()
    
    st.markdown("<div class='main-header'>🏥 Smart Exception Attendance System</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Just enter the Leaves/Offs. The system auto-fills 'P' (Present) for everything else.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    # --- PANEL 1: STAFF MANAGEMENT ---
    with col1:
        st.markdown("<h3 class='section-title'>👥 1. Staff Master List</h3>", unsafe_allow_html=True)
        st.caption("You can add new doctors or edit their postings here.")
        
        edited_staff = st.data_editor(
            st.session_state.staff_list,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="staff_editor"
        )
        st.session_state.staff_list = edited_staff

    # --- PANEL 2: LEAVE ENTRY (EXCEPTION TRACKER) ---
    with col2:
        st.markdown("<h3 class='section-title'>📝 2. Enter Exceptions (Leaves/Offs)</h3>", unsafe_allow_html=True)
        st.caption("Only enter the dates when a doctor was NOT present. 'P' will be auto-filled.")
        
        # Dynamic configuration for the exception table
        doctor_names = st.session_state.staff_list["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"].dropna().tolist()
        
        leave_config = {
            "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Doctor Name)": st.column_config.SelectboxColumn(options=doctor_names, required=True),
            "ਤਾਰੀਖ (Date 1-31)": st.column_config.SelectboxColumn(options=DAYS_ORDER, required=True),
            "ਛੁੱਟੀ ਦੀ ਕਿਸਮ (Leave Type)": st.column_config.SelectboxColumn(options=LEAVE_TYPES, required=True)
        }
        
        edited_leaves = st.data_editor(
            st.session_state.leave_records,
            column_config=leave_config,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="leave_editor"
        )
        st.session_state.leave_records = edited_leaves

    # --- PANEL 3: GENERATE & DOWNLOAD ---
    st.markdown("<h3 class='section-title'>🚀 3. Final Auto-Generated Sheet</h3>", unsafe_allow_html=True)
    
    # Generate the massive final sheet in the background
    final_attendance_df = generate_final_attendance()
    
    # Display preview (collapsed by default to save space)
    with st.expander("👁️ Preview Final Auto-Filled Sheet", expanded=False):
        st.dataframe(final_attendance_df, use_container_width=True, hide_index=True)
        
    # Excel Export Logic
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Report')
        return output.getvalue()

    excel_data = convert_df_to_excel(final_attendance_df)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Final Excel Sheet (Auto-Filled with 'P')",
        data=excel_data,
        file_name=f"Smart_Attendance_{datetime.now().strftime('%b_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
