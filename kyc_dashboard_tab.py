import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. DATA TARGET TETAP
    data_target = {
        'Cabang': ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan'],
        'Target': [182, 13, 30, 29, 23, 5, 80, 5, 21, 58, 6]
    }
    df_master = pd.DataFrame(data_target)

    # 2. DATABASE REALISASI (Session State)
    if 'db_realisasi' not in st.session_state:
        st.session_state.db_realisasi = pd.DataFrame({
            'Cabang': df_master['Cabang'],
            'Januari': [0]*11, 'Februari': [0]*11, 'Maret': [0]*11, 'April': [0]*11,
            'Mei': [0]*11, 'Juni': [0]*11, 'Juli': [0]*11, 'Agustus': [0]*11,
            'September': [0]*11, 'Oktober': [0]*11, 'November': [0]*11, 'Desember': [0]*11
        })

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data"])

    # --- TAB INPUT DATA ---
    with tab_input:
        with st.form("form_update"):
            c1, c2, c3 = st.columns(3)
            bln = c1.selectbox("Bulan:", ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
            cbg = c2.selectbox("Cabang:", df_master['Cabang'])
            jml = c3.number_input("Jumlah:", min_value=0, step=1)
            if st.form_submit_button("Update Data"):
                # Pastikan update berdasarkan nama Cabang yang benar
                st.session_state.db_realisasi.loc[st.session_state.db_realisasi['Cabang'] == cbg, bln] = int(jml)
                st.success(f"Data {cbg} bulan {bln} diperbarui!")

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        filter_bln = st.select_slider("Progress akumulatif s/d bulan:", options=list_bulan)

        # Perhitungan Akumulasi
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        # Gabungkan data target dan realisasi dengan benar (Merge agar index aman)
        df_real_sum = st.session_state.db_realisasi[['Cabang'] + bulan_terpilih].copy()
        df_real_sum['Sudah'] = df_real_sum[bulan_terpilih].sum(axis=1)
        
        df_final = pd.merge(df_master, df_real_sum[['Cabang', 'Sudah']], on='Cabang')
        
        # Logika Perhitungan Persen Cabang
        df_final['Belum'] = (df_final['Target'] - df_final['Sudah']).clip(lower=0)
        
        # Format Persen tanpa desimal (langsung bulat)
        df_final['% Sudah'] = ((df_final['Sudah'] / df_final['Target']) * 100).fillna(0).astype(int).astype(str) + "%"
        df_final['% Belum'] = ((df_final['Belum'] / df_final['Target']) * 100).fillna(0).astype(int).astype(str) + "%"

        # Tampilan Metrics Atas
        t_target = df_final['Target'].sum()
        t_sudah = df_final['Sudah'].sum()
        t_belum = df_final['Belum'].sum()
        p_sudah = int((t_sudah / t_target) * 100) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Total Sudah", f"{t_sudah}", f"{p_sudah}%")
        m3.metric("⏳ Total Belum", f"{t_belum}", f"{100 - p_sudah}%", delta_color="inverse")

        st.divider()

        # URUTAN KOLOM & RATA TENGAH
        # Urutan: Cabang, Target, Sudah, % Sudah, Belum, % Belum
        df_tabel = df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']]
        
        # Gunakan CSS untuk Rata Tengah (Center Alignment)
        st.markdown("""
            <style>
                .stDataFrame td, .stDataFrame th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Tabel Monitoring Progress s/d {filter_bln}</p>", unsafe_allow_html=True)
        
        # Menampilkan tabel dengan gaya standar (font hitam, rata tengah via CSS)
        st.dataframe(df_tabel, use_container_width=True, hide_index=True)

        # Grafik Progress
        st.bar_chart(df_final.set_index('Cabang')[['Sudah', 'Belum']], color=["#2ecc71", "#e74c3c"])
