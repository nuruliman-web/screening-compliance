import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah Perorangan 2026")
    
    # --- 1. INITIAL DATABASE TARGET (Data Statis) ---
    data_target = {
        'Cabang': ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'],
        'Target_Tahunan': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6]
    }
    df_main = pd.DataFrame(data_target)

    # --- 2. FITUR INPUT (SIMULASI DATABASE REALISASI) ---
    # Di dunia nyata, ini biasanya disimpan di st.session_state atau Database (SQLite/GSheets)
    if 'db_realisasi' not in st.session_state:
        # Template awal: Semua bulan nol
        st.session_state.db_realisasi = pd.DataFrame({
            'Cabang': df_main['Cabang'],
            'Januari': [0]*11, 'Februari': [0]*11, 'Maret': [0]*11, 'April': [0]*11,
            'Mei': [0]*11, 'Juni': [0]*11, 'Juli': [0]*11, 'Agustus': [0]*11,
            'September': [0]*11, 'Oktober': [0]*11, 'November': [0]*11, 'Desember': [0]*11
        })

    # --- TAB MENU: DASHBOARD & INPUT DATA ---
    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data Bulanan"])

    with tab_input:
        st.markdown("##### 📝 Form Update Pengkinian Data")
        with st.form("form_input"):
            col_b, col_c, col_n = st.columns(3)
            bulan_input = col_b.selectbox("Pilih Bulan yang ingin di-update:", 
                                         ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
            cabang_input = col_c.selectbox("Pilih Cabang:", df_main['Cabang'])
            jumlah_input = col_n.number_input("Jumlah Nasabah dikinikan bulan ini:", min_value=0, step=1)
            
            submit = st.form_submit_button("Simpan Data")
            if submit:
                # Update nilai di session state
                idx = st.session_state.db_realisasi.index[st.session_state.db_realisasi['Cabang'] == cabang_input][0]
                st.session_state.db_realisasi.at[idx, bulan_input] = jumlah_input
                st.success(f"Berhasil update data {cabang_input} bulan {bulan_input}")

    with tab_view:
        # --- 3. FILTER BULAN ---
        st.markdown("##### 📅 Filter Progress")
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        bulan_filter = st.select_slider("Tampilkan progress sampai dengan bulan:", options=list_bulan)

        # --- 4. LOGIKA PERHITUNGAN ---
        idx_bulan = list_bulan.index(bulan_filter) + 1
        bulan_terpilih = list_bulan[:idx_bulan]
        
        # Hitung realisasi akumulatif sampai bulan terpilih
        df_main['Dikinikan'] = st.session_state.db_realisasi[bulan_terpilih].sum(axis=1)
        df_main['Belum_Dikinikan'] = df_main['Target_Tahunan'] - df_main['Dikinikan']
        # Pastikan sisa tidak minus
        df_main['Belum_Dikinikan'] = df_main['Belum_Dikinikan'].clip(lower=0)
        df_main['Progress (%)'] = (df_main['Dikinikan'] / df_main['Target_Tahunan'] * 100).round(1)

        # --- 5. TAMPILAN METRICS ---
        total_target = df_main['Target_Tahunan'].sum()
        total_dikinikan = df_main['Dikinikan'].sum()
        total_sisa = df_main['Belum_Dikinikan'].sum()
        pct_total = round((total_dikinikan / total_target * 100), 1)

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{total_target} Nasabah")
        m2.metric("✅ Sudah Dikinikan", f"{total_dikinikan}", f"{pct_total}%")
        m3.metric("⏳ Belum Dikinikan", f"{total_sisa}", delta_color="inverse")

        st.divider()

        # --- 6. GRAFIK BATANG ---
        st.markdown(f"**📊 Grafik Pencapaian s/d {bulan_filter}**")
        chart_data = df_main.set_index('Cabang')[['Dikinikan', 'Belum_Dikinikan']]
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"]) # Hijau sudah, Merah belum

        # --- 7. TABEL DETAIL ---
        st.markdown("**📋 Detail Per Cabang**")
        
        def color_progress(val):
            color = 'red' if val < 30 else 'orange' if val < 70 else 'green'
            return f'color: {color}; font-weight: bold'

        styled_df = df_main.style.map(color_progress, subset=['Progress (%)'])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.caption("Fokus Data: Nasabah Perorangan 2026")
