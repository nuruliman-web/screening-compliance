import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening Pro", layout="wide")

st.title("🔍 Database Screening (Exact & Fuzzy)")
st.write("Sistem pencarian presisi dengan identifikasi lokasi kolom.")

# 2. Fungsi Load Data
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, sheet_name=None)
    return None

NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: Iman")
    threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 90)

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def proses_baris(row):
                    skor_tertinggi = 0
                    kolom_ditemukan = "-"
                    
                    for col_name, val in row.items():
                        if pd.notna(val):
                            teks_data = str(val).strip().lower()
                            
                            # LOGIKA SKOR:
                            # 1. Cek Exact Match dulu
                            if query == teks_data:
                                skor = 100
                            else:
                                # 2. Jika tidak exact, gunakan token_sort_ratio
                                # Ini akan memberikan skor < 100 jika ada kata tambahan (seperti 'Nurul')
                                skor = fuzz.token_sort_ratio(query, teks_data)
                            
                            if skor > skor_tertinggi:
                                skor_tertinggi = skor
                                kolom_ditemukan = col_name
                                
                    return pd.Series([skor_tertinggi, kolom_ditemukan])

                # Tambahkan dua kolom info di depan
                df[['Skor (%)', 'Terdeteksi di Kolom']] = df.apply(proses_baris, axis=1)
                
                # Filter berdasarkan threshold
                result = df[df['Skor (%)'] >= threshold].sort_values(by='Skor (%)', ascending=False)

                # Pindahkan kolom info ke paling kiri agar mudah dilihat
                cols = ['Skor (%)', 'Terdeteksi di Kolom'] + [c for c in df.columns if c not in ['Skor (%)', 'Terdeteksi di Kolom']]
                result = result[cols]

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 SHEET: {sheet_name}", expanded=True):
                        st.success(f"Ditemukan {len(result)} kecocokan.")
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.warning(f"HASIL NIHIL: Tidak ada nama yang cocok dengan ambang batas {threshold}%.")
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")
