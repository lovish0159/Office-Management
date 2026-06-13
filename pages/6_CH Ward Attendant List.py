import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Office Management Portal", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header { font-size: 2.2rem; color: #1e293b; font-weight: 800; margin-bottom: 5px; text-align: center;}
        .sub-header { color: #64748b; font-size: 16px; margin-bottom: 25px; text-align: center;}
        .metric-card { background-color: #f8fafc; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2563eb; }
        .metric-label { font-size: 14px; color: #475569; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GOOGLE SHEETS CONNECTION (SHEET 6)
# ==========================================
@st.cache_data(ttl=60)
def load_office_data():
    try:
        # Streamlit secrets se connection establish karna
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # 🎯 EXPERT FIX: Sirf "Sheet6" se data uthana
        df = conn.read(worksheet="Sheet6")
        
        # Khali (empty) rows ko clean karna
        df = df.dropna(how="all")
        return df
    except Exception as e:
        st.error(f"⚠️ Data load karne mein error. Kripya check karein ki 'Sheet6' Google Sheet mein maujood hai. Error: {e}")
        # Error aane par blank format dikhaye
        return pd.DataFrame({
            'Employee Name': [],
            'Designation': [],
            'Posting Position': [],
            'Status': []
        })

# ==========================================
# 3. DASHBOARD INTERFACE
# ==========================================
def main():
    st.markdown("<div class='main-header'>🏢 Office Management & Staff Portal</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Establishment & Posting Data (Live from Sheet 6)</div>", unsafe_allow_html=True)

    # Sheet 6 se data load karein
    df = load_office_data()

    if df.empty:
        st.warning("⚠️ Sheet 6 abhi khali hai ya connect nahi hui hai. Kripya Google Sheet mein data enter karein.")
        return

    # Columns check (Taaki error na aaye agar column ka naam thoda alag ho)
    if 'Status' not in df.columns:
        df['Status'] = 'Active' # Default status agar sheet mein na ho
    if 'Designation' not in df.columns:
        df['Designation'] = 'Unknown'

    # --- TOP METRICS ROW ---
    total_staff = len(df)
    total_designations = df['Designation'].nunique()
    active_staff = len(df[df['Status'].astype(str).str.contains('Active', case=False, na=False)])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_staff}</div><div class='metric-label'>Total Personnel</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{total_designations}</div><div class='metric-label'>Unique Designations</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{active_staff}</div><div class='metric-label'>Currently Active</div></div>", unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # --- INTERACTIVE FILTERING SYSTEM ---
    st.markdown("### 🔍 Staff Lookup by Designation")
    
    # Dropdown ke liye designations ki list nikalna
    all_designations = ["-- All Staff --"] + sorted(df['Designation'].dropna().unique().tolist())
    
    selected_desig = st.selectbox("Designation select karein:", all_designations)

    if selected_desig != "-- All Staff --":
        # Sirf selected designation ka data filter karna
        filtered_df = df[df['Designation'] == selected_desig]
        st.success(f"✅ Found {len(filtered_df)} record(s) for **{selected_desig}**")
    else:
        # Pura data dikhana
        filtered_df = df
        st.info("👆 Upar list mein se koi Designation select karke staff filter karein.")

    # Table format ko clean karke screen par dikhana
    filtered_df = filtered_df.reset_index(drop=True)
    filtered_df.index = filtered_df.index + 1  # Serial number 1 se shuru ho
    
    st.dataframe(filtered_df, use_container_width=True)

    st.divider()
    st.caption("🔒 Secure Office Data Environment | Connected to Google Sheets")

if __name__ == "__main__":
    main()
