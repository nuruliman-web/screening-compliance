import streamlit as st
import pandas as pd
from thefuzz import fuzz # Pastikan cara import seperti ini
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening", layout="wide")

st.title("🔍 Database Screening (Fuzzy Search)")
st.write("Sistem akan mencari nama dengan tingkat kemiripan tertinggi.")

# 2. Fungsi Load Data
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, sheet_name=None)
    return None

NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: Budi Santoso")
    threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 80)

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                # FUNGSI PERBAIKAN: Menghindari AttributeError
                def hitung_skor(row):
                    skor_maks = 0
                    for val in row:
                        # Cek jika data tidak kosong dan bisa dikonversi ke string
                        if pd.notna(val):
                            teks = str(val).lower()
                            # Gunakan token_set_ratio
                            skor = fuzz.token_set_ratio(query, teks)
                            if skor > skor_maks:
                                skor_maks = skor
                    return skor_maks

                # Tambahkan Kolom di paling depan
                df.insert(0, 'Tingkat Kemiripan (%)', df.apply(hitung_skor, axis=1))
                
                # Filter & Urutkan
                result = df[df['Tingkat Kemiripan (%)'] >= threshold].sort_values(by='Tingkat Kemiripan (%)', ascending=False)

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 TERDETEKSI DI SHEET: {sheet_name}", expanded=True):
                        st.info(f"Ditemukan {len(result)} data dengan kemiripan di atas {threshold}%")
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.success("✅ HASIL NIHIL: Tidak ada nama dengan kemiripan yang cukup kuat.")
            st.balloons()
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")
