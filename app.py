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
        .main-header { font-size: 2.5rem; color: #1e3a8a; font-weight: 800; margin-bottom: 0px; text-align: center;}
        .sub-header { color: #64748b; font-size: 16px; margin-bottom: 20px; text-align: center;}
        .card { background-color: #f8fafc; border-radius: 10px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px; text-align: center;}
        
        /* Styling the Radio buttons to look like a top navigation bar */
        div.row-widget.stRadio > div { flex-direction: row; justify-content: center; background-color: #f1f5f9; padding: 10px; border-radius: 10px; }
        div.row-widget.stRadio > div > label { margin-right: 15px; padding: 5px 10px; cursor: pointer; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. PAGE CONTENT FUNCTIONS
# ==========================================
def show_home():
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'><h3>🩺 Regular Staff</h3><h1 style='color:#2563eb;'>142</h1><p>Active Employees</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card'><h3>🤝 Outsource Staff</h3><h1 style='color:#16a34a;'>85</h1><p>Active Employees</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='card'><h3>🔄 Deputation</h3><h1 style='color:#dc2626;'>12</h1><p>Currently on Deputation</p></div>", unsafe_allow_html=True)
    
    st.divider()
    st.info("👆 **Tip:** Upar diye gaye menu se kisi bhi module par click karke uski details check karein.")

def show_regular_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🩺 Regular Staff Management")
    st.caption("Manage roster, attendance, and current postings of all regular employees.")
    st.dataframe(pd.DataFrame({"Emp ID": ["R-101", "R-102"], "Name": ["Dr. Rajiv", "Simran Kaur"], "Designation": ["MO", "Staff Nurse"]}), use_container_width=True)

def show_outsource_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🤝 Outsource Staff Management")
    st.caption("Manage contracts, agencies, and duty rosters for outsourced personnel.")
    st.dataframe(pd.DataFrame({"ID": ["OS-501", "OS-502"], "Name": ["Ramesh", "Sunita"], "Agency": ["A1 Services", "A1 Services"]}), use_container_width=True)

def show_regular_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📄 Regular Staff Detailed Records")
    st.caption("View deep analytics, service records, and personal details of regular staff.")
    st.info("Detailed profile view will load here.")

def show_outsource_staff_detail():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("📋 Outsource Staff Detailed Records")
    st.caption("View contract renewals, EPF details, and personal records of outsourced staff.")
    st.info("Detailed outsource records will load here.")

def show_deputation_staff():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🔄 Deputation Staff Register")
    st.caption("Track staff sent to or received from other institutions on deputation.")
    st.warning("No staff currently on deputation out of the station.")

def show_ward_attendant_list():
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🏥 CH Ward Attendant List")
    st.caption("Specific roster and ward allocations for Class-IV Ward Attendants.")
    st.dataframe(pd.DataFrame({"Ward": ["Emergency", "ICU", "OPD"], "Attendant Assigned": ["Karmjit Singh", "Gurpreet Kaur", "Sandeep"]}), use_container_width=True)

# ==========================================
# 3. TOP NAVIGATION CONTROLLER
# ==========================================
def main():
    # Main Header
    st.markdown("<div class='main-header'>🏢 Civil Hospital HR Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Centralized Staff Management System</div>", unsafe_allow_html=True)
    
    # 🎯 EXPERT FIX: Top Horizontal Radio Buttons
    selected_page = st.radio(
        "",  # Label ko khali chhod diya taaki clean lage
        [
            "🏠 Home",
            "1️⃣ Regular Staff",
            "2️⃣ Outsource Staff",
            "3️⃣ Regular Staff Detail",
            "4️⃣ Outsource Staff Detail",
            "5️⃣ Deputation Staff",
            "6️⃣ CH Ward Attendant"
        ],
        horizontal=True  # Yeh code radio buttons ko ek line (Top Menu) mein set kar dega
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
