import streamlit as st
import pandas as pd
import io

def run_sipesat():
    st.markdown("### 📋 Pengolahan Laporan Triwulan SIPESAT")
    st.write("Tahap 1: Tentukan periode pelaporan dan unggah File Pertama (M4CU).")

    # --- INPUT PILIHAN TRIWULAN DAN TAHUN ---
    st.subheader("🗓️ Pilih Periode Laporan")
    col_tw, col_thn = st.columns(2)
    
    with col_tw:
        triwulan_pilihan = st.selectbox(
            "⏳ Pilih Triwulan (Quarter):",
            [
                "Triwulan 1 (Januari - Maret)",
                "Triwulan 2 (April - Juni)",
                "Triwulan 3 (Juli - September)",
                "Triwulan 4 (Oktober - Desember)"
            ],
            key="sipesat_tw"
        )
        
    with col_thn:
        tahun_pilihan = st.number_input(
            "📅 Masukkan Tahun:",
            min_value=2000,
            max_value=2099,
            value=2026,
            step=1,
            key="sipesat_tahun"
        )

    st.divider()

    # --- UPLOAD FILE UTAMA ---
    st.subheader("📤 Upload File")
    uploaded_file1 = st.file_uploader(
        "Pilih File Pertama (M4CU)", 
        type=["csv", "xlsx", "xls"], 
        key="uploader_m4cu"
    )

    if uploaded_file1 is not None:
        try:
            # 1. Membaca file dan memaksa tipe data string agar data angka/kode aman
            if uploaded_file1.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file1, dtype=str)
            else:
                df_raw = pd.read_excel(uploaded_file1, dtype=str)
            
            # Membersihkan nama kolom dari spasi tidak terlihat
            df_raw.columns = df_raw.columns.str.strip()

            # 2. Menentukan Batas Bulan Berdasarkan Triwulan yang Dipilih User
            if "Triwulan 1" in triwulan_pilihan:
                bulan_start, bulan_end = "01", "03"
            elif "Triwulan 2" in triwulan_pilihan:
                bulan_start, bulan_end = "04", "06"
            elif "Triwulan 3" in triwulan_pilihan:
                bulan_start, bulan_end = "07", "09"
            else:
                bulan_start, bulan_end = "10", "12"

            # Membuat format tanggal YYYYMMDD untuk menyaring data
            start_date = f"{tahun_pilihan}{bulan_start}01"
            end_date = f"{tahun_pilihan}{bulan_end}31"

            # 3. Validasi & Filter Kolom T (Beginning Date Customer)
            if 'Beginning Date Customer' in df_raw.columns:
                df_raw['Beginning Date Customer'] = df_raw['Beginning Date Customer'].fillna('').astype(str).str.strip()
                
                # Filter data berdasarkan range tanggal triwulan
                kondisi_tanggal = (df_raw['Beginning Date Customer'] >= start_date) & (df_raw['Beginning Date Customer'] <= end_date)
                df_filtered = df_raw[kondisi_tanggal].copy()
            else:
                st.error("❌ Kolom 'Beginning Date Customer' tidak ditemukan pada file M4CU!")
                return

            # Jika hasil filter kosong
            if df_filtered.empty:
                st.warning(f"⚠️ Tidak ditemukan data nasabah baru untuk {triwulan_pilihan} Tahun {tahun_pilihan}.")
                return

            st.success(f"✅ Berhasil memproses data! Ditemukan {len(df_filtered)} nasabah baru.")

            # 4. Pembersihan Data 8 Kolom Hijau yang Ditentukan
            kolom_wajib = ['Customer code', 'Customer Name', 'Address-1', 'Address-2', 'City', 'NPWP Nasabah', 'Customer type']
            for col in kolom_wajib:
                if col in df_filtered.columns:
                    df_filtered[col] = df_filtered[col].fillna('').astype(str).str.strip()

            # Logika Menggabungkan Kolom E, F, G menjadi satu Alamat Kapital
            def gabung_alamat_lengkap(row):
                komponen = []
                if row.get('Address-1'): komponen.append(row['Address-1'])
                if row.get('Address-2'): komponen.append(row['Address-2'])
                if row.get('City'): komponen.append(row['City'])
                return ", ".join(komponen).upper()

            df_filtered['ALAMAT_MUTASI'] = df_filtered.apply(gabung_alamat_lengkap, axis=1)

            # Logika Membaca Tipe Konsumen dari Kolom AF (I atau C)
            def cek_tipe_nasabah(x):
                if x.upper() == 'I': return "I (Individu)"
                elif x.upper() == 'C': return "C (Company)"
                return x

            df_filtered['TIPE_DETAIL'] = df_filtered['Customer type'].apply(cek_tipe_nasabah)

            # 5. Menyusun Output Hasil Penyaringan File Pertama
            df_hasil_m4cu = pd.DataFrame({
                'Customer Code (KEY)': df_filtered['Customer code'],
                'Nama Nasabah': df_filtered['Customer Name'].str.upper(),
                'Alamat Lengkap (E+F+G)': df_filtered['ALAMAT_MUTASI'],
                'NPWP': df_filtered['NPWP Nasabah'],
                'Tgl Registrasi (T)': df_filtered['Beginning Date Customer'],
                'Tipe (AF)': df_filtered['TIPE_DETAIL']
            })

            # Menyimpan daftar key Customer Code ke dalam memory session state untuk dicocokkan dengan File 2 nanti
            st.session_state['list_key_customer'] = df_filtered['Customer code'].tolist()

            # 6. Menampilkan Hasil Preview ke Layar Aplikasi
            st.subheader(f"📊 Hasil Filter Nasabah Baru - {triwulan_pilihan} ({tahun_pilihan})")
            st.dataframe(df_hasil_m4cu, use_container_width=True, hide_index=True)
            
            st.info("💡 Data kunci 'Customer Code' berhasil didapatkan. Silakan persiapkan File Kedua (GI) untuk dicocokkan.")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
