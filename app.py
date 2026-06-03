import streamlit as st
from streamlit_option_menu import option_menu

# Import tabs
import kyc_dashboard_tab
import screening_tab
import bulk_admin_tab
import user_tab
import log_tab
import kegiatan_tracker
import sipesat_tab  # <-- TAMBAHAN: Import menu baru SIPESAT

# Check login status
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("pages/login.py")

# Application entry point
def main():
    st.set_page_config(
        page_title="Screening Compliance",
        page_icon="🛡️",
        layout="wide"
    )

    # Top Menu Navigation
    # Tambahkan "SIPESAT" ke dalam list menu dan berikan ikon "table"
    selected = option_menu(
        menu_title=None,
        options=["KYC Dashboard", "Screening", "SIPESAT", "Bulk Admin", "User Management", "Activity Log", "Kegiatan Tracker"],
        icons=["speedometer2", "shield-check", "table", "person-gear", "people", "journal-text", "list-check"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "16px"}, 
            "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

    # Routing logic based on selected menu
    if selected == "KYC Dashboard":
        kyc_dashboard_tab.show()
    elif selected == "Screening":
        screening_tab.show()
    elif selected == "SIPESAT":
        sipesat_tab.show()  # <-- TAMBAHAN: Menampilkan halaman SIPESAT
    elif selected == "Bulk Admin":
        bulk_admin_tab.show()
    elif selected == "User Management":
        user_tab.show()
    elif selected == "Activity Log":
        log_tab.show()
    elif selected == "Kegiatan Tracker":
        kegiatan_tracker.show()

if __name__ == "__main__":
    main()
