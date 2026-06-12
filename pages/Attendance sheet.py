import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==========================================
# ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Smart Attendance Register", page_icon="🏥", layout="wide")

# ==========================================
# SECURITY PROTOCOL (Streamlit Secrets)
# ==========================================
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        # Code is secure for GitHub. Password fetches from Streamlit Cloud Secrets.
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Clear from memory
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
# CORE ATTENDANCE ENGINE & AUTO-FILL
# ==========================================
def initialize_data():
    """Sets up the dataframe based on the official Civil Hospital format."""
    # Dates from 16 to 30 and 1 to 15
    dates_part1 = [str(i) for i in range(16, 31)]
    dates_part2 = [str(i) for i in range(1, 16)]
    all_dates = dates_part1 + dates_part2

    # Sample data matching the first few entries of the uploaded sheet
    data = {
        "ਲੜੀ ਨੰ.": [1, 2, 3, 4, 5],
        "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ": ["ਡਾ: ਰੋਹਿਣੀ ਚੋਪੜਾ", "ਡਾ: ਨਵਦੀਪ ਸਿੰਘ", "ਡਾ: ਲਵਦੀਪ ਸਿੰਘ", "ਡਾ: ਨਵਦੀਪ ਰਾਈ", "ਡਾ: ਦੀਪਕ ਗਰਗ"],
        "ਅਹੁਦਾ": ["ਮੈਡੀਕਲ ਅਫਸਰ", "ਮੈਡੀਕਲ ਅਫਸਰ", "ਮੈਡੀਕਲ ਅਫਸਰ", "ਮੈਡੀਕਲ ਅਫਸਰ", "ਮੈਡੀਕਲ ਅਫਸਰ"],
        "ਅਸਲ ਪੋਸਟਿੰਗ": ["ਚਿਲਡਰਨ ਹਸਪਤਾਲ", "ਤਲਵੰਡੀ ਸਾਬੋ", "ਐਸ.ਡੀ.ਐਚ ਘੁੱਦਾ", "ਤਲਵੰਡੀ ਸਾਬੋ", "ਚਿਲਡਰਨ ਹਸਪਤਾਲ"]
    }
    df = pd.DataFrame(data)
    
    # ⚡ TIME SAVER: Auto-fill all dates with 'P' (Present)
    for date in all_dates:
        df[date] = "P"
        
    df["ਵਿਸ਼ੇਸ਼ ਕਥਨ (Remarks)"] = ""
    return df

def main():
    if not check_password():
        return

    # Header
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🏥 ਹਾਜਰੀ ਰਿਪੋਰਟ (Attendance Report)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b;'>ਦਫਤਰ ਸੀਨੀਅਰ ਮੈਡੀਕਲ ਅਫਸਰ ਇੰ. ਸਿਵਲ ਹਸਪਤਾਲ ਬਠਿੰਡਾ</p>", unsafe_allow_html=True)
    st.divider()

    # Load Data
    if "attendance_df" not in st.session_state:
        st.session_state.attendance_df = initialize_data()

    st.markdown("### 📝 Digital Register (Double Click to Edit)")
    
    # Dropdown Options extracted from the document
    status_codes = ["P", "A", "D/O", "T", "CL", "CE", "JD", "CCL", "SL"]
    
    # Configure strict columns to prevent typing errors
    column_config = {
        "ਲੜੀ ਨੰ.": st.column_config.NumberColumn(disabled=True),
        "ਅਧਿਕਾਰੀ ਦਾ ਨਾਮ": st.column_config.TextColumn(disabled=False), # Allow adding new doctors
    }
    
    # Apply dropdowns to all date columns
    for col in st.session_state.attendance_df.columns:
        if col.isdigit():
            column_config[col] = st.column_config.SelectboxColumn(
                options=status_codes,
                required=True
            )

    # Render Interactive Editor
    edited_df = st.data_editor(
        st.session_state.attendance_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic" # Add rows dynamically
    )

    # Save state
    st.session_state.attendance_df = edited_df

    st.divider()
    st.markdown("### 📥 Export & Download")
    
    # Excel Generation
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Attendance Report')
        return output.getvalue()

    excel_data = convert_df_to_excel(st.session_state.attendance_df)

    st.download_button(
        label="📊 Download Ready Excel Sheet",
        data=excel_data,
        file_name=f"Hospital_Attendance_{datetime.now().strftime('%d_%b_%Y')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

if __name__ == "__main__":
    main()
