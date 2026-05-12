import streamlit as st
import pandas as pd
import os

def login_screen():
    st.title("🔐 Login Screening System")
    USER_DB_FILE = "users_db.csv"

    email_input = st.text_input("Email:").lower().strip() # <--- HARUS lower() dan strip()
    
    if st.button("Masuk"):
        if os.path.exists(USER_DB_FILE):
            df_users = pd.read_csv(USER_DB_FILE)
            
            # Pastikan kolom Email dibaca sebagai string dan dibersihkan
            df_users['Email'] = df_users['Email'].astype(str).str.lower().str.strip()
            
            if email_input in df_users['Email'].values:
                # CEK STATUS USER
                user_data = df_users[df_users['Email'] == email_input].iloc[0]
                
                if user_data['Status'] == 'Blocked':
                    st.error("🚫 Akun Anda diblokir. Hubungi Admin.")
                else:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = email_input
                    st.session_state['role'] = user_data['Role']
                    st.success("Berhasil Login!")
                    st.rerun()
            else:
                st.error("❌ Email tidak terdaftar! Periksa kembali atau hubungi Admin.")
        else:
            st.error("Database tidak ditemukan!")
