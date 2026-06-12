import streamlit as st
import pandas as pd
import io
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Smart Exception Attendance", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header { font-size: 2.2rem; color: #1e3a8a; text-align: center; font-weight: bold; margin-bottom: 5px; }
        .sub-header { text-align: center; color: #64748b; margin-bottom: 25px; }
        .punjabi-text { font-size: 1.2rem; color: #000000; text-align: center; font-weight: bold; padding: 10px; background-color: #f1f5f9; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 20px;}
        .section-title { color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURITY & AUTHENTICATION
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔒 Secure Admin Portal</h2>", unsafe_allow_html=True)
        st.text_input("Enter Master Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 Secure Admin Portal</h2>", unsafe_allow_html=True)
        st.text_input("Enter Master Password:", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect Password. Access Denied.")
        return False
    return True

# ==========================================
# 3. GOOGLE SHEETS DATA FETCHING
# ==========================================
@st.cache_data(ttl=60) # Data 60 seconds tak cache rahega, fast loading ke liye
def load_staff_from_gsheet():
    try:
        # Establish connection to Google Sheets
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Apni Google Sheet se data read karein (Sheet1 aapka tab name hona chahiye)
        df = conn.read(worksheet="Sheet1")
        # Khali rows ko hata dein
        df = df.dropna(how="all")
        return df
    except Exception as e:
        st.error(f"⚠️ Google Sheet se connect karne mein error: {e}")
        # Agar sheet connect na ho toh backup data use karein
        return pd.DataFrame({
            "ਲੜੀ ਨੰ. (S.No)": [1],
            "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)": ["Sheet connection failed"],
            "ਅਹੁਦਾ (Designation)": ["N/A"],
            "ਅਸਲ ਪੋਸਟਿੰਗ (Posting)": ["N/A"]
        })

# ==========================================
# 4. STATE MANAGEMENT
# ==========================================
DAYS_ORDER = [str(i) for i in range(16, 32)] + [str(i) for i in range(1, 16)]
LEAVE_TYPES = ["CL", "D/O", "T", "CE", "JD", "CCL", "SL", "A", "Off", "-"]

def init_state():
    if "staff_list" not in st.session_state:
        # Data ab Google Sheet se aayega
        st.session_state.staff_list = load_staff_from_gsheet()
    
    if "leave_records" not in st.session_state:
        st.session_state.leave_records = pd.DataFrame(
            columns=["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Doctor Name)", "ਤਾਰੀਖ (Date 1-31)", "ਛੁੱਟੀ ਦੀ ਕਿਸਮ (Leave Type)"]
        )

# ==========================================
# 5. CORE LOGIC: AUTO-FILL ENGINE
# ==========================================
def generate_final_attendance():
    df = st.session_state.staff_list.copy()
    
    for day in DAYS_ORDER:
        df[day] = "P"
        
    for index, row in st.session_state.leave_records.iterrows():
        doc_name = row["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Doctor Name)"]
        leave_date = str(row["ਤਾਰੀਖ (Date 1-31)"])
        leave_status = row["ਛੁੱਟੀ ਦੀ ਕਿਸਮ (Leave Type)"]
        
        if pd.notna(doc_name) and pd.notna(leave_date) and pd.notna(leave_status):
            if leave_date.endswith('.0'): 
                leave_date = leave_date[:-2]
                
            if doc_name in df["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"].values and leave_date in df.columns:
                df.loc[df["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"] == doc_name, leave_date] = leave_status

    df["ਵਿਸ਼ੇਸ਼ ਕਥਨ (Remarks)"] = ""
    return df

# ==========================================
# 6. USER INTERFACE & PUNJABI PDF TEXT
# ==========================================
def main():
    if not check_password():
        return

    init_state()
    
    st.markdown("<div class='main-header'>🏥 Hospital Attendance System</div>", unsafe_allow_html=True)
    
    # --- OFFICIAL PUNJABI LETTERHEAD (From PDF) ---
    st.markdown("""
        <div class='punjabi-text'>
            ਦਫਤਰ ਸੀਨੀਅਰ ਮੈਡੀਕਲ ਅਫਸਰ ਇੰ. ਸਿਵਲ ਹਸਪਤਾਲ ਬਠਿੰਡਾ। <br>
            <span style='font-weight: normal; font-size: 1rem;'>ਤਸਦੀਕ ਕੀਤਾ ਜਾਂਦਾ ਹੈ ਕਿ ਹੈ ਕਿ ਮੈਡੀਕਲ ਅਫਸਰ ਹੇਠ ਲਿਖੇ ਅਨੁਸਾਰ ਆਪਣੀ ਡਿਊਟੀ ਤੇ ਹਾਜਰ ਰਹੇ ।</span>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("<h3 class='section-title'>👥 1. Live Staff List (From G-Sheet)</h3>", unsafe_allow_html=True)
        st.caption("Yeh data automatically aapki Google Sheet se aa raha hai. Taza karne ke liye page refresh karein.")
        st.dataframe(st.session_state.staff_list, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("<h3 class='section-title'>📝 2. Enter Exceptions (Leaves/Offs)</h3>", unsafe_allow_html=True)
        st.caption("Only enter the dates when a doctor was NOT present. 'P' will be auto-filled.")
        
        doctor_names = st.session_state.staff_list["ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)"].dropna().tolist()
        
        if not doctor_names or doctor_names == ["Sheet connection failed"]:
            st.warning("Google Sheet list empty hai ya connect nahi hui.")
            doctor_names = ["No Doctors Available"]
            
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

    st.markdown("<h3 class='section-title'>🚀 3. Final Auto-Generated Sheet</h3>", unsafe_allow_html=True)
    
    final_attendance_df = generate_final_attendance()
    
    with st.expander("👁️ Preview Final Auto-Filled Sheet", expanded=False):
        st.dataframe(final_attendance_df, use_container_width=True, hide_index=True)
        
        # PDF se official utara text
        st.markdown("""
        **ਉਤਾਰਾ:-** <br>
        1. ਸਿਵਲ ਸਰਜਨ ਬਠਿੰਡਾ ਜੀ <br>
        2. ਸੀਨੀਅਰ ਮੈਡੀਕਲ ਅਫਸਰ ਚਿਲਡਰਨ ਤੇ ਜਨਰਲ ਹਪਸਤਾਲ ਬਠਿੰਡਾ
        """, unsafe_allow_html=True)
        
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
        file_name=f"Hospital_Attendance_{datetime.now().strftime('%b_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
