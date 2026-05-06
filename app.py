import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os, io, time, uuid
from datetime import datetime, timedelta

# 1. KONFIGURASI & SESSION STATE
st.set_page_config(page_title="Screening System Pro", layout="wide", initial_sidebar_state="collapsed")

if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())

# 2. CSS & JS ANTI-HISTORY (LEBIH GALAK)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; }
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
    .search-container { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border: 1px solid #dee2e6; margin-bottom: 20px; }
    </style>
    <script>
        setInterval(() => {
            const inputs = window.parent.document.getElementsByTagName('input');
            for (let i = 0; i < inputs.length; i++) {
                inputs[i].setAttribute('autocomplete', 'new-password');
                inputs[i].setAttribute('spellcheck', 'false');
            }
        }, 500);
    </script>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOAD DATA DENGAN SPINNER
@st.cache_data(ttl=300)
def load_all_databases(links):
    all_data, stats, total = {}, {}, 0
    for name, url in links.items():
        try:
            df = pd.read_csv(url)
            all_data[name], stats[name], total = df, len(df), total + len(df)
        except: continue
    return all_data, stats, total

# --- LOGIKA CORE ---
# (Fungsi log_activity tetap sama seperti punyamu)

# 4. HALAMAN LOGIN
if not st.session_state.auth:
    st.title("🔐 Screening System Login")
    u_email = st.text_input("Masukkan Email Kerja:", key=f"login_{st.session_state.form_key}").lower().strip()
    if st.button("Masuk"):
        if u_email in ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]:
            st.session_state.auth = True
            st.session_state.email_user = u_email
            st.session_state.last_activity = time.time()
            st.rerun()
        else: st.error("Akses Ditolak!")
    st.stop()

# 5. HALAMAN UTAMA
with st.spinner("Mengunduh Database Terbaru..."):
    db, db_stats, total_all = load_all_databases(LINK_SHEETS)

# Tombol Logout di Pojok Kanan Atas
c_user, c_logout = st.columns([8, 1])
c_user.write(f"Logged in as: **{st.session_state.email_user}**")
if c_logout.button("Logout"):
    st.session_state.auth = False
    st.rerun()

st.title("🔍 Screening System")

tabs = st.tabs(["🔎 Pencarian", "📊 Dashboard Admin"]) if st.session_state.email_user == "imanmuhamad9@gmail.com" else st.tabs(["🔎 Pencarian"])

with tabs[0]:
    with st.container():
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1: metode = st.radio("Cari Berdasarkan:", ["Nama", "NIK", "Paspor"], horizontal=True)
        with col2: query = st.text_input("Ketik Kata Kunci:", key=f"q_{st.session_state.form_key}")
        with col3: threshold = st.slider("Minimal Akurasi", 50, 100, 85)
        st.markdown('</div>', unsafe_allow_html=True)

    if query:
        # Validasi NIK
        if metode == "NIK" and len(query) != 16:
            st.error("❌ NIK harus tepat 16 digit!")
        else:
            found = False
            for sn, df_data in db.items():
                # Logika pencarian yang sudah kamu buat (sangat bagus)
                # ... (Masukkan fungsi find_match kamu di sini)
                
                # Tambahkan fitur: Highlight sel yang mengandung query
                def highlight_match(s):
                    return ['background-color: #fff3cd' if query.lower() in str(x).lower() else '' for x in s]

                # Menampilkan hasil dengan warna
                # st.dataframe(display_df.style.apply(highlight_match))
