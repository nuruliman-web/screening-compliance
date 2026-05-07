import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # --- 1. DATA MASTER CABANG & BULAN ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V11) ---
    if 'db_kyc_v11' not in st.session_state:
        st.session_state.db_kyc_v11 = {}

    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring KYC 2026 (Fix Sync)</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA (DITENGAH) ---
    st.markdown("---")
    # Pakai columns supaya rapi di tengah
    c1, c2, c3 = st.columns(3)
    with c1:
        # Tambahkan 'key' unik supaya sinkron
        thn_v = st.selectbox("📅 Pilih Tahun:", list_tahun, index=2, key="sync_thn")
    with c2:
        kat_v = st.selectbox("📂 Kategori Nasabah:", ["Perorangan", "Korporasi"], key="sync_kat")
    with c3:
        bln_v = st.selectbox("📆 s/d Bulan:", list_bulan, key="sync_bln")
    st.markdown("---")

    # Inisialisasi struktur data jika tahun/kategori baru dibuka
    if thn_v not in st.session_state.db_kyc_v11:
        st.session_state.db_kyc_v11[thn_v] = {
            'Perorangan': {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang},
            'Korporasi': {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang}
        }

    tab_view, tab_input_progres, tab_input_target = st.tabs([
        f"📈 Dashboard {kat_v}", "✍️ Input Progres Bulanan", "⚙️ Input Target Tahunan"
    ])

    # --- TAB 1: VIEW DASHBOARD (INI YANG TADI NYANGKUT) ---
    with tab_view:
        # Ambil data spesifik sesuai filter di atas
        data_sumber = st.session_state.db_kyc_v11[thn_v][kat_v]
        
        idx_bln = list_bulan.index(bln_v) + 1
        range_bln = list_bulan[:idx_bln]
        
        rows = []
        for cbg in list_cabang:
            target = data_sumber[cbg]['t']
            # Hitung total realisasi dari Januari sampai bulan terpilih
            real_akumulasi = sum(data_sumber[cbg]['r'][m] for m in range_bln)
            
            sudah = min(real_akumulasi, target) if target > 0 else real_akumulasi
            belum = max(0, target - sudah)
            persen = int(round((sudah / target) * 100)) if target > 0 else (100 if sudah > 0 else 0)
            
            rows.append({
                'Cabang': cbg, 'Target': target, 'Realisasi': sudah, 
                '%': f"{persen}%", 'Sisa': belum, 'v_s': sudah, 'v_b': belum
            })
        
        df = pd.DataFrame(rows)

        # A. Grafik Batang
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Progres {kat_v} {thn_v} s/d {bln_v}</p>", unsafe_allow_html=True)
        chart_df = df.set_index('Cabang')[['v_s', 'v_b']]
        chart_df.columns = ['Sudah', 'Belum']
        # Warna beda: Perorangan (Hijau), Korporasi (Biru)
        st.bar_chart(chart_df, color=["#2ecc71" if kat_v == "Perorangan" else "#3498db", "#e74c3c"])

        # B. Metrics
        t_target = df['Target'].sum()
        t_real = df['Realisasi'].sum()
        t_persen = int(round((t_real / t_target) * 100)) if t_target > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric(f"🎯 Target {kat_v}", f"{t_target}")
        m2.metric("✅ Pencapaian", f"{t_real}", f"{t_persen}%")
        m3.metric("⏳ Sisa", f"{t_target - t_real}", f"{100-t_persen}%", delta_color="inverse")

        st.divider()

        # C. Tabel
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        st.dataframe(df[['Cabang', 'Target', 'Realisasi', '%', 'Sisa']], use_container_width=True, hide_index=True)

    # --- TAB 2: INPUT PROGRES ---
    with tab_input_progres:
        st.subheader(f"✍️ Update Progres {kat_v} - {thn_v}")
        with st.form("form_real_v11"):
            col1, col2, col3 = st.columns(3)
            in_bln = col1.selectbox("Bulan:", list_bulan)
            in_cbg = col2.selectbox("Cabang:", list_cabang)
            in_val = col3.number_input("Tambah Realisasi:", min_value=0, step=1)
            
            if st.form_submit_button("✅ Simpan Progres"):
                st.session_state.db_kyc_v11[thn_v][kat_v][in_cbg]['r'][in_bln] += int(in_val)
                st.success("Data berhasil ditambah!")
                st.rerun()

    # --- TAB 3: INPUT TARGET ---
    with tab_input_target:
        st.subheader(f"⚙️ Setting Target {kat_v} - {thn_view if 'thn_view' in locals() else thn_v}")
        st.warning("Input target total untuk satu tahun penuh di sini.")
        with st.form("form_target_v11"):
            tcols = st.columns(4)
            for i, cbg in enumerate(list_cabang):
                cur_t = st.session_state.db_kyc_v11[thn_v][kat_v][cbg]['t']
                new_t = tcols[i % 4].number_input(f"Target {cbg}", min_value=0, value=cur_t)
                st.session_state.db_kyc_v11[thn_v][kat_v][cbg]['t'] = new_t
            
            if st.form_submit_button("💾 Simpan Target"):
                st.success("Target berhasil diperbarui!")
                st.rerun()
