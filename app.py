import streamlit as st
import pandas as pd
import os
import hashlib
from auth_utils import load_user_db, USER_DB_FILE, hash_pass

# Import file modul lain
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

# KONFIGURASI LAYAR (Fullscreen/Wide)
st.set_page_config(page_title="Screening System", layout="wide")

def login_screen():
    st.title("🔐 Login Screening System")
    
    # Input Form
    email_input = st.text_input("Email:").lower().strip()
    pass_input = st.text_input("Password:", type="password") # Input password disembunyikan
    
    if st.button("Masuk"):
        if email_input and pass_input:
            df_users = load_user_db()
            
            # Normalisasi data email di DB
            df_users['Email'] = df_users['Email'].astype(str).str.lower().str.strip()
            
            if email_input in df_users['Email'].values:
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                
                # 1. Cek Status Blokir
                if str(user_data.get('Status', 'Active')) == 'Blocked':
                    st.error("🚫 Akun Anda diblokir. Hubungi Admin.")
                
                # 2. Logika Cek Password (DITAMBAHKAN KEMBALI)
                else:
                    hashed_input = hash_pass(pass_input)
                    # Pastikan kolom password di CSV namanya 'Password'
                    password_di_db = str(user_data.get('Password', ''))
                    
                    if hashed_input == password_di_db:
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
            st.warning("Silakan masukkan Email dan Password.")

def main_interface():
    # Header Info & Logout
    c1, c2 = st.columns([10, 1])
    c1.markdown(f"👤 **User:** {st.session_state['user']} | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()
        
    st.divider()

    # Load data database (API/Sheets)
    db_p, stats, total = sc.fetch_all_data()

    # Tampilan Menu Tab (Tetap Fullscreen)
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

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        login_screen()
    else:
        main_interface()

if __name__ == "__main__":
    main()
