import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. FIX TARGET (Pangkalan Kerinci 21, Total 452)
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # 2. DATABASE BARU (V5 - Biar Error Lama Ilang)
    if 'db_kyc_v5_fix' not in st.session_state:
        st.session_state.db_kyc_v5_fix = {
            cbg: {m: 0 for m in list_bulan} for cbg in list_cabang
        }

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data"])

    # --- TAB INPUT DATA ---
    with tab_input:
        st.warning("⚠️ Input di sini akan MENAMBAHKAN jumlah yang sudah ada.")
        with st.form("form_input_v5"):
            c1, c2, c3 = st.columns(3)
            bln_in = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg_in = c2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = c3.number_input("Tambah Realisasi:", min_value=0, step=1)
            
            submit = st.form_submit_button("Simpan & Tambahkan")
            if submit:
                # LOGIC BARU: DITAMBAHKAN (bukan diganti)
                st.session_state.db_kyc_v5_fix[cbg_in][bln_in] += int(jml_in)
                st.success(f"Berhasil! Data {cbg_in} bulan {bln_in} sekarang bertambah {jml_in}.")
        
        if st.button("🗑️ Reset Ulang Semua Data"):
            st.session_state.db_kyc_v5_fix = {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
            st.rerun()

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        # Pilihan periode di atas
        filter_bln = st.selectbox("📅 Lihat Progress Akumulatif s/d Bulan:", list_bulan)

        # Proses Data
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            # Jumlahkan semua realisasi dari bulan 1 sampai bulan terpilih
            total_realisasi = sum(st.session_state.db_kyc_v5_fix[cbg][m] for m in bulan_terpilih)
            
            sudah = min(total_realisasi, target)
            belum = max(0, target - sudah)
            p_sudah = round((sudah / target) * 100) if target > 0 else 0
            
            rows.append({
                'Cabang': cbg, 'Target': target, 'Sudah': sudah, 
                '% Sudah': f"{p_sudah}%", 'Belum': belum, '% Belum': f"{100-p_sudah}%",
                'Progress': sudah, 'Sisa': belum
            })
        
        df_final = pd.DataFrame(rows)

        # A. METRICS
        t_target = sum(target_map.values())
        t_sudah = df_final['Sudah'].sum()
        total_p = round((t_sudah / t_target) * 100) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Target Total", f"{t_target}")
        m2.metric("✅ Pencapaian", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Sisa", f"{t_target - t_sudah}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # B. TABEL (RATA TENGAH)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📋 Tabel Detail s/d {filter_bln}</p>", unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        
        st.dataframe(df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']], 
                     use_container_width=True, hide_index=True)

        # C. GRAFIK BATANG (DI BAWAH)
        st.bar_chart(df_final.set_index('Cabang')[['Progress', 'Sisa']], color=["#2ecc71", "#e74c3c"])

    st.caption("Update 2026 - Fixed Input Logic")
