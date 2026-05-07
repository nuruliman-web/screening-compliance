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

    # Ambil database dari fungsi fetch yang sudah ada di screening_tab
    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database pemerintah. Cek koneksi Google Sheets.")
        return

    # --- 1. PILIH DATABASE ---
    st.markdown("##### 1. Pilih Database Tujuan")
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.selectbox("Pilih Database Pemerintah:", list_sheet)

    # --- 2. UPLOAD DATA NASABAH ---
    st.markdown("##### 2. Upload & Mapping Kolom")
    file_nasabah = st.file_uploader("Upload Excel Nasabah", type=['xlsx'])

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        
        # Bersihkan format tanggal agar tidak ada waktu
        for col in df_nasabah.columns:
            if pd.api.types.is_datetime64_any_dtype(df_nasabah[col]):
                df_nasabah[col] = df_nasabah[col].dt.strftime('%Y-%m-%d')

        cols = df_nasabah.columns.tolist()
        col_target = st.selectbox("Pilih Kolom Nasabah yang ingin di-screening:", ["-- Pilih Kolom --"] + cols)

        threshold = 100
        if col_target != "-- Pilih Kolom --":
            valid_samples = df_nasabah[col_target].dropna()
            sample_val = clean_number_string(valid_samples.iloc[0]) if not valid_samples.empty else ""
            
            is_nik = str(sample_val).isdigit() and len(str(sample_val)) >= 10
            is_tgl = bool(re.match(r'\d{4}-\d{2}-\d{2}', str(sample_val)))

            if not is_nik and not is_tgl:
                st.info("💡 Mode Nama (Fuzzy) Aktif")
                threshold = st.slider("Ambang Batas Kemiripan Nama (%)", 50, 100, 85)

            # --- 3. EKSEKUSI ---
            if st.button("🚀 Jalankan Screening"):
                target_db = db_pemerintah[db_tujuan]
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, row_n in df_nasabah.iterrows():
                    val_nasabah = clean_number_string(row_n[col_target])
                    if val_nasabah is None: continue
                    
                    if i % 10 == 0:
                        progress = (i + 1) / len(df_nasabah)
                        progress_bar.progress(progress)
                        status_text.text(f"Memproses data ke-{i+1}...")

                    for _, row_p in target_db.iterrows():
                        match_details = []
                        row_is_match = False

                        for col_db in target_db.columns:
                            val_db = clean_number_string(row_p[col_db])
                            if val_db is None: continue
                                
                            score = 0
                            found = False

                            if is_nik or is_tgl:
                                if val_nasabah == val_db:
                                    score, found = 100, True
                            else:
                                score = fuzz.token_sort_ratio(val_nasabah.lower(), val_db.lower())
                                if score >= threshold: found = True
                            
                            if found:
                                match_details.append(f"{col_db} ({score}%)")
                                row_is_match = True
                        
                        if row_is_match:
                            res_entry = row_n.to_dict()
                            res_entry["Ket Match"] = ", ".join(match_details)
                            for k, v in row_p.items():
                                if isinstance(v, pd.Timestamp): v = v.strftime('%Y-%m-%d')
                                res_entry[f"DB_{k}"] = v
                            results.append(res_entry)
                            break 

                progress_bar.progress(1.0)
                status_text.text("Selesai!")

                # --- 4. DOWNLOAD CSV (OPTIMAL FOR EXCEL) ---
                if results:
                    df_res = pd.DataFrame(results)
                    st.warning(f"⚠️ Terdeteksi {len(df_res)} data match!")
                    st.dataframe(df_res)
                    
                    # BIAR BISA DIBUKA EXCEL TANPA BERANTAKAN:
                    # 1. Gunakan encoding 'utf-8-sig' (BOM)
                    # 2. Gunakan separator koma atau semicolon (disini pakai koma standar)
                    csv_data = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    
                    st.download_button(
                        label="📥 Download Hasil Screening (CSV)",
                        data=csv_data,
                        file_name="Hasil_Bulk_Screening.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("✅ Bersih! Tidak ada data yang cocok.")
