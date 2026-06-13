import streamlit as st
import pandas as pd

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

# 🛡️ STRICT ANTI-THEFT & ATTRACTIVE UI CSS
st.markdown("""
    <style>
        /* Hide Header, Footer, and Streamlit Menus */
        #MainMenu, footer, header {visibility: hidden !important;}
        [data-testid="stToolbar"], [data-testid="stElementToolbar"] {visibility: hidden !important; display: none !important;}
        
        * {
            -webkit-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        @media print { html, body { display: none !important; } }

        /* PROFESSIONAL BIG FONT UI STYLING */
        .main-header { font-size: 3rem; color: #1e3a8a; font-weight: 900; margin-bottom: 0px; text-align: center; letter-spacing: 1px;}
        .sub-header { color: #475569; font-size: 1.5rem; margin-bottom: 30px; text-align: center; font-weight: 500;}
        
        /* Top Navigation Menu Styling (Bigger Fonts) */
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f8fafc; padding: 15px; border-radius: 12px; flex-wrap: wrap; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
        div.row-widget.stRadio > div > label { margin-right: 20px; padding: 8px 15px; cursor: pointer; font-size: 1.2rem !important; font-weight: bold; color: #1e293b;}
        
        /* Welcome Text Styling */
        .welcome-text { font-size: 4.5rem; color: #0f172a; font-weight: 900; text-align: center; margin-top: 5vh; letter-spacing: 2px;}
        
        /* 🎨 ATTRACTIVE GOOGLE SHEET BUTTON */
        .gsheet-btn {
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #059669); /* Bright Green Gradient */
            color: #ffffff !important;
            padding: 12px 25px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 800;
            font-size: 1.2rem;
            margin-top: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            transition: all 0.3s ease;
            text-align: center;
        }
        .gsheet-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
            background: linear-gradient(135deg, #059669, #047857);
        }

        /* 🎨 ATTRACTIVE CARDS */
        .card { 
            background: linear-gradient(to bottom right, #ffffff, #f1f5f9); 
            border-radius: 15px; 
            padding: 25px; 
            border-left: 5px solid #2563eb; 
            margin-bottom: 15px; 
            text-align: center; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.08);
            transition: 0.3s;
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.12); }
        .card.green-border { border-left: 5px solid #10b981; }
        .card.red-border { border-left: 5px solid #ef4444; }
        
        /* Table Search Header */
        .table-title { font-size: 1.8rem; color: #1e3a8a; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;}
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
            st.markdown("<h3 style='font-size: 1.5rem;'>🔐 Admin Login</h3>", unsafe_allow_html=True)
            input_username = st.text_input("👤 Username")
            input_password = st.text_input("🔑 Password", type="password")
            submit_button = st.form_submit_button("Secure Login", use_container_width=True)

            if submit_button:
                try:
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
# 3. DIRECT GOOGLE SHEETS LOADER (CLEAN DATA)
# ==========================================
@st.cache_data(ttl=60)
def load_data_from_sheet(sheet_name):
    SHEET_ID = "1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo"
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(csv_url)
        df = df.dropna(how="all") 
        df = df.dropna(axis=1, how="all")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        if not df.empty:
            df = df.reset_index(drop=True)
            df.index = df.index + 1
        return df
    except Exception as e:
        return pd.DataFrame({"System Alert": [f"⚠️ Error: Data for '{sheet_name}' is unavailable."]})

# ==========================================
# 4. ADVANCED PAGE DESIGNS (WITH SEARCH)
# ==========================================
def render_smart_table(df, title):
    st.markdown(f"<div class='table-title'>{title}</div>", unsafe_allow_html=True)
    
    if "System Alert" in df.columns or df.empty:
        st.dataframe(df, use_container_width=True)
        return
        
    st.markdown(f"<p style='font-size: 1.2rem; color: #334155;'><strong>Total Records Found:</strong> {len(df)}</p>", unsafe_allow_html=True)
    search_query = st.text_input("🔍 Search (Type name, ID, or any detail...)", "")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if search_query:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
        st.dataframe(filtered_df, use_container_width=True, hide_index=False)
    else:
        st.dataframe(df, use_container_width=True, hide_index=False)

def show_home():
    # 🎯 EXPERT FIX: Welcome Text & Colorful Live Google Sheet Button
    st.markdown("<div class='welcome-text'>WELCOME</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Civil Hospital HR Management Portal</div>", unsafe_allow_html=True)
    
    # The Colorful Button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        st.markdown(
            """
            <div style="text-align: center;">
                <a href="https://docs.google.com/spreadsheets/d/1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo/edit" target="_blank" class="gsheet-btn">
                    📊 OPEN LIVE GOOGLE SHEET
                </a>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 🎯 EXPERT FIX: Attractive Data Cards
    with st.spinner("Fetching live data from Google Sheets..."):
        df1 = load_data_from_sheet("Sheet1")
        df2 = load_data_from_sheet("Sheet2")
        df6 = load_data_from_sheet("Sheet6")
        
        count1 = 0 if "System Alert" in df1.columns else len(df1)
        count2 = 0 if "System Alert" in df2.columns else len(df2)
        count6 = 0 if "System Alert" in df6.columns else len(df6)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb; font-size: 3rem; margin: 10px 0;'>{count1}</h1><p style='color:#475569; font-weight:bold;'>Records in Sheet 1</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card green-border'><h3>🤝 Outsource Staff</h3><h1 style='color:#10b981; font-size: 3rem; margin: 10px 0;'>{count2}</h1><p style='color:#475569; font-weight:bold;'>Records in Sheet 2</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card red-border'><h3>🏥 Ward Attendants</h3><h1 style='color:#ef4444; font-size: 3rem; margin: 10px 0;'>{count6}</h1><p style='color:#475569; font-weight:bold;'>Records in Sheet 6</p></div>", unsafe_allow_html=True)

def show_regular_staff():
    df = load_data_from_sheet("Sheet1")
    render_smart_table(df, "🩺 Regular Staff Management")

def show_outsource_staff():
    df = load_data_from_sheet("Sheet2")
    render_smart_table(df, "🤝 Outsource Staff Management")

def show_regular_staff_detail():
    df = load_data_from_sheet("Sheet3")
    render_smart_table(df, "📄 Regular Staff Detailed Records")

def show_outsource_staff_detail():
    df = load_data_from_sheet("Sheet4")
    render_smart_table(df, "📋 Outsource Staff Detailed Records")

def show_deputation_staff():
    df = load_data_from_sheet("Sheet5")
    render_smart_table(df, "🔄 Deputation Staff Register")

def show_ward_attendant_list():
    df = load_data_from_sheet("Sheet6")
    render_smart_table(df, "🏥 CH Ward Attendant List")

# ==========================================
# 5. MAIN NAVIGATION CONTROLLER
# ==========================================
def main():
    if not check_login():
        return

    col_a, col_b = st.columns([8, 1])
    with col_a:
        st.markdown(f"<p style='font-size: 1.2rem; color: #1e3a8a;'><strong>Welcome, {st.session_state['current_user']}!</strong></p>", unsafe_allow_html=True)
    with col_b:
        st.button("🚪 Logout", on_click=logout)

    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
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
