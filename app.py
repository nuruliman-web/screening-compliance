import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# --- KODE CSS (Sembunyikan Menu, Header, Footer, & Profil) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stSidebarUserContent"] {display: none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SISTEM LOGIN EMAIL
# ---------------------------------------------------------
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Akses Terbatas")
    st.write("Silakan masukkan email terdaftar untuk mengakses sistem.")
    
    email_input = st.text_input("Masukkan Email Anda:").lower().strip()
    
    if st.button("Masuk"):
        if email_input in ALLOWED_EMAILS:
            st.session_state.authenticated = True
            st.session_state.user_email = email_input
            st.rerun()
        else:
            st.error("❌ Email tidak terdaftar.")
    st.stop()

# ---------------------------------------------------------
# 3. SIDEBAR (PENGATURAN & LOGOUT)
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Pengaturan")
    st.write(f"User: **{st.session_state.user_email}**")
    
    # --- SLIDER PARAMETER (Ditaruh di sini supaya selalu muncul) ---
    st.subheader("Parameter Screening")
    threshold = st.slider("Ambang Kemiripan Nama (%)", 50, 100, 85, help="Semakin tinggi persen, semakin harus mirip persis.")
    
    st.divider()
    
    # --- TOMBOL LOGOUT ---
    if st.button("🚪 Keluar / Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# ---------------------------------------------------------
# 4. APLIKASI UTAMA
# ---------------------------------------------------------
st.title("🔍 Screening APU, PPT, dan PPPSPM")

# FUNGSI LOAD DATA
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
            st.error(f"Gagal membaca database: {e}")
            return None
    return None

NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    # PILIHAN METODE
    metode = st.radio("Pilih Metode Pencarian:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    
    if metode == "Nama":
        search_query = st.text_input("Masukkan Nama:", placeholder="Contoh: AGUNG GUNARDI")
    else:
        search_query = st.text_input("Masukkan NIK/Paspor:", placeholder="Contoh: D 000974")

    # LOGIKA PENCARIAN
    if search_query:
        query_clean = " ".join(search_query.split()).lower()
        found_any_global = False
        all_results_for_download = [] 
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def check_row_match(row_db):
                    found_cols = []
                    max_score_in_row = 0
                    
                    if metode == "Nama":
                        cols_to_scan = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        cols_to_scan = df.columns

                    for col_name in cols_to_scan:
                        val = row_db[col_name]
                        if pd.notna(val):
                            teks_db = " ".join(str(val).split()).lower()
                            if metode == "Nama":
                                score = fuzz.token_sort_ratio(query_clean, teks_db)
                                if score >= threshold:
                                    if score > max_score_in_row: max_score_in_row = score
                                    found_cols.append(f"{col_name} ({score}%)")
                            else:
                                if query_clean == teks_db:
                                    max_score_in_row = 100
                                    found_cols.append(f"{col_name} (100%)")
                    
                    return max_score_in_row, ", ".join(found_cols)

                res_match = df.apply(lambda r: pd.Series(check_row_match(r)), axis=1)
                
                # Masukkan kolom SKOR & STATUS di depan hasil
                df.insert(0, 'SKOR_KEMIRIPAN', res_match[0])
                df.insert(1, 'STATUS_MATCH', res_match[1])
                
                limit = threshold if metode == "Nama" else 100
                matches = df[df['SKOR_KEMIRIPAN'] >= limit].copy()
                
                if not matches.empty:
                    found_any_global = True
                    matches = matches.sort_values(by='SKOR_KEMIRIPAN', ascending=False)
                    all_results_for_download.append(matches)
                    
                    with st.expander(f"🚩 HASIL {sheet_name}: Ditemukan {len(matches)} data", expanded=True):
                        st.dataframe(matches, use_container_width=True, hide_index=True)

        # FITUR DOWNLOAD
        if found_any_global:
            st.divider()
            final_report = pd.concat(all_results_for_download, ignore_index=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_report.to_excel(writer, index=False, sheet_name='Hasil_Screening')
            
            st.download_button(
                label="📥 Download Hasil Screening (Excel)",
                data=output.getvalue(),
                file_name=f"Hasil_{search_query}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        if not found_any_global:
            st.warning(f"HASIL NIHIL: '{search_query}' tidak ditemukan.")
else:
    st.error(f"Database 'database.xlsx' tidak ditemukan.")
