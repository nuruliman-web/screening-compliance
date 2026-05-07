import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah 2026")
    st.write("Monitoring realisasi KYC Review bulanan terhadap target tahunan.")

    # --- 1. SETUP DATA TARGET (Urutan Pertama) ---
    # Data berdasarkan tabel target yang kamu kasih sebelumnya
    data_target = {
        'Cabang': [
            'KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 
            'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'
        ],
        'Target_Perorangan': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6],
        'Target_Badan_Usaha': [32, 3, 0, 0, 1, 2, 1, 0, 0, 7, 0]
    }
    # Definisikan df_target di sini supaya tidak error 'not defined'
    df_target = pd.DataFrame(data_target)
    # Hitung total target per baris (Perorangan + BU)
    df_target['Total_Target'] = df_target['Target_Perorangan'] + df_target['Target_Badan_Usaha']

    # --- 2. SETUP DATA REALISASI ---
    # Simulasi data yang sudah dikerjakan (Update ini tiap bulan)
    realisasi_data = {
        'Cabang': df_target['Cabang'],
        'Jan': [10, 2, 5, 4, 3, 1, 12, 0, 5, 10, 1],
        'Feb': [20, 1, 10, 5, 6, 2, 18, 2, 4, 15, 2],
        'Mar': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Contoh bulan berjalan
    }
    df_realisasi = pd.DataFrame(realisasi_data)

    # --- 3. LOGIKA PERHITUNGAN ---
    # Hitung total yang sudah dikerjakan sampai saat ini
    df_target['Realisasi_Total'] = df_realisasi[['Jan', 'Feb', 'Mar']].sum(axis=1)
    # Hitung sisa yang belum dikerjakan
    df_target['Sisa_Target'] = df_target['Total_Target'] - df_target['Realisasi_Total']
    # Hitung persentase pencapaian
    df_target['Persentase'] = (df_target['Realisasi_Total'] / df_target['Total_Target'] * 100).round(1)

    # --- 4. TAMPILAN KPI (TOP METRICS) ---
    t_target = df_target['Total_Target'].sum()
    t_realisasi = df_target['Realisasi_Total'].sum()
    t_sisa = df_target['Sisa_Target'].sum()
    pct_total = round((t_realisasi / t_target * 100), 1)

    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 Total Target 2026", f"{t_target} Akun")
    m2.metric("✅ Total Realisasi", f"{t_realisasi} Akun", f"{pct_total}%")
    m3.metric("⏳ Sisa Backlog", f"{t_sisa} Akun", delta_color="inverse")

    st.divider()

    # --- 5. GRAFIK MONITORING ---
    st.markdown("**📊 Grafik Realisasi per Cabang**")
    # Tampilkan chart batang sederhana
    chart_data = df_target.set_index('Cabang')[['Realisasi_Total', 'Total_Target']]
    st.bar_chart(chart_data)

    # --- 6. TABEL DETAIL DENGAN WARNA ---
    st.markdown("**📋 Detail Tabel Monitoring Pengkinian Data**")
    
    def style_persentase(val):
        # Merah jika < 30%, Kuning < 70%, Hijau jika sudah tinggi
        color = 'red' if val < 30 else 'orange' if val < 70 else 'green'
        return f'background-color: {color}; color: white; font-weight: bold'

    # Pilih kolom yang mau ditampilkan
    df_display = df_target[['Cabang', 'Target_Perorangan', 'Target_Badan_Usaha', 'Total_Target', 'Realisasi_Total', 'Sisa_Target', 'Persentase']]
    
    st.dataframe(
        df_display.style.applymap(style_persentase, subset=['Persentase']),
        use_container_width=True,
        hide_index=True
    )

    st.info("Catatan: Data realisasi diupdate secara manual pada kodingan setiap awal bulan setelah proses rekapitulasi.")
