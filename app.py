import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, hash_pass

# Import modul lain
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

# KUNCI FULLSCREEN
st.set_page_config(page_title="Screening System", layout="wide")

def login_screen():
    # Header Dihapus Total sesuai permintaan
    st.title("🔐 Login Screening System")
    
    email_input = st.text_input("Email:").lower().strip()
    pass_input = st.text_input("Password:", type="password")
    
    if st.button("Masuk", use_container_width=True):
        if email_input and pass_input:
            df_users = load_user_db()
            
            if email_input in df_users['Email'].values:
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                
                if str(user_data.get('Status', 'Active')) == 'Blocked':
                    st.error("🚫 Akun Anda diblokir.")
                else:
                    if hash_pass(pass_input) == str(user_data.get('Password', '')):
                        st.session_state['logged_in'] = True
                        st.session_state['user'] = email_input
                        st.session_state['role'] = user_data.get('Role', 'User')
                        st.success("Berhasil Login!")
                        st.rerun()
                    else:
                        st.error("❌ Password salah!")
            else:
                st.error("❌ Email tidak terdaftar!")
        else:
            st.warning("Masukkan Email dan Password.")

def main_interface():
    # Header & Logout
    c1, c2 = st.columns([10, 2])
    c1.markdown(f"👤 **User:** {st.session_state['user']} | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.divider()
    db_p, stats, total = sc.fetch_all_data()

    # Menu Tabs (Fullscreen)
    if st.session_state['role'] == "Admin":
        tabs = st.tabs(["🔍 Single", "🚀 Bulk", "📊 KYC", "📝 Log", "👥 User", "🕒 Admin Log"])
        with tabs[0]: sc.run_pencarian(st.session_state['user'], db_p, True)
        with tabs[1]: bat.run_bulk_screening()
        with tabs[2]: kyc.run_kyc_dashboard()
        with tabs[3]: kt.run_kegiatan_tracker()
        with tabs[4]: ut.run_user_management()
        with tabs[5]: lt.run_log_admin(stats, total)
    else:
        tabs = st.tabs(["🔍 Single", "🚀 Bulk", "📊 KYC", "📝 Log"])
        with tabs[0]: sc.run_pencarian(st.session_state['user'], db_p, False)
        with tabs[1]: bat.run_bulk_screening()
        with tabs[2]: kyc.run_kyc_dashboard()
        with tabs[3]: kt.run_kegiatan_tracker()

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if not st.session_state['logged_in']:
        login_screen()
    else:
        main_interface()

if __name__ == "__main__":
    main()
