import streamlit as st
import pandas as pd
from auth_utils import load_whitelist, save_whitelist, load_user_db, USER_DB_FILE

def run_user_management():
    st.markdown("### 👥 Manajemen Akses & Pengguna")
    
    # 1. FORM TAMBAH USER BARU
    with st.container():
        st.markdown('<div style="background-color:#f0f2f6; padding:20px; border-radius:10px;">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Tambah Email User Baru:", placeholder="contoh: user@gmail.com")
        if c2.button("➕ Tambah Ke Whitelist", use_container_width=True):
            whitelist = load_whitelist()
            if new_email and "@" in new_email:
                if new_email.lower().strip() not in whitelist:
                    whitelist.append(new_email.lower().strip())
                    save_whitelist(whitelist)
                    st.success(f"✅ {new_email} berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah ada di daftar.")
            else:
                st.error("❌ Format email salah.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 2. TABEL DAFTAR USER
    whitelist = load_whitelist()
    user_db = load_user_db()
    
    # Header Tabel Manual
    h1, h2, h3, h4 = st.columns([2, 1, 1, 2])
    h1.write("**Email User**")
    h2.write("**Status**")
    h2.write("") # Spasi
    h3.write("") # Spasi
    h4.write("**Aksi / Kontrol**")
    st.markdown("---")

    for email in whitelist:
        # Cek apakah user sudah registrasi (ada di users_db.csv)
        is_registered = not user_db[user_db['Email'] == email].empty
        
        col_email, col_status, col_reset, col_delete = st.columns([2, 1, 1, 1])
        
        # Kolom Nama
        col_email.write(f"**{email}**")
        
        # Kolom Status
        if is_registered:
            col_status.markdown('<span style="color:#28a745; font-weight:bold;">● AKTIF</span>', unsafe_allow_html=True)
        else:
            col_status.markdown('<span style="color:#ffc107; font-weight:bold;">● PENDING</span>', unsafe_allow_html=True)
        
        # Kolom Reset Password
        if is_registered:
            if col_reset.button("🔄 Reset", key=f"res_{email}", help="Hapus password agar user bisa buat baru"):
                # Hapus hanya baris user tersebut di DB password
                new_db = user_db[user_db['Email'] != email]
                new_db.to_csv(USER_DB_FILE, index=False)
                st.toast(f"Password {email} berhasil di-reset!")
                st.rerun()
        else:
            col_reset.write("-")

        # Kolom Hapus User (Admin Utama tidak bisa hapus diri sendiri)
        if email == st.session_state.user:
            col_delete.write("*(You)*")
        else:
            if col_delete.button("🗑️ Hapus", key=f"del_{email}", help="Hapus akses user ini selamanya"):
                # 1. Hapus dari Whitelist
                new_whitelist = [e for e in whitelist if e != email]
                save_whitelist(new_whitelist)
                # 2. Hapus dari DB Password (jika ada)
                new_db = user_db[user_db['Email'] != email]
                new_db.to_csv(USER_DB_FILE, index=False)
                st.toast(f"User {email} telah dihapus.")
                st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("""
        💡 **Keterangan:**
        - **AKTIF:** User sudah mendaftarkan password dan bisa login.
        - **PENDING:** Email terdaftar tapi user belum pernah login/bikin password.
        - **RESET:** Menghapus password user. Saat login lagi, user akan diminta buat password baru.
    """)
