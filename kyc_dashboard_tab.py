import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 2. DATABASE SESSION (V31) ---
    if 'db_kyc_v31' not in st.session_state:
        st.session_state.db_kyc_v31 = {
            thn: { kat: { c: {
                't': {r: 0 for r in risk_cats}, 
                'r': {m: 0 for m in list_bulan}
            } for c in list_cabang } 
            for kat in ["Perorangan", "Korporasi"] } for thn in list_tahun
        }

    st.markdown("<h1 style='text-align: center; color: #0F172A; font-family: sans-serif;'>📊 KYC Analytics Dashboard</h1>", unsafe_allow_html=True)
    
    # --- 3. FILTER UTAMA ---
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        with f1: thn_v = st.selectbox("📅 Pilih Tahun", list_tahun, index=2) 
        with f2: kat_v = st.selectbox("📂 Pilih Kategori", ["Perorangan", "Korporasi"])
        with f3: bln_v = st.selectbox("📆 Posisi Bulan s/d", list_bulan, index=0)

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard Utama", "✍️ Update Progres", "⚙️ Setup Target Risk"])

    # --- TAB 1: VIEW DASHBOARD ---
    with tab_v:
        db_ref = st.session_state.db_kyc_v31[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        
        rows = []
        for cbg in list_cabang:
            targets = db_ref[cbg]['t']
            total_t = sum(targets.values())
            
            # Logic Latest Status
            real_tampil = 0
            for i in range(idx_pilihan, -1, -1):
                val = db_ref[cbg]['r'][list_bulan[i]]
                if val > 0:
                    real_tampil = val
                    break
            
            p_sudah = int(round((real_tampil / total_t) * 100)) if total_t > 0 else (100 if real_tampil > 0 else 0)
            sisa = max(0, total_t - real_tampil)
            p_sisa = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg, 
                'High': targets['High'], 'Medium': targets['Medium'], 'Low': targets['Low'],
                'Total Target': total_t, 
                'Realisasi': real_tampil, 
                '% Progres': f"{p_sudah}%", 
                'Sisa': sisa, 
                '% Sisa': f"{p_sisa}%" # INI SUDAH DIPASTIKAN ADA
            })
        
        df = pd.DataFrame(rows)
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Total Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa Keseluruhan", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#4F46E5", "#EF4444"])
        
        st.markdown("### 📋 Tabel Rincian Data")
        # Kolom % Sisa sekarang masuk ke tampilan
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.markdown("### ✍️ Input Realisasi Bulanan")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            u_cbg = c1.selectbox("Pilih Cabang", list_cabang, key="up_cbg")
            old_val = st.session_state.db_kyc_v31[thn_v][kat_v][u_cbg]['r'][bln_v]
            u_val = c2.number_input(f"Angka Realisasi s/d {bln_v}:", min_value=0, value=None if old_val==0 else old_val)
            
            if st.button("💾 Simpan Progres", use_container_width=True):
                st.session_state.db_kyc_v31[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
                st.toast("Data Disimpan!")
                time.sleep(0.5)
                st.rerun()

    # --- TAB 3: TARGET PER RISK (CLEAN DESIGN) ---
    with tab_t:
        st.markdown("### 🎯 Pengaturan Target Risiko")
        st.write("Silakan isi target per kategori risiko untuk masing-masing cabang.")
        
        with st.form("form_target_modern"):
            # Header Legend
            l1, l2, l3, l4 = st.columns([2, 1, 1, 1])
            l1.markdown("**Nama Cabang**")
            l2.markdown("🔴 **High**")
            l3.markdown("🟡 **Medium**")
            l4.markdown("🟢 **Low**")
            st.divider()

            for cbg in list_cabang:
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{cbg}**")
                curr = st.session_state.db_kyc_v31[thn_v][kat_v][cbg]['t']
                
                # Input yang diletakkan sejajar dengan rapi
                st.session_state.db_kyc_v31[thn_v][kat_v][cbg]['t']['High'] = c2.number_input(f"H_{cbg}", min_value=0, value=curr['High'], label_visibility="collapsed")
                st.session_state.db_kyc_v31[thn_v][kat_v][cbg]['t']['Medium'] = c3.number_input(f"M_{cbg}", min_value=0, value=curr['Medium'], label_visibility="collapsed")
                st.session_state.db_kyc_v31[thn_v][kat_v][cbg]['t']['Low'] = c4.number_input(f"L_{cbg}", min_value=0, value=curr['Low'], label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Simpan Seluruh Target Tahunan", use_container_width=True):
                st.success("Berhasil! Target tahunan telah diperbarui.")
                time.sleep(0.5)
                st.rerun()
