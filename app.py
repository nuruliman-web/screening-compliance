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
    div.stButton > button { border-radius: 8px !important; height: 40px !important; }
    .pw-form { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. SESSION STATE
if "auth" not in st.session_state: st.session_state.auth = False
if "f_key" not in st.session_state: st.session_state.f_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# 3. LOGIN SYSTEM
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    email_in = st.text_input("Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    if email_in in load_whitelist():
        db_u = load_user_db()
        user_row = db_u[db_u['Email'] == email_in]
        if user_row.empty:
            p1 = st.text_input("Buat Password Baru:", type="password")
            if st.button("Daftarkan Akun"):
                import pandas as pd
                new_u = pd.DataFrame([[email_in, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False); st.success("Berhasil!"); time.sleep(1); st.rerun()
        else:
            pwd = st.text_input("Password:", type="password", key=f"p_{st.session_state.f_key}")
            if st.button("Masuk"):
                if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                    st.session_state.auth, st.session_state.user = True, email_in; log_activity(email_in, "Login Berhasil"); st.rerun()
                else: st.error("Password Salah!")
    st.stop()

# 4. HEADER LAYOUT (REVISI)
is_admin = st.session_state.user == "imanmuhamad9@gmail.com"
col_user, col_title = st.columns([2.8, 3.2])

with col_user:
    # Baris 1: Nama & Logout Sejajar
    u_c1, u_c2 = st.columns([2.5, 1], vertical_alignment="center")
    u_c1.markdown(f'<div class="user-box" style="margin-bottom:0px">👤 <b>{st.session_state.user}</b></div>', unsafe_allow_html=True)
    if u_c2.button("🚪 Logout", key="lo_btn", use_container_width=True):
        st.session_state.auth = False; st.rerun()
    
    # Baris 2: Ubah Password di bawahnya
    if st.button("🔑 Ubah Password", key="up_btn", use_container_width=True):
        st.session_state.show_pw_form = not st.session_state.show_pw_form

with col_title:
    # Judul baru
    st.markdown('<div class="header-title">🔍 SCREENING DATABASE APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

# 5. PW CHANGE FORM
if st.session_state.show_pw_form:
    with st.container():
        st.markdown('<div class="pw-form">', unsafe_allow_html=True)
        c_p1, c_p2, c_p3 = st.columns([2, 2, 1], vertical_alignment="bottom")
        old_p = c_p1.text_input("Password Lama", type="password")
        new_p = c_p2.text_input("Password Baru", type="password")
        if c_p3.button("💾 Simpan", use_container_width=True):
            if update_password(st.session_state.user, new_p):
                st.success("Password diganti!"); time.sleep(1); st.session_state.show_pw_form = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# 6. TABS
db, stats, total = screening.fetch_all_data()
if is_admin:
    t1, t2, t3 = st.tabs(["🔍 Pencarian", "📊 Log Aktivitas", "👥 Manajemen User"])
    with t1: screening.run_pencarian(st.session_state.user, db, is_admin)
    with t2: admin_log.run_log_admin(stats, total)
    with t3: admin_user.run_user_management()
else:
    t = st.tabs(["🔍 Pencarian"])
    with t[0]: screening.run_pencarian(st.session_state.user, db, is_admin)
