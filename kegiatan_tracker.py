import streamlit as st
import pandas as pd
from datetime import datetime
import os

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan (Local Storage)</h3>", unsafe_allow_html=True)
    
    # NAMA FILE PENYIMPANAN LOKAL
    LOCAL_DB = "log_kegiatan_lokal.csv"

    # 1. BACA DATA DARI FILE LOKAL
    if os.path.exists(LOCAL_DB):
        df_log = pd.read_csv(LOCAL_DB)
    else:
        # Jika file belum ada, buat template kosong
        df_log = pd.DataFrame(columns=["Tgl Kegiatan", "Nama Kegiatan", "No Surat/Jumlah", "Tujuan Kegiatan", "Keterangan"])

    # 2. FORM INPUT
    with st.form("form_kegiatan", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Tanggal", datetime.now())
        nama = c2.text_input("Nama Kegiatan")
        no_surat = st.text_input("No Surat/Jumlah")
        tujuan = st.text_input("Tujuan")
        ket = st.text_area("Keterangan")
        
        # Tombol Simpan sekarang langsung menulis ke file
        submit = st.form_submit_button("💾 Simpan Kegiatan")
        
        if submit:
            if nama:
                # Membuat data baru
                new_data = pd.DataFrame([{
                    "Tgl Kegiatan": tgl.strftime('%Y-%m-%d'),
                    "Nama Kegiatan": nama,
                    "No Surat/Jumlah": no_surat,
                    "Tujuan Kegiatan": tujuan,
                    "Keterangan": ket
                }])
                
                # Gabungkan dengan data lama
                df_combined = pd.concat([df_log, new_data], ignore_index=True)
                
                # Simpan ke CSV lokal
                df_combined.to_csv(LOCAL_DB, index=False)
                
                st.success(f"✅ Berhasil menyimpan kegiatan: {nama}")
                st.rerun() # Refresh tampilan agar data baru muncul
            else:
                st.warning("Nama kegiatan harus diisi!")

    st.divider()
    
    # 3. TAMPILKAN RIWAYAT & TOMBOL DOWNLOAD
    st.markdown("### 📋 Riwayat Kegiatan")
    if not df_log.empty:
        st.dataframe(df_log, use_container_width=True)
        
        # Fitur tambahan: Download data yang sudah terkumpul
        csv_download = df_log.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Semua Log (Excel/CSV)",
            data=csv_download,
            file_name="riwayat_kegiatan.csv",
            mime="text/csv"
        )
    else:
        st.info("Belum ada riwayat kegiatan.")
