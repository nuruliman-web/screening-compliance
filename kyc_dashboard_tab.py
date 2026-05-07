import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah Perorangan 2026")
    
    # --- 1. DATA TARGET TETAP ---
    data_target = {
        'Cabang': ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'],
        'Target_Tahunan': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6]
    }
    df_main = pd.DataFrame(data_target)

    # --- 2. DATABASE REALISASI (Session State) ---
    if 'db_realisasi' not in st.session_state:
        st.session_state.db_realisasi = pd.DataFrame({
            'Cabang': df_main['Cabang'],
            'Januari': [0]*11, 'Februari': [0]*11, 'Maret': [0]*11, 'April': [0]*11,
            'Mei': [0]*11, 'Juni': [0]*11, 'Juli': [0]*11, 'Agustus': [0]*11,
            'September': [0]*11, 'Oktober': [0]*11, 'November': [0]*11, 'Desember': [0]*11
        })

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data Bulanan"])

    # --- TAB INPUT ---
    with tab_input:
        st.markdown("##### 📝 Form Update Pengkinian Data")
        with st.form("form_input"):
            col_b, col_c, col_n = st.columns(3)
            bulan_input = col_b.selectbox("Pilih Bulan:", ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
            cabang_input = col_c.selectbox("Pilih Cabang:", df_main['Cabang'])
            jumlah_input = col_n.number_input("Jumlah Nasabah:", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                idx = st.session_state.db_realisasi.index[st.session_state.db_realisasi['Cabang'] == cabang_input][0]
                st.session_state.db_realisasi.at[idx, bulan_input] = int(jumlah_input)
                st.success(f"Update Berhasil untuk {cabang_input}!")

    # --- TAB DASHBOARD ---
    with tab_view:
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        bulan_filter = st.select_slider("Progress akumulatif s/d bulan:", options=list_bulan)

        # Logika Perhitungan
        idx_bulan = list_bulan.index(bulan_filter) + 1
        bulan_terpilih = list_bulan[:idx_bulan]
        
        df_main['Dikinikan'] = st.session_state.db_realisasi[bulan_terpilih].sum(axis=1).astype(int)
        df_main['Belum_Dikinikan'] = (df_main['Target_Tahunan'] - df_main['Dikinikan']).clip(lower=0).astype(int)
        
        # HITUNG PERSENTASE PER CABANG (Bandingkan ke Target masing-masing)
        df_main['Persen_Sudah'] = (df_main['Dikinikan'] / df_main['Target_Tahunan'] * 100).round(1)
        df_main['Persen_Belum'] = (df_main['Belum_Dikinikan'] / df_main['Target_Tahunan'] * 100).round(1)

        # --- TOP METRICS (ALL DASHBOARD) ---
        t_target = int(df_main['Target_Tahunan'].sum())
        t_dikinikan = int(df_main['Dikinikan'].sum())
        t_sisa = int(df_main['Belum_Dikinikan'].sum())
        
        # Persentase All Dashboard (Total vs Total)
        pct_all_sudah = (t_dikinikan / t_target * 100)
        pct_all_belum = (t_sisa / t_target * 100)

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target Seluruhnya", f"{t_target}")
        m2.metric("✅ Total Sudah Dikinikan", f"{t_dikinikan}", f"{pct_all_sudah:.1f}%")
        m3.metric("⏳ Total Belum Dikinikan", f"{t_sisa}", f"{pct_all_belum:.1f}%", delta_color="inverse")

        st.divider()

        # --- GRAFIK ---
        st.markdown(f"**📊 Komparasi Progress s/d {bulan_filter}**")
        chart_data = df_main.set_index('Cabang')[['Dikinikan', 'Belum_Dikinikan']]
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"])

        # --- TABEL DETAIL ---
        st.markdown("**📋 Detail Monitoring Per Cabang**")
        
        # Mapping nama kolom agar lebih rapi di tabel
        df_final = df_main.rename(columns={
            'Target_Tahunan': 'Target',
            'Dikinikan': 'Sudah (Akun)',
            'Belum_Dikinikan': 'Belum (Akun)',
            'Persen_Sudah': '% Sudah',
            'Persen_Belum': '% Belum'
        })

        def color_logic(val):
            return 'color: #2ecc71; font-weight: bold' if val > 70 else 'color: #e67e22; font-weight: bold' if val > 30 else 'color: #e74c3c; font-weight: bold'

        styled_df = df_final.style.format({
            '% Sudah': '{:.1f}%',
            '% Belum': '{:.1f}%'
        }).map(color_logic, subset=['% Sudah'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.caption(f"Update terakhir: {bulan_filter} 2026")
