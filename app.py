import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

# Import file lain (pastikan file-file ini ada di folder yang sama)
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

# KUNCI FULLSCREEN: Harus dipanggil paling atas!
st.set_page_config(page_title="Screening System", layout="wide")

def login_screen():
    # Tampilan judul dan form asli
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
                    st.success("Berhasil Login!")
                    st.rerun()
            else:
                st.error("❌ Email tidak terdaftar!")
        else:
            st.warning("Masukkan email.")

    # MENU DARURAT SUDAH DIHAPUS DARI SINI

def main_interface():
    # HEADER LOGOUT (Fullscreen, di atas)
    c1, c2 = st.columns([10, 1])
    c1.markdown(f"👤 **User:** {st.session_state['user']} | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
        
    st.divider()

    # LOAD DATA DATABASE SEKALI UNTUK SEMUA TAB
    db_p, stats, total = sc.fetch_all_data()

    # MENGGUNAKAN TABS MENDATAR AGAR TETAP FULLSCREEN (TIDAK ADA SIDEBAR)
    if st.session_state['role'] == "Admin":
        t1, t2, t3, t4, t5, t6 = st.tabs([
            "🔍 Single Screening", "🚀 Bulk Screening", "📊 KYC Dashboard", 
            "📝 Log Kegiatan", "👥 Management User", "🕒 Activity Log"
        ])
        with t1: sc.run_pencarian(st.session_state['user'], db_p, True)
        with t2: bat.run_bulk_screening()
        with t3: kyc.run_kyc_dashboard()
        with t4: kt.run_kegiatan_tracker()
        with t5: ut.run_user_management()
        with t6: lt.run_log_admin(stats, total)
    else:
        t1, t2, t3, t4 = st.tabs([
            "🔍 Single Screening", "🚀 Bulk Screening", "📊 KYC Dashboard", "📝 Log Kegiatan"
        ])
        with t1: sc.run_pencarian(st.session_state['user'], db_p, False)
        with t2: bat.run_bulk_screening()
        with t3: kyc.run_kyc_dashboard()
        with t4: kt.run_kegiatan_tracker()

# TRIGGER UTAMA UNTUK MENJALANKAN APLIKASI
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_screen()
    else:
        main_interface()

if __name__ == "__main__":
    main()
