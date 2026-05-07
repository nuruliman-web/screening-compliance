import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # Judul Rata Tengah
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. MASTER DATA TARGET (Kunci Utama)
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())

    # 2. DATABASE REALISASI (Session State)
    if 'db_realisasi' not in st.session_state:
        # Buat tabel kosong awal
        st.session_state.db_realisasi = {cbg: {m: 0 for m in ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']} for cbg in list_cabang}

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data"])

    # --- TAB INPUT DATA ---
    with tab_input:
        st.info("Input jumlah nasabah yang sudah dikinikan di sini.")
        with st.form("form_update"):
            c1, c2, c3 = st.columns(3)
            bln = c1.selectbox("Pilih Bulan:", ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'])
            cbg = c2.selectbox("Pilih Cabang:", list_cabang)
            jml = c3.number_input("Jumlah Realisasi:", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                st.session_state.db_realisasi[cbg][bln] = int(jml)
                st.success(f"Data {cbg} untuk {bln} berhasil disimpan!")

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        filter_bln = st.select_slider("Tampilkan progress s/d bulan:", options=list_bulan)

        # 3. PROSES DATA (Logic Akurat)
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            # Jumlahkan realisasi hanya sampai bulan yang difilter
            sudah = sum(st.session_state.db_realisasi[cbg][m] for m in bulan_terpilih)
            
            # Cek agar 'Sudah' tidak melebihi 'Target' (Standard Banking)
            sudah_capped = min(sudah, target)
            belum = max(0, target - sudah_capped)
            
            # Hitung Persen Bulat
            p_sudah = int((sudah_capped / target) * 100) if target > 0 else 0
            p_belum = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg,
                'Target': target,
                'Sudah': sudah_capped,
                '% Sudah': f"{p_sudah}%",
                'Belum': belum,
                '% Belum': f"{p_belum}%",
                '_p_val': p_sudah # buat sorting/grafik internal
            })
        
        df_final = pd.DataFrame(rows)

        # 4. METRICS UTAMA (TOTAL)
        total_t = sum(target_map.values())
        total_s = df_final['Sudah'].sum()
        total_b = total_t - total_s
        total_p = int((total_s / total_t) * 100)

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{total_t}")
        m2.metric("✅ Total Sudah", f"{total_s}", f"{total_p}%")
        m3.metric("⏳ Total Belum", f"{total_b}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # 5. TABEL RATA TENGAH & FONT ITEM
        st.markdown("""
            <style>
                div[data-testid="stDataFrame"] td {text-align: center !important;}
                div[data-testid="stDataFrame"] th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Tabel Monitoring Progress s/d {filter_bln}</p>", unsafe_allow_html=True)
        
        # Tampilkan tabel tanpa warna-warni font (Hitam Standar)
        st.dataframe(df_final.drop(columns=['_p_val']), use_container_width=True, hide_index=True)

        # 6. GRAFIK
        st.bar_chart(df_final.set_index('Cabang')[['Sudah', 'Belum']], color=["#2ecc71", "#e74c3c"])

    st.caption(f"Update: 2026 | Mode: Akumulatif s/d {filter_bln}")
