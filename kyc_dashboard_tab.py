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

    # --- 3. FUNGSI SYNC LOKAL ---
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

    # --- 4. FUNGSI INJEKSI DATA MANUAL (DARI GAMBAR) ---
    def get_default_target(cbg, kat):
        # Mengambil data dari kolom "Total Nasabah" di gambar
        # Dimasukkan ke Low Risk terlebih dahulu agar total summary-nya cocok 100%
        if kat == "Perorangan":
            if cbg == 'KPO':                return {'High': 0, 'Medium': 0, 'Low': 182}
            elif cbg == 'Tangerang':        return {'High': 0, 'Medium': 0, 'Low': 13}
            elif cbg == 'Depok':            return {'High': 0, 'Medium': 0, 'Low': 30}
            elif cbg == 'Bekasi':           return {'High': 0, 'Medium': 0, 'Low': 52}
            elif cbg == 'Bogor':            return {'High': 0, 'Medium': 0, 'Low': 5}
            elif cbg == 'Jambi':            return {'High': 0, 'Medium': 0, 'Low': 80}
            elif cbg == 'Pekanbaru':        return {'High': 0, 'Medium': 0, 'Low': 5}
            elif cbg == 'Pangkalan Kerinci': return {'High': 0, 'Medium': 0, 'Low': 21}
            elif cbg == 'Pontianak':        return {'High': 0, 'Medium': 0, 'Low': 58}
            elif cbg == 'Siantan':          return {'High': 0, 'Medium': 0, 'Low': 6}
            
        elif kat == "Korporasi":  # Badan Usaha
            if cbg == 'KPO':                return {'High': 0, 'Medium': 0, 'Low': 32}
            elif cbg == 'Tangerang':        return {'High': 0, 'Medium': 0, 'Low': 3}
            elif cbg == 'Bekasi':           return {'High': 0, 'Medium': 0, 'Low': 1}
            elif cbg == 'Bogor':            return {'High': 0, 'Medium': 0, 'Low': 2}
            elif cbg == 'Jambi':            return {'High': 0, 'Medium': 0, 'Low': 1}
            elif cbg == 'Pontianak':        return {'High': 0, 'Medium': 0, 'Low': 7}
            
        return {'High': 0, 'Medium': 0, 'Low': 0}

    def get_default_realisasi(cbg, kat):
        # Base template isi 0 untuk semua bulan
        realisasi = {m: 0 for m in list_bulan}
        
        # Mengambil data dari kolom "Telah Dikinikan" secara kumulatif
        if kat == "Perorangan":
            if cbg == 'KPO':                realisasi.update({'Januari': 57, 'Februari': 57, 'Maret': 57, 'April': 182})
            elif cbg == 'Tangerang':        realisasi.update({'Januari': 12, 'Februari': 12, 'Maret': 12, 'April': 13})
            elif cbg == 'Depok':            realisasi.update({'Januari': 0, 'Februari': 0, 'Maret': 30, 'April': 30})
            elif cbg == 'Bekasi':           realisasi.update({'Januari': 0, 'Februari': 0, 'Maret': 0, 'April': 4})
            elif cbg == 'Bogor':            realisasi.update({'Januari': 3, 'Februari': 4, 'Maret': 4, 'April': 5})
            elif cbg == 'Jambi':            realisasi.update({'Januari': 12, 'Februari': 12, 'Maret': 33, 'April': 43})
            elif cbg == 'Pekanbaru':        realisasi.update({'Januari': 5, 'Februari': 5, 'Maret': 5, 'April': 5})
            elif cbg == 'Pangkalan Kerinci': realisasi.update({'Januari': 1, 'Februari': 7, 'Maret': 21, 'April': 21})
            elif cbg == 'Pontianak':        realisasi.update({'Januari': 58, 'Februari': 58, 'Maret': 58, 'April': 58})
            elif cbg == 'Siantan':          realisasi.update({'Januari': 6, 'Februari': 6, 'Maret': 6, 'April': 6})
                
        elif kat == "Korporasi":  # Badan Usaha
            if cbg == 'KPO':                realisasi.update({'Januari': 0, 'Februari': 0, 'Maret': 0, 'April': 32})
            elif cbg == 'Tangerang':        realisasi.update({'Januari': 3, 'Februari': 3, 'Maret': 3, 'April': 3})
            elif cbg == 'Bekasi':           realisasi.update({'Januari': 0, 'Februari': 0, 'Maret': 0, 'April': 0})
            elif cbg == 'Bogor':            realisasi.update({'Januari': 2, 'Februari': 2, 'Maret': 2, 'April': 2})
            elif cbg == 'Jambi':            realisasi.update({'Januari': 0, 'Februari': 0, 'Maret': 0, 'April': 0})
            elif cbg == 'Pontianak':        realisasi.update({'Januari': 7, 'Februari': 7, 'Maret': 7, 'April': 7})
                
        return realisasi

    # --- 5. INISIALISASI SESSION STATE ---
    if 'db_kyc_v37' not in st.session_state:
        data_lokal = load_from_local()
        if data_lokal:
            st.session_state.db_kyc_v37 = data_lokal
        else:
            # Jika file CSV tidak ada, buat template baru + suntik data manual di atas
            st.session_state.db_kyc_v37 = {
                thn: { 
                    kat: { 
                        c: {
                            't': get_default_target(c, kat), 
                            'r': get_default_realisasi(c, kat)
                        } for c in list_cabang 
                    } for kat in ["Perorangan", "Korporasi"] 
                } for thn in list_tahun
            }

    # --- 6. INTERFACE UTAMA ---
    st.markdown("<h1 style='text-align: center; color: #0F172A;'>📊 PENGKINIAN DATA NASABAH (LOCAL)</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        with f1: thn_v = st.selectbox("📅 Pilih Tahun", list_tahun, index=2) # Default ke 2026
        with f2: kat_v = st.selectbox("📂 Pilih Kategori", ["Perorangan", "Korporasi"])
        with f3: bln_v = st.selectbox("📆 Posisi Bulan s/d", list_bulan, index=3) # Default langsung ke April

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
            
            # Algoritma mencari realisasi bulan aktif atau bulan sebelumnya jika bulan ini kosong
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
        
        # Bagian Metric Card Atas
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Total Target'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi {bln_v}", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")
        
        # Grafik & Tabel Data
        st.bar_chart(df.set_index('Cabang')[['Realisasi', 'Sisa']], color=["#4F46E5", "#EF4444"])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Download Button
        csv_db = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Summary Laporan (CSV)", csv_db, f"Summary_KYC_{kat_v}_{bln_v}.csv", "text/csv")

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
                save_to_local(st.session_state.db_kyc_v37) # Save ke file lokal CSV
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
            save_to_local(st.session_state.db_kyc_v37) # Save ke file lokal CSV
            st.success("Target Berhasil Diperbarui!")
            time.sleep(0.5)
            st.rerun()

if __name__ == "__main__":
    run_kyc_dashboard()
