import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# --- CSS (Hanya sembunyikan profil, sidebar tetap wajib ada) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebarUserContent"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INISIALISASI SESSION STATE
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

# ---------------------------------------------------------
# 3. SIDEBAR (DIBUAT DULUAN SUPAYA TIDAK HILANG)
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ PENGATURAN")
    if st.session_state.authenticated:
        st.info(f"User: {st.session_state.user_email}")
        
        st.divider()
        # SLIDER PARAMETER
        threshold = st.slider("Ambang Kemiripan (%)", 50, 100, 85)
        st.caption("Atur sensitivitas nama di sini.")
        
        st.divider()
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    else:
        st.warning("Silakan Login")
        # Definisikan threshold default agar tidak error saat login belum dilakukan
        threshold = 85 

# ---------------------------------------------------------
# 4. LOGIKA HALAMAN (LOGIN VS KONTEN)
# ---------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🔐 Akses Terbatas")
    email_input = st.text_input("Masukkan Email:").lower().strip()
    if st.button("Masuk"):
        if email_input in ALLOWED_EMAILS:
            st.session_state.authenticated = True
            st.session_state.user_email = email_input
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# --- HALAMAN UTAMA SETELAH LOGIN ---
st.title("🔍 Screening APU, PPT, dan PPPSPM")

@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        try:
            data = pd.read_excel(file_path, sheet_name=None)
            for sheet in data:
                for col in data[sheet].columns:
                    if pd.api.types.is_datetime64_any_dtype(data[sheet][col]):
                        data[sheet][col] = data[sheet][col].dt.strftime('%Y-%m-%d')
            return data
        except Exception as e:
            st.error(f"Gagal baca DB: {e}")
            return None
    return None

NAMA_FILE_DATABASE = "database.xlsx"
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    metode = st.radio("Metode:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    search_query = st.text_input("Masukkan Data:")

    if search_query:
        query_clean = " ".join(search_query.split()).lower()
        found_any_global = False
        all_results = []
        
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def check_row(row):
                    m_score = 0
                    m_cols = []
                    cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                    for c in cols:
                        if pd.notna(row[c]):
                            db_val = " ".join(str(row[c]).split()).lower()
                            if metode == "Nama":
                                s = fuzz.token_sort_ratio(query_clean, db_val)
                                if s >= threshold:
                                    if s > m_score: m_score = s
                                    m_cols.append(f"{c} ({s}%)")
                            else:
                                if query_clean == db_val:
                                    m_score = 100
                                    m_cols.append(f"{c} (MATCH)")
                    return m_score, ", ".join(m_cols)

                res = df.apply(lambda r: pd.Series(check_row(r)), axis=1)
                df.insert(0, 'SKOR', res[0])
                df.insert(1, 'LOKASI', res[1])
                
                limit = threshold if metode == "Nama" else 100
                matches = df[df['SKOR'] >= limit].copy()
                
                if not matches.empty:
                    found_any_global = True
                    matches = matches.sort_values(by='SKOR', ascending=False)
                    all_results.append(matches)
                    with st.expander(f"🚩 {sheet_name}"):
                        st.dataframe(matches, hide_index=True)

        if found_any_global:
            final_df = pd.concat(all_results)
            output = io.BytesIO()
            with pd.ExcelWriter(output) as w: final_df.to_excel(w, index=False)
            st.download_button("📥 Download Excel", output.getvalue(), "Hasil.xlsx")
        elif search_query:
            st.warning("Data tidak ditemukan.")
else:
    st.error("Database tidak ditemukan.")
