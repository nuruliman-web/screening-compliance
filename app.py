import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening Pro", layout="wide")

st.title("🔍 Database Screening (Strict Name Search)")
st.write("Pencarian khusus pada kolom Nama, Nama1, dst. dengan identifikasi kolom.")

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
                
                # Hanya ambil kolom yang ada unsur kata 'nama' (Case Insensitive)
                kolom_nama = [col for col in df.columns if 'nama' in col.lower()]
                
                if not kolom_nama:
                    continue

                def proses_baris(row):
                    skor_tertinggi = 0
                    kolom_ditemukan = "-"
                    
                    # Hanya looping di kolom yang masuk kriteria 'kolom_nama'
                    for col in kolom_nama:
                        val = row[col]
                        if pd.notna(val):
                            teks_data = str(val).strip().lower()
                            
                            # Logika Skor Exact
                            if query == teks_data:
                                skor = 100
                            else:
                                # Logika Skor Fuzzy (Akan turun jika ada tambahan kata)
                                skor = fuzz.token_sort_ratio(query, teks_data)
                            
                            if skor > skor_tertinggi:
                                skor_tertinggi = skor
                                kolom_ditemukan = col
                                
                    return pd.Series([skor_tertinggi, kolom_ditemukan])

                # Jalankan fungsi hanya pada kolom nama yang difilter
                df[['Skor (%)', 'Terdeteksi di Kolom']] = df[kolom_nama].apply(proses_baris, axis=1)
                
                # Filter & Sort
                result = df[df['Skor (%)'] >= threshold].sort_values(by='Skor (%)', ascending=False)

                # Rapikan urutan kolom (Info skor di depan)
                prio_cols = ['Skor (%)', 'Terdeteksi di Kolom']
                other_cols = [c for c in df.columns if c not in prio_cols]
                result = result[prio_cols + other_cols]

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 SHEET: {sheet_name}", expanded=True):
                        st.success(f"Ditemukan {len(result)} kecocokan pada kolom identitas.")
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.warning(f"HASIL NIHIL: Tidak ditemukan kemiripan di atas {threshold}% pada kolom Nama.")
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")

st.sidebar.markdown("---")
st.sidebar.caption("Sistem saat ini hanya memindai kolom dengan header mengandung kata 'Nama'.")
