import streamlit as st
import pandas as pd

def run_sipesat():
    st.markdown("### 📊 Pembaca File SIPESAT .tab (Tanpa Header)")
    st.write("Silakan upload file `.tab` kamu. Sistem akan otomatis menyusunnya menjadi kolom nomor.")

    # --- TOMBOL UPLOAD FILE ---
    uploaded_file = st.file_uploader(
        "📤 Upload File .tab Kamu", 
        type=["tab", "txt"], 
        key="uploader_tab_tanpa_header"
    )

    if uploaded_file is not None:
        try:
            # Membaca file .tab yang tidak memiliki judul baris atas (header=None)
            # Ditambahkan encoding_errors='ignore' supaya anti-crash jika ada karakter aneh
            df = pd.read_csv(
                uploaded_file, 
                sep='\t', 
                header=None, 
                dtype=str, 
                encoding='utf-8', 
                encoding_errors='ignore'
            )
            
            st.success(f"✅ Berhasil memproses file: {uploaded_file.name}")
            st.info(f"📋 Terdeteksi total: {len(df)} baris data dan {len(df.columns)} kolom.")
            
            # Menampilkan preview tabel ke layar
            st.subheader("👀 Preview Data Hasil Pembacaan:")
            st.dataframe(df, use_container_width=True)
            
            # Menyimpan data asli ke memory session state
            st.session_state['data_mentah_tab'] = df

        except Exception as e:
            st.error(f"❌ Gagal membaca file. Pesan error: {e}")

# Memastikan fungsi dipanggil agar tombol upload muncul di aplikasi
