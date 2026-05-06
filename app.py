import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Screening System", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS ANTI-BIRU, ANTI-KLIK & WARNA HITAM
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Memaksa semua link/email di sidebar jadi hitam dan tidak bisa diklik */
    .stSidebar a {
        color: black !important;
        text-decoration: none !important;
        pointer-events: none !important;
        cursor: default !important;
    }
    .user-box {
        color: black !important;
        line-height: 1.2; /* Mengunci jarak antar baris supaya rapat */
        pointer-events: none !important;
        cursor: default !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN SYSTEM
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
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 4. SIDEBAR (LOGOUT DI DASAR BANGET & EMAIL HITAM RAPAT)
with st.sidebar:
    # Menggunakan satu blok HTML agar "User Login" dan "Email" rapat
    st.markdown(f'''
        <div class="user-box">
            <b>User Login:</b><br>
            {st.session_state.email_user}
        </div>
    ''', unsafe_allow_html=True)
    
    st.divider()
    
    st.write("🎯 **Akurasi Nama (%)**")
    threshold = st.slider("Akurasi", 50, 100, 85, label_visibility="collapsed")
    
    # Spacer dinamis untuk dorong logout ke dasar
    st.markdown('<div style="height: 65vh;"></div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# 5. APLIKASI UTAMA
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
