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

# 3. CSS CUSTOM (UPDATE DESAIN BLOCK)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    .user-info { color: black !important; font-weight: bold; margin-bottom: 5px; }
    
    /* Desain Banner Block */
    .header-banner { 
        background-color: #0068c9; 
        color: white; 
        padding: 20px; 
        border-radius: 10px; 
        font-size: 28px; 
        font-weight: bold; 
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    
    .block-container { padding-top: 1rem; }
    .stButton > button { width: auto; padding: 2px 15px; font-size: 12px; }
    .search-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #0068c9;
        margin-top: 20px;
    }
    .stat-card {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #e6e9ef;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI LOGGING
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(log_file):
        try: pd.read_csv(log_file)
        except: os.remove(log_file)
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

# 6. HEADER DENGAN BANNER BLOCK (TENGAH KE KANAN)
col_user, col_banner = st.columns([1, 3]) # Banner dapet porsi lebih gede (3/4 layar)

with col_user:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout")
        st.session_state.auth = False
        st.rerun()

with col_banner:
    # Desain nge-block besar
    st.markdown('<div class="header-banner">🔍 Screening Data APU, PPT, dan PPPSPM</div>', unsafe_allow_html=True)

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
        except:
            continue
    return all_data, stats, total

db, db_stats, total_all = load_all_databases()

# 8. TABS
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
tabs = st.tabs(["🔍 Screening Nasabah", "📜 Log Admin"]) if is_admin else st.tabs(["🔍 Screening Nasabah"])

# --- TAB SCREENING ---
with tabs[0]:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: metode = st.radio("Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
    with c2: query = st.text_input("Cari Data:", placeholder="Ketik nama atau NIK...")
    with c3: threshold = st.slider("🎯 Akurasi (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    if query and db:
        q_clean = " ".join(query.split()).lower()
        found = False
        results_to_export = []

        for sn, df_data in db.items():
            def find_match(row):
                matches_info = []
                max_score =
