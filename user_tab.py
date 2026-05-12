import streamlit as st
import pandas as pd
import os

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna (Local Storage)")
    USER_DB_FILE = "users_db.csv"

    # 1. LOAD DATA
    if os.path.exists(USER_DB_FILE):
        df_users = pd.read_csv(USER_DB_FILE)
    else:
        df_users = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])

    # 2. FORM TAMBAH USER
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com").lower().strip() # <--- PENTING
        new_role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses"):
            if new_email and "@" in new_email:
                if new_email not in df_users['Email'].astype(str).tolist():
                    new_row = pd.DataFrame([{"Email": new_email, "Password": "", "Role": new_role, "Status": "Active"}])
                    df_save = pd.concat([df_users, new_row], ignore_index=True)
                    df_save.to_csv(USER_DB_FILE, index=False)
                    st.success(f"✅ {new_email} tersimpan!")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah ada di database.")
            else:
                st.error("❌ Email tidak valid.")

    # 3. DAFTAR USER
    st.divider()
    if not df_users.empty:
        df_users = df_users.dropna(how='all')
        for i, row in df_users.iterrows():
            with st.container(border=True):
                col_mail, col_role, col_stat, col_act = st.columns([2.5, 1, 1, 1.5], vertical_alignment="center")
                
                email = str(row['Email']).strip().lower()
                u_role = str(row['Role']) if pd.notnull(row['Role']) else "USER"
                u_status = str(row['Status']) if pd.notnull(row['Status']) else "Active"
                is_reg = str(row['Password']).strip() != "" and pd.notnull(row['Password'])

                col_mail.write(f"**{email}**")
                col_role.code(u_role.upper())
                
                if u_status == 'Blocked': col_stat.error("🔴 BLOCKED")
                elif is_reg: col_stat.success("🟢 AKTIF")
                else: col_stat.warning("🟡 PENDING")

                if email != st.session_state.get('user', ''):
                    if col_act.button("🗑️ Hapus", key=f"del_{i}"):
                        df_users.drop(i).to_csv(USER_DB_FILE, index=False)
                        st.rerun()
