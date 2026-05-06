import streamlit as st
import uuid
import time
import pandas as pd
from auth_utils import hash_pass, load_user_db, load_whitelist, log_activity, update_password, USER_DB_FILE
import screening_tab as screening
import log_tab as admin_log
import user_tab as admin_user

# ==========================================
# 1. KONFIGURASI HALAMAN & SESSION INITIALIZATION
# ==========================================
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

# --- WAJIB: Inisialisasi semua session state di paling atas ---
if "auth" not in st.session_state:
    st.session_state.auth = False
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()
if "f_key" not in st.session_state:
    st.session_state.f_key = str(uuid.uuid4()) # INI PENTING BIAR GAK ERROR
if "show_pw_form" not in st.session_state:
    st.session_state.show_pw_form = False
if "login_attempts" not in st.session_state:
    st.session_state.login_attempts = 0

# ... (Logika Timeout & CSS tetap sama)

# ==========================================
# 2. LOGIN SYSTEM
# ==========================================
df_w = load_whitelist()

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    
    # Sekarang key f_key sudah aman karena sudah dibuat di atas
    email_in = st.text_input("Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    
    if email_in != "":
        user_match = df_w[df_w['Email'] == email_in]
        
        if not user_match.empty:
            user_info = user_match.iloc[0]
            
            # 1. CEK STATUS BLOKIR
            if user_info.get('Status') == 'Blocked':
                st.error(f"❌ Akun {email_in} TERBLOKIR!")
                st.info("Anda salah password 3x. Hubungi Admin untuk buka blokir.")
                st.stop()

            # 2. PROSES LOGIN
            db_u = load_user_db()
            user_row = db_u[db_u['Email'] == email_in]
            
            if user_row.empty:
                p1 = st.text_input("Buat Password Baru:", type="password", key=f"new_p_{st.session_state.f_key}")
                if st.button("Daftar"):
                    if p1:
                        new_u = pd.DataFrame([[email_in, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([db_u, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Berhasil! Silakan Login."); time.sleep(1); st.rerun()
                    else:
                        st.warning("Password tidak boleh kosong.")
            else:
                pwd = st.text_input("Password:", type="password", key=f"p_{st.session_state.f_key}")
                if st.button("Masuk"):
                    if hash_pass(pwd) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.login_attempts = 0
                        st.session_state.auth, st.session_state.user = True, email_in
                        log_activity(email_in, "Login")
                        st.rerun()
                    else:
                        st.session_state.login_attempts += 1
                        if st.session_state.login_attempts >= 3:
                            df_w.loc[df_w['Email'] == email_in, 'Status'] = 'Blocked'
                            save_whitelist(df_w)
                            log_activity(email_in, "AKUN TERBLOKIR")
                            st.rerun()
                        else:
                            st.error(f"Sandi Salah! Sisa percobaan: {3 - st.session_state.login_attempts}")
        else:
            st.error("Email tidak terdaftar di Whitelist!")
    st.stop()

# ==========================================
# 2. LOGIN SYSTEM (FIX INDEX ERROR)
# ==========================================
df_w = load_whitelist()

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    email_in = st.text_input("Email:", key=f"e_{st.session_state.f_key}").lower().strip()
    
    if email_in != "":
        # Cari data user di whitelist
        user_match = df_w[df_w['Email'] == email_in]
        
        if not user_match.empty:
            # Ambil data user secara aman
            user_info = user_match.iloc[0]
            
            # 1. CEK STATUS BLOKIR
            # Pakai .get() supaya kalau kolom Status belum ada, nggak error
            if user_info.get('Status') == 'Blocked':
                st.error(f"❌ Akun {email_in} TERBLOKIR!")
                st.info("Anda salah password 3x. Hubungi Admin untuk buka blokir.")
                st.stop()

            # 2. PROSES LOGIN
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
                        st.session_state.login_attempts = 0
                        st.session_state.auth, st.session_state.user = True, email_in
                        log_activity(email_in, "Login")
                        st.rerun()
                    else:
                        # Tambah hitungan salah
                        st.session_state.login_attempts = st.session_state.get('login_attempts', 0) + 1
                        
                        if st.session_state.login_attempts >= 3:
                            # Update status jadi Blocked di file CSV
                            df_w.loc[df_w['Email'] == email_in, 'Status'] = 'Blocked'
                            save_whitelist(df_w)
                            log_activity(email_in, "AKUN TERBLOKIR")
                            st.rerun()
                        else:
                            st.error(f"Sandi Salah! Sisa percobaan: {3 - st.session_state.login_attempts}")
        else:
            st.error("Email tidak terdaftar di Whitelist!")
            
    st.stop()
# ==========================================
# 3. IDENTIFIKASI ROLE (UNTUK MENU)
# ==========================================
# Cari role user yang sedang login
user_info = df_w[df_w['Email'] == st.session_state.user]
user_role = user_info.iloc[0]['Role'] if not user_info.empty else "User"
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
