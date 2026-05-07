import streamlit as st
import pandas as pd
import time
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan & Tracker Unit AML</h3>", unsafe_allow_html=True)
    
    # --- 1. INISIALISASI SESSION STATE ---
    if 'log_kegiatan' not in st.session_state:
        st.session_state.log_kegiatan = []

    # --- 2. FORM INPUT KEGIATAN ---
    with st.expander("➕ Input Kegiatan Baru", expanded=True):
        with st.form("form_kegiatan_aml", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tgl = st.date_input("Tanggal", datetime.now())
                nama = st.text_input("Nama Kegiatan", placeholder="LTKT / Pelatihan / dsb")
            with col2:
                no_surat = st.text_input("No Surat / Jumlah Peserta")
                tujuan = st.text_input("Tujuan Kegiatan")
            
            if st.form_submit_button("Simpan ke Tabel"):
                if nama:
                    new_data = {
                        "Tgl Kegiatan": tgl.strftime("%d/%m/%Y"),
                        "Nama Kegiatan": nama,
                        "No Surat/Jumlah": no_surat,
                        "Tujuan Kegiatan": tujuan
                    }
                    st.session_state.log_kegiatan.append(new_data)
                    st.success("Data berhasil ditambahkan!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("Nama Kegiatan wajib diisi.")

    st.divider()

    # --- 3. TABEL TRACKER ---
    st.markdown("### 📋 History Kegiatan")
    
    if st.session_state.log_kegiatan:
        df_log = pd.DataFrame(st.session_state.log_kegiatan)
        # Tambah kolom No di awal
        df_log.insert(0, 'No', range(1, len(df_log) + 1))
        
        # Tabel Editor (Bisa Edit, Tidak bisa Hapus baris)
        edited_log = st.data_editor(
            df_log,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed", # Kunci baris agar tidak bisa dihapus
            column_config={
                "No": st.column_config.Column(disabled=True, width="small"),
                "Tgl Kegiatan": st.column_config.TextColumn("Tanggal", alignment="center"),
                "Nama Kegiatan": st.column_config.TextColumn("Kegiatan", alignment="center"),
                "No Surat/Jumlah": st.column_config.TextColumn("No Surat/Jumlah", alignment="center"),
                "Tujuan Kegiatan": st.column_config.TextColumn("Tujuan", alignment="center"),
            }
        )
        
        c1, c2 = st.columns([4, 1])
        if c1.button("💾 Simpan Perubahan Edit", use_container_width=True):
            # Simpan balik ke session (buang kolom No)
            st.session_state.log_kegiatan = edited_log.drop(columns=['No']).to_dict('records')
            st.toast("Perubahan disimpan!")
            time.sleep(0.5)
            st.rerun()
            
        # Download Report
        csv_data = edited_log.to_csv(index=False, sep=";").encode('utf-8')
        c2.download_button("📥 CSV", csv_data, "Log_Kegiatan.csv", "text/csv", use_container_width=True)
    else:
        st.info("Belum ada data kegiatan.")
