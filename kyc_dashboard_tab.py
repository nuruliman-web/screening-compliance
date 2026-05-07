import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 2. DATABASE SESSION (V29) ---
    if 'db_kyc_v29' not in st.session_state:
        st.session_state.db_kyc_v29 = {
            thn: { kat: { c: {
                't': {r: 0 for r in risk_cats}, 
                'r': {m: 0 for m in list_bulan}
            } for c in list_cabang } 
            for kat in ["Perorangan", "Korporasi"] } for thn in list_tahun
        }

    st.markdown("<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring Pengkinian Data Nasabah</h2>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    st.markdown("---")
    f1, f2, f3 = st.columns(3)
    with f1: thn_v = st.selectbox("📅 Tahun:", list_tahun, index=2) 
    with f2: kat_v = st.selectbox("📂 Kategori:", ["Perorangan", "Korporasi"])
    with f3: bln_v = st.selectbox("📆 Posisi Bulan:", list_bulan, index=0)
    st.markdown("---")

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard Utama", "✍️ Update Progres", "⚙️ Input Target Risk"])

    # --- TAB 1: VIEW DASHBOARD ---
    with tab_v:
        db_ref = st.session_state.db_kyc_v29[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        
        rows = []
        for cbg in list_cabang:
            targets = db_ref[cbg]['t']
            total_target = sum(targets.values())
            
            # Logika Latest Status (Terbawa)
            real_tampil = 0
            for i in range(idx_pilihan, -1, -1):
                val = db_ref[cbg]['r'][list_bulan[i]]
                if val > 0:
                    real_tampil = val
                    break
            
            p_sudah = int(round((real_tampil / total_target) * 100)) if total_target > 0 else (100 if real_tampil > 0 else 0)
            sisa = max(0, total_target - real_tampil)
            
            rows.append({
                'Cabang': cbg, 'High': targets['High'], 'Medium': targets['Medium'], 'Low': targets['Low'],
                'Total Target': total_target, 'Realisasi': real_tampil, '% Capaian': f"{p_sudah}%", 'Sisa': sisa
            })
        
        df = pd.DataFrame(rows)
        
        # Metrics
        tt, tr = df['Total Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi s/d {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#3498db", "#e74c3c"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES (TETAP SAMA) ---
    with tab_p:
        st.subheader(f"✍️ Update Progres: {bln_v}")
        c1, c2 = st.columns(2)
        u_cbg = c1.selectbox("Pilih Cabang:", list_cabang, key="up_cbg")
        old_val = st.session_state.db_kyc_v29[thn_v][kat_v][u_cbg]['r'][bln_v]
        u_val = c2.number_input(f"Total Nasabah Selesai ({bln_v}):", min_value=0, value=None if old_val==0 else old_val)
        
        if st.button("💾 Simpan Progres", use_container_width=True):
            st.session_state.db_kyc_v29[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
            st.toast("Progres berhasil disimpan!")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: TARGET PER RISK (BARU) ---
    with tab_t:
        st.subheader("⚙️ Setting Target Berdasarkan Tingkat Risiko")
        st.caption("Masukkan target per kategori risiko untuk tiap cabang (Total Target akan otomatis terhitung).")
        
        with st.form("f_target_risk"):
            # Header Tabel Manual
            h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
            h1.write("**Cabang**")
            h2.write("**High**")
            h3.write("**Medium**")
            h4.write("**Low**")
            
            for cbg in list_cabang:
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{cbg}**")
                curr_t = st.session_state.db_kyc_v29[thn_v][kat_v][cbg]['t']
                
                st.session_state.db_kyc_v29[thn_v][kat_v][cbg]['t']['High'] = c2.number_input(f"H-{cbg}", min_value=0, value=curr_t['High'], label_visibility="collapsed")
                st.session_state.db_kyc_v29[thn_v][kat_v][cbg]['t']['Medium'] = c3.number_input(f"M-{cbg}", min_value=0, value=curr_t['Medium'], label_visibility="collapsed")
                st.session_state.db_kyc_v29[thn_v][kat_v][cbg]['t']['Low'] = c4.number_input(f"L-{cbg}", min_value=0, value=curr_t['Low'], label_visibility="collapsed")
            
            if st.form_submit_button("💾 Simpan Semua Target Risk", use_container_width=True):
                st.success("Target Risk Berhasil Diperbarui!")
                time.sleep(0.5)
                st.rerun()
