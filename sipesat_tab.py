import streamlit as st
import pandas as pd

def run_sipesat():
    st.markdown("### 📋 Pembaca File M4CU (.tab)")
    st.write("Silakan upload file `.tab` kamu di bawah ini untuk langsung melihat isinya.")

    # 1. Tombol Upload File (Tanpa batasan type agar Streamlit tidak error duluan)
    uploaded_file = st.file_uploader(
        "📤 Upload File .tab Kamu di Sini", 
        type=None, 
        key="uploader_sipesat_simple"
    )

    if uploaded_file is not None:
        try:
            # 2. Membaca file menggunakan pemisah Tab (\t) dan tanpa judul kolom (header=None)
            df = pd.read_csv(
                uploaded_file, 
                sep='\t', 
                header=None, 
                dtype=str, 
                encoding='utf-8', 
                encoding_errors='ignore'
            )
            
            st.success(f"✅ File '{uploaded_file.name}' berhasil dibaca!")
            st.info(f"📋 Total data: {len(df)} baris dan {len(df.columns)} kolom.")
            
            # 3. Langsung tampilkan isinya berupa tabel utuh di layar
            st.subheader("👀 Isi Data File Kamu:")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Gagal membaca isi file. Error: {e}")
