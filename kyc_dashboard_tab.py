import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah 2026")
    st.write("Monitoring pencapaian KYC Review Cabang secara bulanan.")

    # 1. DATA TARGET (Berdasarkan Data Perbankan)
    data_target = {
        'Cabang': [
            'KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 
            'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'
        ],
        'Target_Perorangan': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6],
        'Target_Badan_Usaha': [32, 3, 0, 0, 1, 2, 1, 0, 0, 7, 0]
    }
    df_target = pd.DataFrame(data_target)

    # 2. DATA REALISASI (Simulasi input tiap bulan)
    realisasi_dummy = {
        'Cabang': df_target['Cabang'],
        'Jan': [15, 2, 8, 5, 4, 1, 10, 1, 3, 12, 1],
        'Feb': [25, 3, 10, 6, 8, 2, 15, 2, 4, 15, 2],
    }
    df_realisasi = pd.DataFrame(realisasi_dummy)

    # Hitung Total
    total_target_per_br = df_target['Target_Perorangan'] + df_target['Target_Badan_Usaha']
    df_target['Realisasi_Total'] = df_realisasi[['Jan', 'Feb']].sum(axis=1)
    df_target['Sisa_Target'] = total_target_per_br - df_target['Realisasi_Total']
    df_target['Persentase'] = (df_target['Realisasi_Total'] / total_target_per_br * 100).round(1)

    # 3. METRICS UTAMA
    total_t = total_target_per_br.sum()
    total_r = df_target['Realisasi_Total'].sum()
    overall_pct = round((total_r / total_t) * 100, 1)

    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 Total Target 2026", f"{total_t} Akun")
    m2.metric("✅ Total Realisasi", f"{total_r} Akun", f"{overall_pct}%")
    m3.metric("⏳ Sisa Backlog", f"{total_t - total_r} Akun")

    st.divider()

    # 4. VISUALISASI SEDERHANA (Tanpa Plotly - Pasti Jalan)
    st.markdown("**📊 Progress Realisasi per Cabang**")
    # Bikin bar chart horizontal pake bawaan streamlit
    chart_data = df_target.set_index('Cabang')[['Realisasi_Total']]
    st.bar_chart(chart_data)

    # 5. TABEL MONITORING DENGAN WARNA
    st.markdown("**📋 Detail Monitoring Cabang**")
    
    def color_pct(val):
        color = 'red' if val < 30 else 'orange' if val < 70 else 'green'
        return f'background-color: {color}; color: white'

    df_show = df_target[['Cabang', 'Target_Perorangan', 'Target_Badan_Usaha', 'Realisasi_Total', 'Sisa_Target', 'Persentase']]
    
    # Menampilkan tabel dengan highlight pada kolom persentase
    st.dataframe(
        df_show.style.applymap(color_pct, subset=['Persentase']),
        use_container_width=True,
        hide_index=True
    )

    st.info("💡 Data di atas direkap setiap awal bulan berdasarkan hasil pengkinian data di sistem Core Banking.")
