import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan (Sync to GSheets)</h3>", unsafe_allow_html=True)
    
    # 1. KONEKSI GSHEETS
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. LOAD DATA DARI TAB 'Kegiatan_Log'
    # ttl=0 supaya data selalu update saat di-refresh
    try:
        df_gsheet = conn.read(worksheet="Kegiatan_Log", ttl=0)
        # Bersihkan data kosong jika ada
        df_gsheet = df_gsheet.dropna(how='all')
    except Exception:
        df_gsheet = pd.DataFrame(columns=["Tgl Kegiatan", "Nama Kegiatan", "No Surat/Jumlah", "Tujuan Kegiatan", "Keterangan"])

    # Simpan ke session state agar sinkron dengan UI
    st.session_state.log_kegiatan = df_gsheet.to_dict('records')

    # 3. FORM INPUT
    with st.expander("➕ Input Kegiatan Baru", expanded=True):
        with st.form("form_kegiatan", clear_on_submit=True):
            c1, c2 = st.columns(2)
            tgl = c1.date_input("Tanggal", datetime.now())
            nama = c2.text_input("Nama Kegiatan")
            
            c3, c4 = st.columns(2)
            no_surat = c3.text_input("No Surat/Jumlah")
            tujuan = c4.text_input("Tujuan")
            
            ket = st.text_area("Keterangan")
            
            if st.form_submit_button("💾 Simpan Permanen ke GSheets"):
                if nama:
                    new_row = {
                        "Tgl Kegiatan": tgl.strftime("%d/%m/%Y"),
                        "Nama Kegiatan": nama,
                        "No Surat/Jumlah": no_surat,
                        "Tujuan Kegiatan": tujuan,
                        "Keterangan": ket
                    }
                    
                    # Tambahkan ke data lama
                    updated_df = pd.concat([df_gsheet, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # KIRIM KE GSHEETS
                    conn.update(worksheet="Kegiatan_Log", data=updated_df)
                    
                    st.success("Data berhasil tersimpan di Google Sheets!")
                    st.rerun()
                else:
                    st.warning("Nama kegiatan tidak boleh kosong!")

    st.divider()

    # 4. TAMPILKAN DAN EDIT DATA
    if st.session_state.log_kegiatan:
        df_display = pd.DataFrame(st.session_state.log_kegiatan)
        
        # Tambahkan nomor urut untuk tampilan
        df_display.insert(0, 'No', range(1, len(df_display) + 1))
        
        st.markdown("### 📋 Riwayat Kegiatan")
        edited_df = st.data_editor(
            df_display, 
            use_container_width=True, 
            hide_index=True, 
            num_rows="dynamic" # Bisa tambah/hapus baris langsung di tabel
        )
        
        # Tombol Update jika ada perubahan di tabel (data_editor)
        if st.button("💾 Simpan Perubahan Edit"):
            # Buang kolom 'No' sebelum simpan
            final_df = edited_df.drop(columns=['No'])
            conn.update(worksheet="Kegiatan_Log", data=final_df)
            st.success("Perubahan tabel berhasil disinkronkan!")
            st.rerun()
    else:
        st.info("Belum ada data di Google Sheets. Silakan input kegiatan baru.")
