import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Screening System", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS SAKTI: HAPUS MENU KANAN, TAPI SIDEBAR KIRI TETAP ADA
st.markdown("""
    <style>
    /* 1. Sembunyikan tombol menu tiga titik di pojok kanan atas */
    #MainMenu {visibility: hidden;}
    
    /* 2. Sembunyikan header Streamlit secara keseluruhan agar lebih bersih */
    header {visibility: hidden;}
    
    /* 3. Kembalikan fungsionalitas tombol sidebar (panah) agar tetap muncul walau header di-hide */
    .st-emotion-cache-zq5wmm {
        visibility: visible !important;
        top: 10px !important;
    }
    
    /* 4. Anti-Klik & Warna Hitam untuk Email di Sidebar */
    .stSidebar a {
        color: black !important;
        text-decoration: none !important;
        pointer-events: none !important;
        cursor: default !important;
    }
    .user-box {
        color: black !important;
        line-height: 1.2;
        pointer-events: none !important;
        cursor: default !important;
    }
    
    /* 5. Hilangkan footer "Made with Streamlit" */
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LANJUTAN KODE (Sama seperti sebelumnya) ---

# 3. FUNGSI LOGGING
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

# 4. SETTING TIMEOUT (10 Menit)
TIMEOUT_SECONDS = 600 
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

if st.session_state.get("auth"):
    current_time = time.time()
    if (current_time - st.session_state.last_activity) > TIMEOUT_SECONDS:
        log_activity(st.session_state.email_user, "Auto-Logout (Timeout)")
        st.session_state.auth = False
        st.rerun()

st.session_state.last_activity = time.time()

# 5. LOGIN SYSTEM
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    user_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            st.session_state.last_activity = time.time()
            log_activity(user_email, "Login")
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# Role Logic
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
can_download = st.session_state.email_user != "xxx@gmail.com"

# 6. SIDEBAR
with st.sidebar:
    st.markdown(f'<div class="user-box"><b>👤User Login:</b><br>{st.session_state.email_user}</div>', unsafe_allow_html=True)
    st.divider()
    st.write("🎯 **Akurasi Nama (%)**")
    threshold = st.slider("Akurasi", 50, 100, 85, label_visibility="collapsed")
    st.markdown('<div style="height: 60vh;"></div>', unsafe_allow_html=True)
    st.divider()
    if st.button("🚪 Keluar / Logout", use_container_width=True):
        log_activity(st.session_state.email_user, "Manual Logout")
        st.session_state.auth = False
        st.rerun()

# 7. MENU UTAMA (TABS)
if is_admin:
    tab_screening, tab_log = st.tabs(["🔍 Screening Nasabah", "📜 Log Aktivitas Admin"])
else:
    tab_screening, = st.tabs(["🔍 Screening Nasabah"])
    tab_log = None

with tab_screening:
    st.title("🔍 Screening APU, PPT, dan PPPSPM")
    @st.cache_data
    def load_db(path):
        if os.path.exists(path):
            try:
                data = pd.read_excel(path, sheet_name=None)
                for s in data:
                    for c in data[s].columns:
                        if pd.api.types.is_datetime64_any_dtype(data[s][c]):
                            data[s][c] = data[s][c].dt.strftime('%Y-%m-%d')
                return data
            except: return None
        return None

    db = load_db("database.xlsx")
    if db:
        metode = st.radio("Pilih Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
        query = st.text_input("Cari Data:", placeholder="Masukkan Nama atau NIK...")
        if query:
            q_clean = " ".join(query.split()).lower()
            found = False
            results = []
            target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
            for sn in target_sheets:
                if sn in db:
                    df = db[sn].copy()
                    def score_row(row):
                        top = 0
                        cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                        for c in cols:
                            if pd.notna(row[c]):
                                val = " ".join(str(row[c]).split()).lower()
                                if metode == "Nama":
                                    s = fuzz.token_sort_ratio(q_clean, val)
                                    top = max(top, s)
                                else:
                                    if q_clean == val: top = 100
                        return top
                    df.insert(0, 'SKOR', df.apply(score_row, axis=1))
                    limit = threshold if metode == "Nama" else 100
                    match = df[df['SKOR'] >= limit].copy()
                    if not match.empty:
                        found = True
                        match = match.sort_values('SKOR', ascending=False)
                        results.append(match)
                        with st.expander(f"🚩 Database: {sn}", expanded=True):
                            st.dataframe(match, hide_index=True, use_container_width=True)
            if found and can_download:
                st.divider()
                final_df = pd.concat(results)
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
                st.download_button("📥 Download Hasil Screening (Excel)", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
            elif query and not found:
                st.warning("Data tidak ditemukan.")
    else:
        st.error("File 'database.xlsx' tidak ditemukan.")

if tab_log and is_admin:
    with tab_log:
        st.title("Audit Log Aktivitas")
        if os.path.exists("log_aktivitas.csv"):
            df_log = pd.read_csv("log_aktivitas.csv").iloc[::-1]
            csv_buffer = io.StringIO()
            df_log.to_csv(csv_buffer, index=False)
            st.download_button("📥 Download Log (.csv)", csv_buffer.getvalue(), "Log.csv", mime="text/csv")
            st.divider()
            st.dataframe(df_log, use_container_width=True, hide_index=True)
