import streamlit as st
import pandas as pd
import time
import os

def run_kyc_dashboard():
    # --- 1. SETUP PENYIMPANAN LOKAL ---
    LOCAL_DB_FILE = "database_kyc_lokal.csv"

    # --- 2. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- 3. FUNGSI SYNC LOKAL (Ganti GSheets) ---
    def load_from_local():
        if not os.path.exists(LOCAL_DB_FILE):
            return None
        try:
            df = pd.read_csv(LOCAL_DB_FILE)
            # Rekonstruksi data ke Dictionary
            new_db = {thn: {kat: {c: {'t': {r: 0 for r in risk_cats}, 'r': {m: 0 for m in list_bulan}} 
                      for c in list_cabang} for kat in ["Perorangan", "Korporasi"]} for thn in list_tahun}
            
            for _, row in df.iterrows():
                thn, kat, cbg = int(row['Tahun']), row['Kategori'], row['Cabang']
                if thn in new_db:
                    new_db[thn][kat][cbg]['t'] = {
                        'High': int(row['T_High']), 'Medium': int(row['T_Med']), 'Low': int(row['T_Low'])
                    }
                    for bln in list_bulan:
                        new_db[thn][kat][cbg]['r'][bln] = int(row[bln])
            return new_db
        except:
            return None

    def save_to_local(db):
        rows = []
        for thn in list_tahun:
            for kat in ["Perorangan", "Korporasi"]:
                for cbg in list_cabang:
                    data = db[thn][kat][cbg]
                    row = {
                        "Tahun": thn, "Kategori": kat, "Cabang": cbg,
                        "T_High": data['t']['High'], "T_Med": data['t']['Medium'], "T_Low": data['t']['Low']
                    }
                    row.update(data['r'])
                    rows.append(row)
        df_save = pd.DataFrame(rows)
        df_save.to_csv(LOCAL_DB_FILE, index=False)

    # --- 4. INISIALISASI SESSION STATE ---
    if 'db_kyc_v37' not in st.session_state:
        data_lokal = load_from_local()
        if data_lokal:
            st.session_state.db_kyc_v37 = data_lokal
        else:
            # Template Default
            st.session_state.db_kyc_v37 = {
                thn: { kat: { c: {
                    't': {r: 0 for r in risk_cats}, 
                    'r': {m: 0 for m in list_bulan}
                } for c in list_cabang } 
                for kat in ["Perorangan", "Korporasi"] } for thn in list_tahun
            }

    st.markdown("<h1 style='text-align: center; color: #0F172A;'>📊 PENGKINIAN DATA NASABAH (LOCAL)</h1>", unsafe_allow_html=True)
    
    # --- 5. FILTER UTAMA ---
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
                'Cabang': cbg, 'High Risk': t['High'], 'Medium Risk': t['Medium'], 'Low Risk': t['Low'],
                'Total Target': total_t, 'Realisasi': real_tampil, 'Sisa': max(0, total_t - real_tampil),
                '% Capaian': f"{p_sudah}%"
            })
        
        df = pd.DataFrame(rows)
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Total Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")
        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#4F46E5", "#EF4444"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Tambahkan tombol download database
        csv_db = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Summary Laporan (CSV)", csv_db, "Summary_KYC.csv", "text/csv")

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
                save_to_local(st.session_state.db_kyc_v37) # <--- SAVE LOKAL
                st.success("Berhasil Simpan ke Database Lokal!")
                time.sleep(0.5)
                st.rerun()

    # --- TAB 3: TARGET RISK ---
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
        
        edited_df = st.data_editor(pd.DataFrame(data_target), use_container_width=True, hide_index=True)
        
        if st.button("💾 Simpan Perubahan Target", use_container_width=True):
            for _, row in edited_df.iterrows():
                c = row['Cabang']
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['High'] = int(row['High']) if pd.notnull(row['High']) else 0
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['Medium'] = int(row['Medium']) if pd.notnull(row['Medium']) else 0
                st.session_state.db_kyc_v37[thn_v][kat_v][c]['t']['Low'] = int(row['Low']) if pd.notnull(row['Low']) else 0
            save_to_local(st.session_state.db_kyc_v37) # <--- SAVE LOKAL
            st.success("Target Berhasil Diperbarui!")
            time.sleep(0.5)
            st.rerun()
