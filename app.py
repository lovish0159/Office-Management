import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header { font-size: 2.5rem; color: #1e3a8a; font-weight: 800; margin-bottom: 0px; text-align: center;}
        .sub-header { color: #64748b; font-size: 16px; margin-bottom: 20px; text-align: center;}
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px; text-align: center;}
        
        /* Styling the Radio buttons to look like a top navigation bar */
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f1f5f9; padding: 10px; border-radius: 10px; flex-wrap: wrap;}
        div.row-widget.stRadio > div > label { margin-right: 15px; padding: 5px 10px; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GOOGLE SHEETS DYNAMIC LOADER
# ==========================================
@st.cache_data(ttl=60)
def load_data_from_sheet(sheet_name):
    """Specific sheet se data nikalne ka master function"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=sheet_name)
        df = df.dropna(how="all") # Clean empty rows
        
        # Agar sheet mein data hai toh serial number theek karein
        if not df.empty:
            df = df.reset_index(drop=True)
            df.index = df.index + 1
            
        return df
    except Exception as e:
        # Agar koi specific sheet google sheets mein nahi bani hai
        return pd.DataFrame({"System Alert": [f"⚠️ {sheet_name} not found or empty. Please create it in Google Sheets."]})

# ==========================================
# 3. PAGE CONTENT FUNCTIONS
# ==========================================
def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb;'>Sheet 1</h1><p>Live Data Connected</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>🤝 Outsource Staff</h3><h1 style='color:#16a34a;'>Sheet 2</h1><p>Live Data Connected</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>🏥 Ward Attendants</h3><h1 style='color:#dc2626;'>Sheet 6</h1><p>Live Data Connected</p></div>", unsafe_allow_html=True)
    
    st.divider()
    st.info("👆 **Tip:** Upar diye gaye menu se kisi bhi module par click karke Google Sheets ka live data check karein.")

def show_regular_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🩺 Regular Staff Management (Sheet 1)")
    st.caption("Live data fetched directly from Google Sheet 1.")
    df = load_data_from_sheet("Sheet1")
    st.dataframe(df, use_container_width=True)

def show_outsource_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🤝 Outsource Staff Management (Sheet 2)")
    st.caption("Live data fetched directly from Google Sheet 2.")
    df = load_data_from_sheet("Sheet2")
    st.dataframe(df, use_container_width=True)

def show_regular_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📄 Regular Staff Detailed Records (Sheet 3)")
    st.caption("Live data fetched directly from Google Sheet 3.")
    df = load_data_from_sheet("Sheet3")
    st.dataframe(df, use_container_width=True)

def show_outsource_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📋 Outsource Staff Detailed Records (Sheet 4)")
    st.caption("Live data fetched directly from Google Sheet 4.")
    df = load_data_from_sheet("Sheet4")
    st.dataframe(df, use_container_width=True)

def show_deputation_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🔄 Deputation Staff Register (Sheet 5)")
    st.caption("Live data fetched directly from Google Sheet 5.")
    df = load_data_from_sheet("Sheet5")
    st.dataframe(df, use_container_width=True)

def show_ward_attendant_list():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🏥 CH Ward Attendant List (Sheet 6)")
    st.caption("Live data fetched directly from Google Sheet 6.")
    df = load_data_from_sheet("Sheet6")
    st.dataframe(df, use_container_width=True)

# ==========================================
# 4. TOP NAVIGATION CONTROLLER
# ==========================================
def main():
    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Centralized Staff Management System</div>", unsafe_allow_html=True)
    
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

    # Routing logic based on Radio Button selection
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
