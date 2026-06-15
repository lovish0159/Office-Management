import streamlit as st
import pandas as pd

# ==========================================
# 1. PREMIUM WEB CONFIGURATION
# ==========================================
st.set_page_config(page_title="HR Portal | Civil Hospital Bathinda", page_icon="🏥", layout="wide")

# 🎨 ADVANCED CSS INJECTION
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
        html, body, [class*="css"]  { font-family: 'Poppins', sans-serif !important; }
        #MainMenu, footer, header {visibility: hidden !important;}
        [data-testid="stToolbar"], [data-testid="stElementToolbar"] {visibility: hidden !important; display: none !important;}
        * { -webkit-user-select: none !important; user-select: none !important; }
        .block-container { padding-top: 1rem !important; max-width: 95% !important; }
        
        div.row-widget.stRadio > div {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            padding: 10px 15px; border-radius: 50px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
            gap: 5px; justify-content: center; margin-bottom: 20px;
        }
        div.row-widget.stRadio > div > label {
            background: rgba(255, 255, 255, 0.05); color: #f8fafc !important;
            border-radius: 30px; padding: 10px 20px;
            transition: all 0.3s ease-in-out; cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        div.row-widget.stRadio > div > label:hover {
            background: #3b82f6 !important; transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); border-color: #3b82f6;
        }
        
        .hero-banner {
            background: linear-gradient(135deg, #1d4ed8, #2563eb, #3b82f6);
            border-radius: 20px; padding: 80px 20px; text-align: center; color: white;
            box-shadow: 0 20px 25px -5px rgba(37, 99, 235, 0.2);
            margin-top: 2vh; margin-bottom: 40px; animation: fadeIn 1s ease-in-out;
        }
        .hero-title { font-size: 4rem; font-weight: 800; letter-spacing: -1.5px; margin-bottom: 10px; line-height: 1.1; }
        .hero-subtitle { font-size: 1.2rem; font-weight: 300; opacity: 0.9; margin-bottom: 30px;}
        .system-badge { background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 50px; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;}
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURE AUTHENTICATION 
# ==========================================
def check_login():
    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    if st.session_state["logged_in"]: return True

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin-bottom: 20px;'>
                <h1 style='color: #1e293b; font-weight: 800;'>🔐 HR Portal</h1>
                <p style='color: #64748b;'>Enter credentials to access the establishment records</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("👤 Administrator ID")
            pwd = st.text_input("🔑 Security Password", type="password")
            if st.form_submit_button("Authenticate System", use_container_width=True):
                try:
                    if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials Provided.")
                except KeyError:
                    st.error("⚠️ System Offline: Streamlit Secrets are not configured.")
    return False

# ==========================================
# 3. BULLETPROOF GOOGLE SHEETS ENGINE
# ==========================================
@st.cache_data(ttl=60)
def load_data_from_sheet(sheet_name):
    SHEET_ID = "1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo"
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(csv_url)
        df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')].reset_index(drop=True)
        
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if df[col].dropna().apply(lambda x: float(x).is_integer()).all():
                    df[col] = df[col].astype('Int64').astype(str).str.replace('<NA>', '', regex=False)
        return df
    except Exception: 
        return pd.DataFrame({"System Alert": [f"Connection interrupted for {sheet_name}. Verify data link."]})

def render_smart_table(df, title):
    st.markdown(f"<h2 style='color:#1e293b; font-weight:700; margin-bottom: 20px;'>{title}</h2>", unsafe_allow_html=True)
    
    col_search, col_space = st.columns([1, 2])
    with col_search:
        search = st.text_input("🔍 Live Search:", placeholder="Enter name or ID...")
    
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df
    
    def color_coding(val):
        v = str(val).strip().upper()
        if v in ["ABSENT", "VACANT", "0", "NONE"]: return "color: white; background-color: #ef4444; font-weight: 600; border-radius: 5px;"
        if v in ["PRESENT", "ACTIVE", "REGULAR"]: return "color: white; background-color: #10b981; font-weight: 600; border-radius: 5px;"
        return ""
    
    styled_df = display_df.style.map(color_coding) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_coding)
    
    # 🎯 EXPERT FIX: Removed hide_index=True which causes crashes with Pandas Styler
    st.dataframe(styled_df, use_container_width=True, height=600)

# ==========================================
# 4. DASHBOARD ROUTER & UI
# ==========================================
def main():
    if not check_login(): return

    col_empty, col_refresh, col_btn = st.columns([8, 1, 1])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear() 
    with col_btn:
        st.button("Log Out 🚪", on_click=lambda: st.session_state.update({"logged_in": False}), use_container_width=True)
    
    page = st.radio(
        "", 
        ["🏠 Home", "1️⃣ Regular", "2️⃣ Outsource", "3️⃣ Regular Detail", "4️⃣ Outsource Detail", "5️⃣ Deputation", "6️⃣ Ward Attendant", "7️⃣ MO Posting"], 
        horizontal=True
    )

    if page == "🏠 Home":
        st.markdown("""
            <div class='hero-banner'>
                <span class='system-badge'>Administration Portal 2.0</span>
                <h1 class='hero-title'>Welcome to Civil Hospital Bathinda</h1>
                <p class='hero-subtitle'>Centralized Human Resource & Establishment Management System</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        sheet_map = {
            "1️⃣ Regular": ("Sheet1", "🩺 Regular Staff Management"), 
            "2️⃣ Outsource": ("Sheet2", "🤝 Outsource Staff Roster"), 
            "3️⃣ Regular Detail": ("Sheet3", "📄 Regular Staff Records"), 
            "4️⃣ Outsource Detail": ("Sheet4", "📋 Outsource Contracts & Details"), 
            "5️⃣ Deputation": ("Sheet5", "🔄 Deputation Register"), 
            "6️⃣ Ward Attendant": ("Sheet6", "🏥 Ward Attendant List"),
            "7️⃣ MO Posting": ("Sheet7", "👨‍⚕️ MO Posting Positions")
        }
        target_sheet, display_title = sheet_map[page]
        render_smart_table(load_data_from_sheet(target_sheet), display_title)

if __name__ == "__main__":
    main()
