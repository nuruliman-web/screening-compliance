import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

def login_screen():
    st.title("🔐 Login Screening System")
    
    df_users = load_user_db() #

    email_input = st.text_input("Email:").lower().strip() # 
    
    if st.button("Masuk"):
        if email_input:
            # Standarisasi kolom email untuk pencarian
            df_users['Email'] = df_users['Email'].astype(str).str.lower().str.strip() # 
            
            if email_input in df_users['Email'].values:
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                
                if str(user_data['Status']) == 'Blocked':
                    st.error("🚫 Akun Anda diblokir.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = email_input
                    st.session_state['role'] = user_data.get('Role', 'User')
                    st.success("Berhasil Login!")
                    st.rerun()
            else:
                st.error("❌ Email tidak terdaftar!") [cite: 1]
        else:
            st.warning("Masukkan email.")

    # --- TOMBOL HAPUS OTOMATIS (Gunakan jika data bermasalah) ---
    with st.expander("🛠️ Menu Darurat (Hapus Database Lama)"):
        st.warning("Gunakan ini jika email tetap tidak terdaftar setelah didaftarkan.")
        if st.button("🔥 Reset & Hapus Semua Database"):
            files_to_delete = ["users_db.csv", "whitelist.csv"]
            for f in files_to_delete:
                if os.path.exists(f):
                    os.remove(f)
            st.success("Database lama berhasil dihapus! Silakan refresh halaman.")
            st.rerun()
