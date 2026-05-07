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
                # Pastikan angka disimpan sebagai integer murni
                st.session_state.db_realisasi.at[idx, bulan_input] = int(jumlah_input)
                st.success(f"Berhasil simpan data {cabang_input}!")

    # --- TAB DASHBOARD ---
    with tab_view:
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        bulan_filter = st.select_slider("Progress akumulatif s/d bulan:", options=list_bulan)

        # Logika Perhitungan
        idx_bulan = list_bulan.index(bulan_filter) + 1
        bulan_terpilih = list_bulan[:idx_bulan]
        
        # Buat dataframe kerja agar tidak ganggu master data
        df_work = df_main.copy()
        
        # Ambil total realisasi dari session state
        df_work['Sudah'] = st.session_state.db_realisasi[bulan_terpilih].sum(axis=1).astype(int)
        
        # Hitung Belum (Target - Sudah)
        df_work['Belum'] = (df_work['Target_Tahunan'] - df_work['Sudah']).clip(lower=0).astype(int)
        
        # HITUNG PERSENTASE (Sudah / Target) & (Belum / Target)
        df_work['% Sudah'] = (df_work['Sudah'] / df_work['Target_Tahunan'] * 100).round(1)
        df_work['% Belum'] = (df_work['Belum'] / df_work['Target_Tahunan'] * 100).round(1)

        # --- TOP METRICS (TOTAL ALL) ---
        t_target = int(df_work['Target_Tahunan'].sum())
        t_sudah = int(df_work['Sudah'].sum())
        t_belum = int(df_work['Belum'].sum())
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Total Sudah", f"{t_sudah}", f"{(t_sudah/t_target*100):.1f}%")
        m3.metric("⏳ Total Belum", f"{t_belum}", f"{(t_belum/t_target*100):.1f}%", delta_color="inverse")

        st.divider()

        # --- GRAFIK ---
        st.markdown(f"**📊 Bar Chart Progress s/d {bulan_filter}**")
        chart_data = df_work.set_index('Cabang')[['Sudah', 'Belum']]
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"])

        # --- TABEL DETAIL (URUTAN KOLOM DISESUAIKAN) ---
        st.markdown("**📋 Detail Monitoring Per Cabang**")
        
        # Urutan Kolom: Cabang, Target, Sudah, % Sudah, Belum, % Belum
        df_final = df_work[['Cabang', 'Target_Tahunan', 'Sudah', '% Sudah', 'Belum', '% Belum']]
        
        def color_progress(val):
            return 'color: #2ecc71; font-weight: bold' if val >= 100 else 'color: #e67e22; font-weight: bold' if val > 0 else 'color: #e74c3c'

        # Styling & Format Tampilan
        styled_df = df_final.style.format({
            '% Sudah': '{:.1f}%',
            '% Belum': '{:.1f}%'
        }).map(color_progress, subset=['% Sudah'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.caption(f"Fokus Data Perorangan 2026 | Perhitungan s/d {bulan_filter}")
