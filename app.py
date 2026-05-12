import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

# IMPORT HALAMAN LAIN
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

st.set_page_config(page_title="Screening System", layout="wide")

def main():
    # 1. CEK SESSION LOGIN
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_screen()
    else:
        main_interface()

def login_screen():
    st.title("🔐 Login Screening System")
    df_users = load_user_db()
    
    email_input = st.text_input("Email:").lower().strip()
    
    if st.button("Masuk"):
        if email_input:
            df_users['Email'] = df_users['Email'].astype(str).str.lower().str.strip()
            if email_input in df_users['Email'].values:
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                if str(user_data.get('Status', 'Active')) == 'Blocked':
                    st.error("🚫 Akun Anda diblokir.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = email_input
                    st.session_state['role'] = user_data.get('Role', 'User')
                    st.rerun()
            else:
                st.error("❌ Email tidak terdaftar!")
        else:
            st.warning("Masukkan email.")

    with st.expander("🛠️ Menu Darurat"):
        if st.button("🔥 Reset Database"):
            if os.path.exists(USER_DB_FILE): os.remove(USER_DB_FILE)
            st.rerun()

def main_interface():
    # SIDEBAR MENU
    st.sidebar.title(f"Menu ({st.session_state['role']})")
    st.sidebar.write(f"User: {st.session_state['user']}")
    
    menu = ["🔍 Single Screening", "🚀 Bulk Screening", "📊 KYC Dashboard", "📝 Log Kegiatan"]
    if st.session_state['role'] == "Admin":
        menu += ["👥 Management User", "🕒 Activity Log"]
    
    choice = st.sidebar.radio("Pilih Navigasi:", menu)
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # LOAD DATA DATABASE PEMERINTAH (UNTUK STATS)
    db_p, stats, total = sc.fetch_all_data()

    # LOGIK NAVIGASI
    if choice == "🔍 Single Screening":
        sc.run_pencarian(st.session_state['user'], db_p, st.session_state['role'] == "Admin")
    elif choice == "🚀 Bulk Screening":
        bat.run_bulk_screening()
    elif choice == "📊 KYC Dashboard":
        kyc.run_kyc_dashboard()
    elif choice == "📝 Log Kegiatan":
        kt.run_kegiatan_tracker()
    elif choice == "👥 Management User":
        ut.run_user_management()
    elif choice == "🕒 Activity Log":
        lt.run_log_admin(stats, total)

if __name__ == "__main__":
    main()
