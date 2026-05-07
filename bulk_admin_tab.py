import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time

def run_bulk_screening():
    st.markdown("### 🚀 Bulk Screening Pro (Super Admin)")
    st.write("Upload file nasabah dan pilih database tujuan untuk pengecekan massal.")

    # 1. LOAD DATABASE DARI GOOGLE SHEETS / EXCEL
    # Di sini saya asumsikan fungsi fetch_all_data sudah ada di screening_tab
    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database pemerintah. Cek koneksi Google Sheets.")
        return

    # 2. PILIHAN DATABASE TUJUAN (Radio Button)
    st.markdown("##### 1. Pilih Database Tujuan")
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.radio("Cek nasabah terhadap database:", list_sheet, horizontal=True)

    # 3. UPLOAD FILE NASABAH
    st.markdown("##### 2. Upload Data Nasabah")
    file_nasabah = st.file_uploader("Upload Excel Nasabah (Ribuan Data OK)", type=['xlsx'])

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        st.success(f"✅ {len(df_nasabah)} data nasabah berhasil dimuat.")
        
        cols = df_nasabah.columns.tolist()
        
        # 4. PILIH PARAMETER SCREENING
        st.markdown("##### 3. Pilih Parameter & Mapping Kolom")
        c1, c2 = st.columns(2)
        
        mode = c1.radio("Gunakan Parameter:", ["NIK (Exact)", "Nama (Fuzzy)", "Tanggal Lahir"], horizontal=True)
        col_target = c2.selectbox(f"Pilih Kolom {mode} di File Anda:", cols)

        threshold = 80
        if mode == "Nama (Fuzzy)":
            threshold = st.slider("Tingkat Kemiripan Nama (%)", 70, 100, 85)

        # 5. EKSEKUSI SCREENING
        if st.button("🚀 Mulai Bulk Screening"):
            target_db = db_pemerintah[db_tujuan]
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            start_time = time.time()

            # Iterasi Data Nasabah
            for i, row_n in df_nasabah.iterrows():
                val_nasabah = str(row_n[col_target]).strip().lower()
                found = False
                
                # Update Progress tiap 10 data biar gak berat
                if i % 10 == 0:
                    progress = (i + 1) / len(df_nasabah)
                    progress_bar.progress(progress)
                    status_text.text(f"Memproses data ke-{i+1} dari {len(df_nasabah)}...")

                # Loop di Database Pemerintah (Pencarian)
                for _, row_p in target_db.iterrows():
                    # Mapping kolom di DB Pemerintah (sesuaikan dengan nama kolom di sheetmu)
                    # Kita asumsikan kolom di DB Pemerintah mengandung kata kunci target
                    for col_p in target_db.columns:
                        val_p = str(row_p[col_p]).strip().lower()
                        
                        match = False
                        if mode == "NIK (Exact)":
                            if val_nasabah == val_p: match = True
                        elif mode == "Nama (Fuzzy)":
                            if fuzz.token_sort_ratio(val_nasabah, val_p) >= threshold: match = True
                        elif mode == "Tanggal Lahir":
                            if val_nasabah in val_p: match = True
                        
                        if match:
                            # Ambil semua data row pemerintah yang match
                            match_info = row_p.to_dict()
                            match_info['Nasabah_Ref'] = val_nasabah # Referensi input
                            results.append(match_info)
                            found = True
                            break
                    if found: break # Langsung ke nasabah berikutnya kalau sudah ketemu match

            end_time = time.time()
            progress_bar.progress(1.0)
            status_text.text(f"Selesai dalam {round(end_time - start_time, 2)} detik.")

            # 6. TAMPILKAN HASIL
            if results:
                df_res = pd.DataFrame(results)
                st.warning(f"⚠️ Ditemukan {len(df_res)} indikasi kecocokan!")
                st.dataframe(df_res)
                
                # Tombol Download Hasil
                csv = df_res.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Laporan Match (CSV)", csv, "hasil_screening.csv", "text/csv")
            else:
                st.success("✅ Aman! Tidak ada data nasabah yang cocok dengan database tersebut.")
