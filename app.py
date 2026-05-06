import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
import uuid
import hashlib
from datetime import datetime, timedelta

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System Multi-Database", layout="wide", initial_sidebar_state="collapsed")

# 2. DAFTAR LINK DATABASE (GOOGLE SHEETS)
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

# 3. CSS CUSTOM (DESAIN ASLI KAMU)
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

# 4. FUNGSI DATABASE & KEAMANAN
USER_DB_FILE = "users_db.csv"
WHITELIST_FILE = "whitelist.csv"

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

def load_user_db():
    if os.path.exists(USER_DB_FILE): return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["Email", "PasswordHash"])

def load_whitelist():
    if os.path.exists(WHITELIST_FILE): return pd.read_csv(WHITELIST_FILE)['Email'].tolist()
    return ["imanmuhamad9@gmail.com"]

# 5. SESSION STATE & LOGIN
if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

ALLOWED_EMAILS = load_whitelist()

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    df_users = load_user_db()
    u_email = st.text_input("Masukkan Email Anda:", key=f"m_{st.session_state.form_key}").lower().strip()
    
    if u_email:
        if u_email not in ALLOWED_EMAILS:
            st.error("Email Anda tidak terdaftar dalam sistem. Silakan hubungi Administrator.")
        else:
            user_row = df_users[df_users['Email'] == u_email]
            if user_row.empty:
                st.info(f"Akun {u_email} belum memiliki password. Silakan buat password baru.")
                p1 = st.text_input("Buat Password Baru:", type="password", key="p1")
                p2 = st.text_input("Konfirmasi Password:", type="password", key="p2")
                if st.button("Daftarkan Akun Sekarang"):
                    if p1 == p2 and len(p1) >= 4:
                        new_u = pd.DataFrame([[u_email, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([df_users, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Akun berhasil didaftarkan! Silakan masukkan password untuk login."); time.sleep(1.5)
                        st.rerun()
            else:
                u_pass = st.text_input("Masukkan Password:", type="password", key=f"p_{st.session_state.form_key}")
                if st.button("Login Ke Sistem"):
                    if hash_pass(u_pass) == user_row.iloc[0]['PasswordHash']:
                        st.session_state.auth = True
                        st.session_state.email_user = u_email
                        st.session_state.last_activity = time.time()
                        log_activity(u_email, "Login Berhasil")
                        st.rerun()
                    else: st.error("Password yang Anda masukkan salah!")
    st.stop()

# 6. HEADER & SESSION TIMEOUT
is_super_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
if (time.time() - st.session_state.last_activity) > (15 * 60):
    st.session_state.auth = False; st.rerun()
st.session_state.last_activity = time.time()

h_col1, h_col2 = st.columns([2.2, 3.8])
with h_col1:
    st.markdown(f'<div class="user-box">👤 Login sebagai: <b>{st.session_state.email_user}</b></div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    if b1.button("🔑 Ganti Password"): st.session_state.show_pw_form = not st.session_state.show_pw_form
    if b2.button("🚪 Logout"): st.session_state.auth = False; st.rerun()

with h_col2:
    st.markdown('<div class="header-title">SCREENING DATA APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

if st.session_state.show_pw_form:
    with st.container():
        f1, f2, f3 = st.columns([2, 2, 1.2], vertical_alignment="bottom")
        old_p = f1.text_input("Password Lama", type="password")
        new_p = f2.text_input("Password Baru", type="password")
        if f3.button("💾 Simpan"):
            df_u = load_user_db()
            idx = df_u[df_u['Email'] == st.session_state.email_user].index
            if hash_pass(old_p) == df_u.loc[idx[0], 'PasswordHash'] and len(new_p) >= 4:
                df_u.loc[idx[0], 'PasswordHash'] = hash_pass(new_p)
                df_u.to_csv(USER_DB_FILE, index=False)
                st.success("Password diperbarui!"); time.sleep(1); st.session_state.show_pw_form = False; st.rerun()
            else: st.error("Gagal!")
st.divider()

# 7. LOAD DATA (DENGAN CACHING BIAR NGGAK LOADING TERUS)
@st.cache_data(ttl=600)
def fetch_all_data():
    all_d, stats, total = {}, {}, 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url)
            all_d[name], stats[name], total = df, len(df), total + len(df)
        except: continue
    return all_d, stats, total

db, db_stats, total_all = fetch_all_data()

# 8. TAB NAVIGATION
tabs = st.tabs(["🔍 Menu Pencarian", "📊 Log Aktivitas & Statistik"]) if is_super_admin else st.tabs(["🔍 Menu Pencarian"])

with tabs[0]:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: metode = st.radio("Metode Pencarian:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: query = st.text_input("Input Data Yang Dicari:", placeholder="Ketik nama atau nomor di sini...", key="q_main")
    with c3: threshold = st.slider("Ambang Batas Kemiripan (Akurasi %):", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if query:
        q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
        # LOGIC PENCARIAN ASLI (LENGKAP)
        if metode == "Nama" and any(char.isdigit() for char in query):
            st.error("❌ Pencarian berdasarkan Nama tidak boleh mengandung angka!")
        elif metode == "NIK" and len(q_strip) < 16:
            st.error(f"❌ Nomor NIK harus minimal 16 digit! (Input Anda: {len(q_strip)} digit)")
        elif metode == "Paspor" and len(q_strip) < 7:
            st.error(f"❌ Nomor Paspor harus minimal 7 karakter!")
        else:
            log_activity(st.session_state.email_user, f"Melakukan pencarian {metode}: {query}")
            q_clean = " ".join(query.split()).lower()
            found, results_all = False, []
            
            for db_name, df_data in db.items():
                def check_row(row):
                    best_score, match_cols = 0, []
                    # Jika NIK/Paspor, cek semua kolom. Jika Nama, cek kolom yang ada kata 'nama'
                    target_cols = df_data.columns if metode in ["NIK", "Paspor"] else [c for c in df_data.columns if 'nama' in c.lower()]
                    
                    for col in target_cols:
                        score = fuzz.token_sort_ratio(q_clean, str(row[col]).lower())
                        if score >= threshold:
                            match_cols.append(f"{col} ({score}%)")
                            if score > best_score: best_score = score
                    
                    return pd.Series([best_score, "Match pada: " + ", ".join(match_cols)]) if best_score > 0 else pd.Series([0, "-"])

                df_temp = df_data.copy()
                df_temp[['_score', 'KETERANGAN STATUS']] = df_temp.apply(check_row, axis=1)
                matches = df_temp[df_temp['_score'] > 0].copy()
                
                if not matches.empty:
                    found = True
                    final_res = matches.sort_values('_score', ascending=False).drop(columns=['_score'])
                    results_all.append(final_res)
                    with st.expander(f"🚩 Hasil Ditemukan di Database: {db_name}", expanded=True):
                        st.dataframe(final_res, hide_index=True, use_container_width=True)
            
            if found:
                st.success(f"Pencarian selesai. Data ditemukan di {len(results_all)} database.")
                if is_super_admin:
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf) as writer: pd.concat(results_all).to_excel(writer, index=False)
                    st.download_button("📥 Download Semua Hasil Temuan (Excel)", buf.getvalue(), "Hasil_Screening.xlsx", use_container_width=True)
            else:
                st.warning("Data tidak ditemukan di seluruh database dengan ambang batas akurasi tersebut.")

if is_super_admin:
    with tabs[1]:
        st.subheader("📊 Statistik Database & Log Aktivitas")
        # Stat Cards
        s_cols = st.columns(len(db_stats) + 1)
        for i, (name, count) in enumerate(db_stats.items()):
            s_cols[i].markdown(f'<div class="stat-card"><small>{name}</small><br><b>{count:,} Data</b></div>', unsafe_allow_html=True)
        s_cols[-1].markdown(f'<div style="background-color: #0068c9; color: white; padding: 15px; border-radius: 10px; text-align: center; height: 100px;"><small>TOTAL DATABASE</small><br><b>{total_all:,} Data</b></div>', unsafe_allow_html=True)
        
        st.divider()
        
        if os.path.exists("log_aktivitas.csv"):
            log_df = pd.read_csv("log_aktivitas.csv")
            c1, c2 = st.columns(2)
            with c1:
                buf_log = io.BytesIO()
                with pd.ExcelWriter(buf_log) as writer: log_df.to_excel(writer, index=False)
                st.download_button("📥 Download Log Aktivitas (Excel)", buf_log.getvalue(), "Log_Sistem.xlsx", use_container_width=True)
            with c2:
                if st.button("🔥 Bersihkan Semua Log", use_container_width=True):
                    os.remove("log_aktivitas.csv"); st.rerun()
            
            st.write("**Tabel Riwayat Aktivitas Terbaru:**")
            st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
