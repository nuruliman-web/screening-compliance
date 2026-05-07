import streamlit as st
import pandas as pd
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan</h3>", unsafe_allow_html=True)
    
    # ID Spreadsheet kamu
    sheet_id = "1jAiB7RPcjkEOZB7WoUaxOn55W1p7J8Hmyb2GBLaED4U"
    # URL untuk baca data (format CSV export)
    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Kegiatan_Log"

    # 1. BACA DATA
    try:
        df_gsheet = pd.read_csv(sheet_url)
    except:
        df_gsheet = pd.DataFrame(columns=["Tgl Kegiatan", "Nama Kegiatan", "No Surat/Jumlah", "Tujuan Kegiatan", "Keterangan"])

    # 2. FORM INPUT
    with st.form("form_kegiatan", clear_on_submit=True):
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Tanggal", datetime.now())
        nama = c2.text_input("Nama Kegiatan")
        no_surat = st.text_input("No Surat/Jumlah")
        tujuan = st.text_input("Tujuan")
        ket = st.text_area("Keterangan")
        
        submit = st.form_submit_button("💾 Simpan ke GSheets")
        
        if submit:
            if nama:
                # Karena simpan permanen ke GSheets butuh Service Account, 
                # Kita arahkan user untuk pakai cara manual yang tetap keren:
                
                new_row = f"{tgl.strftime('%d/%m/%Y')}\t{nama}\t{no_surat}\t{tujuan}\t{ket}"
                
                st.info("💡 Karena kebijakan keamanan Google, silakan salin baris di bawah ini dan paste ke baris terakhir Google Sheets kamu:")
                st.code(new_row)
                st.link_button("Buka Google Sheets", f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit")
            else:
                st.warning("Nama kegiatan harus diisi!")

    st.divider()
    st.markdown("### 📋 Riwayat Saat Ini")
    st.dataframe(df_gsheet, use_container_width=True)
