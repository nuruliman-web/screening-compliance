import streamlit as st
import pandas as pd

# 1. Konfigurasi Tampilan
st.set_page_config(page_title="Compliance Screening", layout="wide")

st.title("🔍 Database Screening Tools")
st.write("Gunakan alat ini untuk memeriksa nama nasabah di database JUDOL, DTTOT, DPPSPM, dan SIPENDAR.")

# 2. Upload File di Sidebar
st.sidebar.header("📁 Database Management")
uploaded_file = st.sidebar.file_uploader("Upload File Excel Database", type=["xlsx"])

if uploaded_file:
    # Load semua sheet sekaligus
    # Kita tidak simpan di GitHub, tapi upload manual setiap sesi agar AMAN
    db_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    # 3. Input Nama yang Dicari
    search_query = st.text_input("Masukkan Nama Nasabah:", placeholder="Contoh: Budi Santoso")

    if search_query:
        query = search_query.strip().lower()
        found_any = False
        
        st.divider()
        st.subheader(f"Hasil Pencarian untuk: '{search_query}'")

        # Daftar sheet yang akan diperiksa sesuai permintaanmu
        target_sheets = ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']
        
        for sheet_name in target_sheets:
            if sheet_name in db_sheets:
                df = db_sheets[sheet_name]
                
                # LOGIKA PENCARIAN:
                # Memeriksa seluruh baris dan seluruh kolom secara otomatis
                # Mengabaikan besar/kecil huruf (Case Insensitive)
                mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(query, na=False).any(), axis=1)
                result = df[mask]

                if not result.empty:
                    found_any = True
                    with st.expander(f"🚩 TERDETEKSI DI SHEET: {sheet_name}", expanded=True):
                        st.warning(f"Ditemukan {len(result)} baris data yang cocok.")
                        st.dataframe(result, use_container_width=True)
            else:
                st.sidebar.error(f"Sheet '{sheet_name}' TIDAK DITEMUKAN!")

        # 4. Notifikasi Jika Hasil Nihil
        if not found_any:
            st.success("✅ HASIL NIHIL: Nama tersebut tidak ditemukan di database manapun.")
            st.balloons()
else:
    st.info("Silakan upload file Excel database melalui menu di sebelah kiri untuk memulai pencarian.")

# Footer Sidebar
st.sidebar.markdown("---")
st.sidebar.write("Maintainer: Admin Compliance")
