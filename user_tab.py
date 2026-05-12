import streamlit as st
import pandas as pd
import os
from auth_utils import load_user_db, USER_DB_FILE, hash_pass

def run_user_management():
    st.markdown("### 👥 Manajemen & Daftar Pengguna")
    
    # 1. FORM UNTUK MENAMBAH USER (KARENA LOGIN DIHAPUS)
    with st.expander("➕ Tambah User Baru ke Database", expanded=False):
        with st.form("form_add_user", clear_on_submit=True):
            new_email = st.text_input("Email User:").lower().strip()
            new_role = st.selectbox("Role:", ["Admin", "User"])
            new_status = st.selectbox("Status:", ["Active", "Blocked"])
            # Password default (bisa diisi manual atau dikosongkan)
            new_pass = st.text_input("Password (Default):", value="1234", type="password")
            
            submit = st.form_submit_button("💾 Simpan User")
            
            if submit:
                if new_email and "@" in new_email:
                    df_users = load_user_db()
                    if new_email not in df_users['Email'].tolist():
                        new_data = pd.DataFrame([{
                            "Email": new_email,
                            "Password": hash_pass(new_pass),
                            "Role": new_role,
                            "Status": new_status
                        }])
                        df_save = pd.concat([df_users, new_data], ignore_index=True)
                        df_save.to_csv(USER_DB_FILE, index=False)
                        st.success(f"✅ User {new_email} berhasil ditambahkan!")
                        st.rerun()
                    else:
                        st.warning("⚠️ User dengan email tersebut sudah ada.")
                else:
                    st.error("❌ Mohon masukkan email yang valid.")

    st.divider()

    # 2. TAMPILAN TABEL USER
    df_display = load_user_db()
    if not df_display.empty:
        # Sembunyikan kolom password
        cols_show = [c for c in df_display.columns if 'password' not in c.lower()]
        st.dataframe(df_display[cols_show], use_container_width=True, hide_index=True)
        st.caption(f"Total: {len(df_display)} user terdaftar.")
    else:
        st.info("Belum ada user di database. Gunakan menu 'Tambah User' di atas.")
