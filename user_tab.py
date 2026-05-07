import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna (Sync to GSheets)")
    
    # 1. KONEKSI GSHEETS
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. LOAD DATA USER DARI TAB 'User_DB'
    try:
        df_users = conn.read(worksheet="User_DB", ttl=0)
        # Jika sheet kosong, buat dataframe template
        if df_users.empty:
            df_users = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])
    except:
        df_users = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])

    # 3. CONTAINER TAMBAH USER BARU (WHITELIST)
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com")
        new_role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses", use_container_width=True):
            if new_email and "@" in new_email:
                email_clean = new_email.lower().strip()
                if email_clean not in df_users['Email'].values:
                    # Tambah baris baru (Password kosong karena belum registrasi)
                    new_row = pd.DataFrame([{
                        "Email": email_clean, 
                        "Password": "", 
                        "Role": new_role, 
                        "Status": "Active"
                    }])
                    df_save = pd.concat([df_users, new_row], ignore_index=True)
                    
                    # Update ke GSheets
                    conn.update(worksheet="User_DB", data=df_save)
                    st.success(f"✅ {email_clean} berhasil ditambahkan ke database.")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah terdaftar.")
            else:
                st.error("❌ Format email tidak valid.")

    st.divider()

    # 4. DAFTAR USER & KONTROL
    st.markdown("#### 📋 Daftar Pengguna Terdaftar")
    
    if not df_users.empty:
        for i, row in df_users.iterrows():
            with st.container(border=True):
                col_mail, col_role, col_stat, col_act = st.columns([2.5, 1, 1, 1.5], vertical_alignment="center")
                
                email = row['Email']
                u_role = row['Role']
                u_status = row['Status']
                is_registered = row['Password'] != "" # Jika password isi, berarti sudah daftar

                col_mail.write(f"**{email}**")
                
                # Badge Role
                role_color = "blue" if u_role == "Admin" else "gray"
                col_role.markdown(f"<{role_color}>{u_role.upper()}</{role_color}>", unsafe_allow_html=True)
                
                # Badge Status
                if u_status == 'Blocked':
                    col_stat.error("🔴 BLOCKED")
                elif is_registered:
                    col_stat.success("🟢 AKTIF")
                else:
                    col_stat.warning("🟡 PENDING")

                # Kontrol Tombol
                if email != st.session_state.get('user'): # Jangan hapus diri sendiri
                    if col_act.button("🔄 Reset/Hapus", key=f"del_{email}"):
                        # Hapus user dari dataframe
                        df_final = df_users[df_users['Email'] != email]
                        conn.update(worksheet="User_DB", data=df_final)
                        st.success(f"Akses {email} telah dihapus!")
                        st.rerun()
                else:
                    col_act.write("(Anda)")
    else:
        st.info("Belum ada user yang didaftarkan.")
