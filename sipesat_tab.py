import streamlit as st

def run_sipesat():
    st.markdown("### 📝 Pembaca File SIPESAT (.tab / .txt)")
    st.write("Silakan upload file dengan format **.tab** atau **.txt** kamu di bawah ini untuk melihat isinya.")

    # --- TOMBOL UPLOAD FILE ---
    # Di sini kita tambahkan 'tab' di bagian type agar diizinkan oleh Streamlit
    uploaded_file = st.file_uploader(
        "📤 Upload File (.tab atau .txt)", 
        type=["tab", "txt"], 
        key="uploader_tab_sipesat"
    )

    if uploaded_file is not None:
        try:
            # 1. Membaca isi file .tab sebagai teks string
            isi_teks = uploaded_file.read().decode("utf-8", errors="ignore")
            
            st.success(f"✅ File {uploaded_file.name} berhasil dibaca!")
            
            # 2. Menampilkan isi dokumen ke dalam kotak teks di Streamlit
            st.subheader("📄 Preview Isi File:")
            st.text_area(
                label="Isi dokumen asli:", 
                value=isi_teks, 
                height=400, 
                disabled=True
            )
            
            # Menyimpan isi teks ke memori session agar aman
            st.session_state['isi_file_tab_sipesat'] = isi_teks
            
            st.info("💡 Isinya sudah muncul di atas. Silakan dicek dulu apakah datanya sudah kelihatan kelihatan rapi atau belum!")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")

# Memanggil fungsi agar menu langsung muncul di tab
run_sipesat()
