import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V21) ---
    if 'db_kyc_v21' not in st.session_state:
        db = {thn: {kat: {c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang} 
              for kat in ["Perorangan", "Korporasi"]} for thn in list_tahun}
        
        # INJECT DATA DARI FOTO
        target_per_2026 = {'KPO': 4280, 'Tangerang': 1485, 'Depok': 1205, 'Bekasi': 1563, 'Kelapa Gading': 841, 'Bogor': 729, 'Jambi': 782, 'Pekanbaru': 876, 'Pangkalan Kerinci': 168, 'Pontianak': 171, 'Siantan': 127}
        real_per_2026 = {'KPO': 141, 'Tangerang': 53, 'Depok': 42, 'Bekasi': 33, 'Kelapa Gading': 31, 'Bogor': 20, 'Jambi': 27}
        target_kor_2026 = {'KPO': 182, 'Tangerang': 57, 'Depok': 37, 'Bekasi': 45, 'Kelapa Gading': 32, 'Bogor': 19, 'Jambi': 27, 'Pekanbaru': 21, 'Pangkalan Kerinci': 6, 'Pontianak': 11, 'Siantan': 5}
        real_kor_2026 = {'KPO': 9, 'Tangerang': 2, 'Depok': 1, 'Bekasi': 2, 'Kelapa Gading': 2, 'Bogor': 1, 'Jambi': 2}

        for c in list_cabang:
            db[2026]['Perorangan'][c]['t'] = target_per_2026.get(c, 0)
            db[2026]['Perorangan'][c]['r']['Januari'] = real_per_2026.get(c, 0)
            db[2026]['Korporasi'][c]['t'] = target_kor_2026.get(c, 0)
            db[2026]['Korporasi'][c]['r']['Januari'] = real_kor_2026.get(c, 0)
        
        st.session_state.db_kyc_v21 = db

    st.markdown("<h3 style='text-align: center;'>📊 Monitoring Pengkinian Data Nasabah</h3>", unsafe_allow_html=True)
    
    # --- 3. FILTER ---
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1: thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2)
    with f2: kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"])
    with f3: bln_v = st.selectbox("📆 s/d Bulan:", list_bulan, index=4)
    st.markdown("---")

    t_view, t_upd, t_tar = st.tabs([f"📈 Dashboard", "✍️ Update Progres", "⚙️ Target"])

    # --- TAB 1: VIEW & CSV AUTO-COLUMN ---
    with t_view:
        data = st.session_state.db_kyc_v21[thn_v][kat_v]
        rows = []
        for cbg in list_cabang:
            t = data[cbg]['t']
            r = sum(data[cbg]['r'][m] for m in list_bulan[:list_bulan.index(bln_v)+1])
            sdh = min(r, t) if t > 0 else r
            p_sdh = int(round((sdh / t) * 100)) if t > 0 else (100 if sdh > 0 else 0)
            rows.append({'Cabang': cbg, 'Target': t, 'Realisasi': sdh, '% Sudah': f"{p_sdh}%", 'Sisa': max(0, t-sdh), '% Belum': f"{100-p_sdh}%"})
        
        df = pd.DataFrame(rows)

        # TRICK AGAR EXCEL OTOMATIS JADI KOLOM:
        # Tambahkan "sep=;" di baris paling atas file CSV
        csv_string = df.to_csv(index=False, sep=';')
        csv_output = "sep=;\n" + csv_string
        
        st.download_button("📥 Download Excel (CSV)", csv_output.encode('utf-8'), f"Report_{kat_v}_{bln_v}.csv", "text/csv")

        # Visual Dashboard
        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#3498db", "#e74c3c"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE (FAST SAVE) ---
    with t_upd:
        c1, c2, c3 = st.columns(3)
        u_bln = c1.selectbox("Bulan:", list_bulan, key="u_bln")
        u_cbg = c2.selectbox("Cabang:", list_cabang, key="u_cbg")
        cur = st.session_state.db_kyc_v21[thn_v][kat_v][u_cbg]['r'][u_bln]
        u_val = c3.number_input("Total Realisasi:", min_value=0, value=None if cur==0 else cur)
        
        if st.button("💾 Simpan Progres", use_container_width=True):
            st.session_state.db_kyc_v21[thn_v][kat_v][u_cbg]['r'][u_bln] = int(u_val) if u_val is not None else 0
            st.toast("Data Disimpan!")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: TARGET ---
    with t_tar:
        with st.form("f_tar"):
            t_cols = st.columns(4)
            for i, c in enumerate(list_cabang):
                val_t = st.session_state.db_kyc_v21[thn_v][kat_v][c]['t']
                st.session_state.db_kyc_v21[thn_v][kat_v][c]['t'] = t_cols[i%4].number_input(f"Target {c}", min_value=0, value=None if val_t==0 else val_t)
            if st.form_submit_button("Simpan Semua Target"):
                st.rerun()
