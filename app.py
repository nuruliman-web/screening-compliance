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

# 2. FUNGSI LOGGING (Mencatat Login/Logout)
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

# 3. SETTING TIMEOUT (Contoh: 10 Menit)
TIMEOUT_SECONDS = 600 # 10 menit x 60 detik

if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

# Cek apakah sudah timeout
if st.session_state.get("auth"):
    current_time = time.time()
    elapsed_time = current_time - st.session_state.last_activity
    
    if elapsed_time > TIMEOUT_SECONDS:
        log_activity(st.session_state.email_user, "Auto-Logout (Timeout)")
        st.session_state.auth = False
        st.session_state.last_activity = time.time()
        st.rerun()

# Update waktu setiap ada interaksi
st.session_state.last_activity = time.time()

# 4. CSS ANTI-BIRU & STYLE
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stSidebar a { color: black !important; text-decoration: none !important; pointer-events: none !important; }
    .user-box { color: black !important; line-height: 1.2; pointer-events: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. LOGIN SYSTEM
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    user_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            st.session_state.last_activity = time.time() # Reset timer
            log_activity(user_email, "Login") # CATAT LOGIN
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 6. SIDEBAR
with st.sidebar:
    st.markdown(f'''<div class="user-box"><b>👤User Login:</b><br>{st.session_state.email_user}</div>''', unsafe_allow_html=True)
    st.divider()
    st.write("🎯 **Akurasi Nama (%)**")
    threshold = st.slider("Akurasi", 50, 100, 85, label_visibility="collapsed")
    
    # Tombol Lihat Log (Hanya untuk admin tertentu jika mau)
    if st.session_state.email_user == "imanmuhamad9@gmail.com":
        if st.checkbox("Lihat Log Aktivitas"):
            if os.path.exists("log_aktivitas.csv"):
                st.dataframe(pd.read_csv("log_aktivitas.csv").tail(10))
    
    st.markdown('<div style="height: 50vh;"></div>', unsafe_allow_html=True)
    st.divider()
    if st.button("🚪 Keluar / Logout", use_container_width=True):
        log_activity(st.session_state.email_user, "Manual Logout") # CATAT LOGOUT
        st.session_state.auth = False
        st.rerun()

# 7. APLIKASI UTAMA (Sama seperti kodemu sebelumnya)
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
            st.divider()
            final_df = pd.concat(results)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
            st.download_button("📥 Download Hasil (Excel)", buf.getvalue(), "Hasil_Screening.xlsx", use_container_width=True)
        elif query:
            st.warning("Data tidak ditemukan.")
else:
    st.error("File 'database.xlsx' tidak ditemukan.")
