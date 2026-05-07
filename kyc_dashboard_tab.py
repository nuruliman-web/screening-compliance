import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 2. DATABASE SESSION (V37) ---
    if 'db_kyc_v37' not in st.session_state:
        st.session_state.db_kyc_v37 = {
            thn: { kat: { c: {
                't': {r: 0 for r in risk_cats}, 
                'r': {m: 0 for m in list_bulan}
            } for c in list_cabang } 
            for kat in ["Perorangan", "Korporasi"] } for thn in list_tahun
        }

    st.markdown("<h1 style='text-align: center; color: #0F172A;'>📊 KYC Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        with f1: thn_v = st.selectbox("📅 Pilih Tahun", list_tahun, index=2) 
        with f2: kat_v = st.selectbox("📂 Pilih Kategori", ["Perorangan", "Korporasi"])
        with f3: bln_v = st.selectbox("📆 Posisi Bulan s/d", list_bulan, index=0)

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard Utama", "✍️ Update Progres", "⚙️ Setup Target Risk"])

    # --- TAB 1: DASHBOARD ---
    with tab_v:
        db_ref = st.session_state.db_kyc_v37[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        rows = []
        for cbg in list_cabang:
            t = db_ref[cbg]['t']
            total_t = sum(t.values())
            real_tampil = 0
            for i in range(idx_pilihan, -1, -1):
                val = db_ref[cbg]['r'][list_bulan[i]]
                if val > 0:
                    real_tampil = val
                    break
            
            p_sudah = int(round((real_tampil / total_t) * 100)) if total_t > 0 else (100 if real_tampil > 0 else 0)
            rows.append({
                'Cabang': cbg, 
                'High Risk': t['High'], 
                'Medium Risk': t['Medium'], 
                'Low Risk': t['Low'],
                'Total Target': total_t, 
                'Realisasi': real_tampil, 
                'Sisa': max(0, total_t - real_tampil),
                '% Capaian': f"{p_sudah}%"
            })
        
        df = pd.DataFrame(rows)
        
        # Metrics & Chart
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Total Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")
        
        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#4F46E5", "#EF4444"])
        
        # --- BAGIAN DOWNLOAD (FIXED) ---
        st.divider()
        c_t, c_d = st.columns([4,1])
        c_t.markdown("### 📋 Tabel Rincian Data")
        
        # Pakai sep=";" supaya Excel langsung deteksi kolom A, B, C, D dst.
        csv_data = df.to_csv(index=False, sep=";").encode('utf-8')
        c_d.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"Report_KYC_{kat_v}_{bln_v}.csv",
            mime='text/csv',
        )

        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={col: st.column_config.Column(alignment="center") for col in df.columns})

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.markdown("### ✍️ Input Realisasi")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            u_cbg = c1.selectbox("Pilih Cabang", list_cabang)
            old_val = st.session_state.db_kyc_v37[thn_v][kat_v][u_cbg]['r'][bln_v]
            u_val = c2.number_input(f"Total Selesai {bln_v}:", min_value=0, value=None if old_val==0 else old_val)
            if st.button("💾 Simpan Progres", use_container_width=True):
                st.session_state.db_kyc_v37[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
                st.rerun()

    # --- TAB 3: TARGET RISK (TABLE EDITOR) ---
    with tab_t:
        st.markdown("### 🎯 Setup Target Risiko")
        data_target = []
        for cbg in list_cabang:
            t = st.session_state.db_kyc_v37[thn_v][kat_v][cbg]['t']
            data_target.append({
                "Cabang": cbg,
                "High": None if t['High'] == 0 else t['High'],
                "Medium": None if t['Medium'] == 0 else t['Medium'],
                "Low": None if t['Low'] == 0 else t['Low']
            })
        
        edited_df = st.data_editor(
            pd.DataFrame(data_target),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cabang": st.column_config.Column(disabled=True),
                "High": st.column_config.NumberColumn("🔴 High", min_value=0),
                "Medium": st.column_config.NumberColumn("🟡 Medium", min_value=0),
                "Low": st.column_config.NumberColumn("🟢 Low", min_value=0),
            }
        )
        
        if st.button("💾 Simpan Perubahan", use_container_width=True):
            for _, row in edited_df.iterrows():
                c = row['Cabang']
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['High'] = int(row['High']) if pd.notnull(row['High']) else 0
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['Medium'] = int(row['Medium']) if pd.notnull(row['Medium']) else 0
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['Low'] = int(row['Low']) if pd.notnull(row['Low']) else 0
            st.success("Tersimpan!")
            time.sleep(0.5)
            st.rerun()
