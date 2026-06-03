import streamlit as st
import pandas as pd
import io

def run_sipesat():
    st.markdown("### 📋 Pengolahan Laporan Triwulan SIPESAT (File 1: M4CU)")
    st.write("Tahap 1: Silakan pilih periode triwulan dan unggah File Pertama (M4CU).")

    # --- INPUT FILTER PERIODE ---
    col_thn, col_tw = st.columns(2)
    with col_thn:
        # Input Tahun (Default tahun berjalan 2026)
        tahun_pilihan = st.number_input("📅 Masukkan Tahun Laporan", min_value=2000, max_value=2099, value=2026, step=1)
    
    with col_tw:
        # Pilihan Triwulan
        triwulan = st.selectbox(
            "⏳ Pilih Triwulan (Quarter)",
            ["Triwulan 1 (Jan - Mar)", "Triwulan 2 (Apr - Jun)", "Triwulan 3 (Jul - Sep)", "Triwulan 4 (Okt - Des)"]
        )

    st.divider()

    # --- TOMBOL UPLOAD FILE 1 ---
    uploaded_file1 = st.file_uploader(
        "📤 Upload File Pertama (M4CU - format CSV atau Excel)", 
        type=["csv", "xlsx", "xls"], 
        key="uploader_m4cu"
    )

    if uploaded_file1 is not None:
        try:
            # 1. Membaca file (memaksa semua dibaca sebagai text/string agar format angka aman)
            if uploaded_file1.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file1, dtype=str)
            else:
                df_raw = pd.read_excel(uploaded_file1, dtype=str)
            
            st.success("✅ File M4CU berhasil di-upload!")

            # 2. Menentukan Batas Bulan Berdasarkan Triwulan yang Dipilih
            if "Triwulan 1" in triwulan:
                bulan_start, bulan_end = "01", "03"
            elif "Triwulan 2" in triwulan:
                bulan_start, bulan_end = "04", "06"
            elif "Triwulan 3" in triwulan:
                bulan_start, bulan_end = "07", "09"
            else:
                bulan_start, bulan_end = "10", "12"

            # Membuat range tanggal internal dalam format YYYYMMDD
            start_date = f"{tahun_pilihan}{bulan_start}01"
            # Menentukan tanggal akhir (handling kasar 30/31 desember/juni dll aman dengan string comparison)
            end_date = f"{tahun_pilihan}{bulan_end}31" 

            # 3. Proses Membersihkan Nama Kolom (menghindari spasi tak terlihat)
            df_raw.columns = df_raw.columns.str.strip()

            # 4. Filter Data Berdasarkan Kolom T (Beginning Date Customer)
            # Pastikan kolom T ada
            if 'Beginning Date Customer' in df_raw.columns:
                # Bersihkan data tanggal dari spasi kosong atau NaN
                df_raw['Beginning Date Customer'] = df_raw['Beginning Date Customer'].fillna('').astype(str).str.strip()
                
                # Cari yang masuk dalam range tanggal triwulan pilihan
                kondisi_tanggal = (df_raw['Beginning Date Customer'] >= start_date) & (df_raw['Beginning Date Customer'] <= end_date)
                df_filtered = df_raw[kondisi_tanggal].copy()
            else:
                st.error("❌ Kolom 'Beginning Date Customer' tidak ditemukan di file ini!")
                return

            # Cek apakah ada data yang lolos filter
            if df_filtered.empty:
                st.warning(f"⚠️ Tidak ada data nasabah baru di {triwulan} Tahun {tahun_pilihan}.")
                return
            
            st.info(f"🔍 Ditemukan {len(df_filtered)} nasabah baru untuk periode yang dipilih.")

            # 5. Ekstraksi dan Pemetaan 8 Kolom Hijau yang Disepakati
            # Mengisi kolom kosong dengan string kosong agar tidak muncul tulisan 'nan'
            for col in ['Customer code', 'Customer Name', 'Address-1', 'Address-2', 'City', 'NPWP Nasabah', 'Customer type']:
                if col in df_filtered.columns:
                    df_filtered[col] = df_filtered[col].fillna('').astype(str).str.strip()

            # Logika A: Melebur Kolom E, F, G menjadi 1 Kolom Alamat Lengkap
            def gabung_alamat(row):
                bagian = []
                if row.get('Address-1'): bagian.append(row['Address-1'])
                if row.get('Address-2'): bagian.append(row['Address-2'])
                if row.get('City'): bagian.append(row['City'])
                return ", ".join(bagian).upper() # Otomatis jadikan HURUF KAPITAL

            df_filtered['ALAMAT_GABUNGAN'] = df_filtered.apply(gabung_alamat, axis=1)

            # Logika B: Membaca Customer Type (AF)
            def arti_tipe(x):
                if x.upper() == 'I': return "I (Individu)"
                elif x.upper() == 'C': return "C (Company)"
                return x

            df_filtered['TIPE_KONSUMEN_DETAIL'] = df_filtered['Customer type'].apply(arti_tipe)

            # 6. Menyusun Tabel Hasil Sementara (Khusus Data File 1)
            # Kita siapkan struktur tabel untuk di-review user
            df_hasil_file1 = pd.DataFrame({
                'Customer Code (KEY)': df_filtered['Customer code'],
                'Nama Nasabah': df_filtered['Customer Name'].str.upper(),
                'Alamat Lengkap (E+F+G)': df_filtered['ALAMAT_GABUNGAN'],
                'NPWP': df_filtered['NPWP Nasabah'],
                'Tgl Registrasi (T)': df_filtered['Beginning Date Customer'],
                'Tipe (AF)': df_filtered['TIPE_KONSUMEN_DETAIL']
            })

            # Simpan data 'Customer Code' yang lolos ke dalam session_state agar bisa dibaca File 2 nanti
            st.session_state['list_key_customer'] = df_filtered['Customer code'].tolist()
            st.session_state['data_file1_filtered'] = df_hasil_file1

            # 7. Tampilkan Preview Hasil Filter ke Layar Streamlit
            st.subheader("✨ Preview Data Terfilter (File 1)")
            st.dataframe(df_hasil_file1, hide_index=True)

            # Tanda bahwa Tahap 1 Sukses
            st.success("💡 Kunci data (Customer Code) sudah disimpan! Silakan lanjut ke File Kedua (GI) jika sudah siap.")

        except Exception as e:
            st.error(f"Terjadi kesalahan sistem: {e}")
