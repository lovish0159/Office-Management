import streamlit as st
import pandas as pd

# ==========================================
# 1. ENTERPRISE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Hospital HR Portal", page_icon="🏢", layout="wide")

# Pro Website CSS
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main-header { font-size: 2.5rem; color: #1e3a8a; font-weight: 800; margin-bottom: 5px; }
        .sub-header { color: #64748b; font-size: 16px; margin-bottom: 25px; }
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px;}
        .css-1d391kg { padding-top: 2rem; } /* Reduce top padding */
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PAGE CONTENT FUNCTIONS
# ==========================================
def show_home():
    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Centralized Staff Management System</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb;'>142</h1><p>Active Employees</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>🤝 Outsource Staff</h3><h1 style='color:#16a34a;'>85</h1><p>Active Employees</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>🔄 Deputation</h3><h1 style='color:#dc2626;'>12</h1><p>Currently on Deputation</p></div>", unsafe_allow_html=True)
    
    st.divider()
    st.info("👈 **Navigation Instructions:** Kripya left side (Sidebar) mein diye gaye Radio Buttons ka istemal karke alag-alag modules open karein.")

def show_regular_staff():
    st.header("🩺 Regular Staff Management")
    st.caption("Manage roster, attendance, and current postings of all regular employees.")
    # Yahan aap apna Regular Staff ka code aur tables daal sakte hain
    st.dataframe(pd.DataFrame({"Emp ID": ["R-101", "R-102"], "Name": ["Dr. Rajiv", "Simran Kaur"], "Designation": ["MO", "Staff Nurse"]}), use_container_width=True)

def show_outsource_staff():
    st.header("🤝 Outsource Staff Management")
    st.caption("Manage contracts, agencies, and duty rosters for outsourced personnel.")
    # Yahan aap apna Outsource Staff ka code daal sakte hain
    st.dataframe(pd.DataFrame({"ID": ["OS-501", "OS-502"], "Name": ["Ramesh", "Sunita"], "Agency": ["A1 Services", "A1 Services"]}), use_container_width=True)

def show_regular_staff_detail():
    st.header("📄 Regular Staff Detailed Records")
    st.caption("View deep analytics, service records, and personal details of regular staff.")
    st.info("Detailed profile view will load here. Connect your Google Sheet for live data.")

def show_outsource_staff_detail():
    st.header("📋 Outsource Staff Detailed Records")
    st.caption("View contract renewals, EPF details, and personal records of outsourced staff.")
    st.info("Detailed outsource records will load here.")

def show_deputation_staff():
    st.header("🔄 Deputation Staff Register")
    st.caption("Track staff sent to or received from other institutions on deputation.")
    st.warning("No staff currently on deputation out of the station.")

def show_ward_attendant_list():
    st.header("🏥 CH Ward Attendant List")
    st.caption("Specific roster and ward allocations for Class-IV Ward Attendants.")
    st.dataframe(pd.DataFrame({"Ward": ["Emergency", "ICU", "OPD"], "Attendant Assigned": ["Karmjit Singh", "Gurpreet Kaur", "Sandeep"]}), use_container_width=True)

# ==========================================
# 3. WEBSITE NAVIGATION CONTROLLER (SIDEBAR)
# ==========================================
def main():
    # Sidebar Title
    st.sidebar.markdown("## 🧭 Main Menu")
    
    # 🎯 EXPERT FIX: Radio Buttons for Website Navigation
    selected_page = st.sidebar.radio(
        "Select a Module to Open:",
        [
            "🏠 Home Dashboard",
            "1️⃣ Regular Staff",
            "2️⃣ Outsource Staff",
            "3️⃣ Regular Staff Detail",
            "4️⃣ Outsource Staff Detail",
            "5️⃣ Deputation Staff",
            "6️⃣ CH Ward Attendant List"
        ]
    )
    
    st.sidebar.divider()
    st.sidebar.caption("Secure HR Environment v2.0")

    # Routing logic based on Radio Button selection
    if selected_page == "🏠 Home Dashboard":
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
    elif selected_page == "6️⃣ CH Ward Attendant List":
        show_ward_attendant_list()

if __name__ == "__main__":
    main()
