import streamlit as st
import pandas as pd

def run_sipesat():
    st.markdown("### 📊 Pembaca File SIPESAT (.tab / .txt / .csv)")
    st.write("Silakan upload file `.tab` kamu di bawah ini untuk melihat isinya dalam bentuk tabel rapi.")

    # --- TOMBOL UPLOAD FILE ---
    # Kita izinkan format tab, txt, dan csv sekalian agar fleksibel
    uploaded_file = st.file_uploader(
        "📤 Upload File Kamu", 
        type=["tab", "txt", "csv"], 
        key="uploader_tab_sipesat"
    )

    if uploaded_file is not None:
        try:
            # 1. Deteksi format pembatas (jika .tab atau .txt biasanya pakai Tab/sep='\t')
            if uploaded_file.name.endswith('.csv'):
                sep_karakter = ','
            else:
                sep_karakter = '\t' # Karakter TAB untuk file .tab

            # 2. Membaca file dengan aman (mengabaikan error karakter aneh & memaksa string)
            df = pd.read_csv(
                uploaded_file, 
                sep=sep_karakter, 
                dtype=str, 
                encoding='utf-8', 
                encoding_errors='ignore'
            )
            
            st.success(f"✅ File '{uploaded_file.name}' berhasil dibaca dengan sempurna!")
            
            # 3. Menampilkan info jumlah data
            st.info(f"📋 Total data yang terdeteksi: {len(df)} baris dan {len(df.columns)} kolom.")
            
            # 4. Menampilkan isi dokumen dalam bentuk TABEL RAPI (bisa di-scroll)
            st.subheader("📊 Preview Data Tabel:")
            st.dataframe(df, use_container_width=True)
            
            # Menyimpan data ke memori session state agar bisa diolah nanti
            st.session_state['data_tab_sipesat'] = df

        except Exception as e:
            st.error(f"❌ Gagal membaca file. Error sistem: {e}")
            st.info("💡 Tips: Pastikan file tidak sedang dibuka di Excel saat di-upload.")
