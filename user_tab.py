import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna (Local Storage)")
    
    # 1. LOAD DATA
    df_users = load_user_db()

    # 2. FORM TAMBAH USER
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="budi@gmail.com").lower().strip()
        new_role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses", use_container_width=True):
            if new_email and "@" in new_email:
                # Cek duplikat dengan aman
                if new_email not in df_users['Email'].astype(str).str.lower().str.strip().tolist():
                    new_row = pd.DataFrame([{
                        "Email": new_email, 
                        "Password": "", 
                        "Role": new_role, 
                        "Status": "Active"
                    }])
                    df_save = pd.concat([df_users, new_row], ignore_index=True)
                    df_save.to_csv(USER_DB_FILE, index=False)
                    st.success(f"✅ {new_email} berhasil didaftarkan!")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah ada.")
            else:
                st.error("❌ Email tidak valid.")

    # 3. DAFTAR USER
    st.divider()
    if not df_users.empty:
        df_users = df_users.dropna(subset=['Email']) # Hapus baris kosong jika ada
        for i, row in df_users.iterrows():
            with st.container(border=True):
                col_mail, col_role, col_stat, col_act = st.columns([2.5, 1, 1, 1.5], vertical_alignment="center")
                
                u_email = str(row['Email']).strip().lower()
                u_role = str(row['Role']) if pd.notnull(row['Role']) else "User"
                u_status = str(row['Status']) if pd.notnull(row['Status']) else "Active"
                
                col_mail.write(f"**{u_email}**")
                col_role.code(u_role.upper())
                
                if u_status == 'Blocked': col_stat.error("🔴 BLOCKED")
                else: col_stat.success("🟢 ACTIVE")

                if u_email != st.session_state.get('user', ''):
                    if col_act.button("🗑️ Hapus", key=f"del_{i}"):
                        df_users.drop(i).to_csv(USER_DB_FILE, index=False)
                        st.rerun()
