import streamlit as st
import pandas as pd
import os

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening", layout="wide")

st.title("🔍 Database Screening Terpadu")
st.write("Sistem otomatis memeriksa database JUDOL, DTTOT, DPPSPM, dan SIPENDAR.")

# 2. Fungsi Membaca File yang Tersimpan di GitHub
@st.cache_data
def load_internal_data(file_path):
    try:
        # Membaca seluruh sheet dalam file yang ada di repository
        db_sheets = pd.read_excel(file_path, sheet_name=None)
        return db_sheets
    except Exception as e:
        st.error(f"Error: File '{file_path}' tidak ditemukan di server atau format salah.")
        return None

# Tentukan nama file sesuai yang kamu upload ke GitHub tadi
NAMA_FILE_DATABASE = "database.xlsx" 

if os.path.exists(NAMA_FILE_DATABASE):
    db_sheets = load_internal_data(NAMA_FILE_DATABASE)
    
    # 3. Input Nama yang Dicari
    search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Ketik nama di sini...")

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        st.divider()
        st.subheader(f"Hasil Pencarian untuk: '{search_query}'")

        # Daftar sheet yang wajib ada
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name]
                
                # Logika penyisiran seluruh kolom (nama, nama1, nama2, dst)
                mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(query, na=False).any(), axis=1)
                result = df[mask]

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 TERDETEKSI DI SHEET: {sheet_name}", expanded=True):
                        st.warning(f"Ditemukan {len(result)} data yang cocok.")
                        st.dataframe(result, use_container_width=True)
            else:
                st.sidebar.error(f"Sheet '{sheet_name}' tidak ada dalam file.")

        if not found_any:
            st.success("✅ HASIL NIHIL: Nama tidak ditemukan di database.")
            st.balloons()
else:
    st.error(f"File '{NAMA_FILE_DATABASE}' belum di-upload ke GitHub!")

# Info Status di Sidebar
st.sidebar.success("✅ Database Terhubung (Internal)")
st.sidebar.info("Untuk update data, silakan upload file baru ke GitHub dengan nama yang sama.")
