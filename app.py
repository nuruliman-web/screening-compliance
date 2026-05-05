import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# Judul Utama Baru
st.title("🔍 Screening APU, PPT, dan PPPSPM")
# st.write(...) baris ini sudah saya hapus agar tampilan lebih bersih

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
                    
                    if metode == "Nama":
                        kolom_target = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        kolom_target = df.columns # NIK/Paspor cari di SEMUA kolom

                    for col in kolom_target:
                        val = row[col]
