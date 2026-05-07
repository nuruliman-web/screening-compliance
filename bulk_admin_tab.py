import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time
import re
from io import BytesIO

def clean_number_string(val):
    """
    Membersihkan NIK/Angka dari tanda petik, spasi, atau format scientific.
    Mengembalikan None jika data kosong agar tidak terjadi False Positive.
    """
    if pd.isna(val) or str(val).lower() == 'none' or str(val).strip() == '':
        return None
    
    # Ubah ke string, hapus spasi, dan hapus petik satu di depan
    s = str(val).strip().replace("'", "")
    
    # Handle format scientific Excel (misal 3.2E+15)
    if 'e+' in s.lower():
        try:
            s = format(float(s), '.0f')
        except:
            pass
    return s

def run_bulk_screening():
    st.markdown("### 🚀 Bulk Screening Data Blacklist")
    st.write("Sistem otomatis mendeteksi kecocokan berdasarkan kolom yang Anda pilih.")

    # Ambil database dari fungsi fetch yang sudah ada di screening_tab
    import screening_tab as sc
    db_pemerintah, stats, total = sc.fetch_all_data()

    if db_pemerintah is None:
        st.error("Gagal memuat database pemerintah. Cek koneksi Google Sheets Anda.")
        return

    # --- 1. PILIH DATABASE ---
    st.markdown("##### 1. Pilih Database Tujuan Screening")
    list_sheet = list(db_pemerintah.keys())
    db_tujuan = st.selectbox("Pilih Database Pemerintah untuk pembanding:", list_sheet)

    # --- 2. UPLOAD DATA NASABAH ---
    st.markdown("##### 2. Upload & Mapping Kolom")
    file_nasabah = st.file_uploader("Upload Excel Nasabah (Format .xlsx)", type=['xlsx'])

    if file_nasabah:
        df_nasabah = pd.read_excel(file_nasabah)
        
        # Bersihkan format tanggal di semua kolom agar tidak muncul jam (00:00:00)
        for col in df_nasabah.columns:
            if pd.api.types.is_datetime64_any_dtype(df_nasabah[col]):
                df_nasabah[col] = df_nasabah[col].dt.strftime('%Y-%m-%d')

        cols = df_nasabah.columns.tolist()
        col_target = st.selectbox("Pilih Kolom dari Excel Anda yang ingin di-screening:", ["-- Pilih Kolom --"] + cols)

        # Variabel kontrol
        threshold = 100
        
        if col_target != "-- Pilih Kolom --":
            # Ambil sampel data pertama yang tidak kosong untuk deteksi tipe data
            valid_samples = df_nasabah[col_target].dropna()
            sample_val = clean_number_string(valid_samples.iloc[0]) if not valid_samples.empty else ""
            
            # Deteksi: Jika bukan NIK (angka panjang) dan bukan Tanggal (YYYY-MM-DD), maka mode Nama (Fuzzy)
            is_nik = str(sample_val).isdigit() and len(str(sample_val)) >= 10
            is_tgl = bool(re.match(r'\d{4}-\d{2}-\d{2}', str(sample_val)))

            if not is_nik and not is_tgl:
                st.info("💡 Kolom terdeteksi sebagai Nama/Teks. Gunakan slider untuk mengatur sensitivitas fuzzy.")
                threshold = st.slider("Ambang Batas Kemiripan Nama (%)", 50, 100, 85)
            else:
                st.success(f"✅ Kolom terdeteksi sebagai {'NIK' if is_nik else 'Tanggal'}. Menggunakan logika Exact Match (100%).")

            # --- 3. EKSEKUSI SCREENING ---
            if st.button("🚀 Jalankan Screening"):
                target_db = db_pemerintah[db_tujuan]
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                start_time = time.time()

                for i, row_n in df_nasabah.iterrows():
                    # Ambil data nasabah dan bersihkan
                    val_nasabah = clean_number_string(row_n[col_target])
                    
                    # Jika data di kolom target kosong/None, abaikan baris ini
                    if val_nasabah is None:
                        continue
                    
                    val_nasabah_lower = val_nasabah.lower()

                    # Update Progress setiap 10 baris
                    if i % 10 == 0:
                        progress = (i + 1) / len(df_nasabah)
                        progress_bar.progress(progress)
                        status_text.text(f"Memproses {i+1} dari {len(df_nasabah)} data...")

                    # Bandingkan dengan setiap baris di Database Pemerintah
                    for _, row_p in target_db.iterrows():
                        match_details = []
                        row_is_match = False

                        for col_db in target_db.columns:
                            val_db = clean_number_string(row_p[col_db])
                            
                            if val_db is None:
                                continue
                                
                            val_db_lower = val_db.lower()
                            score = 0
                            found_in_col = False

                            # A. Logika NIK
                            if is_nik:
                                if val_nasabah == val_db:
                                    score, found_in_col = 100, True
                            
                            # B. Logika Tanggal
                            elif is_tgl:
                                if val_nasabah == val_db:
                                    score, found_in_col = 100, True
                            
                            # C. Logika Nama (Fuzzy)
                            else:
                                score = fuzz.token_sort_ratio(val_nasabah_lower, val_db_lower)
                                if score >= threshold:
                                    found_in_col = True
                            
                            if found_in_col:
                                match_details.append(f"{col_db} ({score}%)")
                                row_is_match = True
                        
                        # Jika ditemukan kecocokan dalam satu row DB
                        if row_is_match:
                            # Gabungkan Data Nasabah (Kiri) + Info Match + Data DB (Kanan)
                            res_entry = row_n.to_dict()
                            res_entry["Ket Match"] = ", ".join(match_details)
                            
                            for k, v in row_p.items():
                                # Pastikan tanggal di DB juga bersih saat ditampilkan
                                if isinstance(v, pd.Timestamp):
                                    v = v.strftime('%Y-%m-%d')
                                res_entry[f"DB_{k}"] = v
                            
                            results.append(res_entry)
                            break # Pindah ke nasabah berikutnya (optimasi)

                progress_bar.progress(1.0)
                status_text.text(f"Screening Selesai dalam {round(time.time() - start_time, 2)} detik.")

                # --- 4. TAMPILKAN HASIL & DOWNLOAD EXCEL ---
                if results:
                    df_res = pd.DataFrame(results)
                    st.warning(f"⚠️ Terdeteksi {len(df_res)} data yang cocok dengan database!")
                    st.dataframe(df_res, use_container_width=True)
                    
                    # Logika Export ke Excel (.xlsx)
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_res.to_excel(writer, index=False, sheet_name='Hasil_Screening')
                    
                    processed_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 Download Laporan Match",
                        data=processed_data,
                        file_name="Hasil_Bulk_Screening.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.success("✅ Tidak ada data nasabah yang cocok dengan data blacklist.")
