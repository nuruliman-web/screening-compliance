import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db # Import fungsi yang sudah kita perbaiki

def login_screen():
    st.title("🔐 Login Screening System")
    
    # Gunakan fungsi load yang sudah diproteksi
    df_users = load_user_db()

    email_input = st.text_input("Email:").lower().strip()
    
    if st.button("Masuk"):
        if email_input:
            # Standarisasi kolom email di dataframe untuk pencarian
            df_users['Email'] = df_users['Email'].astype(str).str.lower().str.strip()
            
            if email_input in df_users['Email'].values:
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                
                # Cek Status
                if str(user_data['Status']) == 'Blocked':
                    st.error("🚫 Akun Anda diblokir. Hubungi Admin.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = email_input
                    st.session_state['role'] = user_data['Role']
                    st.success(f"Selamat Datang, {email_input}!")
                    st.rerun()
            else:
                st.error("❌ Email tidak terdaftar! Pastikan Admin sudah menambahkan email Anda.")
        else:
            st.warning("Silakan masukkan email.")
