import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS CUSTOM (HAPUS HEADER)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    .user-info { color: black !important; font-weight: bold; }
    .block-container { padding-top: 1rem; }
    .stButton > button { width: auto; padding: 2px 15px; font-size: 12px; }
    .search-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0068c9;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGGING (ANTI ERROR & AUTO REPAIR)
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Kalau file log rusak/error, langsung hapus otomatis biar gak ParserError
    if os.path.exists(log_file):
        try:
            pd.read_csv(log_file)
        except:
            os.remove(log_file)
            
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

# 4. LOGIN SYSTEM
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    user_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            log_activity(user_email, "Login")
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 5. HEADER
col_header, _ = st.columns([1, 4])
with col_header:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout")
        st.session_state.auth = False
        st.rerun()
st.divider()

# 6. DATABASE LOADER
@st.cache_data(ttl=60)
def load_db(path):
    if os.path.exists(path):
        try:
            data = pd.read_excel(path, sheet_name=None)
            stats = {s: len(data[s]) for s in data}
            return data, stats
        except: return None, None
    return None, None

db, db_stats = load_db("database.xlsx")

# 7. TABS
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
can_download = st.session_state.email_user != "xxx@gmail.com"

if is_admin:
    tab_screening, tab_log = st.tabs(["🔍 Screening Nasabah", "📜 Log & Statistik Admin"])
else:
    tab_screening, = st.tabs(["🔍 Screening Nasabah"])
    tab_log = None

# --- TAB 1: SCREENING ---
with tab_screening:
    if db:
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col_m, col_c, col_s = st.columns([1, 2, 2])
        with col_m: metode = st.radio("Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
        with col_c: query = st.text_input("Cari Data:", placeholder="Ketik Nama/NIK...")
        with col_s: threshold = st.slider("🎯 Akurasi (%)", 50, 100, 85)
        st.markdown('</div>', unsafe_allow_html=True)

        if query:
            q_clean = " ".join(query.split()).lower()
            found = False
            results = []
            target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
            log_activity(st.session_state.email_user, f"Cari {metode}")

            for sn in target_sheets:
                if sn in db:
                    df = db[sn].copy()
                    
                    def process_row(row):
                        best_s = 0
                        reason = "-"
                        cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                        for c in cols:
                            val = " ".join(str(row[c]).split()).lower()
                            if metode == "Nama":
                                s = fuzz.token_sort_ratio(q_clean, val)
                                if s > best_s:
                                    best_s = s
                                    reason = f"Nama mirip di: {c}"
                            else:
                                if q_clean == val:
                                    best_s = 100
                                    reason = f"NIK Cocok di: {c}"
                        return pd.Series([best_s, reason])

                    df[['SKOR', 'ALASAN MATCH']] = df.apply(process_row, axis=1)
                    limit = threshold if metode == "Nama" else 100
                    match = df[df['SKOR'] >= limit].copy()
                    
                    if not match.empty:
                        found = True
                        match = match.sort_values('SKOR', ascending=False)
                        results.append(match)
                        with st.expander(f"🚩 Database: {sn}", expanded=True):
                            # Tampilkan tabel standar (Tanpa styling yang bikin error)
                            st.dataframe(match, hide_index=True, use_container_width=True)

            if found and can_download:
                st.divider()
                final_df = pd.concat(results)
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
                st.download_button("📥 Download Hasil", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
            elif query and not found:
                st.warning("Data tidak ditemukan.")
    else: st.error("Database tidak ditemukan.")

# --- TAB 2: LOG ---
if tab_log and is_admin:
    with tab_log:
        if os.path.exists("log_aktivitas.csv"):
            df_l = pd.read_csv("log_aktivitas.csv").iloc[::-1]
            st.dataframe(df_l, use_container_width=True, hide_index=True)
