import streamlit as st

def run_sipesat():
    st.markdown("### 📝 Pembaca File Notepad (.txt) SIPESAT")
    st.write("Silakan upload file Notepad kamu di bawah ini untuk melihat isinya.")

    # --- TOMBOL UPLOAD FILE NOTEPAD ---
    uploaded_txt = st.file_uploader(
        "📤 Upload File Notepad (.txt)", 
        type=["txt"], 
        key="uploader_notepad_sipesat"
    )

    if uploaded_txt is not None:
        try:
            # 1. Membaca isi file notepad sebagai teks string
            # Menggunakan isi file yang di-upload langsung
            isi_teks = uploaded_txt.read().decode("utf-8", errors="ignore")
            
            st.success("✅ File Notepad berhasil dibaca!")
            
            # 2. Menampilkan isi notepad ke dalam kotak teks di Streamlit
            st.subheader("📄 Isi File Notepad Kamu:")
            st.text_area(
                label="Isi dokumen asli:", 
                value=isi_teks, 
                height=400, 
                disabled=True
            )
            
            # Menyimpan isi teks ke memori session agar tidak hilang saat di-refresh
            st.session_state['isi_notepad_sipesat'] = isi_teks
            
            st.info("💡 Isi file sudah muncul di atas. Silakan dicek apakah datanya sudah sesuai!")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file notepad: {e}")

# Memanggil fungsi agar menu langsung muncul di tab
run_sipesat()
