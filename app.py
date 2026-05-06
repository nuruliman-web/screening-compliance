import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Screening System Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. CSS CUSTOM: HAPUS HEADER, WARNAI TABEL, & UKURAN ELEMEN
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    .user-info { color: black !important; font-weight: bold; margin-bottom: 0px; }
    .block-container { padding-top: 1rem; }
    .stButton > button { width: auto !important; height: auto !important; padding: 2px 15px !important; font-size: 12px !important; }
    .search-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0068c9;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGGING (Dengan Auto-Reset jika file error)
def log_activity(email, action, detail="-"):
    log_file = "log_aktivitas.csv"
    
    # Logika Auto-Fix: Hapus file jika format pembatas (separator) salah
    if os.path.exists(log_file):
        try:
            pd.read_csv(log_file, sep=';', nrows=1)
        except:
            os.remove(log_file)
            
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    detail_clean = str(detail).replace(";", "|") 
    new_data = pd.DataFrame([[now, email, action, detail_clean]], columns=["Waktu", "User", "Aktivitas", "Detail"])
    
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False, sep=';')
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False, sep=';')

# 4. LOGIN & TIMEOUT SYSTEM
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    user_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            log_activity(user_email, "Login", "Berhasil masuk")
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 5. HEADER (User Info & Logout)
col_header, _ = st.columns([1, 4])
with col_header:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout", "Manual logout")
        st.session_state.auth = False
        st.rerun()
st.divider()

# 6. DATABASE LOADER (Auto-Refresh)
@st.cache_data(ttl=60)
def load_db(path):
    if os.path.exists(path):
        try:
            data = pd.read_excel(path, sheet_name=None)
            stats = {s: len(data[s]) for s in data}
            for s in data:
                for c in data[s].columns:
                    if pd.api.types.is_datetime64_any_dtype(data[s][c]):
                        data[s][c] = data[s][c].dt.strftime('%Y-%m-%d')
            return data, stats
        except: return None, None
    return None, None

db, db_stats = load_db("database.xlsx")

# 7. TABS PERMISSIONS
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
        # KOTAK PENCARIAN TERPADU
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col_metode, col_cari, col_slide = st.columns([1, 2, 2])
        with col_metode:
            metode = st.radio("Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
        with col_cari:
            query = st.text_input("Cari Data:", placeholder="Masukkan Nama atau NIK...")
        with col_slide:
            threshold = st.slider("🎯 Akurasi Pencarian (%)", 50, 100, 85)
        st.markdown('</div>', unsafe_allow_html=True)

        if query:
            q_clean = " ".join(query.split()).lower()
            found = False
            results = []
            target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
            log_activity(st.session_state.email_user, "Pencarian", f"Query: {query} | Acc: {threshold}%")

            for sn in target_sheets:
                if sn in db:
                    df = db[sn].copy()
                    
                    def check_row(row):
                        best_s = 0
                        reason = "-"
                        cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                        for c in cols:
                            val = " ".join(str(row[c]).split()).lower()
                            if metode == "Nama":
                                s = fuzz.token_sort_ratio(q_clean, val)
                                if s > best_s:
                                    best_s = s
                                    reason = f"Kemiripan Nama di kolom '{c}'"
                            else:
                                if q_clean == val:
                                    best_s = 100
                                    reason = f"NIK Cocok di kolom '{c}'"
                        return pd.Series([best_s, reason])

                    df[['SKOR', 'ALASAN MATCH']] = df.apply(check_row, axis=1)
                    limit = threshold if metode == "Nama" else 100
                    match = df[df['SKOR'] >= limit].copy()
                    
                    if not match.empty:
                        found = True
                        match = match.sort_values('SKOR', ascending=False)
                        results.append(match)
                        
                        with st.expander(f"🚩 Database: {sn} ({len(match)} ditemukan)", expanded=True):
                            # HIGHLIGHT: Memberi warna kuning pada baris hasil
                            styled_df = match.style.background_gradient(subset=['SKOR'], cmap='YlGn') \
                                                   .applymap(lambda x: 'background-color: #ffffcc', subset=['ALASAN MATCH'])
                            st.dataframe(styled_df, hide_index=True, use_container_width=True)

            if found and can_download:
                st.divider()
                final_df = pd.concat(results)
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
                st.download_button("📥 Download Hasil Screening", buf.getvalue(), f"Hasil_{query}.xlsx", use_container_width=True)
            elif query and not found:
                st.warning(f"Data '{query}' tidak ditemukan.")
    else:
        st.error("Database 'database.xlsx' tidak ditemukan.")

# --- TAB 2: LOG & STATISTIK (Admin Only) ---
if tab_log and is_admin:
    with tab_log:
        cl, cr = st.columns([1, 2])
        with cl:
            st.subheader("📊 Statistik Database")
            if db_stats:
                st.table(pd.DataFrame(list(db_stats.items()), columns=['Nama Sheet', 'Total Data']))
                st.metric("Total Seluruh Data", sum(db_stats.values()))
        with cr:
            st.subheader("📜 Audit Trail Detail")
            if os.path.exists("log_aktivitas.csv"):
                try:
                    df_l = pd.read_csv("log_aktivitas.csv", sep=';').iloc[::-1]
                    st.dataframe(df_l, use_container_width=True, hide_index=True)
                except:
                    st.error("Gagal membaca log aktivitas.")
