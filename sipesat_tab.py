import streamlit as st
import pandas as pd

def run_sipesat():
    st.markdown("### 📊 Pembaca File SIPESAT .tab")
    st.write("Silakan upload file `.tab` kamu di bawah ini.")

    # --- TOMBOL UPLOAD FILE (DIPERBAIKI) ---
    # Kita hapus pembatasan type agar Streamlit tidak crash duluan saat file dimasukkan
    uploaded_file = st.file_uploader(
        "📤 Upload File .tab Kamu", 
        type=None, 
        key="uploader_tab_sipesat_final"
    )

    if uploaded_file is not None:
        try:
            # Pastikan yang dimasukkan benar file yang berakhiran .tab
            if not uploaded_file.name.endswith('.tab'):
                st.warning("⚠️ Mohon masukkan file yang berakhiran format .tab")
                return

            # Membaca data mentah dari file .tab dengan pembatas TAB (\t)
            # header=None karena file tidak memiliki judul di baris pertama
            df = pd.read_csv(
                uploaded_file, 
                sep='\t', 
                header=None, 
                dtype=str, 
                encoding='utf-8', 
                encoding_errors='ignore'
            )
            
            st.success(f"✅ File '{uploaded_file.name}' BERHASIL MASUK DAN DIBACA!")
            st.info(f"📋 Terdeteksi: {len(df)} baris data dan {len(df.columns)} kolom.")
            
            # Menampilkan hasil pembacaan ke layar berbentuk tabel nomor
            st.subheader("👀 Preview Data Tabel:")
            st.dataframe(df, use_container_width=True)
            
            # Menyimpan data asli ke memori agar aman
            st.session_state['data_mentah_tab'] = df

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat membaca jeroan file: {e}")
