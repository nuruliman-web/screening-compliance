import streamlit as st
import pandas as pd
from thefuzz import fuzz
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
    # 3. Input Pencarian
    search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: Budi Santoso")
    
    # Slider untuk mengatur sensitivitas (opsional)
    threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 80)

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                # Fungsi untuk menghitung skor kemiripan tertinggi dalam satu baris
                def hitung_skor(row):
                    # Ambil semua isi sel dalam baris sebagai string
                    teks_baris = row.astype(str).tolist()
                    # Cari skor tertinggi di antara semua kolom nama
                    skor_maks = 0
                    for teks in teks_baris:
                        # Menggunakan token_set_ratio agar lebih akurat untuk nama yang terbalik
                        skor = fuzz.token_set_ratio(query, teks.lower())
                        if skor > skor_maks:
                            skor_maks = skor
                    return skor_maks

                # Tambahkan Kolom Tingkat Kemiripan di paling depan
                df.insert(0, 'Tingkat Kemiripan (%)', df.apply(hitung_skor, axis=1))
                
                # Filter data berdasarkan ambang batas (threshold)
                result = df[df['Tingkat Kemiripan (%)'] >= threshold].sort_values(by='Tingkat Kemiripan (%)', ascending=False)

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 TERDETEKSI DI SHEET: {sheet_name}", expanded=True):
                        st.info(f"Ditemukan {len(result)} data dengan kemiripan di atas {threshold}%")
                        # Menampilkan tabel
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.success("✅ HASIL NIHIL: Tidak ada nama dengan kemiripan yang cukup kuat.")
            st.balloons()
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")

st.sidebar.markdown("---")
st.sidebar.write("**Tips:**")
st.sidebar.write("Jika hasil terlalu banyak, naikkan ambang kemiripan ke 90% atau 100% (Exact Match).")
