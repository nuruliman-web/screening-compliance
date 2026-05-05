import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening Pro", layout="wide")

st.title("🔍 Database Screening Multi-Metode")
st.write("Metode: Nama (Fuzzy) atau Identitas NIK/Paspor (Exact).")

# 2. Fungsi Load Data
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path, sheet_name=None)
    return None

NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    # 3. Pilihan Metode Pencarian
    metode = st.radio("Pilih Metode Pencarian:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    
    if metode == "Nama":
        search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: Iman")
        threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 90)
    else:
        search_query = st.text_input("Masukkan NIK atau Nomor Paspor:", placeholder="Contoh: 3201... atau A1234xxx")
        st.sidebar.info("NIK wajib 16 digit. Nomor Paspor bebas. Pencarian bersifat Exact Match.")

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        # VALIDASI KHUSUS IDENTITAS
        if metode == "NIK / Nomor Paspor":
            # Jika hanya angka (NIK), cek apakah 16 digit
            if query.isdigit() and len(query) != 16:
                st.error(f"❌ NIK harus 16 digit! (Inputan Anda: {len(query)} digit)")
                st.stop() # Berhenti di sini, jangan lanjut cari
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def proses_baris(row):
                    skor_tertinggi = 0
                    kolom_ditemukan = "-"
                    
                    if metode == "Nama":
                        kolom_target = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        kolom_target = df.columns # Identitas cari di semua kolom

                    for col in kolom_target:
                        val = row[col]
                        if pd.notna(val):
                            teks_data = str(val).strip().lower()
                            
                            if metode == "Nama":
                                if query == teks_data:
                                    skor = 100
                                else:
                                    skor = fuzz.token_sort_ratio(query, teks_data)
                            else:
                                # Logika Identitas (Exact)
                                skor = 100 if query == teks_data else 0
                            
                            if skor > skor_tertinggi:
                                skor_tertinggi = skor
                                kolom_ditemukan = col
                                
                    return pd.Series([skor_tertinggi, kolom_ditemukan])

                df[['Skor (%)', 'Terdeteksi di Kolom']] = df.apply(proses_baris, axis=1)
                
                # Filter hasil
                if metode == "Nama":
                    result = df[df['Skor (%)'] >= threshold]
                else:
                    result = df[df['Skor (%)'] == 100]

                if not result.empty:
                    found_any = True
                    result = result.sort_values(by='Skor (%)', ascending=False)
                    prio_cols = ['Skor (%)', 'Terdeteksi di Kolom']
                    other_cols = [c for c in df.columns if c not in prio_cols]
                    result = result[prio_cols + other_cols]

                    with st.expander(f"🚩 SHEET: {sheet_name}", expanded=True):
                        st.success(f"Ditemukan {len(result)} kecocokan.")
                        st.dataframe(result, use_container_width=True)
            
        if not found_any:
            st.warning(f"HASIL NIHIL: Tidak ditemukan data yang cocok.")
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")
