import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 2. DATABASE SESSION (V30) ---
    if 'db_kyc_v30' not in st.session_state:
        st.session_state.db_kyc_v30 = {
            thn: { kat: { c: {
                't': {r: 0 for r in risk_cats}, 
                'r': {m: 0 for m in list_bulan}
            } for c in list_cabang } 
            for kat in ["Perorangan", "Korporasi"] } for thn in list_tahun
        }

    # Header Kece
    st.markdown("<h1 style='text-align: center; color: #0F172A;'>✨ KYC Track Master</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B;'>Monitoring pengkinian data nasabah dengan gaya.</p>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        with f1: thn_v = st.selectbox("📅 Tahun", list_tahun, index=2) 
        with f2: kat_v = st.selectbox("📂 Kategori", ["Perorangan", "Korporasi"])
        with f3: bln_v = st.selectbox("📆 Posisi Bulan", list_bulan, index=0)

    tab_v, tab_p, tab_t = st.tabs(["📊 Dashboard", "✏️ Update Progres", "🎯 Setup Target"])

    # --- TAB 1: VIEW DASHBOARD ---
    with tab_v:
        db_ref = st.session_state.db_kyc_v30[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        
        rows = []
        for cbg in list_cabang:
            targets = db_ref[cbg]['t']
            total_target = sum(targets.values())
            
            # Logic Latest Status
            real_tampil = 0
            for i in range(idx_pilihan, -1, -1):
                val = db_ref[cbg]['r'][list_bulan[i]]
                if val > 0:
                    real_tampil = val
                    break
            
            p_sudah = int(round((real_tampil / total_target) * 100)) if total_target > 0 else (100 if real_tampil > 0 else 0)
            sisa = max(0, total_target - real_tampil)
            p_sisa = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg, 'High': targets['High'], 'Medium': targets['Medium'], 'Low': targets['Low'],
                'Target': total_target, 'Realisasi': real_tampil, 
                '% Progres': f"{p_sudah}%", 'Sisa': sisa, '% Sisa': f"{p_sisa}%",
                'v_s': real_tampil, 'v_b': sisa
            })
        
        df = pd.DataFrame(rows)
        
        # Metrics Clean
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa Keseluruhan", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        st.bar_chart(df.set_index('Cabang')[['v_s', 'v_b']].rename(columns={'v_s':'Selesai','v_b':'Sisa'}), color=["#6366F1", "#F87171"])
        
        st.markdown("### 📋 Detail Data")
        st.dataframe(df[['Cabang', 'High', 'Medium', 'Low', 'Target', 'Realisasi', '% Progres', 'Sisa', '% Sisa']], 
                     use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.markdown("### ✏️ Input Progres Terbaru")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            u_cbg = c1.selectbox("Pilih Cabang", list_cabang, key="up_cbg")
            old_val = st.session_state.db_kyc_v30[thn_v][kat_v][u_cbg]['r'][bln_v]
            u_val = c2.number_input(f"Total Nasabah Selesai di {bln_v}", min_value=0, value=None if old_val==0 else old_val)
            
            if st.button("🚀 Simpan Data Progres", use_container_width=True):
                st.session_state.db_kyc_v30[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
                st.toast("Mantap! Data berhasil diupdate.", icon="🔥")
                time.sleep(0.5)
                st.rerun()

    # --- TAB 3: TARGET PER RISK (DESIGN GEN-Z) ---
    with tab_t:
        st.markdown("### 🎯 Setup Target Tahunan")
        st.info("Input target High, Medium, dan Low untuk masing-masing cabang. Total akan terhitung otomatis.")
        
        with st.form("f_target_aesthetic"):
            # Kita bagi 2 kolom besar untuk list cabang biar gak terlalu panjang ke bawah
            main_col1, main_col2 = st.columns(2)
            
            for idx, cbg in enumerate(list_cabang):
                # Pilih kolom kiri atau kanan
                target_col = main_col1 if idx % 2 == 0 else main_col2
                
                with target_col.container(border=True):
                    st.markdown(f"📍 **{cbg}**")
                    curr_t = st.session_state.db_kyc_v30[thn_v][kat_v][cbg]['t']
                    
                    # Input mungil berjajar
                    i1, i2, i3 = st.columns(3)
                    st.session_state.db_kyc_v30[thn_v][kat_v][cbg]['t']['High'] = i1.number_input(f"H-{cbg}", min_value=0, value=curr_t['High'], label_visibility="collapsed")
                    st.session_state.db_kyc_v30[thn_v][kat_v][cbg]['t']['Medium'] = i2.number_input(f"M-{cbg}", min_value=0, value=curr_t['Medium'], label_visibility="collapsed")
                    st.session_state.db_kyc_v30[thn_v][kat_v][cbg]['t']['Low'] = i3.number_input(f"L-{cbg}", min_value=0, value=curr_t['Low'], label_visibility="collapsed")
                    
                    # Label tipis di bawah input
                    i1.caption("High")
                    i2.caption("Med")
                    i3.caption("Low")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("✨ Simpan Semua Target Tahun Ini", use_container_width=True):
                st.success("Target Risk Berhasil Diperbarui!")
                time.sleep(0.5)
                st.rerun()
