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
        search_query = st.text_input("Masukkan NIK atau Nomor Paspor:", placeholder="Contoh: D 000974")
        st.sidebar.info("Pencarian Identitas menyisir seluruh kolom di semua sheet.")

    if search_query:
        # Membersihkan inputan CS dari spasi berlebih
        query = " ".join(search_query.split()).lower()
        found_any = False
        
        # Validasi NIK jika hanya angka
        if metode == "NIK / Nomor Paspor":
            if search_query.strip().isdigit() and len(search_query.strip()) != 16:
                st.error(f"❌ NIK harus 16 digit! (Inputan Anda: {len(search_query.strip())} digit)")
                st.stop()
        
        st.divider()
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def proses_baris(row):
                    skor_tertinggi = 0
                    kolom_ditemukan = "-"
                    
                    # Tentukan target kolom
                    if metode == "Nama":
                        kolom_target = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        kolom_target = df.columns # NIK/Paspor cari di SEMUA kolom

                    for col in kolom_target:
                        val = row[col]
                        if pd.notna(val):
                            # Bersihkan data excel dari spasi ganda untuk pencocokan
                            teks_data = " ".join(str(val).split()).lower()
                            
                            if metode == "Nama":
                                if query == teks_data:
                                    skor = 100
                                else:
                                    skor = fuzz.token_sort_ratio(query, teks_data)
                            else:
                                # Logika Identitas (Exact setelah spasi dibersihkan)
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
            st.warning(f"HASIL NIHIL: Data '{search_query}' tidak ditemukan.")
            st.info("Tips: Pastikan tidak ada karakter aneh di file Excel Anda.")
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' tidak ditemukan di GitHub!")
