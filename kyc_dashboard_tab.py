import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V20) ---
    if 'db_kyc_v20' not in st.session_state:
        db = {thn: {kat: {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang} 
              for kat in ["Perorangan", "Korporasi"]} for thn in list_tahun}
        
        # --- INJECT DATA PERORANGAN 2026 (Dari Foto) ---
        target_per_2026 = {'KPO': 4280, 'Tangerang': 1485, 'Depok': 1205, 'Bekasi': 1563, 'Kelapa Gading': 841, 'Bogor': 729, 'Jambi': 782, 'Pekanbaru': 876, 'Pangkalan Kerinci': 168, 'Pontianak': 171, 'Siantan': 127}
        real_per_2026 = {'KPO': 141, 'Tangerang': 53, 'Depok': 42, 'Bekasi': 33, 'Kelapa Gading': 31, 'Bogor': 20, 'Jambi': 27, 'Pekanbaru': 0, 'Pangkalan Kerinci': 0, 'Pontianak': 0, 'Siantan': 0}
        
        # --- INJECT DATA KORPORASI 2026 (Dari Foto) ---
        target_kor_2026 = {'KPO': 182, 'Tangerang': 57, 'Depok': 37, 'Bekasi': 45, 'Kelapa Gading': 32, 'Bogor': 19, 'Jambi': 27, 'Pekanbaru': 21, 'Pangkalan Kerinci': 6, 'Pontianak': 11, 'Siantan': 5}
        real_kor_2026 = {'KPO': 9, 'Tangerang': 2, 'Depok': 1, 'Bekasi': 2, 'Kelapa Gading': 2, 'Bogor': 1, 'Jambi': 2, 'Pekanbaru': 0, 'Pangkalan Kerinci': 0, 'Pontianak': 0, 'Siantan': 0}

        for c in list_cabang:
            db[2026]['Perorangan'][c]['t'] = target_per_2026.get(c, 0)
            db[2026]['Perorangan'][c]['r']['Januari'] = real_per_2026.get(c, 0)
            db[2026]['Korporasi'][c]['t'] = target_kor_2026.get(c, 0)
            db[2026]['Korporasi'][c]['r']['Januari'] = real_kor_2026.get(c, 0)
        
        st.session_state.db_kyc_v20 = db

    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring Pengkinian Data Nasabah</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1: thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2)
    with f2: kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"], index=0)
    with f3: bln_v = st.selectbox("📆 s/d Bulan:", list_bulan, index=4)
    st.markdown("---")

    tab_v, tab_p, tab_t = st.tabs([f"📈 Dashboard {kat_v}", "✍️ Update Progres", "⚙️ Target Tahunan"])

    # --- TAB 1: VIEW & DOWNLOAD ---
    with tab_v:
        data = st.session_state.db_kyc_v20[thn_v][kat_v]
        idx_bln = list_bulan.index(bln_v) + 1
        rows = []
        for cbg in list_cabang:
            t = data[cbg]['t']
            r = sum(data[cbg]['r'][m] for m in list_bulan[:idx_bln])
            sdh = min(r, t) if t > 0 else r
            blm = max(0, t - sdh)
            p_sdh = int(round((sdh / t) * 100)) if t > 0 else (100 if sdh > 0 else 0)
            rows.append({'Cabang': cbg, 'Target': t, 'Realisasi': sdh, '% Sudah': f"{p_sdh}%", 'Sisa': blm, '% Belum': f"{100-p_sdh}%", 'v_s': sdh, 'v_b': blm})
        
        df = pd.DataFrame(rows)
        
        # FIX CSV: Pakai index=False dan pastikan format teks aman
        csv = df[['Cabang', 'Target', 'Realisasi', '% Sudah', 'Sisa', '% Belum']].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Report (CSV)", csv, f"KYC_{kat_v}_{thn_v}.csv", "text/csv")

        st.bar_chart(df.set_index('Cabang')[['v_s', 'v_b']].rename(columns={'v_s':'Sudah','v_b':'Belum'}), color=["#2ecc71" if kat_v=="Perorangan" else "#3498db", "#e74c3c"])
        
        c_m1, c_m2, c_m3 = st.columns(3)
        tt, tr = df['Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        c_m1.metric("🎯 Total Target", tt)
        c_m2.metric("✅ Realisasi", tr, f"{tp}%")
        c_m3.metric("⏳ Sisa", tt-tr, f"{100-tp}%", delta_color="inverse")
        
        st.dataframe(df[['Cabang', 'Target', 'Realisasi', '% Sudah', 'Sisa', '% Belum']], use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES (FIX LAG SAVE) ---
    with tab_p:
        st.subheader(f"Update Progres {kat_v} {thn_v}")
        # Gunakan key unik agar tidak conflict saat rerun
        col_pa, col_pb, col_pc = st.columns(3)
        p_bln = col_pa.selectbox("Bulan:", list_bulan, key="p_bln_sel")
        p_cbg = col_pb.selectbox("Cabang:", list_cabang, key="p_cbg_sel")
        
        cur_val = st.session_state.db_kyc_v20[thn_v][kat_v][p_cbg]['r'][p_bln]
        p_val = col_pc.number_input("Total Realisasi:", min_value=0, value=None if cur_val==0 else cur_val, key="p_val_input")
        
        if st.button("✅ Simpan Progres Sekarang", use_container_width=True):
            save_val = int(p_val) if p_val is not None else 0
            st.session_state.db_kyc_v20[thn_v][kat_v][p_cbg]['r'][p_bln] = save_val
            st.toast(f"Data {p_cbg} Berhasil Disimpan!", icon="✅")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: TARGET ---
    with tab_t:
        st.subheader(f"Setting Target {kat_v} {thn_v}")
        with st.form("form_target_v20"):
            tcols = st.columns(4)
            new_targets = {}
            for i, c in enumerate(list_cabang):
                ct = st.session_state.db_kyc_v20[thn_v][kat_v][c]['t']
                new_targets[c] = tcols[i%4].number_input(f"{c}", min_value=0, value=None if ct==0 else ct)
            
            if st.form_submit_button("💾 Simpan Semua Target", use_container_width=True):
                for c, val in new_targets.items():
                    st.session_state.db_kyc_v20[thn_v][kat_v][c]['t'] = int(val) if val is not None else 0
                st.success("Target Terupdate!")
                time.sleep(0.5)
                st.rerun()
