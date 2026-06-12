import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Secure Attendance Portal", page_icon="🏥", layout="wide")

# ==========================================
# 2. ADVANCED SECURITY PROTOCOL (Hidden Password)
# ==========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        # 🎯 EXPERT FIX: Password ab code mein nahi, Streamlit Secrets se aayega
        if st.session_state["password"] == st.secrets["ADMIN_PASSWORD"]: 
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Memory se delete
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔒 Secure Login Portal</h2>", unsafe_allow_html=True)
        st.text_input("Enter Admin Password to Access Register:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center;'>🔒 Secure Login Portal</h2>", unsafe_allow_html=True)
        st.text_input("Enter Admin Password to Access Register:", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect Password. Access Denied.")
        return False
    return True

# ==========================================
# 3. CORE ATTENDANCE ENGINE
# ==========================================
def initialize_data():
    data = {
        "ਲੜੀ ਨੰ. (S.No)": [1, 2, 3, 4, 5],
        "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)": ["Dr. Gopi Mehra", "Dr. Navjot Singh", "Dr. Ramandeep Kaur", "Dr. Deepak Sharma", "Dr. Vishal Agarwal"],
        "ਅਹੁਦਾ (Designation)": ["Medical Officer", "Medical Officer", "Medical Officer", "Medical Officer", "Medical Officer"],
        "ਅਸਲ ਪੋਸਟਿੰਗ (Posting)": ["Emergency", "OPD", "Ward", "ICU", "Dispensary"]
    }
    df = pd.DataFrame(data)
    
    for day in range(16, 32):
        df[str(day)] = "P" 
    for day in range(1, 16):
        df[str(day)] = "P"
        
    df["ਵਿਸ਼ੇਸ਼ ਕਥਨ (Remarks)"] = ""
    return df

def main():
    if not check_password():
        return

    st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🏥 ਹਾਜ਼ਰੀ ਰਿਪੋਰਟ (Attendance Report)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>ਦਫਤਰ ਸੀਨੀਅਰ ਮੈਡੀਕਲ ਅਫਸਰ ਇੰਚ: ਸਿਵਲ ਹਸਪਤਾਲ</p>", unsafe_allow_html=True)
    st.divider()

    if "attendance_df" not in st.session_state:
        st.session_state.attendance_df = initialize_data()

    st.markdown("### 📝 Mark Daily Attendance")
    st.info("💡 Instructions: Double click on any cell under a date to change the attendance status.")

    status_codes = ["P", "A", "D/O", "T", "CL", "EL", "ML", "C"]
    
    column_config = {
        "ਲੜੀ ਨੰ. (S.No)": st.column_config.NumberColumn(disabled=True),
        "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ (Name)": st.column_config.TextColumn(disabled=True),
        "ਅਹੁਦਾ (Designation)": st.column_config.TextColumn(disabled=True),
        "ਅਸਲ ਪੋਸਟਿੰਗ (Posting)": st.column_config.TextColumn(disabled=True),
    }
    
    for col in st.session_state.attendance_df.columns:
        if col.isdigit():
            column_config[col] = st.column_config.SelectboxColumn(
                options=status_codes,
                required=True
            )

    edited_df = st.data_editor(
        st.session_state.attendance_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic" 
    )

    st.session_state.attendance_df = edited_df

    st.divider()
    st.markdown("### 📥 Export Final Report")
    
    @st.cache_data
    def convert_df_to_excel(df):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Report')
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_df_to_excel(st.session_state.attendance_df)

    st.download_button(
        label="📊 Download Attendance Sheet (Excel)",
        data=excel_data,
        file_name=f"Attendance_Report_{datetime.now().strftime('%b_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

if __name__ == "__main__":
    main()
