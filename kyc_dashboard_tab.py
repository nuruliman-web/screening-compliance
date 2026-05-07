import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("### 📊 Dashboard Pengkinian Data Nasabah Perorangan 2026")
    
    # --- 1. DATA TARGET ---
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
                st.success(f"Update Berhasil!")

    with tab_view:
        # --- 3. FILTER & LOGIKA ---
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        bulan_filter = st.select_slider("Progress s/d bulan:", options=list_bulan)

        idx_bulan = list_bulan.index(bulan_filter) + 1
        bulan_terpilih = list_bulan[:idx_bulan]
        
        # Hitung angka bulat (integer) agar tidak ada .0000
        df_main['Dikinikan'] = st.session_state.db_realisasi[bulan_terpilih].sum(axis=1).astype(int)
        df_main['Belum_Dikinikan'] = (df_main['Target_Tahunan'] - df_main['Dikinikan']).clip(lower=0).astype(int)
        
        # Hitung Persentase dengan pembulatan 1 desimal
        df_main['Progress (%)'] = (df_main['Dikinikan'] / df_main['Target_Tahunan'] * 100).round(1)

        # --- 4. TOP METRICS ---
        total_t = int(df_main['Target_Tahunan'].sum())
        total_d = int(df_main['Dikinikan'].sum())
        total_s = int(df_main['Belum_Dikinikan'].sum())
        pct_total = f"{(total_d / total_t * 100):.1f}%" # Format langsung ke string %

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{total_t}")
        m2.metric("✅ Sudah Dikinikan", f"{total_d}", pct_total)
        m3.metric("⏳ Belum Dikinikan", f"{total_s}", delta_color="inverse")

        st.divider()

        # --- 5. GRAFIK ---
        st.markdown(f"**📊 Grafik Pencapaian s/d {bulan_filter}**")
        chart_data = df_main.set_index('Cabang')[['Dikinikan', 'Belum_Dikinikan']]
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"])

        # --- 6. TABEL DETAIL (FORMATTING FIXED) ---
        st.markdown("**📋 Detail Per Cabang**")
        
        def color_progress(val):
            color = 'red' if val < 30 else 'orange' if val < 70 else 'green'
            return f'color: {color}; font-weight: bold'

        # Gunakan format .style.format untuk menambahkan tanda % secara otomatis tanpa mengubah angka aslinya
        styled_df = df_main.style.format({
            'Progress (%)': '{:.1f}%'  # Menampilkan 1 angka desimal + tanda %
        }).map(color_progress, subset=['Progress (%)'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
