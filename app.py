import streamlit as st
import uuid
import time
import pandas as pd
from auth_utils import hash_pass, load_user_db, load_whitelist, log_activity, update_password, USER_DB_FILE
import screening_tab as screening
import log_tab as admin_log
import user_tab as admin_user

# ==========================================
# 1. KONFIGURASI HALAMAN & TIMEOUT
# ==========================================
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

# KONFIGURASI WAKTU (3 MENIT = 180 DETIK)
TIMEOUT_SECONDS = 180 

# Logika Cek Timeout
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

if st.session_state.auth:
    current_time = time.time()
    elapsed_time = current_time - st.session_state.last_activity
    
    if elapsed_time > TIMEOUT_SECONDS:
        st.session_state.auth = False
        st.warning("Sesi Anda telah berakhir karena tidak ada aktivitas selama 3 menit.")
        time.sleep(2)
        st.rerun()
    else:
        # Update waktu aktivitas terakhir setiap ada interaksi
        st.session_state.last_activity = current_time

# --- CSS TETAP SAMA ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    
    .user-box { 
        background-color: #f8f9fa; 
        padding: 8px 15px; 
        border-radius: 8px; 
        border: 1px solid #e6e9ef;
        min-height: 40px;
        font-size: 14px;
        color: #31333F;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    
    div.stButton > button { 
        border-radius: 8px !important; 
        height: 40px !important;
        font-size: 14px !important;
    }

    .header-title { 
        color: #1f1f1f; 
        font-size: 22px; 
        font-weight: 800; 
        text-align: center; 
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIN SYSTEM (VERSI FIX ROLE)
# ==========================================
if "auth" not in st.session_state: st.session_state.auth = False
if "f_key" not in st.session_state: st.session_state.f_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# Ambil data whitelist sebagai DataFrame
df_w = load_whitelist()

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    email_in = st.text_input("Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    
    # PERBAIKAN DI SINI: Cek email di dalam kolom DataFrame
    if email_in in df_w['Email'].values:
        db_u = load_user_db()
        user_row = db_u[db_u['Email'] == email_in]
        
        if user_row.empty:
            p1 = st.text_input("Buat Password Baru:", type="password")
            if st.button("Daftar"):
                new_u = pd.DataFrame([[email_in, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False)
                st.success("Berhasil! Silakan Login."); time.sleep(1); st.rerun()
        else:
            pwd = st.text_input("Password:", type="password", key=f"p_{st.session_state.f_key}")
            if st.button("Masuk"):
                if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                    # Berhasil Login
                    st.session_state.auth = True
                    st.session_state.user = email_in
                    log_activity(email_in, "Login")
                    st.rerun()
                else: 
                    st.error("Password Salah!")
    elif email_in != "":
        st.error("Email Anda tidak terdaftar di Whitelist. Hubungi Admin.")
    st.stop()

# ==========================================
# 3. IDENTIFIKASI ROLE (UNTUK MENU)
# ==========================================
# Cari role user yang sedang login dari dataframe whitelist
current_user_data = df_w[df_w['Email'] == st.session_state.user]
if not current_user_data.empty:
    user_role = current_user_data.iloc[0]['Role']
else:
    user_role = "User" # Default jika tidak ditemukan

is_admin = (user_role == "Admin")
# ==========================================
# 3. HEADER (USER INFO & JUDUL)
# ==========================================
# Cek Role User dari Whitelist
user_info = df_w[df_w['Email'] == st.session_state.user]
user_role = user_info.iloc[0]['Role'] if not user_info.empty else "User"
is_admin = (user_role == "Admin")

col_user, col_title = st.columns([2.5, 3.5])

with col_user:
    # Baris 1: Nama & Logout
    c_u1, c_u2 = st.columns([2, 1])
    c_u1.markdown(f'<div class="user-box">👤 {st.session_state.user} ({user_role})</div>', unsafe_allow_html=True)
    if c_u2.button("🚪 Logout", use_container_width=True):
        st.session_state.auth = False; st.rerun()
    
    # Baris 2: Ubah Password
    if st.button("🔑 Ubah Password", use_container_width=True):
        st.session_state.show_pw_form = not st.session_state.show_pw_form

with col_title:
    st.markdown('<div class="header-title">🔍 SCREENING DATABASE APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

# ==========================================
# 4. PW CHANGE FORM
# ==========================================
if st.session_state.show_pw_form:
    with st.container():
        st.markdown('<div class="pw-form">', unsafe_allow_html=True)
        c_p1, c_p2, c_p3 = st.columns([2, 2, 1], vertical_alignment="bottom")
        old_p = c_p1.text_input("Sandi Lama", type="password")
        new_p = c_p2.text_input("Sandi Baru", type="password")
        if c_p3.button("Simpan", use_container_width=True):
            if update_password(st.session_state.user, new_p):
                st.success("Selesai!"); time.sleep(1); st.session_state.show_pw_form = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 5. TABS NAVIGATION
# ==========================================
db, stats, total = screening.fetch_all_data()

if is_admin:
    t1, t2, t3 = st.tabs(["🔍 Pencarian", "📊 Log Admin", "👥 User"])
    with t1: screening.run_pencarian(st.session_state.user, db, is_admin)
    with t2: admin_log.run_log_admin(stats, total)
    with t3: admin_user.run_user_management()
else:
    t1 = st.tabs(["🔍 Pencarian"])
    with t1[0]: screening.run_pencarian(st.session_state.user, db, is_admin)
