import streamlit as st
import pandas as pd
from auth_utils import load_whitelist, save_whitelist, load_user_db, USER_DB_FILE

def run_user_management():
    # Header Menu
    st.markdown("### 👥 Manajemen Pengguna")
    st.write("Kelola akses email, status akun, dan kontrol keamanan user.")
    
    # 1. CONTAINER TAMBAH USER
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com")
        role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses", use_container_width=True):
            df_w = load_whitelist()
            if new_email and "@" in new_email:
                email_clean = new_email.lower().strip()
                if email_clean not in df_w['Email'].values:
                    # Tambahkan kolom Status default Active saat daftar baru
                    new_row = pd.DataFrame([{"Email": email_clean, "Role": role, "Status": "Active"}])
                    df_w = pd.concat([df_w, new_row], ignore_index=True)
                    save_whitelist(df_w)
                    st.success(f"✅ {email_clean} berhasil ditambahkan.")
                    st.rerun()
                else:
                    st.warning("⚠️ Email sudah terdaftar.")
            else:
                st.error("❌ Format email tidak valid.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. DAFTAR USER
    df_w = load_whitelist()
    user_db = load_user_db()
    
    # Header Tabel
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-bottom: 2px solid #dee2e6; margin-bottom: 10px;">
            <div style="display: flex; font-weight: bold; color: #495057;">
                <div style="flex: 0.3;">NO</div>
                <div style="flex: 2.2;">EMAIL PENGGUNA</div>
                <div style="flex: 1;">PERAN</div>
                <div style="flex: 1; text-align: center;">STATUS</div>
                <div style="flex: 2.5; text-align: center;">KONTROL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for i, (index, row) in enumerate(df_w.iterrows(), start=1):
        email = row['Email']
        u_role = row['Role']
        u_status = row.get('Status', 'Active') # Ambil status blokir
        is_registered = not user_db[user_db['Email'] == email].empty
        
        with st.container():
            col_no, col_mail, col_role, col_stat, col_act = st.columns([0.3, 2.2, 1, 1, 2.5], vertical_alignment="center")
            
            col_no.write(f"{i}")
            
            # Email (No-Click)
            col_mail.markdown(f'<div style="color: #31333F; pointer-events: none;">{email}</div>', unsafe_allow_html=True)
            
            # Peran
            role_color = "#0068c9" if u_role == "Admin" else "#6c757d"
            col_role.markdown(f'<b style="color:{role_color}; font-size:12px;">{u_role.upper()}</b>', unsafe_allow_html=True)
            
            # Status Badge (Warna merah kalau Blocked)
            if u_status == 'Blocked':
                col_stat.markdown('<div style="text-align:center;"><span style="background-color: #f8d7da; color: #721c24; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">TERBLOKIR</span></div>', unsafe_allow_html=True)
            elif is_registered:
                col_stat.markdown('<div style="text-align:center;"><span style="background-color: #d4edda; color: #155724; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">AKTIF</span></div>', unsafe_allow_html=True)
            else:
                col_stat.markdown('<div style="text-align:center;"><span style="background-color: #fff3cd; color: #856404; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">PENDING</span></div>', unsafe_allow_html=True)
            
            # Kontrol
            with col_act:
                btn1, btn2 = st.columns([1, 1.3])
                
                # TOMBOL RESET (Hanya muncul kalau user sudah aktif atau terblokir)
                if is_registered or u_status == 'Blocked':
                    if btn1.button("🔄 Reset", key=f"res_{email}", use_container_width=True):
                        # 1. Hapus password di DB
                        new_db = user_db[user_db['Email'] != email]
                        new_db.to_csv(USER_DB_FILE, index=False)
                        # 2. Aktifkan kembali di Whitelist
                        df_w.loc[df_w['Email'] == email, 'Status'] = 'Active'
                        save_whitelist(df_w)
                        st.success(f"Akses {email} dipulihkan!")
                        st.rerun()
                
                # TOMBOL HAPUS (Tidak bisa hapus diri sendiri)
                if email != st.session_state.user:
                    if btn2.button("❌ Hapus", key=f"del_{email}", use_container_width=True):
                        df_w_new = df_w.drop(index)
                        save_whitelist(df_w_new)
                        new_db = user_db[user_db['Email'] != email]
                        new_db.to_csv(USER_DB_FILE, index=False)
                        st.rerun()
                else:
                    btn2.markdown('<p style="text-align:center; font-size:11px; color:gray; margin-top:8px;">(Admin)</p>', unsafe_allow_html=True)
            
            st.markdown('<hr style="margin: 5px 0px; border-top: 1px solid #eee;">', unsafe_allow_html=True)

    # Keterangan
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ Keterangan Status", expanded=False):
        st.markdown(f"**Total: {len(df_w)} User**")
        st.markdown("""
        - **TERBLOKIR**: Salah password 3x. Klik **Reset** untuk memulihkan.
        - **AKTIF**: Sudah memiliki password.
        - **PENDING**: Belum pernah login sejak didaftarkan.
        """)
