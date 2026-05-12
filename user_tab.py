import streamlit as st
import pandas as pd
import os

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna (Local Storage)")
    
    # --- 1. SETUP PENYIMPANAN LOKAL ---
    # Menggunakan file yang sama dengan sistem login agar sinkron
    USER_DB_FILE = "users_db.csv"

    # --- 2. LOAD DATA USER ---
    if os.path.exists(USER_DB_FILE):
        try:
            df_users = pd.read_csv(USER_DB_FILE)
            # Pastikan kolom yang dibutuhkan ada
            for col in ['Email', 'Password', 'Role', 'Status']:
                if col not in df_users.columns:
                    df_users[col] = "" if col != 'Status' else 'Active'
        except:
            df_users = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])
    else:
        df_users = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])

    # --- 3. CONTAINER TAMBAH USER BARU ---
    with st.expander("➕ Tambah Akses User Baru (Whitelist)", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com")
        new_role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses", use_container_width=True):
            if new_email and "@" in new_email:
                email_clean = new_email.lower().strip()
                if email_clean not in df_users['Email'].values:
                    # Tambah baris baru
                    new_row = pd.DataFrame([{
                        "Email": email_clean, 
                        "Password": "", # Kosong karena harus registrasi dulu
                        "Role": new_role, 
                        "Status": "Active"
                    }])
                    df_save = pd.concat([df_users, new_row], ignore_index=True)
                    
                    # Simpan ke CSV Lokal
                    df_save.to_csv(USER_DB_FILE, index=False)
                    
                    st.success(f"✅ {email_clean} berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah terdaftar.")
            else:
                st.error("❌ Format email tidak valid.")

    st.divider()

    # --- 4. DAFTAR USER & KONTROL ---
    st.markdown("#### 📋 Daftar Pengguna Terdaftar")
    
    if not df_users.empty:
        for i, row in df_users.iterrows():
            with st.container(border=True):
                col_mail, col_role, col_stat, col_act = st.columns([2.5, 1, 1, 1.5], vertical_alignment="center")
                
                email = row['Email']
                u_role = row['Role']
                u_status = row['Status']
                
                # Cek apakah user sudah set password (registrasi)
                # handle jika Password bernilai NaN
                is_registered = pd.notnull(row['Password']) and str(row['Password']).strip() != ""

                col_mail.write(f"**{email}**")
                
                # Menampilkan Role
                col_role.code(u_role.upper())
                
                # Status Badge
                if u_status == 'Blocked':
                    col_stat.error("🔴 BLOCKED")
                elif is_registered:
                    col_stat.success("🟢 AKTIF")
                else:
                    col_stat.warning("🟡 PENDING")

                # Tombol Hapus (Jangan hapus diri sendiri)
                current_session_user = st.session_state.get('user', '')
                if email != current_session_user:
                    if col_act.button("🗑️ Hapus Akses", key=f"del_{email}", use_container_width=True):
                        df_final = df_users[df_users['Email'] != email]
                        df_final.to_csv(USER_DB_FILE, index=False)
                        st.success(f"Akses {email} telah dihapus!")
                        st.rerun()
                else:
                    col_act.write("*(Akun Anda)*")
    else:
        st.info("Belum ada user dalam database lokal.")
