import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# Judul Utama
st.title("🔍 Screening APU, PPT, dan PPPSPM")

# 2. FUNGSI LOAD DATA
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        try:
            # Membaca file excel dengan semua sheet-nya
            return pd.read_excel(file_path, sheet_name=None)
        except Exception as e:
            st.error(f"Gagal membaca database: {e}")
            return None
    return None

# Nama file di GitHub harus tepat: database.xlsx
NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    # 3. INTERFACE PENCARIAN
    metode = st.radio("Pilih Metode Pencarian:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    
    if metode == "Nama":
        search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: AGUNG")
        threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 70)
    else:
        search_query = st.text_input("Masukkan NIK atau Nomor Paspor:", placeholder="Contoh: D 000974")
        st.sidebar.info("NIK wajib 16 digit. Paspor/Lainnya bebas.")

    # 4. LOGIKA PENCARIAN
    if search_query:
        query_clean = " ".join(search_query.split()).lower()
        found_any = False
        
        # Validasi khusus NIK
        if metode == "NIK / Nomor Paspor":
            input_cek = search_query.strip()
            if input_cek.isdigit() and len(input_cek) != 16:
                st.error(f"❌ NIK harus 16 digit! (Input Anda: {len(input_cek)} digit)")
                st.stop()
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                # Fungsi untuk cek kemiripan tiap baris
                def hitung_skor(row):
                    skor_maks = 0
                    kolom_ketemu = "-"
                    
                    # Tentukan kolom mana yang akan discan
                    if metode == "Nama":
                        cols_to_scan = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        cols_to_scan = df.columns # NIK scan semua kolom

                    for col in cols_to_scan:
                        val = row[col]
                        if pd.notna(val):
                            teks_data = " ".join(str(val).split()).lower()
                            
                            if metode == "Nama":
                                # Pakai token_set_ratio supaya nama parsial tetap tertangkap
                                if query_clean == teks_data:
                                    skor = 100
                                else:
                                    skor = fuzz.token_set_ratio(query_clean, teks_data)
                            else:
                                # NIK/Paspor wajib sama persis
                                skor = 100 if query_clean == teks_data else 0
                            
                            if skor > skor_maks:
                                skor_maks = skor
                                kolom_ketemu = col
                                
                    return pd.Series([skor_maks, kolom_ketemu])

                # Terapkan fungsi ke data
                df[['Skor (%)', 'Terdeteksi di Kolom']] = df.apply(hitung_skor, axis=1)
                
                # Filter berdasarkan hasil skor
                if metode == "Nama":
                    result = df[df['Skor (%)'] >= threshold]
                else:
                    result = df[df['Skor (%)'] == 100]

                if not result.empty:
                    found_any = True
                    result = result.sort_values(by='Skor (%)', ascending=False)
                    
                    # Geser kolom skor ke paling depan
                    prio = ['Skor (%)', 'Terdeteksi di Kolom']
                    cols = prio + [c for c in df.columns if c not in prio]
                    result = result[cols]

                    with st.expander(f"🚩 SHEET: {sheet_name}", expanded=True):
                        st.success(f"Ditemukan {len(result)} kecocokan.")
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.warning(f"HASIL NIHIL: '{search_query}' tidak ditemukan.")
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")
