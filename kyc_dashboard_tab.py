import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah 2026")
    st.write("Monitoring pencapaian KYC Review Cabang secara bulanan.")

    # 1. DATA TARGET (Berdasarkan Gambar yang Anda berikan)
    data_target = {
        'Cabang': [
            'KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 
            'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'
        ],
        'Target_Perorangan': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6],
        'Target_Badan_Usaha': [32, 3, 0, 0, 1, 2, 1, 0, 0, 7, 0] # Sesuai gambar Badan Usaha
    }
    df_target = pd.DataFrame(data_target)

    # 2. SIMULASI DATA REALISASI (Biasanya ditarik dari DB/Spreadsheet)
    # Di sini saya buatkan kolom bulan (Jan, Feb, dst) untuk contoh visualisasi trend
    # Angka ini yang nantinya diupdate tiap awal bulan
    realisasi_dummy = {
        'Cabang': df_target['Cabang'],
        'Jan': [10, 2, 5, 3, 4, 1, 15, 0, 5, 10, 1],
        'Feb': [20, 1, 8, 4, 5, 0, 12, 1, 3, 8, 2],
        'Mar': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # Belum jalan
    }
    df_realisasi = pd.DataFrame(realisasi_dummy)

    # Hitung Total Realisasi & Sisa
    df_target['Realisasi_Total'] = df_realisasi[['Jan', 'Feb', 'Mar']].sum(axis=1)
    df_target['Sisa_Target'] = df_target['Target_Perorangan'] + df_target['Target_Badan_Usaha'] - df_target['Realisasi_Total']
    df_target['Persentase'] = (df_target['Realisasi_Total'] / (df_target['Target_Perorangan'] + df_target['Target_Badan_Usaha']) * 100).round(1)

    # ==========================================
    # 3. METRICS UTAMA (TOP KPI)
    # ==========================================
    total_target = df_target['Target_Perorangan'].sum() + df_target['Target_Badan_Usaha'].sum()
    total_achieved = df_target['Realisasi_Total'].sum()
    total_backlog = df_target['Sisa_Target'].sum()
    overall_pct = round((total_achieved / total_target) * 100, 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🎯 Total Target 2026", f"{total_target} Akun")
    m2.metric("✅ Total Realisasi", f"{total_achieved} Akun", f"{overall_pct}%")
    m3.metric("⏳ Sisa (Backlog)", f"{total_backlog} Akun", delta_color="inverse")
    m4.metric("🏢 Cabang Teraktif", "KPO")

    st.divider()

    # ==========================================
    # 4. VISUALISASI PERFORMA CABANG
    # ==========================================
    col_chart1, col_chart2 = st.columns([6, 4])

    with col_chart1:
        st.markdown("**Pencapaian vs Target per Cabang**")
        # Bar Chart Gabungan
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_target['Cabang'], 
            y=df_target['Target_Perorangan'] + df_target['Target_Badan_Usaha'],
            name='Target', marker_color='#E6E9EF'
        ))
        fig.add_trace(go.Bar(
            x=df_target['Cabang'], 
            y=df_target['Realisasi_Total'],
            name='Realisasi', marker_color='#0068C9'
        ))
        fig.update_layout(barmode='overlay', height=350, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("**Komposisi Target**")
        # Pie Chart
        fig_pie = px.pie(
            values=[df_target['Target_Perorangan'].sum(), df_target['Target_Badan_Usaha'].sum()],
            names=['Perorangan', 'Badan Usaha'],
            hole=0.5,
            color_discrete_sequence=['#0068C9', '#83C9FF']
        )
        fig_pie.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ==========================================
    # 5. TABEL DETAIL MONITORING (Standard Perbankan)
    # ==========================================
    st.markdown("**📋 Detail Progress Pengkinian Data per Cabang**")
    
    # Styling DataFrame
    def style_progress(val):
        color = 'red' if val < 30 else 'orange' if val < 70 else 'green'
        return f'color: {color}; font-weight: bold'

    df_display = df_target[['Cabang', 'Target_Perorangan', 'Target_Badan_Usaha', 'Realisasi_Total', 'Sisa_Target', 'Persentase']]
    st.dataframe(
        df_display.style.map(style_progress, subset=['Persentase']),
        use_container_width=True,
        hide_index=True
    )

    # ==========================================
    # 6. TREND BULANAN
    # ==========================================
    st.markdown("**📈 Trend Realisasi Bulanan (All Branch)**")
    monthly_trend = df_realisasi[['Jan', 'Feb', 'Mar']].sum()
    fig_line = px.line(
        x=monthly_trend.index, 
        y=monthly_trend.values,
        labels={'x': 'Bulan', 'y': 'Jumlah Akun'},
        markers=True
    )
    fig_line.update_traces(line_color='#0068C9', line_width=4)
    fig_line.update_layout(height=300)
    st.plotly_chart(fig_line, use_container_width=True)
