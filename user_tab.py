import streamlit as st
import pandas as pd
from auth_utils import load_whitelist, save_whitelist, load_user_db, USER_DB_FILE

def run_user_management():
    st.markdown("### 👥 Manajemen Pengguna")
    
    # 1. FORM TAMBAH USER + PILIHAN ROLE
    with st.expander("➕ Tambah Akses User Baru", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1], vertical_alignment="bottom")
        new_email = c1.text_input("Email User:", placeholder="contoh: budi@gmail.com")
        role = c2.radio("Peran Akun:", ["User", "Admin"], horizontal=True)
        
        if c3.button("Simpan Akses", use_container_width=True):
            df_w = load_whitelist()
            if new_email and "@" in new_email:
                email_clean = new_email.lower().strip()
                if email_clean not in df_w['Email'].values:
                    new_row = pd.DataFrame([{"Email": email_clean, "Role": role}])
                    df_w = pd.concat([df_w, new_row], ignore_index=True)
                    save_whitelist(df_w)
                    st.success(f"✅ {email_clean} ditambahkan sebagai {role}.")
                    st.rerun()
                else: st.warning("⚠️ Email sudah terdaftar.")
            else: st.error("❌ Email tidak valid.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. DAFTAR USER
    df_w = load_whitelist()
    user_db = load_user_db()
    
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-bottom: 2px solid #dee2e6; margin-bottom: 10px;">
            <div style="display: flex; font-weight: bold; color: #495057;">
                <div style="flex: 2;">EMAIL PENGGUNA</div>
                <div style="flex: 1; text-align: center;">PERAN</div>
                <div style="flex: 1; text-align: center;">STATUS</div>
                <div style="flex: 2; text-align: center;">KONTROL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for index, row in df_w.iterrows():
        email = row['Email']
        u_role = row['Role']
        is_registered = not user_db[user_db['Email'] == email].empty
        
        with st.container():
            col_mail, col_role, col_stat, col_act = st.columns([2, 1, 1, 2], vertical_alignment="center")
            col_mail.markdown(f"**{email}**")
            
            # Kolom Peran (Admin/User)
            role_color = "#0068c9" if u_role == "Admin" else "#6c757d"
            col_role.markdown(f'<div style="text-align:center;"><span style="color:{role_color}; font-weight:bold; font-size:12px;">{u_role.upper()}</span></div>', unsafe_allow_html=True)
            
            # Kolom Status
            if is_registered:
                col_stat.markdown('<div style="text-align:center;"><span style="color: #28a745; font-size: 11px; font-weight: bold;">● AKTIF</span></div>', unsafe_allow_html=True)
            else:
                col_stat.markdown('<div style="text-align:center;"><span style="color: #ffc107; font-size: 11px; font-weight: bold;">● PENDING</span></div>', unsafe_allow_html=True)
            
            with col_act:
                a1, a2 = st.columns([1, 1.2])
                if is_registered and a1.button("🔄 Reset", key=f"res_{email}", use_container_width=True):
                    new_db = user_db[user_db['Email'] != email]
                    new_db.to_csv(USER_DB_FILE, index=False)
                    st.rerun()
                
                if email != st.session_state.user:
                    if a2.button("❌ Hapus Akun", key=f"del_{email}", use_container_width=True):
                        df_w = df_w.drop(index)
                        save_whitelist(df_w)
                        new_db = user_db[user_db['Email'] != email]
                        new_db.to_csv(USER_DB_FILE, index=False)
                        st.rerun()
                else: a2.markdown('<p style="text-align:center; font-size:11px; color:gray; margin-top:8px;">(Current)</p>', unsafe_allow_html=True)
            st.markdown('<hr style="margin: 5px 0px; border-top: 1px solid #eee;">', unsafe_allow_html=True)
