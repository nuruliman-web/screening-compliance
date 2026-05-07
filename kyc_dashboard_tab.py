import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V23 - KOSONG TOTAL) ---
    if 'db_kyc_v23' not in st.session_state:
        # Inisialisasi database semua nol
        st.session_state.db_kyc_v23 = {
            thn: {
                kat: {
                    c: {'t': 0, 'r': {m: 0 for m in list_bulan}} for c in list_cabang
                } for kat in ["Perorangan", "Korporasi"]
            } for thn in list_tahun
        }

    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring Pengkinian Data Nasabah</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1: thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2) # Default 2026
    with f2: kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"])
    with f3: bln_v = st.selectbox("📆 s/d Bulan:", list_bulan, index=0) # Default Januari
    st.markdown("---")

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard", "✍️ Update Progres", "⚙️ Target Tahunan"])

    # --- TAB 1: VIEW DASHBOARD ---
    with tab_v:
        data = st.session_state.db_kyc_v23[thn_v][kat_v]
        idx_bln = list_bulan.index(bln_v) + 1
        rows = []
        for cbg in list_cabang:
            t = data[cbg]['t']
            r = sum(data[cbg]['r'][m] for m in list_bulan[:idx_bln])
            sdh = min(r, t) if t > 0 else r
            p_sdh = int(round((sdh / t) * 100)) if t > 0 else (100 if sdh > 0 else 0)
            rows.append({
                'Cabang': cbg, 'Target': t, 'Realisasi': sdh, 
                '% Sudah': f"{p_sdh}%", 'Sisa': max(0, t-sdh), 
                '% Belum': f"{100-p_sdh}%", 'v_s': sdh, 'v_b': max(0, t-sdh)
            })
        
        df = pd.DataFrame(rows)

        # Download Button (Fix Column Excel)
        csv_string = df[['Cabang', 'Target', 'Realisasi', '% Sudah', 'Sisa', '% Belum']].to_csv(index=False, sep=';')
        csv_output = "sep=;\n" + csv_string
        st.download_button("📥 Download Report (CSV)", csv_output.encode('utf-8'), f"Report_{kat_v}_{thn_v}.csv", "text/csv")

        # Metrics
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Capaian {kat_v} {thn_v} s/d {bln_v}</p>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric("✅ Realisasi", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        # Visual Chart & Table
        st.bar_chart(df.set_index('Cabang')[['v_s', 'v_b']].rename(columns={'v_s':'Sudah','v_b':'Sisa'}), color=["#3498db", "#e74c3c"])
        st.dataframe(df[['Cabang', 'Target', 'Realisasi', '% Sudah', 'Sisa', '% Belum']], use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES (FAST SAVE) ---
    with tab_p:
        st.subheader("✍️ Input Realisasi Bulanan")
        st.info("Pilih bulan dan cabang, lalu masukkan angka total realisasi pada bulan tersebut.")
        c1, c2, c3 = st.columns(3)
        u_bln = c1.selectbox("Bulan:", list_bulan, key="up_bln")
        u_cbg = c2.selectbox("Cabang:", list_cabang, key="up_cbg")
        curr = st.session_state.db_kyc_v23[thn_v][kat_v][u_cbg]['r'][u_bln]
        u_val = c3.number_input("Realisasi:", min_value=0, value=None if curr==0 else curr)
        
        if st.button("💾 Simpan Data Progres", use_container_width=True):
            st.session_state.db_kyc_v23[thn_v][kat_v][u_cbg]['r'][u_bln] = int(u_val) if u_val is not None else 0
            st.toast("Data Berhasil Disimpan!", icon="✅")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: SETTING TARGET ---
    with tab_t:
        st.subheader("⚙️ Input Target Tahunan")
        with st.form("form_target_clean"):
            t_cols = st.columns(4)
            nt = {}
            for i, c in enumerate(list_cabang):
                val_t = st.session_state.db_kyc_v23[thn_v][kat_v][c]['t']
                nt[c] = t_cols[i%4].number_input(f"Target {c}", min_value=0, value=None if val_t==0 else val_t)
            
            if st.form_submit_button("💾 Simpan Semua Target", use_container_width=True):
                for c, v in nt.items():
                    st.session_state.db_kyc_v23[thn_v][kat_v][c]['t'] = int(v) if v is not None else 0
                st.success("Seluruh Target Berhasil Diperbarui!")
                time.sleep(0.5)
                st.rerun()
