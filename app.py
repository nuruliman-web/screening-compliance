import streamlit as st
import uuid, time
from auth_utils import hash_pass, load_user_db, load_whitelist, log_activity, update_password, USER_DB_FILE
import screening_tab as screening
import log_tab as admin_log
import user_tab as admin_user

# 1. SETUP & CSS
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .user-box { background-color: #f8f9fa; padding: 10px 15px; border-radius: 8px; border: 1px solid #e6e9ef; }
    .header-title { color: #1f1f1f; font-size: 22px; font-weight: 800; text-align: center; line-height: 1.2; padding-top: 10px; }
    div.stButton > button { border-radius: 8px !important; height: 40px !important; font-size: 14px !important; }
    /* Form ubah password style */
    .pw-form { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE
if "auth" not in st.session_state: st.session_state.auth = False
if "f_key" not in st.session_state: st.session_state.f_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# 3. LOGIN LOGIC
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    email_input = st.text_input("Masukkan Email Anda:", key=f"e_{st.session_state.f_key}").lower().strip()
    
    if email_input:
        if email_input in load_whitelist():
            db_u = load_user_db()
            user_row = db_u[db_u['Email'] == email_input]
            
            if user_row.empty:
                st.info(f"Halo {email_input}, silakan buat password untuk pertama kali.")
                p1 = st.text_input("Buat Password Baru:", type="password")
                p2 = st.text_input("Konfirmasi Password:", type="password")
                if st.button("Daftarkan Akun"):
                    if p1 == p2 and len(p1) >= 4:
                        import pandas as pd
                        new_u = pd.DataFrame([[email_input, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Berhasil! Silakan masukkan password Anda kembali."); time.sleep(1); st.rerun()
                    else: st.error("Password tidak cocok atau terlalu pendek!")
            else:
                pwd = st.text_input("Masukkan Password:", type="password", key=f"p_{st.session_state.f_key}")
                if st.button("Masuk Ke Sistem"):
                    if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.auth = True
                        st.session_state.user = email_input
                        log_activity(email_input, "Login Berhasil")
                        st.rerun()
                    else: st.error("Password Salah!")
        else: st.error("Email tidak terdaftar!")
    st.stop()

# 4. HEADER (TOMBOL & JUDUL BARU)
is_admin = st.session_state.user == "imanmuhamad9@gmail.com"
col_user, col_title = st.columns([2.5, 3.5])

with col_user:
    st.markdown(f'<div class="user-box">👤 <b>{st.session_state.user}</b></div>', unsafe_allow_html=True)
    btn1, btn2 = st.columns(2)
    if btn1.button("🔑 Ubah Password"):
        st.session_state.show_pw_form = not st.session_state.show_pw_form
    if btn2.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

with col_title:
    # Judul sesuai permintaan (Ikon Cari + Teks Baru)
    st.markdown('<div class="header-title">🔍 SCREENING DATABASE APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

# 5. FORM UBAH PASSWORD (MUNCUL JIKA DIKLIK)
if st.session_state.show_pw_form:
    st.markdown('<div class="pw-form">', unsafe_allow_html=True)
    st.write("### Ganti Password")
    cp_col1, cp_col2, cp_col3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
    old_p = cp_col1.text_input("Password Lama", type="password")
    new_p = cp_col2.text_input("Password Baru", type="password")
    if cp_col3.button("💾 Simpan"):
        db_u = load_user_db()
        current_pass = db_u[db_u['Email'] == st.session_state.user].iloc[0]['PasswordHash']
        if hash_pass(old_p) == current_pass:
            if len(new_p) >= 4:
                update_password(st.session_state.user, new_p)
                st.success("Password berhasil diganti!"); time.sleep(1)
                st.session_state.show_pw_form = False
                st.rerun()
            else: st.error("Password baru terlalu pendek!")
        else: st.error("Password lama salah!")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 6. TAB NAVIGATION
db, stats, total = screening.fetch_all_data()

if is_admin:
    t1, t2, t3 = st.tabs(["🔍 Pencarian", "📊 Log Aktivitas", "👥 Manajemen User"])
    with t1: screening.run_pencarian(st.session_state.user, db, is_admin)
    with t2: admin_log.run_log_admin(stats, total)
    with t3: admin_user.run_user_management()
else:
    t1 = st.tabs(["🔍 Pencarian"])
    with t1[0]: screening.run_pencarian(st.session_state.user, db, is_admin)
