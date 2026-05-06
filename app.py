import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# --- PERBAIKAN CSS: Header dimunculkan sedikit agar tombol Sidebar tidak hilang ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Header tidak di-hidden total agar tombol '>' tetap bisa diklik */
    header {height: 40px; background-color: transparent;}
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEM LOGIN
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login Sistem")
    email = st.text_input("Masukkan Email Anda:").lower().strip()
    if st.button("Masuk"):
        if email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 3. SIDEBAR (Sekarang aman ditutup-buka)
with st.sidebar:
    st.title("⚙️ Kontrol Panel")
    st.write(f"Login: {imanmuhamad9@gmail.com if 'auth' in st.session_state else ''}")
    st.divider()
    threshold = st.slider("Ambang Kemiripan (%)", 50, 100, 85)
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# 4. APLIKASI UTAMA
st.title("🔍 Screening APU, PPT, dan PPPSPM")

@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            data = pd.read_excel(file_path, sheet_name=None)
            for sheet in data:
                for col in data[sheet].columns:
                    if pd.api.types.is_datetime64_any_dtype(data[sheet][col]):
                        data[sheet][col] = data[sheet][col].dt.strftime('%Y-%m-%d')
            return data
        except:
            return None
    return None

db_sheets = load_data("database.xlsx")

if db_sheets:
    metode = st.radio("Pilih Metode:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    query = st.text_input("Input Data Nasabah:", placeholder="Ketik di sini...")

    if query:
        q_clean = " ".join(query.split()).lower()
        found = False
        all_res = []
        
        # Daftar sheet yang mau di-scan
        target = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sn in target:
            if sn in db_sheets:
                df = db_sheets[sn].copy()
                
                def check_row(r):
                    score = 0
                    # Scan kolom nama saja jika metode Nama, scan semua jika NIK
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

                df.insert(0, 'SKOR_KEMIRIPAN', df.apply(check_row, axis=1))
                res = df[df['SKOR_KEMIRIPAN'] > 0].copy()
                
                if not res.empty:
                    found = True
                    res = res.sort_values('SKOR_KEMIRIPAN', ascending=False)
                    all_res.append(res)
                    with st.expander(f"🚩 Database: {sn} (Ditemukan {len(res)} data)", expanded=True):
                        st.dataframe(res, hide_index=True)

        if found:
            st.divider()
            final = pd.concat(all_res)
            out = io.BytesIO()
            with pd.ExcelWriter(out) as w: final.to_excel(w, index=False)
            st.download_button("📥 Download Hasil Lengkap", out.getvalue(), "Hasil_Screening.xlsx")
        elif query:
            st.warning(f"Data '{query}' tidak ditemukan.")
else:
    st.error("Pastikan file 'database.xlsx' sudah ada.")
