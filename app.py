import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS CUSTOM
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

# 3. FUNGSI LOGGING (AUTO REPAIR)
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists(log_file):
        try: pd.read_csv(log_file)
        except: os.remove(log_file)
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
    else: new_data.to_csv(log_file, mode='a', header=False, index=False)

# 4. LOGIN SYSTEM
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

# 5. HEADER
col_h, _ = st.columns([1, 4])
with col_h:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        log_activity(st.session_state.email_user, "Logout")
        st.session_state.auth = False
        st.rerun()
st.divider()

# 6. LOAD DATABASE
@st.cache_data(ttl=60)
def load_db(path):
    if os.path.exists(path):
        try: return pd.read_excel(path, sheet_name=None)
        except: return None
    return None

db = load_db("database.xlsx")

# 7. TABS
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
can_download = st.session_state.email_user != "xxx@gmail.com"
tabs = st.tabs(["🔍 Screening Nasabah", "📜 Log Admin"]) if is_admin else st.tabs(["🔍 Screening Nasabah"])

# --- TAB SCREENING ---
with tabs[0]:
    if db:
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 2])
        with c1: metode = st.radio("Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
        with c2: query = st.text_input("Cari Data:", placeholder="Ketik di sini...")
        with c3: threshold = st.slider("🎯 Akurasi (%)", 50, 100, 85)
        st.markdown('</div>', unsafe_allow_html=True)

        if query:
            q_clean = " ".join(query.split()).lower()
            found = False
            results_to_export = []
            target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
            log_activity(st.session_state.email_user, f"Cari {metode}: {query}")

            for sn in target_sheets:
                if sn in db:
                    df = db[sn].copy()
                    
                    def find_match(row):
                        best_s = 0
                        col_target = "-"
                        # Fokus cari kolom yang ada kata 'nama'
                        check_cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                        
                        for c in check_cols:
                            val = " ".join(str(row[c]).split()).lower()
                            if metode == "Nama":
                                s = fuzz.token_sort_ratio(q_clean, val)
                                if s > best_s: best_s, col_target = s, c
                            else:
                                if q_clean == val: best_s, col_target = 100, c
                        
                        limit = threshold if metode == "Nama" else 100
                        if best_s >= limit:
                            return pd.Series([best_s, f"Match {best_s}% pada '{col_target}'"])
                        return pd.Series([0, "-"])

                    df[['_score', 'ALASAN MATCH']] = df.apply(find_match, axis=1)
                    match = df[df['_score'] > 0].copy()
                    
                    if not match.empty:
                        found = True
                        match = match.sort_values('_score', ascending=False)
                        
                        # TENTUKAN TARGET KOLOM NAMA UNTUK DIWARNAI (STABIL)
                        nama_cols = [c for c in match.columns if 'nama' in c.lower()]
                        
                        # Hapus skor internal agar tabel bersih
                        display_df = match.drop(columns=['_score'])
                        results_to_export.append(display_df)
                        
                        with st.expander(f"🚩 Database: {sn}", expanded=True):
                            # STYLING: Hanya warnai kolom yang namanya mengandung 'NAMA'
                            st.dataframe(
                                display_df.style.applymap(lambda x: 'color: red; font-weight: bold', subset=nama_cols),
                                hide_index=True, 
                                use_container_width=True
                            )

            if found and can_download:
                st.divider()
                final_df = pd.concat(results_to_export)
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
                st.download_button("📥 Download Hasil", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
            elif query and not found:
                st.warning("Data tidak ditemukan.")
    else: st.error("Database tidak ditemukan.")

# --- TAB LOG ---
if is_admin:
    with tabs[1]:
        if os.path.exists("log_aktivitas.csv"):
            st.dataframe(pd.read_csv("log_aktivitas.csv").iloc[::-1], use_container_width=True, hide_index=True)
