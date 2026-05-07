import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Nama file database permanen
DB_FILE = "data_kegiatan.csv"

def load_data_permanen():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE, sep=";").to_dict('records')
    return []

def save_data_permanen(data_list):
    df = pd.DataFrame(data_list)
    df.to_csv(DB_FILE, index=False, sep=";")

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan (Auto-Save)</h3>", unsafe_allow_html=True)
    
    # Ambil data dari file saat pertama kali buka
    if 'log_kegiatan' not in st.session_state:
        st.session_state.log_kegiatan = load_data_permanen()

    with st.expander("➕ Input Kegiatan Baru", expanded=True):
        with st.form("form_kegiatan", clear_on_submit=True):
            c1, c2 = st.columns(2)
            tgl = c1.date_input("Tanggal", datetime.now())
            nama = c2.text_input("Nama Kegiatan")
            c3, c4 = st.columns(2)
            no_surat = c3.text_input("No Surat/Jumlah")
            tujuan = c4.text_input("Tujuan")
            ket = st.text_area("Keterangan")
            
            if st.form_submit_button("💾 Simpan Permanen"):
                if nama:
                    st.session_state.log_kegiatan.append({
                        "Tgl Kegiatan": tgl.strftime("%d/%m/%Y"),
                        "Nama Kegiatan": nama,
                        "No Surat/Jumlah": no_surat,
                        "Tujuan Kegiatan": tujuan,
                        "Keterangan": ket
                    })
                    # LANGSUNG SIMPAN KE FILE
                    save_data_permanen(st.session_state.log_kegiatan)
                    st.success("Data tersimpan permanen di server!")
                    st.rerun()

    st.divider()

    if st.session_state.log_kegiatan:
        df = pd.DataFrame(st.session_state.log_kegiatan)
        df.insert(0, 'No', range(1, len(df) + 1))
        
        edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="fixed")
        
        if st.button("💾 Update Perubahan Edit"):
            st.session_state.log_kegiatan = edited_df.drop(columns=['No']).to_dict('records')
            save_data_permanen(st.session_state.log_kegiatan) # Simpan perubahan edit
            st.success("Perubahan berhasil diperbarui!")
    else:
        st.info("Belum ada data tersimpan.")
