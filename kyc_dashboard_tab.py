import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # Judul Rata Tengah
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. MASTER DATA TARGET (Fixed & Locked)
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # 2. INISIALISASI DATABASE BARU (Ganti Nama biar gak KeyError)
    if 'db_kyc_fixed' not in st.session_state:
        st.session_state.db_kyc_fixed = {
            cbg: {m: 0 for m in list_bulan} for cbg in list_cabang
        }

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data"])

    # --- TAB INPUT DATA ---
    with tab_input:
        st.info("Input jumlah nasabah baru yang sudah dikinikan bulan ini.")
        with st.form("form_update_v2"):
            c1, c2, c3 = st.columns(3)
            bln = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg = c2.selectbox("Pilih Cabang:", list_cabang)
            jml = c3.number_input("Jumlah Realisasi:", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                # Simpan ke database baru
                st.session_state.db_kyc_fixed[cbg][bln] = int(jml)
                st.success(f"Berhasil! Data {cbg} bulan {bln} tersimpan.")
        
        if st.button("🗑️ Reset Semua Data"):
            del st.session_state.db_kyc_fixed
            st.rerun()

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        filter_bln = st.select_slider("Tampilkan progress s/d bulan:", options=list_bulan)

        # 3. PROSES DATA (Logic Capped 100% & No Shifting)
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            # Ambil data dari database baru
            total_input = sum(st.session_state.db_kyc_fixed[cbg][m] for m in bulan_terpilih)
            
            # Capped 100% (KYC Standard)
            sudah = min(total_input, target)
            belum = max(0, target - sudah)
            
            # Hitung Persen Bulat (Tanpa .0)
            p_sudah = int((sudah / target) * 100) if target > 0 else 0
            p_belum = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg,
                'Target': target,
                'Sudah': sudah,
                '% Sudah': f"{p_sudah}%",
                'Belum': belum,
                '% Belum': f"{p_belum}%"
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

        # 5. TABEL RATA TENGAH (CSS FIX)
        st.markdown("""
            <style>
                /* Maksa text di dalam tabel biar ke tengah */
                div[data-testid="stDataFrame"] td {text-align: center !important;}
                div[data-testid="stDataFrame"] th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Tabel Progress s/d {filter_bln}</p>", unsafe_allow_html=True)
        
        # Tabel bersih, font hitam, rata tengah
        st.dataframe(df_final, use_container_width=True, hide_index=True)

        # 6. GRAFIK
        st.bar_chart(df_final.set_index('Cabang')[['Sudah', 'Belum']], color=["#2ecc71", "#e74c3c"])

    st.caption(f"Update: 2026 | Mode: Akumulatif s/d {filter_bln}")
