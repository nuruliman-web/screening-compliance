import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time

def run_bulk_screening():
    st.markdown("### 🚀 Bulk Screening Pro (Super Admin)")
    st.write("Upload file nasabah untuk pengecekan massal dengan detail persentase kemiripan.")

    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database. Cek koneksi.")
        return

    # 1. PILIHAN DATABASE & PARAMETER
    st.markdown("##### 1. Konfigurasi Screening")
    list_sheet = list(db_pemerintah.keys())
    
    c1, c2 = st.columns([1, 1])
    db_tujuan = c1.selectbox("Pilih Database Tujuan:", list_sheet)
    mode = c2.radio("Parameter Utama:", ["NIK", "Nama", "Tanggal Lahir"], horizontal=True)

    # 2. UPLOAD FILE NASABAH
    st.markdown("##### 2. Upload Data Nasabah")
    file_nasabah = st.file_uploader("Upload Excel Nasabah", type=['xlsx'])

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        cols = df_nasabah.columns.tolist()
        col_target = st.selectbox(f"Pilih Kolom {mode} di File Excel Anda:", cols)

        threshold = 80
        if mode == "Nama":
            threshold = st.slider("Ambang Batas Match Nama (%)", 70, 100, 85)

        if st.button("🚀 Jalankan Screening"):
            target_db = db_pemerintah[db_tujuan]
            results = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            start_time = time.time()

            for i, row_n in df_nasabah.iterrows():
                val_nasabah = str(row_n[col_target]).strip().lower()
                
                if i % 10 == 0:
                    progress = (i + 1) / len(df_nasabah)
                    progress_bar.progress(progress)
                    status_text.text(f"Mengecek data ke-{i+1}...")

                for _, row_p in target_db.iterrows():
                    # Gabungkan semua data di row database pemerintah jadi satu string untuk dicari
                    # Atau bisa spesifik ke kolom tertentu jika kamu tahu nama kolomnya
                    for col_p in target_db.columns:
                        val_db = str(row_p[col_p]).strip().lower()
                        
                        is_match = False
                        score = 0
                        
                        if mode == "NIK":
                            if val_nasabah == val_db:
                                is_match = True
                                score = 100
                        elif mode == "Nama":
                            score = fuzz.token_sort_ratio(val_nasabah, val_db)
                            if score >= threshold:
                                is_match = True
                        elif mode == "Tanggal Lahir":
                            if val_nasabah in val_db:
                                is_match = True
                                score = 100
                        
                        if is_match:
                            # BUAT RECORD HASIL
                            res_entry = {
                                "NO": i + 1,
                                "DATA INPUT": val_nasabah,
                                "ASPEK MATCH": mode,
                                "PERSENTASE": f"{score}%",
                                "KETERANGAN": f"Cocok di kolom database: {col_p}"
                            }
                            # MASUKKAN SEMUA DATA DARI DATABASE (BIAR BISA IDENTIFIKASI)
                            for k, v in row_p.items():
                                res_entry[f"DB_{k}"] = v
                            
                            results.append(res_entry)
                            break 
            
            progress_bar.progress(1.0)
            status_text.text("Screening Selesai!")

            # 3. TAMPILKAN HASIL
            if results:
                df_res = pd.DataFrame(results)
                st.warning(f"⚠️ Ditemukan {len(df_res)} data yang terindikasi match!")
                
                # Styling DataFrame agar persentase terlihat jelas
                st.dataframe(df_res, use_container_width=True)
                
                # Export
                csv = df_res.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Laporan Lengkap (.csv)", csv, "Laporan_Screening.csv", "text/csv")
            else:
                st.success("✅ Tidak ditemukan data yang cocok.")
