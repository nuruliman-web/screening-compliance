import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
import uuid
import hashlib
import re
from datetime import datetime, timedelta

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System Multi-Database", layout="wide", initial_sidebar_state="collapsed")

# 2. DAFTAR LINK DATABASE
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

# 3. CSS CUSTOM (DESAIN ASLI)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    .user-box { background-color: #f8f9fa; padding: 10px 15px; border-radius: 8px; border: 1px solid #e6e9ef; margin-bottom: 10px; }
    .header-title { color: #1f1f1f; font-size: 24px; font-weight: 800; text-align: center; padding: 10px; line-height: 1.2; }
    div.stButton > button { width: 100% !important; height: 45px !important; border-radius: 8px !important; }
    div[data-baseweb="input"] { height: 45px !important; }
    .search-box { background-color: #f0f2f6; padding: 20px; border-radius: 12px; border-left: 6px solid #0068c9; margin-bottom: 20px; }
    .stat-card { padding: 15px; border-radius: 10px; background-color: #ffffff; border: 1px solid #e6e9ef; text-align: center; height: 100px; }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI LOGGING & SECURITY
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    try:
        if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
        else: new_data.to_csv(log_file, mode='a', header=False, index=False)
    except: pass

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

USER_DB_FILE = "users_db.csv"
WHITELIST_FILE = "whitelist.csv"

def load_user_db():
    if os.path.exists(USER_DB_FILE): return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["Email", "PasswordHash"])

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        return pd.read_csv(WHITELIST_FILE)['Email'].tolist()
    return ["imanmuhamad9@gmail.com", "x@gmail.com", "xx@gmail.com"]

def save_whitelist(email_list):
    pd.DataFrame(email_list, columns=['Email']).to_csv(WHITELIST_FILE, index=False)

# 5. SESSION STATE
if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# 6. LOGIN SYSTEM
ALLOWED_EMAILS = load_whitelist()
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    df_users = load_user_db()
    u_email = st.text_input("Email:", key=f"m_{st.session_state.form_key}").lower().strip()
    if u_email:
        if u_email not in ALLOWED_EMAILS:
            st.error("Email tidak terdaftar!")
        else:
            user_row = df_users[df_users['Email'] == u_email]
            if user_row.empty:
                st.info(f"Halo {u_email}, buat password baru.")
                p1 = st.text_input("Password Baru:", type="password", key="p1")
                p2 = st.text_input("Konfirmasi Password:", type="password", key="p2")
                if st.button("Daftarkan Akun"):
                    if p1 == p2 and len(p1) >= 4:
                        new_u = pd.DataFrame([[u_email, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([df_users, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Berhasil!"); time.sleep(1); st.rerun()
            else:
                u_pass = st.text_input("Password:", type="password", key=f"p_{st.session_state.form_key}")
                if st.button("Masuk"):
                    if hash_pass(u_pass) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.auth, st.session_state.email_user = True, u_email
                        st.session_state.last_activity = time.time()
                        log_activity(u_email, "Login Success"); st.rerun()
                    else: st.error("Password Salah!")
    st.stop()

# --- SETELAH LOGIN ---
is_super_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
if (time.time() - st.session_state.last_activity) > (5 * 60):
    st.session_state.auth = False; st.rerun()
st.session_state.last_activity = time.time()

# 7. HEADER
h_col1, h_col2 = st.columns([2.2, 3.8])
with h_col1:
    st.markdown(f'<div class="user-box">👤 <b>{st.session_state.email_user}</b></div>', unsafe_allow_html=True)
    b_col1, b_col2 = st.columns(2)
    if b_col1.button("🔑 Ganti Password"):
        st.session_state.show_pw_form = not st.session_state.show_pw_form
    if b_col2.button("🚪 Logout"):
        st.session_state.auth = False; st.rerun()
with h_col2:
    st.markdown('<div class="header-title">SCREENING DATA APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

if st.session_state.show_pw_form:
    st.write("")
    f_col1, f_col2, f_col3 = st.columns([2, 2, 1.5], vertical_alignment="bottom")
    with f_col1: old_p = st.text_input("Password Lama", type="password", key="old_pwd_val")
    with f_col2: new_p = st.text_input("Password Baru", type="password", key="new_pwd_val")
    with f_col3: 
        if st.button("💾 Simpan", key="save_btn_rata"):
            df_u = load_user_db()
            idx = df_u[df_u['Email'] == st.session_state.email_user].index
            if hash_pass(old_p) == df_u.loc[idx[0], 'PasswordHash'] and len(new_p) >= 4:
                df_u.loc[idx[0], 'PasswordHash'] = hash_pass(new_p)
                df_u.to_csv(USER_DB_FILE, index=False)
                st.success("Tersimpan!"); time.sleep(1); st.session_state.show_pw_form = False; st.rerun()
            else: st.error("Gagal!")
st.divider()

# 8. LOAD DATA
@st.cache_data(ttl=300)
def load_db():
    all_d, stats, total = {}, {}, 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url); all_d[name], stats[name], total = df, len(df), total + len(df)
        except: continue
    return all_d, stats, total
db, db_stats, total_all = load_db()

# 9. TABS
if is_super_admin:
    tabs = st.tabs(["🔍 Pencarian", "📊 Log Admin", "👥 Manajemen User"])
else:
    tabs = st.tabs(["🔍 Pencarian"])

with tabs[0]:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: metode = st.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: query = st.text_input("Cari Data:", placeholder="Ketik...", key="q_main")
    with c3: threshold = st.slider("Akurasi (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if query:
        q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
        if metode == "Nama" and any(char.isdigit() for char in query):
            st.error("❌ Pencarian Nama tidak boleh mengandung angka!")
        elif metode == "NIK" and len(q_strip) < 16:
            st.error(f"❌ NIK harus minimal 16 digit! (Input Anda: {len(q_strip)} digit)")
        elif metode == "Paspor" and len(q_strip) < 7:
            st.error(f"❌ Nomor Paspor harus minimal 7 karakter!")
        else:
            log_activity(st.session_state.email_user, f"Cari {metode}: {query}")
            q_clean = " ".join(query.split()).lower()
            found, results_all = False, []
            for sn, df_data in db.items():
                def find_match(row):
                    max_s, m_info = 0, []
                    cols = df_data.columns if metode in ["NIK", "Paspor"] else [c for c in df_data.columns if 'nama' in c.lower()]
                    for c in cols:
                        s = fuzz.token_sort_ratio(q_clean, str(row[c]).lower())
                        if s >= threshold:
                            m_info.append(f"{c} ({s}%)")
                            if s > max_s: max_s = s
                    return pd.Series([max_s, "Match: " + ", ".join(m_info)]) if max_s > 0 else pd.Series([0, "-"])
                
                df_temp = df_data.copy()
                df_temp[['_s', 'KET STATUS']] = df_temp.apply(find_match, axis=1)
                match = df_temp[df_temp['_s'] > 0].copy()
                if not match.empty:
                    found = True
                    res = match.sort_values('_s', ascending=False).drop(columns=['_s'])
                    results_all.append(res)
                    with st.expander(f"🚩 Database: {sn}", expanded=True): 
                        st.dataframe(res, hide_index=True, use_container_width=True)
            
            if found and is_super_admin:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: pd.concat(results_all).to_excel(w, index=False)
                st.download_button("📥 Download Hasil Screening (Excel)", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
            elif not found:
                st.warning("Data tidak ditemukan di database manapun.")

if is_super_admin:
    with tabs[1]:
        cols_stat = st.columns(len(db_stats) + 1)
        for i, (name, count) in enumerate(db_stats.items()):
            cols_stat[i].markdown(f'<div class="stat-card"><small>{name}</small><br><b>{count:,}</b></div>', unsafe_allow_html=True)
        with cols_stat[-1]:
            st.markdown(f'<div style="background-color: #0068c9; color: white; padding: 15px; border-radius: 10px; text-align: center; height: 100px;"><small>TOTAL DATA</small><br><b>{total_all:,}</b></div>', unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("log_aktivitas.csv"):
            log_df = pd.read_csv("log_aktivitas.csv")
            l_col1, l_col2 = st.columns(2)
            buf_log = io.BytesIO()
            with pd.ExcelWriter(buf_log) as w: log_df.to_excel(w, index=False)
            l_col1.download_button("📥 Download Log Aktivitas", buf_log.getvalue(), "Log.xlsx", use_container_width=True)
            if l_col2.button("🔥 Reset / Hapus Semua Log", use_container_width=True):
                os.remove("log_aktivitas.csv"); st.rerun()
        st.divider()
        if os.path.exists("log_aktivitas.csv"): st.dataframe(pd.read_csv("log_aktivitas.csv").iloc[::-1], use_container_width=True, hide_index=True)

    with tabs[2]:
        st.subheader("👥 Manajemen Akses & Verifikasi User")
        df_u_current = load_user_db()
        
        # 1. TAMBAH USER (EMAIL SAJA)
        st.markdown('<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
        c_add1, c_add2 = st.columns([3, 1], vertical_alignment="bottom")
        with c_add1:
            new_mail_input = st.text_input("Tambah Email User Baru:", placeholder="input email...")
        with c_add2:
            if st.button("➕ Tambahkan User", use_container_width=True):
                if new_mail_input and "@" in new_mail_input:
                    low_mail = new_mail_input.lower().strip()
                    if low_mail not in ALLOWED_EMAILS:
                        ALLOWED_EMAILS.append(low_mail)
                        save_whitelist(ALLOWED_EMAILS)
                        st.success("User ditambahkan!"); time.sleep(0.5); st.rerun()
                    else: st.warning("Email sudah terdaftar.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # 2. TABEL MONITORING (EMAIL LANGSUNG, FONT HITAM, RESET, DELETE)
        h_c1, h_c2, h_c3, h_c4 = st.columns([2, 1, 1, 2])
        h_c1.write("**Email User**")
        h_c2.write("**Status Akun**")
        h_c3.write("**Verifikasi**")
        h_c4.write("**Aksi Manajemen**")
        
        for email in ALLOWED_EMAILS:
            user_data = df_u_current[df_u_current['Email'] == email]
            user_registered = not user_data.empty
            
            c_mail, c_stat, c_ver, c_act = st.columns([2, 1, 1, 2])
            c_mail.write(email)
            
            if user_registered:
                c_stat.write("Aktif")
                c_ver.write("Verified")
            else:
                c_stat.write("Terdaftar")
                c_ver.write("Belum Verifikasi")
            
            b_reset, b_del = c_act.columns(2)
            if user_registered:
                if b_reset.button("🔄 Reset", key=f"rs_{email}", use_container_width=True):
                    df_u_new = df_u_current[df_u_current['Email'] != email]
                    df_u_new.to_csv(USER_DB_FILE, index=False)
                    st.rerun()
            
            if email != "imanmuhamad9@gmail.com":
                if b_del.button("🗑️ Hapus", key=f"del_{email}", use_container_width=True):
                    ALLOWED_EMAILS.remove(email)
                    save_whitelist(ALLOWED_EMAILS)
                    df_u_new = df_u_current[df_u_current['Email'] != email]
                    df_u_new.to_csv(USER_DB_FILE, index=False)
                    st.rerun()
            else:
                b_del.write("🛡️ Super")
