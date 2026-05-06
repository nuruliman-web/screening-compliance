import streamlit as st
import uuid
import time
import pandas as pd
from auth_utils import hash_pass, load_user_db, load_whitelist, log_activity, update_password, USER_DB_FILE
import screening_tab as screening
import log_tab as admin_log
import user_tab as admin_user

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Sembunyikan Header Bawaan Streamlit */
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    
    /* Box Nama User - Dibuat presisi 40px agar sejajar tombol */
    .user-box { 
        background-color: #f8f9fa; 
        padding: 0px 15px; 
        border-radius: 8px; 
        border: 1px solid #e6e9ef;
        height: 40px; 
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #31333F;
        font-weight: 600;
        margin-bottom: 0px;
    }
    
    /* Styling Button Utama */
    div.stButton > button { 
        border-radius: 8px !important; 
        height: 40px !important; 
        font-size: 14px !important;
        transition: 0.3s;
    }

    /* Judul Header */
    .header-title { 
        color: #1f1f1f; 
        font-size: 22px; 
        font-weight: 800; 
        text-align: center; 
        line-height: 1.2; 
        padding-top: 5px;
    }

    /* Container Form Password */
    .pw-form { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #dee2e6; 
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Merapatkan jarak antar elemen */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. INISIALISASI SESSION STATE
# ==========================================
if "auth" not in st.session_state: st.session_state.auth = False
if "f_key" not in st.session_state: st.session_state.f_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# ==========================================
# 3. SISTEM LOGIN
# ==========================================
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    email_in = st.text_input("Masukkan Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    
    if email_in:
        whitelist = load_whitelist()
        if email_in in whitelist:
            db_u = load_user_db()
            user_row = db_u[db_u['Email'] == email_in]
            
            if user_row.empty:
                st.info(f"Halo {email_in}, silakan buat password untuk akun Anda.")
                p1 = st.text_input("Buat Password Baru:", type="password")
                if st.button("Daftarkan Akun"):
                    if len(p1) >= 4:
                        new_u = pd.DataFrame([[email_in, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Registrasi Berhasil! Silakan Login.")
                        time.sleep(1); st.rerun()
                    else: st.error("Password minimal 4 karakter!")
            else:
                pwd = st.text_input("Masukkan Password:", type="password", key=f"p_{st.session_state.f_key}")
                if st.button("Masuk Ke Sistem"):
                    if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.auth = True
                        st.session_state.user = email_in
                        log_activity(email_in, "Login Berhasil")
                        st.rerun()
                    else: st.error("Password Salah!")
        else:
            st.error("Email Anda tidak terdaftar dalam whitelist.")
    st.stop()

# ==========================================
# 4. HEADER (TATA LETAK BARU)
# ==========================================
is_admin = st.session_state.user == "imanmuhamad9@gmail.com"

# Grid Utama: Kiri (User Info) | Kanan (Judul)
col_left, col_right = st.columns([2.8, 3.2])

with col_left:
    # Baris 1: Nama User & Logout (Sejajar/Presisi)
    u_c1, u_c2 = st.columns([2.5, 1], vertical_alignment="center")
    u_c1.markdown(f'<div class="user-box">👤 &nbsp;<b>{st.session_state.user}</b></div>', unsafe_allow_html=True)
    if u_c2.button("🚪 Logout", key="lo_btn", use_container_width=True):
        st.session_state.auth = False
        st.rerun()
    
    # Baris 2: Tombol Ubah Password (Di bawahnya)
    st.markdown('<div style="margin-top:8px;"></div>', unsafe_allow_html=True) # Jarak kecil
    if st.button("🔑 Ubah Password", key="up_btn", use_container_width=True):
        st.session_state.show_pw_form = not st.session_state.show_pw_form

with col_right:
    # Judul Aplikasi
    st.markdown('<div class="header-title">🔍 SCREENING DATABASE<br>APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

# ==========================================
# 5. FORM UBAH PASSWORD (TOGGLE)
# ==========================================
if st.session_state.show_pw_form:
    st.markdown('<div class="pw-form">', unsafe_allow_html=True)
    st.write("**Form Perubahan Password**")
    cp1, cp2, cp3 = st.columns([2, 2, 1], vertical_alignment="bottom")
    old_p = cp1.text_input("Password Lama", type="password")
    new_p = cp2.text_input("Password Baru", type="password")
    if cp3.button("💾 Simpan", use_container_width=True):
        db_u = load_user_db()
        current_h = db_u[db_u['Email'] == st.session_state.user].iloc[0]['PasswordHash']
        if hash_pass(old_p) == current_h:
            if len(new_p) >= 4:
                update_password(st.session_state.user, new_p)
                st.success("Password Diperbarui!")
                time.sleep(1)
                st.session_state.show_pw_form = False
                st.rerun()
            else: st.error("Minimal 4 karakter!")
        else: st.error("Password lama salah!")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 6. MENU TAB (MANGGIL FILE EXTERNAL)
# ==========================================
# Ambil data dari screening_tab
db, stats, total = screening.fetch_all_data()

if is_admin:
    t1, t2, t3 = st.tabs(["🔍 Menu Pencarian", "📊 Log Aktivitas Admin", "👥 Manajemen User"])
    with t1:
        screening.run_pencarian(st.session_state.user, db, is_admin)
    with t2:
        admin_log.run_log_admin(stats, total)
    with t3:
        admin_user.run_user_management()
else:
    # User biasa hanya melihat menu pencarian
    t1 = st.tabs(["🔍 Menu Pencarian"])
    with t1[0]:
        screening.run_pencarian(st.session_state.user, db, is_admin)
