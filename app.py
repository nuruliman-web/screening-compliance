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
    initial_sidebar_state="collapsed"
)

# 2. CSS SAKTI: HILANGKAN HEADER, MENU KANAN, & FOOTER
st.markdown("""
    <style>
    /* Hilangkan Header atas total (termasuk tombol sidebar & menu 3 titik) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    
    /* Hilangkan Footer */
    footer {visibility: hidden;}

    /* Styling Teks User agar Hitam & Anti-Klik */
    .user-info {
        color: black !important;
        font-weight: bold;
        pointer-events: none;
        cursor: default;
    }
    
    /* Atur jarak konten agar tidak terlalu mepet ke atas */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

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
    if (time.time() - st.session_state.last_activity) > TIMEOUT_SECONDS:
        log_activity(st.session_state.email_user, "Auto-Logout (Timeout)")
        st.session_state.auth = False
        st.rerun()

st.session_state.last_activity = time.time()

# 5. LOGIN SYSTEM
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
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

# Definisi Role & Izin
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
can_download = st.session_state.email_user != "xxx@gmail.com"

# 6. HEADER HALAMAN (GANTINYA SIDEBAR)
# Kita buat baris atas untuk User Info, Akurasi, dan Logout
col_user, col_acc, col_btn = st.columns([2, 2, 1])

with col_user:
    st.markdown(f'<p class="user-info">👤 User Login: {st.session_state.email_user}</p>', unsafe_allow_html=True)

with col_acc:
    # Slider Akurasi pindah ke sini
    threshold = st.slider("🎯 Akurasi Nama (%)", 50, 100, 85)

with col_btn:
    if st.button("🚪 Logout", use_container_width=True):
        log_activity(st.session_state.email_user, "Manual Logout")
        st.session_state.auth = False
        st.rerun()

st.divider()

# 7. MENU UTAMA (TABS)
if is_admin:
    tab_screening, tab_log = st.tabs(["🔍 Screening Nasabah", "📜 Log Aktivitas Admin"])
else:
    tab_screening, = st.tabs(["🔍 Screening Nasabah"])
    tab_log = None

# --- TAB 1: SCREENING ---
with tab_screening:
    st.subheader("🔍 Screening APU, PPT, dan PPPSPM")
    
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
        c1, c2 = st.columns([1, 3])
        with c1:
            metode = st.radio("Pilih Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
        with c2:
            query = st.text_input("Cari Data Nasabah:", placeholder="Masukkan Nama atau NIK...")

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

            if found:
                if can_download:
                    st.divider()
                    final_df = pd.concat(results)
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
                    st.download_button("📥 Download Hasil Screening (Excel)", buf.getvalue(), "Hasil_Screening.xlsx", use_container_width=True)
            elif query:
                st.warning("Data tidak ditemukan.")
    else:
        st.error("File 'database.xlsx' tidak ditemukan.")

# --- TAB 2: LOG AKTIVITAS (Admin Only) ---
if tab_log and is_admin:
    with tab_log:
        st.subheader("📜 Audit Log Aktivitas")
        if os.path.exists("log_aktivitas.csv"):
            df_log = pd.read_csv("log_aktivitas.csv").iloc[::-1]
            csv_buffer = io.StringIO()
            df_log.to_csv(csv_buffer, index=False)
            st.download_button("📥 Download Seluruh Log (.csv)", csv_buffer.getvalue(), "Log_Aktivitas.csv", mime="text/csv")
            st.divider()
            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada log yang tercatat.")
