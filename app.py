import streamlit as st
import pandas as pd

# ==========================================
# 1. PROFESSIONAL RESPONSIVE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

# 🎨 PROFESSIONAL RESPONSIVE CSS
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden !important;}
        .main-header { font-family: 'Arial', sans-serif; font-size: 2.2rem; color: #0f172a; font-weight: 700; text-align: center; margin-bottom: 5px;}
        .sub-header { font-family: 'Arial', sans-serif; color: #475569; font-size: 1rem; text-align: center; margin-bottom: 25px;}
        .card { background: white; border-radius: 12px; padding: 25px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURE AUTHENTICATION (GitHub Safe)
# ==========================================
def check_password():
    """Secrets se password check karega"""
    # Streamlit Cloud mein 'Secrets' mein inhen set karna hoga
    correct_user = st.secrets.get("ADMIN_USERNAME")
    correct_pass = st.secrets.get("ADMIN_PASSWORD")
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>🔐 Secure Login</h2>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == correct_user and pwd == correct_pass:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    return False

# ==========================================
# 3. DASHBOARD LOGIC
# ==========================================
def main():
    if not check_password():
        return

    st.markdown("<h1 class='main-header'>🏢 Civil Hospital HR Portal</h1>", unsafe_allow_html=True)
    
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

    # Data Loading (Sheet ID remains in code as it is public-access)
    SHEET_ID = "1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo"
    
    selected = st.selectbox("Navigate Section:", [
        "Regular Staff", "Outsource Staff", "Deputation Register", "Ward Attendants"
    ])
    
    # Sheet mapping
    sheet_map = {"Regular Staff": "Sheet1", "Outsource Staff": "Sheet2", 
                 "Deputation Register": "Sheet5", "Ward Attendants": "Sheet6"}
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_map[selected]}"
    df = pd.read_csv(csv_url)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
