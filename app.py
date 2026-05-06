import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System Multi-Database", layout="wide", initial_sidebar_state="collapsed")

# 2. DAFTAR LINK PER SHEET
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

# 3. CSS CUSTOM
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
        background-color: #ffffff; padding: 10px; border-radius: 5px;
        border: 1px solid #e6e9ef; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI LOGGING
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
    else: new_data.to_csv(log_file, mode='a', header=False, index=False)

# 5. LOGIN SYSTEM
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    u_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if u_email in ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]:
            st.session_state.auth = True
            st.session_state.email_user = u_email
            log_activity(u_email, "Login")
            st.rerun()
        else: st.error("Email tidak terdaftar!")
    st.stop()

is_super_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"

# 6. HEADER
col_user, col_banner = st.columns([1, 3])
with col_user:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout")
        st.session_state.auth = False
        st.rerun()
with col_banner:
    st.markdown('<div class="header-banner-clean">🔍 SCREENING DATA APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)
st.divider()

# 7. LOAD DATA
@st.cache_data(ttl=300)
def load_all_databases():
    all_data = {}
    stats = {}
    total = 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url)
            all_data[name] = df
            stats[name] = len(df)
            total += len(df)
        except: continue
    return all_data, stats, total

db, db_stats, total_all = load_all_databases()

# 8. TABS
tabs = st.tabs(["🔍 Screening Nasabah", "📜 Log Admin"]) if is_super_admin else st.tabs(["🔍 Screening Nasabah"])

# --- TAB SCREENING ---
with tabs[0]:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: 
        metode = st.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: 
        query = st.text_input("Cari Data:", placeholder=f"Masukkan {metode}...")
    with c3: 
        threshold = st.slider("🎯 Akurasi Pencarian (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    # VALIDASI NIK
    valid_to_search = True
    if query and metode == "NIK":
        if len(query) != 16:
            st.warning(f"⚠️ NIK harus berjumlah 16 digit! (Input saat ini: {len(query)} digit)")
            valid_to_search = False

    if query and db and valid_to_search:
        q_clean = " ".join(query.split()).lower()
        found = False
        results_to_export = []
        
        for sn, df_data in db.items():
            def find_match(row):
                matches_info = []
                max_score = 0
                
                # LOGIKA GLOBAL: NIK dan Paspor menyisir SEMUA KOLOM
                if metode in ["NIK", "Paspor"]:
                    check_cols = df_data.columns
                else: # Metode Nama hanya cek kolom yang ada kata 'nama'
                    check_cols = [c for c in df_data.columns if 'nama' in c.lower()]

                for c in check_cols:
                    val = " ".join(str(row[c]).split()).lower()
                    
                    # Fuzzy Logic untuk semua metode agar fleksibel
                    s = fuzz.token_sort_ratio(q_clean, val)
                    if s >= threshold:
                        matches_info.append(f"{c} ({s}%)")
                        if s > max_score: max_score = s
                
                if max_score > 0:
                    return pd.Series([max_score, "Match pada: " + ", ".join(matches_info)])
                return pd.Series([0, "-"])

            df_temp = df_data.copy()
            df_temp[['_score', 'ALASAN MATCH']] = df_temp.apply(find_match, axis=1)
            match = df_temp[df_temp['_score'] > 0].copy()
            
            if not match.empty:
                found = True
                match = match.sort_values('_score', ascending=False)
                cols_only = [c for c in match.columns if c not in ['_score', 'ALASAN MATCH']]
                display_df = match[['ALASAN MATCH'] + cols_only]
                results_to_export.append(display_df)
                with st.expander(f"🚩 Database: {sn}", expanded=True):
                    st.dataframe(display_df, hide_index=True, use_container_width=True)

        if found and is_super_admin:
            st.divider()
            final_df = pd.concat(results_to_export)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
            st.download_button("📥 Download Hasil Screening (Excel)", buf.getvalue(), "Hasil_Pencarian.xlsx", use_container_width=True)
        
        if not found:
            st.error(f"Data {metode} tidak ditemukan di seluruh database.")

# --- TAB LOG ---
if is_super_admin:
    with tabs[1]:
        st.subheader("📊 Statistik Database")
        if db_stats:
            cols = st.columns(len(db_stats) + 1)
            for i, (name, count) in enumerate(db_stats.items()):
                with cols[i]:
                    st.markdown(f'<div class="stat-card"><small>{name}</small><br><strong>{count:,}</strong></div>', unsafe_allow_html=True)
            with cols[-1]:
                st.markdown(f'<div class="stat-card" style="background-color: #0068c9; color: white;"><small>TOTAL DATA</small><br><strong>{total_all:,}</strong></div>', unsafe_allow_html=True)
        
        st.divider()
        if os.path.exists("log_aktivitas.csv"):
            log_df = pd.read_csv("log_aktivitas.csv")
            st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
            buf_log = io.BytesIO()
            with pd.ExcelWriter(buf_log) as w: log_df.to_excel(w, index=False)
            st.download_button("📥 Download Log Aktivitas (Excel)", buf_log.getvalue(), "Log_Aktivitas.xlsx", use_container_width=True)
