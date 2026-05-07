import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time
import re

def clean_number_string(val):
    """Membersihkan NIK/Angka dari tanda petik, spasi, atau format scientific"""
    if pd.isna(val) or str(val).lower() == 'none' or str(val).strip() == '':
        return None
    # Ubah ke string, hapus spasi, hapus petik satu di depan
    s = str(val).strip().replace("'", "")
    # Jika format scientific (ada E+), ubah ke angka murni
    if 'e+' in s.lower():
        try:
            s = format(float(s), '.0f')
        except:
            pass
    return s

def run_bulk_screening():
    st.markdown("### 🚀 Bulk Screening Pro (Super Admin)")
    st.write("Sistem otomatis mendeteksi kecocokan berdasarkan kolom yang Anda pilih.")

    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database. Cek koneksi.")
        return

    # 1. PILIH DATABASE
    st.markdown("##### 1. Pilih Database Tujuan")
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.selectbox("Database Pemerintah:", list_sheet)

    # 2. UPLOAD DATA NASABAH
    st.markdown("##### 2. Upload & Mapping Kolom")
    file_nasabah = st.file_uploader("Upload Excel Nasabah", type=['xlsx'])

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        
        # Bersihkan format tanggal di awal agar tidak ada waktu
        for col in df_nasabah.columns:
            if pd.api.types.is_datetime64_any_dtype(df_nasabah[col]):
                df_nasabah[col] = df_nasabah[col].dt.strftime('%Y-%m-%d')

        cols = df_nasabah.columns.tolist()
        col_target = st.selectbox("Pilih Kolom Nasabah yang ingin di-screening:", ["-- Pilih Kolom --"] + cols)

        if col_target != "-- Pilih Kolom --":
            if st.button("🚀 Jalankan Screening Otomatis"):
                target_db = db_pemerintah[db_tujuan]
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Pre-processing Database Pemerintah (Hapus None agar tidak match kosong)
                # Kita asumsikan data di DB juga dibersihkan
                
                for i, row_n in df_nasabah.iterrows():
                    # Ambil nilai nasabah & bersihkan
                    raw_val = row_n[col_target]
                    val_nasabah = clean_number_string(raw_val)
                    
                    # JIKA KOSONG, SKIP (Logika request: None tidak di-screening)
                    if val_nasabah is None:
                        continue
                    
                    val_nasabah_lower = val_nasabah.lower()

                    if i % 10 == 0:
                        progress = (i + 1) / len(df_nasabah)
                        progress_bar.progress(progress)
                        status_text.text(f"Memproses {i+1} nasabah...")

                    for _, row_p in target_db.iterrows():
                        match_details = []
                        row_is_match = False

                        for col_db in target_db.columns:
                            # Bersihkan nilai di DB
                            raw_db = row_p[col_db]
                            val_db = clean_number_string(raw_db)
                            
                            if val_db is None: # Skip jika DB kosong
                                continue
                                
                            val_db_lower = val_db.lower()
                            score = 0
                            found = False

                            # LOGIKA SMART MATCHING:
                            # 1. Jika isinya angka panjang (NIK), gunakan Exact Match
                            if val_nasabah.isdigit() and len(val_nasabah) >= 10:
                                if val_nasabah == val_db:
                                    score, found = 100, True
                            
                            # 2. Jika format Tanggal (YYYY-MM-DD), gunakan Exact Match
                            elif re.match(r'\d{4}-\d{2}-\d{2}', val_nasabah):
                                if val_nasabah == val_db:
                                    score, found = 100, True
                            
                            # 3. Selain itu, gunakan Fuzzy Match (Untuk Nama)
                            else:
                                score = fuzz.token_sort_ratio(val_nasabah_lower, val_db_lower)
                                if score >= 85: # Threshold default 85%
                                    found = True
                            
                            if found:
                                match_details.append(f"{col_db} ({score}%)")
                                row_is_match = True
                        
                        if row_is_match:
                            res_entry = row_n.to_dict()
                            res_entry["Ket Match"] = ", ".join(match_details)
                            for k, v in row_p.items():
                                if isinstance(v, pd.Timestamp):
                                    v = v.strftime('%Y-%m-%d')
                                res_entry[f"DB_{k}"] = v
                            results.append(res_entry)
                            break 

                progress_bar.progress(1.0)
                status_text.text("Selesai!")

                if results:
                    df_res = pd.DataFrame(results)
                    st.warning(f"⚠️ Terdeteksi {len(df_res)} data yang cocok!")
                    st.dataframe(df_res, use_container_width=True)
                    csv = df_res.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Laporan Match (.csv)", csv, "Hasil_Bulk.csv", "text/csv")
                else:
                    st.success("✅ Tidak ditemukan data yang cocok (None diabaikan).")
