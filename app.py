import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening APU, PPT, dan PPPSPM", layout="wide")

st.title("🔍 Screening APU, PPT, dan PPPSPM")
st.write("Sistem secara otomatis membaca data yang diinput dan melakukan screening terhadap database APU, PPT, & PPPSPM untuk mengidentifikasi kecocokan data")

# 2. FUNGSI LOAD DATA
@st.cache_data
def load_internal_data(file_path):
    if os.path.exists(file_path):
        try:
            # Membaca seluruh sheet dalam file excel
            data = pd.read_excel(file_path, sheet_name=None)
            
            # --- PERBAIKAN FORMAT TANGGAL (Menghilangkan 00:00:00) ---
            for sheet in data:
                for col in data[sheet].columns:
                    if pd.api.types.is_datetime64_any_dtype(data[sheet][col]):
                        data[sheet][col] = data[sheet][col].dt.strftime('%Y-%m-%d')
            return data
        except Exception as e:
            st.error(f"Gagal membaca database: {e}")
            return None
    return None

NAMA_FILE_DATABASE = "database.xlsx" 
db_sheets = load_internal_data(NAMA_FILE_DATABASE)

if db_sheets:
    # 3. INTERFACE PENCARIAN
    metode = st.radio("Pilih Metode Pencarian:", ("Nama", "NIK / Nomor Paspor"), horizontal=True)
    
    if metode == "Nama":
        search_query = st.text_input("Masukkan Nama Calon Nasabah:", placeholder="Contoh: AGUNG GUNARDI")
        threshold = st.sidebar.slider("Ambang Kemiripan Minimal (%)", 50, 100, 85)
    else:
        search_query = st.text_input("Masukkan NIK atau Nomor Paspor Calon Nasabah:", placeholder="Contoh: D 000974")
        st.sidebar.info("NIK wajib 16 digit. Paspor bebas.")

    # 4. LOGIKA PENCARIAN
    if search_query:
        query_clean = " ".join(search_query.split()).lower()
        found_any_global = False
        all_results_for_download = [] 
        
        # Validasi NIK
        if metode == "NIK / Nomor Paspor":
            input_val = search_query.strip()
            if input_val.isdigit() and len(input_val) != 16:
                st.error(f"❌ NIK harus 16 digit! (Input: {len(input_val)} digit)")
                st.stop()
        
        st.divider()
        # Daftar sheet yang akan di-scan
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name].copy()
                
                def check_row_match(row_db):
                    found_cols = []
                    max_score_in_row = 0
                    
                    # Pilih kolom scan berdasarkan metode
                    if metode == "Nama":
                        cols_to_scan = [c for c in df.columns if 'nama' in c.lower()]
                    else:
                        cols_to_scan = df.columns

                    for col_name in cols_to_scan:
                        val = row_db[col_name]
                        if pd.notna(val):
                            teks_db = " ".join(str(val).split()).lower()
                            
                            if metode == "Nama":
                                # Pakai token_sort_ratio agar presisi
                                score = fuzz.token_sort_ratio(query_clean, teks_db)
                                if score >= threshold:
                                    if score > max_score_in_row: max_score_in_row = score
                                    found_cols.append(f"{col_name} ({score}%)")
                            else:
                                # Exact match untuk identitas
                                if query_clean == teks_db:
                                    max_score_in_row = 100
                                    found_cols.append(f"{col_name} (COCOK)")
                                    
                    return max_score_in_row, ", ".join(found_cols)

                # Jalankan pengecekan baris
                res_match = df.apply(lambda r: pd.Series(check_row_match(r)), axis=1)
                
                # Masukkan kolom STATUS_KOLOM_ALIAS di paling kiri
                df.insert(0, 'STATUS_KOLOM_ALIAS', res_match[1])
                
                # Filter hanya yang memenuhi threshold
                limit = threshold if metode == "Nama" else 100
                matches = df[res_match[0] >= limit].copy()
                
                if not matches.empty:
                    found_any_global = True
                    all_results_for_download.append(matches)
                    
                    with st.expander(f"🚩 HASIL DATABASE: {sheet_name} (Ditemukan {len(matches)} data)", expanded=True):
                        st.dataframe(matches, use_container_width=True)

        # 5. FITUR DOWNLOAD
        if found_any_global:
            st.divider()
            final_report = pd.concat(all_results_for_download, ignore_index=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_report.to_excel(writer, index=False, sheet_name='Hasil_Screening')
            
            st.download_button(
                label="📥 Download Hasil Screening (Excel)",
                data=output.getvalue(),
                file_name=f"Hasil_Screening_{search_query}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        if not found_any_global:
            st.warning(f"HASIL NIHIL: Data '{search_query}' tidak ditemukan di database manapun.")
else:
    st.error(f"Database tidak tersedia. Pastikan '{NAMA_FILE_DATABASE}' sudah diupload ke GitHub.")
