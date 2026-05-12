import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna")
    df_users = load_user_db()

    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:").lower().strip()
        new_role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses"):
            if new_email and "@" in new_email:
                if new_email not in df_users['Email'].astype(str).str.lower().str.strip().tolist():
                    new_row = pd.DataFrame([{"Email": new_email, "Password": "", "Role": new_role, "Status": "Active"}])
                    df_save = pd.concat([df_users, new_row], ignore_index=True)
                    df_save.to_csv(USER_DB_FILE, index=False)
                    st.success(f"✅ {new_email} terdaftar!")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah ada.")
