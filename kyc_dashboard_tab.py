import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # --- 1. INISIALISASI DATABASE GLOBAL ---
    # Struktur: db[Tahun][Kategori][Cabang] = { 'target': 0, 'realisasi': {Bulan: 0} }
    if 'db_kyc_master' not in st.session_state:
        st.session_state.db_kyc_master = {}

    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # Judul Utama
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Sistem Monitoring KYC Multi-Tahun</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # --- 2. NAVIGASI UTAMA (Tengah) ---
    c1, c2, c3 = st.columns(3)
    with c1:
        thn_view = st.selectbox("📅 Pilih Tahun:", list_tahun, index=2) # Default 2026
    with c2:
        kat_view = st.selectbox("📂 Kategori Nasabah:", ["Perorangan", "Korporasi"])
    with c3:
        bln_view = st.selectbox("📆 s/d Bulan:", list_bulan)

    # Inisialisasi Data Tahun & Kategori jika belum ada
    if thn_view not in st.session_state.db_kyc_master:
        st.session_state.db_kyc_master[thn_view] = {
            'Perorangan': {cbg: {'target': 0, 'realisasi': {m: 0 for m in list_bulan}} for cbg in list_cabang},
            'Korporasi': {cbg: {'target': 0, 'realisasi': {m: 0 for m in list_bulan}} for cbg in list_cabang}
        }

    st.markdown("---")

    # --- 3. TABS SISTEM ---
    tab_dash, tab_input_realisasi, tab_set_target = st.tabs(["📈 Dashboard", "✍️ Input Progres Bulanan", "⚙️ Pengaturan Target Tahunan"])

    # --- TAB A: PENGATURAN TARGET (Manual per Tahun) ---
    with tab_set_target:
        st.subheader(f"🎯 Set Target {kat_view} Tahun {thn_view}")
        st.info("Masukkan total target nasabah yang harus dikinikan untuk masing-masing cabang di tahun ini.")
        
        # Buat tabel input sederhana
        with st.form(f"form_target_{thn_view}_{kat_view}"):
            cols = st.columns(4)
            for i, cbg in enumerate(list_cabang):
                # Ambil nilai target lama jika ada
                val_lama = st.session_state.db_kyc_master[thn_view][kat_view][cbg]['target']
                new_target = cols[i % 4].number_input(f"Target {cbg}", min_value=0, value=val_lama, key=f"t_{thn_view}_{cbg}")
                st.session_state.db_kyc_master[thn_view][kat_view][cbg]['target'] = new_target
            
            if st.form_submit_button("💾 Simpan Semua Target"):
                st.success(f"Target {kat_view} tahun {thn_view} berhasil diperbarui!")
                st.rerun()

    # --- TAB B: INPUT PROGRES BULANAN ---
    with tab_input_realisasi:
        st.subheader(f"✍️ Input Realisasi {kat_view} - {thn_view}")
        with st.form("form_realisasi"):
            cc1, cc2, cc3 = st.columns(3)
            in_bln = cc1.selectbox("Pilih Bulan:", list_bulan)
            in_cbg = cc2.selectbox("Pilih Cabang:", list_cabang)
            in_val = cc3.number_input("Tambahan Realisasi:", min_value=0, step=1)
            
            if st.form_submit_button("✅ Update Progres"):
                st.session_state.db_kyc_master[thn_view][kat_view][in_cbg]['realisasi'][in_bln] += int(in_val)
                st.success("Data progres berhasil ditambahkan!")
                st.rerun()

    # --- TAB C: DASHBOARD UTAMA ---
    with tab_dash:
        # Hitung Data Akumulatif
        idx_akhir = list_bulan.index(bln_view) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            data_cbg = st.session_state.db_kyc_master[thn_view][kat_view][cbg]
            target = data_cbg['target']
            real_raw = sum(data_cbg['realisasi'][m] for m in bulan_terpilih)
            
            sudah = min(real_raw, target) if target > 0 else real_raw
            belum = max(0, target - sudah)
            p_sudah = int(round((sudah / target) * 100)) if target > 0 else (100 if sudah > 0 else 0)
            
            rows.append({
                'Cabang': cbg, 'Target': target, 'Realisasi': sudah, 
                '%': f"{p_sudah}%", 'Sisa': belum, 'v_s': sudah, 'v_b': belum
            })
        
        df = pd.DataFrame(rows)

        # 1. Grafik Batang (Fullscreen Atas)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Grafik Progres {kat_view} {thn_view} s/d {bln_view}</p>", unsafe_allow_html=True)
        chart_data = df.set_index('Cabang')[['v_s', 'v_b']]
        chart_data.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_data, color=["#2ecc71" if kat_view == "Perorangan" else "#3498db", "#e74c3c"])

        # 2. Metrics
        t_target = df['Target'].sum()
        t_sudah = df['Realisasi'].sum()
        total_p = int(round((t_sudah / t_target) * 100)) if t_target > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Total Realisasi", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Total Sisa", f"{t_target - t_sudah}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # 3. Tabel Detail
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        st.dataframe(df[['Cabang', 'Target', 'Realisasi', '%', 'Sisa']], use_container_width=True, hide_index=True)

    st.caption(f"Sistem Monitoring Dinamis - Tahun {thn_view}")
