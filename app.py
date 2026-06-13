import streamlit as st
import pandas as pd

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden !important;}
        [data-testid="stToolbar"], [data-testid="stElementToolbar"] {visibility: hidden !important; display: none !important;}
        * {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        @media print {
            html, body { display: none !important; }
        }
        .main-header { font-size: 2.5rem; color: #1e3a8a; font-weight: 800; margin-bottom: 0px; text-align: center;}
        .sub-header { color: #64748b; font-size: 16px; margin-bottom: 20px; text-align: center;}
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f1f5f9; padding: 10px; border-radius: 10px; flex-wrap: wrap;}
        div.row-widget.stRadio > div > label { margin-right: 15px; padding: 5px 10px; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STREAMLIT SECRETS AUTHENTICATION
# ==========================================
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<div class='main-header'>🏢 Secure HR Portal</div>", unsafe_allow_html=True)
        st.markdown("<div class='sub-header'>Civil Hospital Establishment Access</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 Admin Login")
            input_username = st.text_input("👤 Username")
            input_password = st.text_input("🔑 Password", type="password")
            submit_button = st.form_submit_button("Secure Login", use_container_width=True)

            if submit_button:
                try:
                    # SECRETS SE ID PASSWORD CHECK HOGA
                    SECRET_USER = st.secrets["ADMIN_USERNAME"]
                    SECRET_PASS = st.secrets["ADMIN_PASSWORD"]
                    
                    if input_username == SECRET_USER and input_password == SECRET_PASS:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = input_username
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password.")
                except Exception:
                    st.error("⚠️ Streamlit Secrets set nahi hain.")

    return False

def logout():
    st.session_state["logged_in"] = False
    st.session_state["current_user"] = ""
    st.rerun()

# ==========================================
# 3. DIRECT GOOGLE SHEETS LOADER
# ==========================================
@st.cache_data(ttl=60)
def load_data_from_sheet(sheet_name):
    SHEET_ID = "1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo"
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(csv_url)
        df = df.dropna(how="all") 
        if not df.empty:
            df = df.reset_index(drop=True)
            df.index = df.index + 1
        return df
    except Exception as e:
        return pd.DataFrame({"System Alert": [f"⚠️ Error: Sheet public nahi hai ya '{sheet_name}' tab maujood nahi hai."]})

# ==========================================
# 4. ADVANCED PAGE DESIGNS (WITH LIVE COUNTS)
# ==========================================
def render_smart_table(df, title):
    if "System Alert" in df.columns or df.empty:
        st.dataframe(df, use_container_width=True)
        return
        
    st.markdown(f"**Total Records:** {len(df)}")
    search_query = st.text_input(f"🔍 Search in {title} (Name, ID, etc.):", "")
    
    if search_query:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
        st.success(f"Found {len(filtered_df)} matches")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🎯 EXPERT FIX: Ab Home Page par asli counting show hogi
    with st.spinner("Fetching live data from Google Sheets..."):
        df1 = load_data_from_sheet("Sheet1")
        df2 = load_data_from_sheet("Sheet2")
        df6 = load_data_from_sheet("Sheet6")
        
        count1 = 0 if "System Alert" in df1.columns else len(df1)
        count2 = 0 if "System Alert" in df2.columns else len(df2)
        count6 = 0 if "System Alert" in df6.columns else len(df6)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb;'>{count1}</h1><p>Total Records (Sheet 1)</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card'><h3>🤝 Outsource Staff</h3><h1 style='color:#16a34a;'>{count2}</h1><p>Total Records (Sheet 2)</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card'><h3>🏥 Ward Attendants</h3><h1 style='color:#dc2626;'>{count6}</h1><p>Total Records (Sheet 6)</p></div>", unsafe_allow_html=True)

def show_regular_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🩺 Regular Staff Management")
    df = load_data_from_sheet("Sheet1")
    render_smart_table(df, "Regular Staff")

def show_outsource_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🤝 Outsource Staff Management")
    df = load_data_from_sheet("Sheet2")
    render_smart_table(df, "Outsource Staff")

def show_regular_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📄 Regular Staff Detailed Records")
    df = load_data_from_sheet("Sheet3")
    render_smart_table(df, "Detailed Records")

def show_outsource_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📋 Outsource Staff Detailed Records")
    df = load_data_from_sheet("Sheet4")
    render_smart_table(df, "Outsource Details")

def show_deputation_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🔄 Deputation Staff Register")
    df = load_data_from_sheet("Sheet5")
    render_smart_table(df, "Deputation Register")

def show_ward_attendant_list():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🏥 CH Ward Attendant List")
    df = load_data_from_sheet("Sheet6")
    render_smart_table(df, "Ward Attendants")

# ==========================================
# 5. MAIN NAVIGATION CONTROLLER
# ==========================================
def main():
    if not check_login():
        return

    col_a, col_b = st.columns([8, 1])
    with col_a:
        st.markdown(f"**Welcome, {st.session_state['current_user']}!**")
    with col_b:
        st.button("🚪 Logout", on_click=logout)

    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    
    selected_page = st.radio(
        "",  
        [
            "🏠 Home",
            "1️⃣ Regular Staff",
            "2️⃣ Outsource Staff",
            "3️⃣ Regular Staff Detail",
            "4️⃣ Outsource Staff Detail",
            "5️⃣ Deputation Staff",
            "6️⃣ CH Ward Attendant"
        ],
        horizontal=True  
    )
    
    st.divider()

    if selected_page == "🏠 Home":
        show_home()
    elif selected_page == "1️⃣ Regular Staff":
        show_regular_staff()
    elif selected_page == "2️⃣ Outsource Staff":
        show_outsource_staff()
    elif selected_page == "3️⃣ Regular Staff Detail":
        show_regular_staff_detail()
    elif selected_page == "4️⃣ Outsource Staff Detail":
        show_outsource_staff_detail()
    elif selected_page == "5️⃣ Deputation Staff":
        show_deputation_staff()
    elif selected_page == "6️⃣ CH Ward Attendant":
        show_ward_attendant_list()

if __name__ == "__main__":
    main()
