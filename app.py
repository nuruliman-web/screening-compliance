import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# --- SEMBUNYIKAN MENU ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEM LOGIN SEDERHANA
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    email = st.text_input("Masukkan Email Anda:").lower().strip()
    if st.button("Masuk"):
        if email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 3. TOMBOL LOGOUT & PARAMETER DI SIDEBAR
st.sidebar.title("Kontrol Panel")
threshold = st.sidebar.slider("Ambang Kemiripan (%)", 50, 100, 85)
if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# 4. APLIKASI UTAMA
st.title("🔍 Screening APU, PPT, dan PPPSPM")

@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        data = pd.read_excel(file_path, sheet_name=None)
        for sheet in data:
            for col in data[sheet].columns:
                if pd.api.types.is_datetime64_any_dtype(data[sheet][col]):
                    data[sheet][col] = data[sheet][col].dt.strftime('%Y-%m-%d')
        return data
    return None

db_sheets = load_data("database.xlsx")

if db_sheets:
    metode = st.radio("Pilih Metode:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    query = st.text_input("Input Data Nasabah:")

    if query:
        q_clean = " ".join(query.split()).lower()
        found = False
        all_res = []
        
        target = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        for sn in target:
            if sn in db_sheets:
                df = db_sheets[sn].copy()
                
                def check(r):
                    score = 0
                    cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                    for c in cols:
                        if pd.notna(r[c]):
                            v = " ".join(str(r[c]).split()).lower()
                            if metode == "Nama":
                                s = fuzz.token_sort_ratio(q_clean, v)
                                if s >= threshold: score = max(score, s)
                            else:
                                if q_clean == v: score = 100
                    return score

                df['SKOR'] = df.apply(check, axis=1)
                res = df[df['SKOR'] > 0].copy()
                
                if not res.empty:
                    found = True
                    all_res.append(res)
                    with st.expander(f"🚩 Database: {sn}"):
                        st.dataframe(res.sort_values('SKOR', ascending=False), hide_index=True)

        if found:
            final = pd.concat(all_res)
            out = io.BytesIO()
            with pd.ExcelWriter(out) as w: final.to_excel(w, index=False)
            st.download_button("📥 Download Hasil", out.getvalue(), "Hasil.xlsx")
        elif query:
            st.warning("Data tidak ditemukan.")
else:
    st.error("File 'database.xlsx' tidak ditemukan.")
