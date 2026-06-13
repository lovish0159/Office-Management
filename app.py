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
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px; text-align: center;}
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f1f5f9; padding: 10px; border-radius: 10px; flex-wrap: wrap;}
        div.row-widget.stRadio > div > label { margin-right: 15px; padding: 5px 10px; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 100% HIDDEN PASSWORD SYSTEM (From Secrets)
# ==========================================
def check_password():
    def password_entered():
        # 🎯 EXPERT FIX: Password ab code mein KAHIN BHI nahi hai. 
        # Yeh seedha Streamlit Cloud ki vault (secrets) se check hoga.
        if st.session_state["password"] == st.secrets["admin_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 Secure HR Portal</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Enter Admin Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<br><br><h2 style='text-align: center;'>🔒 Secure HR Portal</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Enter Admin Password:", type="password", on_change=password_entered, key="password")
            st.error("❌ Incorrect Password. Access Denied.")
        return False
    return True

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
        return pd.DataFrame({"System Alert": [f"⚠️ Error: Data load nahi hua ({sheet_name})."]})

# ==========================================
# 4. ADVANCED PAGE DESIGNS (WITH SEARCH & FILTER)
# ==========================================
def render_smart_table(df, title):
    """Har page ke liye ek common smart search engine"""
    if "System Alert" in df.columns or df.empty:
        st.dataframe(df, use_container_width=True)
        return
        
    st.markdown(f"**Total Records:** {len(df)}")
    
    # Search Bar
    search_query = st.text_input(f"🔍 Search in {title} (Name, ID, etc.):", "")
    
    if search_query:
        # Har column mein text dhoondhega
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
        st.success(f"Found {len(filtered_df)} matches for '{search_query}'")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb;'>Sheet 1</h1></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>🤝 Outsource Staff</h3><h1 style='color:#16a34a;'>Sheet 2</h1></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>🏥 Ward Attendants</h3><h1 style='color:#dc2626;'>Sheet 6</h1></div>", unsafe_allow_html=True)

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
    if not check_password():
        return

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
