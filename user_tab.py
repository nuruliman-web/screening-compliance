import streamlit as st
import pandas as pd
from auth_utils import load_whitelist, save_whitelist, load_user_db, USER_DB_FILE

def run_user_management():
    # Header Menu
    st.markdown("### 👥 Manajemen Pengguna")
    st.write("Kelola akses email, status akun, dan kontrol keamanan user.")
    
    # 1. CONTAINER TAMBAH USER
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com")
        if c2.button("Simpan Akses", use_container_width=True):
            whitelist = load_whitelist()
            if new_email and "@" in new_email:
                if new_email.lower().strip() not in whitelist:
                    whitelist.append(new_email.lower().strip())
                    save_whitelist(whitelist)
                    st.success(f"✅ {new_email} berhasil ditambahkan ke whitelist.")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah terdaftar.")
            else:
                st.error("❌ Format email tidak valid.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. DAFTAR USER DENGAN TAMPILAN TABEL
    whitelist = load_whitelist()
    user_db = load_user_db()
    
    # Header Tabel
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-bottom: 2px solid #dee2e6; margin-bottom: 10px;">
            <div style="display: flex; font-weight: bold; color: #495057;">
                <div style="flex: 2.2;">EMAIL PENGGUNA</div>
                <div style="flex: 1.3; text-align: center;">STATUS AKUN</div>
                <div style="flex: 2.5; text-align: center;">KONTROL KEAMANAN</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for email in whitelist:
        is_registered = not user_db[user_db['Email'] == email].empty
        
        with st.container():
            col_mail, col_stat, col_act = st.columns([2.2, 1.3, 2.5], vertical_alignment="center")
            
            # Kolom Email
            col_mail.markdown(f"**{email}**")
            
            # Kolom Status (Badge Style)
            if is_registered:
                col_stat.markdown('<div style="text-align:center;"><span style="background-color: #d4edda; color: #155724; padding: 4px 12px; border-radius: 15px; font-size: 11px; font-weight: bold;">✅ AKTIF</span></div>', unsafe_allow_html=True)
            else:
                col_stat.markdown('<div style="text-align:center;"><span style="background-color: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 15px; font-size: 11px; font-weight: bold;">⏳ PENDING</span></div>', unsafe_allow_html=True)
            
            # Kolom Aksi
            with col_act:
                a1, a2 = st.columns([1, 1.2])
                if is_registered:
                    if a1.button("🔄 Reset", key=f"res_{email}", use_container_width=True, help="Reset password user"):
                        new_db = user_db[user_db['Email'] != email]
                        new_db.to_csv(USER_DB_FILE, index=False)
                        st.toast(f"Password {email} telah di-reset.")
                        st.rerun()
                else:
                    a1.write("")

                if email != st.session_state.user:
                    # PERUBAHAN: Ikon sampah diganti teks "❌ Hapus Akun"
                    if a2.button("❌ Hapus Akun", key=f"del_{email}", use_container_width=True):
                        # Hapus dari whitelist
                        new_whitelist = [e for e in whitelist if e != email]
                        save_whitelist(new_whitelist)
                        # Hapus dari db password jika ada
                        new_db = user_db[user_db['Email'] != email]
                        new_db.to_csv(USER_DB_FILE, index=False)
                        st.toast(f"Akses {email} telah dicabut.")
                        st.rerun()
                else:
                    a2.markdown('<p style="text-align:center; font-size:11px; color:gray; margin-top:8px;">(Admin Utama)</p>', unsafe_allow_html=True)
            
            st.markdown('<hr style="margin: 5px 0px; border-top: 1px solid #eee;">', unsafe_allow_html=True)

    # 3. KETERANGAN LEBIH JELAS (REVISI)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ Panduan & Keterangan Status", expanded=True):
        st.markdown("""
        - **✅ AKTIF**: User sudah memiliki akses dan **sudah mendaftarkan password**. User ini bisa masuk ke sistem sewaktu-waktu.
        - **⏳ PENDING**: User sudah diberikan izin akses (Whitelist), tetapi **belum pernah login** atau belum membuat password.
        - **🔄 Tombol Reset**: Digunakan jika user lupa password. Fitur ini akan menghapus password lama, sehingga saat user login kembali, sistem akan memintanya membuat password baru.
        - **❌ Tombol Hapus Akun**: Mencabut seluruh hak akses user secara permanen. User tidak akan bisa login kembali kecuali didaftarkan ulang oleh Admin.
        """)
