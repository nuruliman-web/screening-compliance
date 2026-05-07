import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V15 - FULL REPLACE LOGIC) ---
    if 'db_kyc_v15' not in st.session_state:
        st.session_state.db_kyc_v15 = {}

    # Judul Dashboard
    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring Pengkinian Data Nasabah</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA (TENGAH) ---
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2, key="sync_thn")
    with c2:
        kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"], key="sync_kat")
    with c3:
        bln_v = st.selectbox("📆 s/d Bulan:", list_bulan, key="sync_bln")
    st.markdown("---")

    # Inisialisasi struktur data tahunan jika belum ada
    if thn_v not in st.session_state.db_kyc_v15:
        st.session_state.db_kyc_v15[thn_v] = {
            'Perorangan': {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang},
            'Korporasi': {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang}
        }

    tab_view, tab_input_progres, tab_input_target = st.tabs([
        f"📈 Dashboard {kat_v}", "✍️ Input Progres Bulanan", "⚙️ Input Target Tahunan"
    ])

    # --- TAB 1: VIEW DASHBOARD ---
    with tab_view:
        data_sumber = st.session_state.db_kyc_v15[thn_v][kat_v]
        idx_bln = list_bulan.index(bln_v) + 1
        range_bln = list_bulan[:idx_bln]
        
        rows = []
        for cbg in list_cabang:
            target = data_sumber[cbg]['t']
            # Hitung total realisasi (Replace logic tetap dijumlahkan untuk progres akumulatif bulanan)
            real_akumulasi = sum(data_sumber[cbg]['r'][m] for m in range_bln)
            
            sudah = min(real_akumulasi, target) if target > 0 else real_akumulasi
            belum = max(0, target - sudah)
            p_sudah = int(round((sudah / target) * 100)) if target > 0 else (100 if sudah > 0 else 0)
            p_belum = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg, 'Target': target, 'Realisasi': sudah, 
                '% Sudah': f"{p_sudah}%", 'Sisa': belum, '% Belum': f"{p_belum}%",
                'v_s': sudah, 'v_b': belum
            })
        
        df = pd.DataFrame(rows)

        # Visualisasi Grafik
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Progres {kat_v} {thn_v} s/d {bln_v}</p>", unsafe_allow_html=True)
        chart_df = df.set_index('Cabang')[['v_s', 'v_b']]
        chart_df.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_df, color=["#2ecc71" if kat_v == "Perorangan" else "#3498db", "#e74c3c"])

        # Metrics Atas
        t_target = df['Target'].sum()
        t_real = df['Realisasi'].sum()
        t_p_sudah = int(round((t_real / t_target) * 100)) if t_target > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric(f"🎯 Target {kat_v}", f"{t_target}")
        m2.metric("✅ Pencapaian", f"{t_real}", f"{t_p_sudah}%")
        m3.metric("⏳ Sisa", f"{t_target - t_real}", f"{100 - t_p_sudah}%", delta_color="inverse")

        st.divider()
        
        # Tabel Detail
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        st.dataframe(df[['Cabang', 'Target', 'Realisasi', '% Sudah', 'Sisa', '% Belum']], use_container_width=True, hide_index=True)

    # --- TAB 2: INPUT PROGRES (REPLACE LOGIC) ---
    with tab_input_progres:
        st.subheader(f"✍️ Update Progres {kat_v} - {thn_v}")
        st.info("Sistem Ganti: Jika salah input, cukup masukkan angka yang benar di bulan dan cabang yang sama.")
        with st.form("form_real_v15", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            in_bln = col1.selectbox("Bulan:", list_bulan)
            in_cbg = col2.selectbox("Cabang:", list_cabang)
            
            # Cek data lama untuk placeholder
            old_val = st.session_state.db_kyc_v15[thn_v][kat_v][in_cbg]['r'][in_bln]
            in_val = col3.number_input(f"Realisasi {in_bln}:", min_value=0, step=1, value=None if old_val == 0 else old_val, placeholder="Ketik angka...")
            
            if st.form_submit_button("✅ Simpan Progres"):
                if in_val is not None:
                    # LOGIKA GANTI (REPLACE)
                    st.session_state.db_kyc_v15[thn_v][kat_v][in_cbg]['r'][in_bln] = int(in_val)
                    st.success(f"Tersimpan! {in_cbg} bulan {in_bln} sekarang adalah {in_val}.")
                    st.toast(f"Data {in_cbg} Terupdate!", icon='✅')
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Isi angka realisasinya dulu!")

    # --- TAB 3: INPUT TARGET (REPLACE LOGIC) ---
    with tab_input_target:
        st.subheader(f"⚙️ Setting Target {kat_v} - {thn_v}")
        st.warning("Mengubah angka di sini akan mengganti target lama secara permanen.")
        with st.form("form_target_v15"):
            tcols = st.columns(4)
            temp_targets = {}
            for i, cbg in enumerate(list_cabang):
                cur_t = st.session_state.db_kyc_v15[thn_v][kat_v][cbg]['t']
                
                # Logic: Jika target 0, kotak kosong. Jika ada isi, tampilkan angka lamanya.
                val_disp = None if cur_t == 0 else cur_t
                
                new_t = tcols[i % 4].number_input(f"Target {cbg}", min_value=0, value=val_disp, step=1, placeholder="0")
                temp_targets[cbg] = new_t if new_t is not None else 0
            
            if st.form_submit_button("💾 Simpan Semua Target"):
                for cbg, val in temp_targets.items():
                    # LOGIKA GANTI (REPLACE)
                    st.session_state.db_kyc_v15[thn_v][kat_v][cbg]['t'] = val
                
                st.success(f"Seluruh Target {kat_v} Tahun {thn_v} Berhasil Diperbarui!")
                st.toast("Targets Updated!", icon='💾')
                time.sleep(1)
                st.rerun()

    st.caption(f"Sistem Monitoring v15.0 | Tahun Aktif: {thn_v} | Kategori: {kat_v}")
