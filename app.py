import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

def login_screen():
    st.title("🔐 Login Screening System")
    
    # Memuat database secara aman
    df_users = load_user_db()

    email_input = st.text_input("Email:").lower().strip()
    
    if st.button("Masuk"):
        if email_input:
            # Standarisasi pencarian email
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

    # Menu reset jika masih ada masalah data lama
    with st.expander("🛠️ Menu Darurat"):
        if st.button("🔥 Reset Database"):
            if os.path.exists(USER_DB_FILE): os.remove(USER_DB_FILE)
            if os.path.exists("whitelist.csv"): os.remove("whitelist.csv")
            st.rerun()
