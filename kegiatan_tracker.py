import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h3 style='text-align: center;'>📝 Log Kegiatan (Sync to GSheets)</h3>", unsafe_allow_html=True)
    
    # 1. KONEKSI GSHEETS
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # 2. LOAD DATA DARI TAB 'Kegiatan_Log'
    try:
        # Coba baca data (ttl=0 biar fresh)
        df_gsheet = conn.read(worksheet="Kegiatan_Log", ttl=0)
        df_gsheet = df_gsheet.dropna(how='all')
        
        # Jika berhasil baca tanpa error, tampilkan indikator sukses kecil
        st.caption("✅ Terhubung ke Google Sheets")
        
    except Exception as e:
        # Jika error (misal nama tab salah atau belum jadi Editor)
        st.error(f"⚠️ Koneksi GSheets Bermasalah: {e}")
        st.info("Pastikan Tab 'Kegiatan_Log' sudah ada dan izin GSheets sudah 'Editor'.")
        df_gsheet = pd.DataFrame(columns=["Tgl Kegiatan", "Nama Kegiatan", "No Surat/Jumlah", "Tujuan Kegiatan", "Keterangan"])

    # Simpan ke session state
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
                    
                    # Gabungkan data lama dengan baris baru
                    updated_df = pd.concat([df_gsheet, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # KIRIM KE GSHEETS
                    try:
                        conn.update(worksheet="Kegiatan_Log", data=updated_df)
                        st.success("Data berhasil tersimpan di Google Sheets!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal mengirim data: {e}")
                else:
                    st.warning("Nama kegiatan tidak boleh kosong!")

    st.divider()

    # 4. TAMPILKAN DAN EDIT DATA
    if st.session_state.log_kegiatan:
        df_display = pd.DataFrame(st.session_state.log_kegiatan)
        
        # Tambahkan nomor urut
        df_display.insert(0, 'No', range(1, len(df_display) + 1))
        
        st.markdown("### 📋 Riwayat Kegiatan")
        edited_df = st.data_editor(
            df_display, 
            use_container_width=True, 
            hide_index=True, 
            num_rows="dynamic"
        )
        
        if st.button("💾 Simpan Perubahan Edit"):
            try:
                final_df = edited_df.drop(columns=['No'])
                conn.update(worksheet="Kegiatan_Log", data=final_df)
                st.success("Perubahan tabel berhasil disinkronkan!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal update: {e}")
    else:
        st.info("Belum ada data di Google Sheets.")
