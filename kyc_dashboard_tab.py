import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 2. DATABASE SESSION (V32) ---
    if 'db_kyc_v32' not in st.session_state:
        st.session_state.db_kyc_v32 = {
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
        db_ref = st.session_state.db_kyc_v32[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        
        rows = []
        for cbg in list_cabang:
            targets = db_ref[cbg]['t']
            total_t = sum(targets.values())
            
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
                'Cabang': cbg, 'High': targets['High'], 'Medium': targets['Medium'], 'Low': targets['Low'],
                'Target': total_t, 'Realisasi': real_tampil, 
                '% Prog': f"{p_sudah}%", 'Sisa': sisa, '% Sisa': f"{p_sisa}%"
            })
        
        df = pd.DataFrame(rows)
        
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#4F46E5", "#EF4444"])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.markdown("### ✍️ Input Realisasi Bulanan")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            u_cbg = c1.selectbox("Pilih Cabang", list_cabang, key="up_cbg")
            old_val = st.session_state.db_kyc_v32[thn_v][kat_v][u_cbg]['r'][bln_v]
            # Value=None membuat input box kosong jika data 0
            u_val = c2.number_input(f"Angka Realisasi s/d {bln_v}:", min_value=0, value=None if old_val==0 else old_val)
            
            if st.button("💾 Simpan Progres", use_container_width=True):
                st.session_state.db_kyc_v32[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
                st.toast("Data Disimpan!")
                time.sleep(0.5)
                st.rerun()

    # --- TAB 3: TARGET PER RISK (RARE DESIGN) ---
    with tab_t:
        st.markdown("### 🎯 Setup Target Risiko")
        st.caption("Kosongkan input jika tidak ada target (otomatis dianggap 0).")
        
        with st.form("form_target_v32"):
            # Header Legend - Ukuran kolom disesuaikan (1.5 untuk nama cabang yang panjang)
            l1, l2, l3, l4 = st.columns([1.5, 1, 1, 1])
            l1.markdown("**Cabang**")
            l2.markdown("🔴 **High**")
            l3.markdown("🟡 **Med**")
            l4.markdown("🟢 **Low**")
            st.divider()

            for cbg in list_cabang:
                c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
                c1.write(f"**{cbg}**")
                curr = st.session_state.db_kyc_v32[thn_v][kat_v][cbg]['t']
                
                # Angka 0 dihapus otomatis dengan value=None
                val_h = c2.number_input(f"H_{cbg}", min_value=0, value=None if curr['High']==0 else curr['High'], label_visibility="collapsed")
                val_m = c3.number_input(f"M_{cbg}", min_value=0, value=None if curr['Medium']==0 else curr['Medium'], label_visibility="collapsed")
                val_l = c4.number_input(f"L_{cbg}", min_value=0, value=None if curr['Low']==0 else curr['Low'], label_visibility="collapsed")
                
                # Assign kembali ke session
                st.session_state.db_kyc_v32[thn_v][kat_v][cbg]['t']['High'] = val_h if val_h is not None else 0
                st.session_state.db_kyc_v32[thn_v][kat_v][cbg]['t']['Medium'] = val_m if val_m is not None else 0
                st.session_state.db_kyc_v32[thn_v][kat_v][cbg]['t']['Low'] = val_l if val_l is not None else 0
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Simpan Seluruh Target Tahunan", use_container_width=True):
                st.success("Target berhasil diperbarui!")
                time.sleep(0.5)
                st.rerun()
