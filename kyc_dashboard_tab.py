import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # Judul Dashboard Rata Tengah
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring Pengkinian Data Perorangan 2026</h2>", unsafe_allow_html=True)
    
    # 1. DATABASE TARGET (Kunci Logika: Pangkalan Kerinci = 21)
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # 2. INISIALISASI DATABASE (Menggunakan Key Unik V6 agar bersih)
    if 'db_kyc_v6_final' not in st.session_state:
        st.session_state.db_kyc_v6_final = {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}

    tab_view, tab_input = st.tabs(["📈 Dashboard Utama", "✍️ Input Data Cabang"])

    # --- TAB INPUT DATA (Logic Tambah/Update) ---
    with tab_input:
        st.info("Input jumlah nasabah yang sudah dikinikan. Data akan otomatis diakumulasikan.")
        with st.form("form_kyc_v6"):
            c1, c2, c3 = st.columns(3)
            bln_in = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg_in = c2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = c3.number_input("Input Realisasi (Akumulasi):", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                # Simpan angka ke bulan spesifik
                st.session_state.db_kyc_v6_final[cbg_in][bln_in] = int(jml_in)
                st.success(f"Data {cbg_in} untuk {bln_in} berhasil disimpan!")
        
        if st.button("🗑️ Reset Database (Hapus Semua Data)"):
            st.session_state.db_kyc_v6_final = {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
            st.rerun()

    # --- TAB VIEW DASHBOARD (Urutan Baru) ---
    with tab_view:
        # A. PILIHAN BULAN (Paling Atas)
        filter_bln = st.selectbox("📅 Pilih Periode Laporan (Akumulatif s/d):", list_bulan)

        # B. LOGIKA PERHITUNGAN (Fixed & Precise)
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            # Jumlahkan dari Januari s/d bulan terpilih
            total_realisasi = sum(st.session_state.db_kyc_v6_final[cbg][m] for m in bulan_terpilih)
            
            # Logika Capped 100% & Tanpa Desimal
            sudah = min(total_realisasi, target)
            belum = max(0, target - sudah)
            p_sudah = int(round((sudah / target) * 100)) if target > 0 else 0
            
            rows.append({
                'Cabang': cbg,
                'Target': int(target),
                'Sudah': int(sudah),
                '% Sudah': f"{p_sudah}%",
                'Belum': int(belum),
                '% Belum': f"{100 - p_sudah}%",
                'Graph_Sudah': sudah,
                'Graph_Belum': belum
            })
        
        df_final = pd.DataFrame(rows)

        # C. DIAGRAM BATANG (Pindah Ke Atas)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Grafik Progress Cabang s/d {filter_bln}</p>", unsafe_allow_html=True)
        chart_data = df_final.set_index('Cabang')[['Graph_Sudah', 'Graph_Belum']]
        chart_data.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"])

        # D. TOTAL METRICS (Di Bawah Grafik)
        t_target = sum(target_map.values())
        t_sudah = df_final['Sudah'].sum()
        total_p = int(round((t_sudah / t_target) * 100)) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Total Sudah", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Total Belum", f"{t_target - t_sudah}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # E. TABEL DETAIL (Rata Tengah & Font Hitam)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📋 Tabel Detail Monitoring Progres</p>", unsafe_allow_html=True)
        
        # CSS Maksa Rata Tengah
        st.markdown("""
            <style>
                div[data-testid="stDataFrame"] td {text-align: center !important;}
                div[data-testid="stDataFrame"] th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        df_display = df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.caption(f"Status Data: Akumulatif {list_bulan[0]} - {filter_bln} 2026")
