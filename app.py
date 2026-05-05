import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os

# 1. Konfigurasi Tampilan Halaman
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

# Judul Aplikasi
st.title("🔍 Screening APU, PPT, dan PPPSPM")

# 2. Fungsi Load Data (Database tersimpan di GitHub dengan nama database.xlsx)
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        try:
            # Membaca seluruh sheet dalam file excel
            return pd.read_excel(file_path, sheet_name=None)
        except Exception as e:
            st.error(f"Gagal membaca database: {e}")
            return None
    return None

# Pastikan nama file di GitHub adalah database.xlsx
NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    # 3. Pilihan Metode Pencarian
    metode = st.radio("Pilih Metode Pencarian:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    
    if metode == "Nama":
        search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: AGUNG")
        threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 70)
        st.sidebar.info("Tips: Gunakan skor 70-80% untuk mencari nama panggilan/singkat.")
    else:
        search_query = st.text_input("Masukkan NIK atau Nomor Paspor:", placeholder="Contoh: D 000974")
        st.sidebar.info("Catatan: NIK wajib 16 digit. Nomor Paspor bebas. Pencarian bersifat Exact Match (Sama Persis).")

    # 4. Proses Pencarian saat ada input
    if search_query:
        # Bersihkan input dari spasi ganda/berlebih
        query_clean = " ".join(search_query.split()).lower()
        found_any = False
        
        # Validasi khusus NIK (harus 16 digit jika isinya hanya angka)
        if metode == "NIK / Nomor Paspor":
            input_murni = search_query.strip()
            if input_murni.isdigit() and len(input_murni) != 16:
                st.error(f"❌ NIK harus 16 digit! (Input Anda: {len(input_murni)} digit)")
                st.stop()
        
        st.divider()
        
        # Daftar sheet yang akan diperiksa
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                # Fungsi internal untuk memproses setiap baris
                def hitung_skor_dan_kolom(row):
                    skor_maks = 0
                    kolom_ketemu = "-"
                    
                    # Pilih kolom target berdasarkan metode
                    if metode == "Nama":
                        # Hanya
