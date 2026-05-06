import streamlit as st
import uuid, time
from auth_utils import hash_pass, load_user_db, load_whitelist, log_activity, USER_DB_FILE
import screening_tab as screening
import log_tab as admin_log
import user_tab as admin_user

# 1. SETUP
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; }
    .user-box { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e6e9ef; }
    .header-title { font-size: 24px; font-weight: 800; text-align: center; }
    .stat-card { padding: 15px; border-radius: 10px; background: white; border: 1px solid #eee; text-align: center; }
    div.stButton > button { border-radius: 8px !important; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGIN
if "auth" not in st.session_state: st.session_state.auth = False
if "f_key" not in st.session_state: st.session_state.f_key = str(uuid.uuid4())

if not st.session_state.auth:
    st.title("🔐 Login System")
    email = st.text_input("Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    if email in load_whitelist():
        db_u = load_user_db()
        user_row = db_u[db_u['Email'] == email]
        if user_row.empty:
            p1 = st.text_input("Buat Password:", type="password")
            if st.button("Daftar"):
                import pandas as pd
                new_u = pd.DataFrame([[email, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False); st.rerun()
        else:
            pwd = st.text_input("Password:", type="password", key=f"p_{st.session_state.f_key}")
            if st.button("Masuk"):
                if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                    st.session_state.auth, st.session_state.user = True, email; st.rerun()
    st.stop()

# 3. HEADER
is_admin = st.session_state.user == "imanmuhamad9@gmail.com"
c1, c2 = st.columns([2, 4])
with c1:
    st.markdown(f'<div class="user-box">👤 <b>{st.session_state.user}</b></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout"): st.session_state.auth = False; st.rerun()
with c2: st.markdown('<div class="header-title">SCREENING DATA MULTI-DATABASE</div>', unsafe_allow_html=True)

# 4. DATA & TABS
db, stats, total = screening.fetch_all_data()
if is_admin:
    t1, t2, t3 = st.tabs(["🔍 Pencarian", "📊 Log Admin", "👥 Manajemen User"])
    with t1: screening.run_pencarian(st.session_state.user, db, is_admin)
    with t2: admin_log.run_log_admin(stats, total)
    with t3: admin_user.run_user_management()
else:
    t1 = st.tabs(["🔍 Pencarian"])
    with t1[0]: screening.run_pencarian(st.session_state.user, db, is_admin)
