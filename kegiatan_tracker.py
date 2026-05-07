import streamlit as st
import pandas as pd
import time
from datetime import datetime

def run_kegiatan_tracker():
    st.markdown("<h1 style='text-align: center; color: #0F172A;'>📝 Log Kegiatan & Tracker AML</h1>", unsafe_allow_html=True)
    st.write("Gunakan halaman ini untuk mencatat laporan LTKT, LTKM, pelatihan, news, dan kegiatan lainnya.")

    # --- 1. DATABASE SESSION ---
    if 'log_kegiatan' not in st.session_state:
        st.session_state.log_kegiatan = []

    # --- 2. FORM INPUT (Manual 1 per 1) ---
    with st.container(border=True):
        st.markdown("### ➕ Tambah Kegiatan Baru")
        with st.form("form_input_kegiatan", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tgl = st.date_input("Tanggal Kegiatan", datetime.now())
                nama = st.text_input("Nama Kegiatan", placeholder="Contoh: Laporan LTKT, Pelatihan Cabang...")
            
            with col2:
                no_surat = st.text_input("No Surat / Jumlah Peserta", placeholder="Contoh: SR-123 / 50 Orang")
                tujuan = st.text_input("Tujuan Kegiatan", placeholder="Contoh: Kepatuhan Regulator / Awareness")
            
            submit_btn = st.form_submit_button("🚀 Masukkan ke Daftar", use_container_width=True)

            if submit_btn:
                if nama:
                    # Simpan data ke session
                    new_entry = {
                        "Tgl Kegiatan": tgl.strftime("%d/%m/%Y"),
                        "Nama Kegiatan": nama,
                        "No Surat/Jumlah": no_surat,
                        "Tujuan Kegiatan": tujuan
                    }
                    st.session_state.log_kegiatan.append(new_entry)
                    st.success("Berhasil dicatat!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("Nama Kegiatan tidak boleh kosong!")

    st.divider()

    # --- 3. TABEL TRACKER (EDIT ONLY - NO DELETE) ---
    st.markdown("### 📋 History Track Kegiatan")
    
    if st.session_state.log_kegiatan:
        # Convert ke DataFrame
        df_log = pd.DataFrame(st.session_state.log_kegiatan)
        
        # Tambahkan Nomor Urut otomatis (No)
        df_log.insert(0, 'No', range(1, len(df_log) + 1))

        # Tampilkan Tabel Editor
        # num_rows="fixed" memastikan user tidak bisa hapus baris atau tambah baris di tabel
        edited_df = st.data_editor(
            df_log,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed", 
            column_config={
                "No": st.column_config.Column(disabled=True, width="small"), # No tidak bisa diedit
                "Tgl Kegiatan": st.column_config.TextColumn("Tanggal", width="medium"),
                "Nama Kegiatan": st.column_config.TextColumn("Nama Kegiatan", width="large"),
                "No Surat/Jumlah": st.column_config.TextColumn("No Surat / Jumlah"),
                "Tujuan Kegiatan": st.column_config.TextColumn("Tujuan"),
            }
        )

        # Tombol Simpan jika ada perubahan data di sel tabel
        c1, c2 = st.columns([4, 1])
        if c1.button("💾 Simpan Perubahan Edit", use_container_width=True):
            # Update session state (buang kolom 'No' sebelum simpan balik)
            st.session_state.log_kegiatan = edited_df.drop(columns=['No']).to_dict('records')
            st.toast("Perubahan berhasil disimpan!")
            time.sleep(0.5)
            st.rerun()

        # Tombol Download buat laporan
        csv = edited_df.to_csv(index=False, sep=";").encode('utf-8')
        c2.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"Log_Kegiatan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            use_container_width=True
        )

    else:
        st.info("Belum ada data kegiatan. Silakan isi form di atas.")

if __name__ == "__main__":
    run_kegiatan_tracker()
