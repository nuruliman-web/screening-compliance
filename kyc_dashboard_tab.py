import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION ---
    if 'db_kyc_v25' not in st.session_state:
        st.session_state.db_kyc_v25 = {
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
    with f1: thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2) 
    with f2: kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"])
    with f3: bln_v = st.selectbox("📆 Pilih Bulan:", list_bulan, index=0) 
    st.markdown("---")

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard", "✍️ Update Progres", "⚙️ Target Tahunan"])

    # --- TAB 1: VIEW DASHBOARD (MONTHLY VIEW) ---
    with tab_v:
        data = st.session_state.db_kyc_v25[thn_v][kat_v]
        
        rows = []
        for cbg in list_cabang:
            target_tahunan = data[cbg]['t']
            # Ambil data HANYA untuk bulan yang terpilih di filter
            realisasi_bulan_ini = data[cbg]['r'][bln_v]
            
            # Hitung sisa terhadap target tahunan
            sisa = max(0, target_tahunan - realisasi_bulan_ini)
            p_sudah = int(round((realisasi_bulan_ini / target_tahunan) * 100)) if target_tahunan > 0 else (100 if realisasi_bulan_ini > 0 else 0)
            
            rows.append({
                'Cabang': cbg, 
                'Target Tahunan': target_tahunan, 
                'Realisasi': realisasi_bulan_ini, 
                '% Capaian': f"{p_sudah}%", 
                'Sisa Target': sisa,
                'v_s': realisasi_bulan_ini, 
                'v_b': sisa
            })
        
        df = pd.DataFrame(rows)

        # Download Button
        csv_string = df[['Cabang', 'Target Tahunan', 'Realisasi', '% Capaian', 'Sisa Target']].to_csv(index=False, sep=';')
        csv_output = "sep=;\n" + csv_string
        st.download_button("📥 Download Report (CSV)", csv_output.encode('utf-8'), f"Report_{kat_v}_{bln_v}_{thn_v}.csv", "text/csv")

        # Metrics
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Data {kat_v} Bulan {bln_v} {thn_v}</p>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Target Tahunan'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa Target", f"{(tt-tr):,}".replace(",", "."), delta_color="inverse")

        # Visual Chart & Table
        st.bar_chart(df.set_index('Cabang')[['v_s', 'v_b']].rename(columns={'v_s':'Realisasi','v_b':'Sisa'}), color=["#3498db", "#e74c3c"])
        st.dataframe(df[['Cabang', 'Target Tahunan', 'Realisasi', '% Capaian', 'Sisa Target']], use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.subheader(f"✍️ Input Realisasi {bln_v}")
        st.write(f"Mengupdate data untuk cabang pada bulan **{bln_v}**.")
        c1, c2 = st.columns(2)
        u_cbg = c1.selectbox("Pilih Cabang:", list_cabang, key="up_cbg")
        curr = st.session_state.db_kyc_v25[thn_v][kat_v][u_cbg]['r'][bln_v]
        u_val = c2.number_input(f"Jumlah di Bulan {bln_v}:", min_value=0, value=None if curr==0 else curr)
        
        if st.button("💾 Simpan Data", use_container_width=True):
            st.session_state.db_kyc_v25[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
            st.toast(f"Data {u_cbg} {bln_v} Berhasil Disimpan!", icon="✅")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: SETTING TARGET ---
    with tab_t:
        st.subheader("⚙️ Input Target Tahunan")
        with st.form("form_target_v25"):
            t_cols = st.columns(4)
            nt = {}
            for i, c in enumerate(list_cabang):
                val_t = st.session_state.db_kyc_v25[thn_v][kat_v][c]['t']
                nt[c] = t_cols[i%4].number_input(f"Target {c}", min_value=0, value=None if val_t==0 else val_t)
            
            if st.form_submit_button("💾 Simpan Semua Target", use_container_width=True):
                for c, v in nt.items():
                    st.session_state.db_kyc_v25[thn_v][kat_v][c]['t'] = int(v) if v is not None else 0
                st.success("Target Terupdate!")
                time.sleep(0.5)
                st.rerun()
