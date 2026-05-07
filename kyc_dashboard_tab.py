import streamlit as st
import pandas as pd
import plotly.express as px

def run_kyc_dashboard():
    # Judul Dashboard
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. DATA TARGET TETAP
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # 2. DATABASE REALISASI (Session State)
    if 'db_kyc_final' not in st.session_state:
        st.session_state.db_kyc_final = {
            cbg: {m: 0 for m in list_bulan} for cbg in list_cabang
        }

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data Bulanan"])

    # --- TAB INPUT DATA ---
    with tab_input:
        with st.form("form_update_v3"):
            c1, c2, c3 = st.columns(3)
            bln_in = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg_in = c2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = c3.number_input("Jumlah Realisasi:", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                st.session_state.db_kyc_final[cbg_in][bln_in] = int(jml_in)
                st.success(f"Data {cbg_in} bulan {bln_in} berhasil di-update!")

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        # A. PILIHAN BULAN (Ganti Slider jadi Dropdown)
        filter_bln = st.selectbox("📅 Pilih Periode (Akumulatif s/d):", list_bulan, index=0)

        # B. PROSES DATA
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            total_realisasi = sum(st.session_state.db_kyc_final[cbg][m] for m in bulan_terpilih)
            
            sudah = min(total_realisasi, target) # Capped 100%
            belum = max(0, target - sudah)
            
            p_sudah = int((sudah / target) * 100) if target > 0 else 0
            p_belum = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg,
                'Target': target,
                'Sudah': sudah,
                '% Sudah': f"{p_sudah}%",
                'Belum': belum,
                '% Belum': f"{p_belum}%",
                'raw_p': p_sudah
            })
        
        df_final = pd.DataFrame(rows)

        # C. DIAGRAM PIPE (PIE CHART) - Total Progress
        t_target = sum(target_map.values())
        t_sudah = df_final['Sudah'].sum()
        t_belum = t_target - t_sudah
        
        # Data untuk Pie Chart
        df_pie = pd.DataFrame({
            'Status': ['Sudah Dikinikan', 'Belum Dikinikan'],
            'Jumlah': [t_sudah, t_belum]
        })
        
        fig = px.pie(df_pie, values='Jumlah', names='Status', 
                     color_discrete_sequence=['#2ecc71', '#e74c3c'],
                     hole=0.4) # Buat jadi donut chart biar keren
        fig.update_traces(textinfo='percent+label', textfont_size=15)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=300)
        
        st.plotly_chart(fig, use_container_width=True)

        # D. TOTAL METRICS
        total_p = int((t_sudah / t_target) * 100) if t_target > 0 else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Total Sudah", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Total Belum", f"{t_belum}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # E. TABEL DETAIL (RATA TENGAH & URUTAN SESUAI)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📋 Detail Progress Tiap Cabang s/d {filter_bln}</p>", unsafe_allow_html=True)
        
        # CSS untuk maksa rata tengah
        st.markdown("""
            <style>
                div[data-testid="stDataFrame"] td {text-align: center !important;}
                div[data-testid="stDataFrame"] th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        # Drop kolom internal sebelum tampil
        df_display = df_final.drop(columns=['raw_p'])
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # F. GRAFIK PER CABANG (Opsional - Bar Chart Tetap Ada di Bawah)
        st.bar_chart(df_final.set_index('Cabang')[['Sudah', 'Belum']], color=["#2ecc71", "#e74c3c"])

    st.caption(f"Update Terakhir: 2026 | Fokus: Nasabah Perorangan")
