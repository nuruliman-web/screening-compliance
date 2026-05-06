import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
import uuid
import hashlib # Tambahan untuk enkripsi password
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

# 3. CSS CUSTOM & ANTI-SUGGEST
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    .user-info { color: black !important; font-weight: bold; margin-bottom: 5px; }
    .header-banner-clean { 
        color: black; padding: 10px; font-size: 32px; font-weight: 800; 
        text-align: center; display: flex; align-items: center; justify-content: center;
        height: 100%; letter-spacing: 1px;
    }
    .block-container { padding-top: 1rem; }
    .search-container {
        background-color: #f0f2f6; padding: 15px; border-radius: 10px;
        border-left: 5px solid #0068c9; margin-top: 20px;
    }
    .stat-card {
        padding: 10px; border-radius: 8px; background-color: #ffffff; 
        border: 1px solid #e6e9ef; text-align: center;
    }
    </style>
    <script>
        const patchInputs = () => {
            const inputs = window.parent.document.getElementsByTagName('input');
            for (let i = 0; i < inputs.length; i++) {
                inputs[i].setAttribute('autocomplete', 'new-password');
                inputs[i].setAttribute('spellcheck', 'false');
            }
        };
        setInterval(patchInputs, 500);
    </script>
    """, unsafe_allow_html=True)

# 4. FUNGSI LOGGING & ENKRIPSI
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    jam_wib = datetime.now() + timedelta(hours=7)
    now = jam_wib.strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    try:
        if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
        else: new_data.to_csv(log_file, mode='a', header=False, index=False)
    except: pass

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 5. INITIAL SESSION STATE
if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())

# 6. LOGIKA TIMEOUT (5 MENIT)
TIMEOUT_LIMIT = 5 * 60 
if st.session_state.auth:
    if "last_activity" in st.session_state:
        elapsed = time.time() - st.session_state.last_activity
        if elapsed > TIMEOUT_LIMIT:
            log_activity(st.session_state.email_user, "Auto-Logout (Timeout)")
            st.session_state.auth = False
            st.rerun()
    st.session_state.last_activity = time.time()

# 7. LOGIN SYSTEM DENGAN PASSWORD RAHASIA
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "x@gmail.com", "xx@gmail.com"]
USER_DB_FILE = "users_db.csv"

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["Email", "PasswordHash"])

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    df_users = load_user_db()
    
    u_email = st.text_input("Email:", key=f"mail_{st.session_state.form_key}").lower().strip()
    
    if u_email:
        if u_email not in ALLOWED_EMAILS:
            st.error("Email tidak diizinkan oleh Admin!")
        else:
            user_row = df_users[df_users['Email'] == u_email]
            
            if user_row.empty:
                st.info(f"Halo {u_email}, silakan buat password untuk pendaftaran pertama.")
                new_p = st.text_input("Buat Password:", type="password", key="new_p")
                conf_p = st.text_input("Konfirmasi Password:", type="password", key="conf_p")
                if st.button("Daftarkan Password", use_container_width=True):
                    if new_p == conf_p and len(new_p) >= 4:
                        hashed = hash_pass(new_p)
                        new_user = pd.DataFrame([[u_email, hashed]], columns=["Email", "PasswordHash"])
                        pd.concat([df_users, new_user]).to_csv(USER_DB_FILE, index=False)
                        st.success("Berhasil! Silakan login ulang.")
                        time.sleep(2)
                        st.rerun()
                    else: st.error("Password tidak cocok atau terlalu pendek!")
            else:
                u_pass = st.text_input("Password:", type="password", key=f"pass_{st.session_state.form_key}")
                if st.button("Masuk", use_container_width=True):
                    if hash_pass(u_pass) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.auth = True
                        st.session_state.email_user = u_email
                        st.session_state.last_activity = time.time()
                        log_activity(u_email, "Login Success")
                        st.rerun()
                    else:
                        log_activity(u_email, "Login Failed (Wrong Password)")
                        st.error("Password Salah!")
    st.stop()

is_super_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"

# 8. HEADER
col_u, col_b = st.columns([1, 3])
with col_u:
    st.markdown(f'<p class="user-info">👤 {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout")
        st.session_state.auth = False
        st.rerun()
with col_b:
    st.markdown('<div class="header-banner-clean">🔍 SCREENING DATA APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)
st.divider()

# 9. LOAD DATA
@st.cache_data(ttl=300)
def load_db():
    all_data, stats, total = {}, {}, 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url)
            all_data[name], stats[name], total = df, len(df), total + len(df)
        except: continue
    return all_data, stats, total

db, db_stats, total_all = load_db()

# 10. TABS
tabs = st.tabs(["🔍 Screening Nasabah", "📜 Log Admin"]) if is_super_admin else st.tabs(["🔍 Screening Nasabah"])

# --- TAB SCREENING ---
with tabs[0]:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: metode = st.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: query = st.text_input("Cari Data:", placeholder=f"Masukkan {metode}...", key=f"q_{st.session_state.form_key}")
    with c3: threshold = st.slider("🎯 Akurasi Pencarian (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        valid = True
        if metode == "NIK" and len(query) != 16:
            st.warning("⚠️ NIK harus 16 digit!")
            valid = False
        if valid:
            search_id = f"search_{query}_{metode}"
            if "last_log" not in st.session_state or st.session_state.last_log != search_id:
                log_activity(st.session_state.email_user, f"Mencari {metode}: {query}")
                st.session_state.last_log = search_id

            q_clean = " ".join(query.split()).lower()
            found = False
            results_all = []
            for sn, df_data in db.items():
                def find_match(row):
                    m_info, max_s = [], 0
                    cols = df_data.columns if metode in ["NIK", "Paspor"] else [c for c in df_data.columns if 'nama' in c.lower()]
                    for c in cols:
                        s = fuzz.token_sort_ratio(q_clean, str(row[c]).lower())
                        if s >= threshold:
                            m_info.append(f"{c} ({s}%)")
                            if s > max_s: max_s = s
                    return pd.Series([max_s, "Match: " + ", ".join(m_info)]) if max_s > 0 else pd.Series([0, "-"])

                df_temp = df_data.copy()
                df_temp[['_score', 'KET']] = df_temp.apply(find_match, axis=1)
                match = df_temp[df_temp['_score'] > 0].copy()
                if not match.empty:
                    found = True
                    res = match.sort_values('_score', ascending=False).drop(columns=['_score'])
                    results_all.append(res)
                    with st.expander(f"🚩 Database: {sn}", expanded=True):
                        st.dataframe(res, hide_index=True, use_container_width=True)

            if found and is_super_admin:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: pd.concat(results_all).to_excel(w, index=False)
                st.download_button("📥 Download Hasil (Excel)", buf.getvalue(), "Hasil_Screening.xlsx", use_container_width=True)
            if not found: st.error("Data tidak ditemukan.")

# --- TAB ADMIN ---
if is_super_admin:
    with tabs[1]:
        st.subheader("📊 Statistik & Manajemen Log")
        if db_stats:
            n_cols = len(db_stats) + 1
            cols = st.columns(n_cols)
            for i, (name, count) in enumerate(db_stats.items()):
                cols[i].markdown(f'<div class="stat-card"><small>{name}</small><br><strong>{count:,}</strong></div>', unsafe_allow_html=True)
            
            with cols[-1]:
                st.markdown(f'<div style="background-color: #0068c9; color: white; padding: 10px; border-radius: 8px; text-align: center;"><small>TOTAL DATA</small><br><strong style="font-size: 20px;">{total_all:,}</strong></div>', unsafe_allow_html=True)
                st.write("") 
                if os.path.exists("log_aktivitas.csv"):
                    try:
                        log_df_raw = pd.read_csv("log_aktivitas.csv")
                        buf_log = io.BytesIO()
                        with pd.ExcelWriter(buf_log) as w: log_df_raw.to_excel(w, index=False)
                        st.download_button("📥 Download Log", buf_log.getvalue(), "Log_Aktivitas.xlsx", use_container_width=True)
                    except: pass
                    if st.button("🔥 Reset/Hapus Log", use_container_width=True):
                        os.remove("log_aktivitas.csv")
                        st.rerun()
        
        st.divider()
        if os.path.exists("log_aktivitas.csv"):
            try:
                log_df = pd.read_csv("log_aktivitas.csv")
                log_df = log_df.loc[:, ~log_df.columns.duplicated()]
                st.write("📋 Riwayat Aktivitas:")
                st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
            except: st.error("Format log bermasalah. Klik Reset di kotak biru.")
        else: st.info("Belum ada log aktivitas.")
