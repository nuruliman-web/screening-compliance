import streamlit as st
import pandas as pd
import time
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan Unit AML</h3>", unsafe_allow_html=True)
    
    # 1. Database Session
    if 'log_kegiatan' not in st.session_state:
        st.session_state.log_kegiatan = []

    # 2. Form Input
    with st.expander("➕ Input Kegiatan Baru", expanded=True):
        with st.form("form_kegiatan", clear_on_submit=True):
            c1, c2 = st.columns(2)
            tgl = c1.date_input("Tanggal Kegiatan", datetime.now())
            nama = c2.text_input("Nama Kegiatan", placeholder="LTKT, Pelatihan, News, dsb")
            
            c3, c4 = st.columns(2)
            no_surat = c3.text_input("No Surat / Jumlah Peserta")
            tujuan = c4.text_input("Tujuan Kegiatan")
            
            # Tambahan Kolom Keterangan di Form
            ket = st.text_area("Keterangan Tambahan", placeholder="Masukkan catatan jika ada...")
            
            if st.form_submit_button("💾 Masukkan ke Daftar"):
                if nama:
                    st.session_state.log_kegiatan.append({
                        "Tgl Kegiatan": tgl.strftime("%d/%m/%Y"),
                        "Nama Kegiatan": nama,
                        "No Surat/Jumlah": no_surat,
                        "Tujuan Kegiatan": tujuan,
                        "Keterangan": ket  # <--- Simpan keterangan
                    })
                    st.toast("Kegiatan dicatat!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Nama kegiatan wajib diisi!")

    st.divider()

    # 3. Tabel Tracker (Edit Only)
    st.markdown("### 📋 History Track")
    if st.session_state.log_kegiatan:
        df = pd.DataFrame(st.session_state.log_kegiatan)
        df.insert(0, 'No', range(1, len(df) + 1))
        
        # Konfigurasi Editor
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed", # Biar nggak bisa dihapus
            column_config={
                "No": st.column_config.Column(disabled=True, width="small"),
                "Tgl Kegiatan": st.column_config.TextColumn("Tanggal", width="small"),
                "Nama Kegiatan": st.column_config.TextColumn("Kegiatan", width="medium"),
                "Keterangan": st.column_config.TextColumn("Keterangan", width="large"),
            }
        )
        
        col_s, col_d = st.columns([4, 1])
        if col_s.button("💾 Simpan Perubahan Edit", use_container_width=True):
            # Simpan balik ke session tanpa kolom No
            st.session_state.log_kegiatan = edited_df.drop(columns=['No']).to_dict('records')
            st.success("Perubahan disimpan!")
            time.sleep(0.5)
            st.rerun()
            
        # Download Report (Pemisah titik koma agar rapi di Excel)
        csv = edited_df.to_csv(index=False, sep=";").encode('utf-8')
        col_d.download_button("📥 CSV", csv, "Log_AML.csv", "text/csv", use_container_width=True)
    else:
        st.info("Belum ada data.")
