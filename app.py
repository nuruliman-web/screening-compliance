import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
import uuid # Untuk bikin key unik/random
from datetime import datetime, timedelta

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

# 2. ANTI-SUGGEST SCRIPT (Tingkat Lanjut)
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
    </style>
    <script>
        // Mencari semua input dan paksa matiin autocomplete & spellcheck
        const patchInputs = () => {
            const inputs = window.parent.document.getElementsByTagName('input');
            for (let i = 0; i < inputs.length; i++) {
                inputs[i].setAttribute('autocomplete', 'new-password'); // Trik 'new-password' lebih ampuh dari 'off'
                inputs[i].setAttribute('spellcheck', 'false');
            }
        };
        setInterval(patchInputs, 500); // Jalankan tiap 0.5 detik biar mantap
    </script>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGGING & DAFTAR LINK (Sama seperti sebelumnya)
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
    else: new_data.to_csv(log_file, mode='a', header=False, index=False)

# 4. TIMEOUT & LOGIN (Dgn Random Key)
if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())

if st.session_state.auth:
    if "last_activity" in st.session_state:
        if time.time() - st.session_state.last_activity > 300:
            st.session_state.auth = False
            st.rerun()
    st.session_state.last_activity = time.time()

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    # Pake key unik biar gak disuggest
    u_email = st.text_input("Email:", key=f"email_{st.session_state.form_key}").lower().strip()
    if st.button("Masuk"):
        if u_email in ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]:
            st.session_state.auth = True
            st.session_state.email_user = u_email
            log_activity(u_email, "Login")
            st.session_state.form_key = str(uuid.uuid4()) # Reset key setelah login
            st.rerun()
        else: st.error("Email tidak terdaftar!")
    st.stop()

# 5. HALAMAN UTAMA (Dgn Random Key di Search)
is_super_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"

col_user, col_banner = st.columns([1, 3])
with col_user:
    st.write(f"👤 **{st.session_state.email_user}**")
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

with col_banner:
    st.markdown('<div class="header-banner-clean">🔍 SCREENING DATA APU, PPT, DAN PPPSPM</div>', unsafe_allow_html=True)

st.divider()

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

tabs = st.tabs(["🔍 Screening", "📜 Log Admin"]) if is_super_admin else st.tabs(["🔍 Screening"])

with tabs[0]:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: metode = st.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: 
        # INI KUNCINYA: Key selalu berubah tiap sesi/login biar Suggestion mampus
        query = st.text_input("Cari Data:", placeholder=f"Masukkan {metode}...", key=f"query_{st.session_state.form_key}")
    with c3: threshold = st.slider("🎯 Akurasi (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    # LOGIKA PENCARIAN (Sama seperti sebelumnya)
    if query and db:
        valid = True
        if metode == "NIK" and len(query) != 16:
            st.warning("⚠️ NIK wajib 16 digit!")
            valid = False
            
        if valid:
            q_clean = query.strip().lower()
            found = False
            results = []
            for sn, df_data in db.items():
                def search_row(row):
                    max_s, cols_match = 0, []
                    check_cols = df_data.columns if metode in ["NIK", "Paspor"] else [c for c in df_data.columns if 'nama' in c.lower()]
                    for c in check_cols:
                        s = fuzz.token_sort_ratio(q_clean, str(row[c]).lower())
                        if s >= threshold:
                            cols_match.append(f"{c} ({s}%)")
                            if s > max_s: max_s = s
                    return pd.Series([max_s, "Match: " + ", ".join(cols_match)]) if max_s > 0 else pd.Series([0, "-"])

                temp = df_data.copy()
                temp[['_s', 'KET']] = temp.apply(search_row, axis=1)
                match = temp[temp['_s'] > 0].copy()
                if not match.empty:
                    found = True
                    match = match.sort_values('_s', ascending=False).drop(columns=['_s'])
                    results.append(match)
                    with st.expander(f"🚩 {sn}", expanded=True):
                        st.dataframe(match, hide_index=True, use_container_width=True)

            if found and is_super_admin:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: pd.concat(results).to_excel(w, index=False)
                st.download_button("📥 Download", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
            if not found: st.error("Data tidak ditemukan.")

# TAB LOG (Sama seperti sebelumnya)
if is_super_admin:
    with tabs[1]:
        # ... (kodingan log seperti sebelumnya)
        pass
