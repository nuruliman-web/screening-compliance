import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # --- 1. DATA TARGET KUNCI ---
    # Perorangan (Total: 452)
    target_perorangan = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    
    # Korporasi (Total: 46 - Sesuai Data Terakhir)
    target_korporasi = {
        'KPO': 32, 'Tangerang': 3, 'Kelapa Gading': 1, 'Bogor': 2, 
        'Jambi': 1, 'Pontianak': 7, 'Depok': 0, 'Bekasi': 0, 
        'Pekanbaru': 0, 'Pangkalan Kerinci': 0, 'Siantan': 0
    }

    list_cabang = list(target_perorangan.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # --- 2. DATABASE SESSION ---
    if 'db_kyc_v10' not in st.session_state:
        st.session_state.db_kyc_v10 = {
            'Perorangan': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang},
            'Korporasi': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
        }

    # Judul Dashboard
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring KYC 2026</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA DI TENGAH (PENGGANTI SIDEBAR) ---
    st.markdown("---")
    f1, f2 = st.columns(2)
    with f1:
        kategori_view = st.selectbox("📂 Pilih Kategori Nasabah:", ["Perorangan", "Korporasi"])
    with f2:
        filter_bln = st.selectbox("📅 Periode Laporan (s/d):", list_bulan)
    st.markdown("---")

    tab_view, tab_input = st.tabs([f"📈 Dashboard {kategori_view}", "✍️ Update Progres"])

    # --- 4. TAB VIEW DASHBOARD ---
    with tab_view:
        # LOGIKA PERHITUNGAN
        active_target = target_perorangan if kategori_view == "Perorangan" else target_korporasi
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = active_target.get(cbg, 0)
            real_raw = sum(st.session_state.db_kyc_v10[kategori_view][cbg][m] for m in bulan_terpilih)
            
            sudah = min(real_raw, target) if target > 0 else real_raw
            belum = max(0, target - sudah)
            p_sudah = int(round((sudah / target) * 100)) if target > 0 else (100 if sudah > 0 else 0)
            
            rows.append({
                'Cabang': cbg, 'Target': int(target), 'Sudah': int(sudah),
                '% Sudah': f"{p_sudah}%", 'Belum': int(belum), '% Belum': f"{100 - p_sudah}%",
                'Val_S': sudah, 'Val_B': belum
            })
        
        df_final = pd.DataFrame(rows)

        # A. DIAGRAM BATANG (FULLSCREEN ATAS)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Grafik Realisasi {kategori_view}</p>", unsafe_allow_html=True)
        chart_data = df_final.set_index('Cabang')[['Val_S', 'Val_B']]
        chart_data.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_data, color=["#3498db" if kategori_view == "Korporasi" else "#2ecc71", "#e74c3c"])

        # B. METRICS
        t_target = sum(active_target.values())
        t_sudah = df_final['Sudah'].sum()
        total_p = int(round((t_sudah / t_target) * 100)) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric(f"🎯 Target {kategori_view}", f"{t_target}")
        m2.metric("✅ Pencapaian", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Sisa", f"{t_target - t_sudah}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # C. TABEL (RATA TENGAH)
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        st.dataframe(df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']], 
                     use_container_width=True, hide_index=True)

    # --- 5. TAB INPUT DATA ---
    with tab_input:
        st.subheader(f"✍️ Form Update {kategori_view}")
        with st.form("form_v10"):
            c_in1, c_in2 = st.columns(2)
            bln_in = c_in1.selectbox("Untuk Bulan:", list_bulan)
            cbg_in = c_in2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = st.number_input("Jumlah Realisasi Baru:", min_value=0, step=1)
            
            # Pilihan kategori otomatis terkunci ke yang sedang dilihat tapi bisa diubah
            kat_in = st.radio("Simpan ke Kategori:", ["Perorangan", "Korporasi"], 
                             index=0 if kategori_view == "Perorangan" else 1, horizontal=True)
            
            if st.form_submit_button("✅ Simpan Data"):
                st.session_state.db_kyc_v10[kat_in][cbg_in][bln_in] += int(jml_in)
                st.success(f"Data {kat_in} - {cbg_in} untuk bulan {bln_in} berhasil diupdate!")
                st.rerun()
        
        if st.button("🗑️ Reset Semua Data Dashboard"):
            del st.session_state.db_kyc_v10
            st.rerun()

    st.caption(f"© 2026 Monitoring Dashboard | Kategori: {kategori_view}")
