import streamlit as st
import pandas as pd

# ==========================================
# 1. PREMIUM WEB CONFIGURATION
# ==========================================
st.set_page_config(page_title="HR Portal | Civil Hospital Bathinda", page_icon="🏥", layout="wide")

# 🎨 PURE CSS INTEGRATION (Tailwind Look Without The Script Risk)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
        
        /* Hide Native Streamlit Elements & Anti-Copy */
        #MainMenu, footer, header {visibility: hidden !important;}
        [data-testid="stToolbar"], [data-testid="stElementToolbar"] {visibility: hidden !important; display: none !important;}
        * { -webkit-user-select: none !important; user-select: none !important; }
        
        .block-container { padding-top: 1.5rem !important; max-width: 95% !important; }
        
        /* Premium Floating Navigation Bar */
        div.row-widget.stRadio > div {
            background-color: #0f172a;
            padding: 12px; 
            border-radius: 50px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            gap: 8px; 
            justify-content: center; 
            margin-bottom: 24px;
            border: 1px solid #1e293b;
            flex-wrap: wrap; /* Fix for mobile devices */
        }
        
        div.row-widget.stRadio > div > label {
            background-color: rgba(255, 255, 255, 0.05); 
            color: #f8fafc !important;
            border-radius: 50px; 
            padding: 8px 20px;
            transition: all 0.2s ease-in-out; 
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 14px;
            font-weight: 500;
        }
        
        div.row-widget.stRadio > div > label:hover {
            background-color: #3b82f6 !important; 
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            border-color: #3b82f6;
        }
        
        /* Modern Dataframe Headers */
        [data-testid="stDataFrame"] th { 
            background-color: #0f172a !important; 
            color: #ffffff !important; 
            font-weight: 600 !important; 
        }
        
        /* Custom Hero Banner */
        .premium-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #1e3a8a 100%);
            color: white; padding: 3rem; border-radius: 1.5rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            text-align: center; border: 1px solid rgba(99, 102, 241, 0.2);
            margin: 1.5rem auto; max-width: 64rem;
            transition: transform 0.3s ease;
        }
        .premium-hero:hover { transform: scale(1.01); }
        .hero-badge {
            background: rgba(59, 130, 246, 0.2); color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.3); padding: 0.25rem 1rem;
            border-radius: 9999px; font-size: 0.75rem; font-weight: 600;
            letter-spacing: 0.05em; text-transform: uppercase; display: inline-block; margin-bottom: 1rem;
        }
        .hero-h1 { font-size: 3rem; font-weight: 800; line-height: 1.2; margin-bottom: 0.75rem; background: linear-gradient(to right, #ffffff, #e2e8f0, #bfdbfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
        .hero-p { color: #cbd5e1; font-size: 1.125rem; font-weight: 300; }
        .hero-dots { display: flex; justify-content: center; gap: 1rem; margin-top: 2rem; font-size: 0.75rem; color: #94a3b8; font-weight: 500;}
        .dot { height: 8px; width: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
        
        /* Login Card */
        .login-wrapper { text-align: center; margin-bottom: 1.5rem; }
        .login-icon { display: inline-flex; padding: 0.75rem; background-color: #eff6ff; color: #2563eb; border-radius: 1rem; margin-bottom: 0.75rem;}
        .login-h1 { font-size: 1.875rem; font-weight: 800; color: #0f172a; margin:0;}
        .login-p { color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURE AUTHENTICATION
# ==========================================
def check_login():
    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    if st.session_state["logged_in"]: return True

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
            <div class="login-wrapper">
                <div class="login-icon">
                    <svg style="width:32px; height:32px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                </div>
                <h1 class="login-h1">Secure Gateway</h1>
                <p class="login-p">Civil Hospital Establishment Authentication</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("👤 Administrator ID")
            pwd = st.text_input("🔑 Security Password", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Authenticate System", use_container_width=True)
            
            if submit:
                try:
                    if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = user
                        st.rerun()
                    else:
                        st.error("❌ Access Denied: Invalid Credentials.")
                except KeyError:
                    st.error("⚠️ Configuration Missing: Streamlit Secrets not found.")
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
    st.markdown(f"""
        <div style="border-bottom: 1px solid #e2e8f0; padding-bottom: 1rem; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.5rem; font-weight: 700; color: #1e293b; margin:0;">{title}</h2>
            <p style="font-size: 0.875rem; color: #64748b; margin:0; padding-top:0.25rem;">Live deployment matrix from database infrastructure</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_search, col_space = st.columns([1, 2])
    with col_search:
        search = st.text_input("🔍 Filter Dataset:", placeholder="Type to instantly filter...")
    
    if search:
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = df[mask]
    else:
        display_df = df
    
    def color_coding(val):
        v = str(val).strip().upper()
        if v in ["ABSENT", "VACANT", "0", "NONE"]: return "color: white; background-color: #ef4444; font-weight: 600;"
        if v in ["PRESENT", "ACTIVE", "REGULAR"]: return "color: white; background-color: #10b981; font-weight: 600;"
        return ""
    
    # Apply text styles
    styled_df = display_df.style.map(color_coding) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_coding)
    
    # 🎯 EXPERT FIX: 100% Crash-Proof way to hide index in Pandas Styler
    if hasattr(styled_df, 'hide'):
        styled_df = styled_df.hide(axis="index")
        
    st.dataframe(styled_df, use_container_width=True, height=580)

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
            <div class="premium-hero">
                <span class="hero-badge">Administration Portal 3.0</span>
                <h1 class="hero-h1">Welcome to Civil Hospital Bathinda</h1>
                <p class="hero-p">Centralized Human Resource & Establishment Management System</p>
                <div class="hero-dots">
                    <div><span class="dot" style="background:#10b981;"></span> Live Sheets Sync</div>
                    <div><span class="dot" style="background:#3b82f6;"></span> Tailwind Style UI</div>
                    <div><span class="dot" style="background:#f59e0b;"></span> Anti-Theft Shield</div>
                </div>
            </div>
            <p style="text-align:center; font-size:0.875rem; color:#94a3b8; font-weight:500;">Please interact with the upper navigation pill bar to load enterprise data records.</p>
        """, unsafe_allow_html=True)
        
    else:
        sheet_map = {
            "1️⃣ Regular": ("Sheet1", "🩺 Regular Staff Management Matrix"), 
            "2️⃣ Outsource": ("Sheet2", "🤝 Outsource Staff Roster System"), 
            "3️⃣ Regular Detail": ("Sheet3", "📄 Regular Staff Master Records"), 
            "4️⃣ Outsource Detail": ("Sheet4", "📋 Outsource Contracts & Procurement Details"), 
            "5️⃣ Deputation": ("Sheet5", "🔄 Inter-Hospital Deputation Register"), 
            "6️⃣ Ward Attendant": ("Sheet6", "🏥 Ward Attendant Floor Allocations"),
            "7️⃣ MO Posting": ("Sheet7", "👨‍⚕️ Medical Officer (MO) Posting Status")
        }
        
        target_sheet, display_title = sheet_map[page]
        render_smart_table(load_data_from_sheet(target_sheet), display_title)

if __name__ == "__main__":
    main()
