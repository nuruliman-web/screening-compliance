import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time

def run_bulk_screening():
    st.markdown("### 🚀 Bulk Screening Pro (Super Admin)")
    st.write("Upload file nasabah untuk pengecekan massal terhadap database spreadsheet.")

    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database. Cek koneksi.")
        return

    # 1. KONFIGURASI
    st.markdown("##### 1. Konfigurasi Screening")
    list_sheet = list(db_pemerintah.keys())
    
    c1, c2 = st.columns([1, 1])
    db_tujuan = c1.selectbox("Pilih Database Tujuan:", list_sheet)
    mode = c2.radio("Parameter Utama:", ["NIK", "Nama", "Tanggal Lahir"], horizontal=True)

    # 2. UPLOAD
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
                    status_text.text(f"Memproses {i+1} dari {len(df_nasabah)} nasabah...")

                for _, row_p in target_db.iterrows():
                    match_details = [] # Untuk nampung multiple match dalam satu row
                    row_is_match = False

                    for col_db in target_db.columns:
                        val_db = str(row_p[col_db]).strip().lower()
                        
                        score = 0
                        found_in_col = False

                        if mode == "NIK":
                            if val_nasabah == val_db:
                                score, found_in_col = 100, True
                        elif mode == "Nama":
                            score = fuzz.token_sort_ratio(val_nasabah, val_db)
                            if score >= threshold:
                                found_in_col = True
                        elif mode == "Tanggal Lahir":
                            if val_nasabah in val_db:
                                score, found_in_col = 100, True
                        
                        if found_in_col:
                            # Format: Nama Kolom (XX%)
                            match_details.append(f"{col_db} ({score}%)")
                            row_is_match = True
                    
                    if row_is_match:
                        # 1. Ambil semua data asli nasabah (Kiri)
                        res_entry = row_n.to_dict()
                        
                        # 2. Tambahkan Ket Match (Gabungan kolom & persentase)
                        res_entry["Ket Match"] = ", ".join(match_details)
                        
                        # 3. Masukkan data database (Kanan)
                        for k, v in row_p.items():
                            res_entry[f"DB_{k}"] = v
                        
                        results.append(res_entry)
                        break # Pindah ke nasabah berikutnya setelah nemu row yang match
            
            progress_bar.progress(1.0)
            status_text.text("Screening Selesai!")

            # 3. TAMPILKAN HASIL
            if results:
                df_res = pd.DataFrame(results)
                st.warning(f"⚠️ Terdeteksi {len(df_res)} data yang cocok!")
                st.dataframe(df_res, use_container_width=True)
                
                csv = df_res.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Laporan Match (.csv)", csv, "Hasil_Bulk_Screening.csv", "text/csv")
            else:
                st.success("✅ Bersih! Tidak ada data nasabah yang cocok dengan database.")
