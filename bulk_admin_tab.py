import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time
import re

def clean_number_string(val):
    """Membersihkan NIK/Angka dari tanda petik, spasi, atau format scientific"""
    if pd.isna(val) or str(val).lower() == 'none' or str(val).strip() == '':
        return None
    s = str(val).strip().replace("'", "")
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

        # Logika Slider Fuzzy
        threshold = 100
        is_fuzzy_mode = False

        if col_target != "-- Pilih Kolom --":
            # Cek sampel data untuk menentukan apakah butuh slider fuzzy (untuk Nama/Teks)
            sample_val = clean_number_string(df_nasabah[col_target].dropna().iloc[0]) if not df_nasabah[col_target].dropna().empty else ""
            
            # Jika isinya bukan angka murni (NIK) dan bukan format tanggal, maka tampilkan slider
            if sample_val and not (str(sample_val).isdigit() and len(str(sample_val)) >= 10) and not re.match(r'\d{4}-\d{2}-\d{2}', str(sample_val)):
                st.info("💡 Kolom terdeteksi sebagai Nama/Teks. Gunakan slider untuk mengatur sensitivitas pencarian.")
                threshold = st.slider("Ambang Batas Kemiripan Nama (%)", 50, 100, 85)
                is_fuzzy_mode = True

            if st.button("🚀 Jalankan Screening Otomatis"):
                target_db = db_pemerintah[db_tujuan]
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, row_n in df_nasabah.iterrows():
                    raw_val = row_n[col_target]
                    val_nasabah = clean_number_string(raw_val)
                    
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
                            raw_db = row_p[col_db]
                            val_db = clean_number_string(raw_db)
                            
                            if val_db is None:
                                continue
                                
                            val_db_lower = val_db.lower()
                            score = 0
                            found = False

                            # LOGIKA MATCHING
                            # 1. NIK (Digit > 10) -> Exact
                            if str(val_nasabah).isdigit() and len(str(val_nasabah)) >= 10:
                                if val_nasabah == val_db:
                                    score, found = 100, True
                            
                            # 2. Tanggal (YYYY-MM-DD) -> Exact
                            elif re.match(r'\d{4}-\d{2}-\d{2}', str(val_nasabah)):
                                if val_nasabah == val_db:
                                    score, found = 100, True
                            
                            # 3. Nama/Teks -> Fuzzy (Sesuai Slider)
                            else:
                                score = fuzz.token_sort_ratio(val_nasabah_lower, val_db_lower)
                                if score >= threshold:
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
                    st.success("✅ Tidak ditemukan data yang cocok.")
