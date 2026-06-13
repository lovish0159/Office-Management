import streamlit as st
import pandas as pd

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

# 🛡️ ANTI-THEFT & RESPONSIVE UI SHIELD
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden !important;}
        [data-testid="stToolbar"], [data-testid="stElementToolbar"] {visibility: hidden !important; display: none !important;}
        * { -webkit-user-select: none !important; -moz-user-select: none !important; user-select: none !important; }
        .main-header { font-size: 2.5rem; color: #1e3a8a; font-weight: 800; text-align: center;}
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f1f5f9; padding: 10px; border-radius: 10px; flex-wrap: wrap;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURE AUTHENTICATION (Using Streamlit Secrets)
# ==========================================
def check_login():
    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    if st.session_state["logged_in"]: return True

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h2 style='text-align:center;'>🏢 Secure HR Portal</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("👤 Username")
            pwd = st.text_input("🔑 Password", type="password")
            if st.form_submit_button("Secure Login", use_container_width=True):
                # 🎯 Password yahan code mein nahi, Streamlit Secrets se aayega
                if user == st.secrets["ADMIN_USERNAME"] and pwd == st.secrets["ADMIN_PASSWORD"]:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = user
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password")
    return False

# ==========================================
# 3. GOOGLE SHEETS LOADER
# ==========================================
@st.cache_data(ttl=60)
def load_data_from_sheet(sheet_name):
    SHEET_ID = "1FpDrz63M5Ix_rphXoonZHCDy_PAOUjsrzYIC3AFkUzo"
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(csv_url).dropna(how="all")
        return df.reset_index(drop=True)
    except: return pd.DataFrame({"Alert": ["Error loading sheet"]})

def render_smart_table(df, title):
    search = st.text_input(f"🔍 Search in {title}:", "")
    display_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)] if search else df
    
    # 🎨 Color Coding Engine
    def color_coding(val):
        v = str(val).strip().upper()
        if v in ["ABSENT", "VACANT", "0", "NONE"]: return "color: white; background-color: #ef4444; font-weight: bold;"
        if v in ["PRESENT", "ACTIVE", "REGULAR"]: return "color: white; background-color: #22c55e; font-weight: bold;"
        return ""
    
    styled_df = display_df.style.map(color_coding) if hasattr(display_df.style, 'map') else display_df.style.applymap(color_coding)
    st.dataframe(styled_df, use_container_width=True)

# ==========================================
# 4. PAGES & NAVIGATION
# ==========================================
def main():
    if not check_login(): return

    st.button("🚪 Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    
    page = st.radio("", ["🏠 Home", "1️⃣ Regular Staff", "2️⃣ Outsource Staff", "3️⃣ Regular Staff Detail", "4️⃣ Outsource Staff Detail", "5️⃣ Deputation Staff", "6️⃣ CH Ward Attendant"], horizontal=True)
    st.divider()

    if page == "🏠 Home":
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown("<div class='card'><h3>🩺 Regular Staff</h3></div>", unsafe_allow_html=True)
        with col2: st.markdown("<div class='card'><h3>🤝 Outsource Staff</h3></div>", unsafe_allow_html=True)
        with col3: st.markdown("<div class='card'><h3>🏥 Ward Attendants</h3></div>", unsafe_allow_html=True)
    else:
        sheet_map = {"1️⃣ Regular Staff": "Sheet1", "2️⃣ Outsource Staff": "Sheet2", "3️⃣ Regular Staff Detail": "Sheet3", "4️⃣ Outsource Staff Detail": "Sheet4", "5️⃣ Deputation Staff": "Sheet5", "6️⃣ CH Ward Attendant": "Sheet6"}
        render_smart_table(load_data_from_sheet(sheet_map[page]), page)

if __name__ == "__main__":
    main()
