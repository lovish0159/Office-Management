import streamlit as st
import pandas as pd

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

# 🛡️ STRICT ANTI-THEFT & ATTRACTIVE UI CSS
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
        @media print { html, body { display: none !important; } }

        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f8fafc; padding: 15px; border-radius: 12px; flex-wrap: wrap; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
        div.row-widget.stRadio > div > label { margin-right: 20px; padding: 8px 15px; cursor: pointer; font-size: 1.1rem !important; font-weight: bold; color: #1e293b;}
        
        .welcome-text { 
            font-size: 4.5rem; 
            font-weight: 900; 
            text-align: center; 
            margin-top: 15vh; 
            letter-spacing: 2px;
            background: linear-gradient(45deg, #1e3a8a, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            line-height: 1.2;
        }
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
        st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🏢 Secure HR Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>Civil Hospital Establishment Access</p>", unsafe_allow_html=True)
        
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
# 4. COLORFUL & ATTRACTIVE PAGE DESIGNS
# ==========================================
def style_table(df, color_hex):
    """Table ke layout aur headers ko color karne ka engine"""
    return df.style.set_properties(**{
        'background-color': '#ffffff',
        'color': '#0f172a',
        'border-color': '#e2e8f0',
        'border-style': 'solid',
        'border-width': '1px',
        'padding': '10px'
    }).set_table_styles([{
        'selector': 'th',
        'props': [
            ('background-color', color_hex), 
            ('color', 'white'), 
            ('font-size', '16px'), 
            ('text-align', 'left')
        ]
    }])

def render_smart_table(df, title, icon, color_hex):
    st.markdown(f"""
        <div style='background: linear-gradient(90deg, {color_hex}22, transparent); border-left: 6px solid {color_hex}; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
            <h2 style='color: {color_hex}; margin: 0; font-weight: 800;'>{icon} {title}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if "System Alert" in df.columns or df.empty:
        st.dataframe(df, use_container_width=True)
        return
        
    st.markdown(f"""
        <p style='font-size: 1.2rem; color: #334155; margin-bottom: 5px;'>
            <strong>Total Records Found:</strong> 
            <span style='background-color: {color_hex}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold;'>{len(df)}</span>
        </p>
    """, unsafe_allow_html=True)
    
    search_query = st.text_input(f"🔍 Search in {title}...", key=title)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Apply filtering and 🎨 Colorful Styling
    if search_query:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
        filtered_df = df[mask]
        styled_df = style_table(filtered_df, color_hex)
        st.dataframe(styled_df, use_container_width=True, hide_index=False)
    else:
        styled_df = style_table(df, color_hex)
        st.dataframe(styled_df, use_container_width=True, hide_index=False)

def show_home():
    st.markdown("<div class='welcome-text'>WELCOME TO<br>CIVIL HOSPITAL BATHINDA</div>", unsafe_allow_html=True)

def show_regular_staff():
    df = load_data_from_sheet("Sheet1")
    render_smart_table(df, "Regular Staff Management", "🩺", "#2563eb") # Blue Theme

def show_outsource_staff():
    df = load_data_from_sheet("Sheet2")
    render_smart_table(df, "Outsource Staff Management", "🤝", "#10b981") # Green Theme

def show_regular_staff_detail():
    df = load_data_from_sheet("Sheet3")
    render_smart_table(df, "Regular Staff Detailed Records", "📄", "#8b5cf6") # Purple Theme

def show_outsource_staff_detail():
    df = load_data_from_sheet("Sheet4")
    render_smart_table(df, "Outsource Staff Detailed Records", "📋", "#f59e0b") # Orange Theme

def show_deputation_staff():
    df = load_data_from_sheet("Sheet5")
    render_smart_table(df, "Deputation Staff Register", "🔄", "#14b8a6") # Teal Theme

def show_ward_attendant_list():
    df = load_data_from_sheet("Sheet6")
    render_smart_table(df, "CH Ward Attendant List", "🏥", "#ef4444") # Red Theme

# ==========================================
# 5. MAIN NAVIGATION CONTROLLER
# ==========================================
def main():
    if not check_login():
        return

    col_a, col_b = st.columns([8, 1])
    with col_a:
        st.markdown(f"<p style='font-size: 1.1rem; color: #64748b; margin-top: 5px;'>Logged in as: <strong>{st.session_state['current_user']}</strong></p>", unsafe_allow_html=True)
    with col_b:
        st.button("🚪 Logout", on_click=logout)

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
    
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 20px;'>", unsafe_allow_html=True)

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
