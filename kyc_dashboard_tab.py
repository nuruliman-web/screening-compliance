import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

def run_kyc_dashboard():
    # --- KONEKSI GSHEETS ---
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]
    risk_cats = ['High', 'Medium', 'Low']

    # --- FUNGSI LOAD DATA DARI GSHEETS ---
    def load_data_from_gsheets():
        try:
            df = conn.read(worksheet="KYC_Data", ttl=0)
            if df.empty: return None
            
            # Susun ulang dari tabel flat ke Dictionary Session State
            db = {str(thn): {kat: {c: {'t': {r: 0 for r in risk_cats}, 'r': {m: 0 for m in list_bulan}} 
                  for c in list_cabang} for kat in ["Perorangan", "Korporasi"]} for thn in list_tahun}
            
            for _, row in df.iterrows():
                thn, kat, cbg = str(row['Tahun']), row['Kategori'], row['Cabang']
                if thn in db and kat in db[thn] and cbg in db[thn][kat]:
                    db[thn][kat][cbg]['t'] = {'High': row['T_High'], 'Medium': row['T_Med'], 'Low': row['T_Low']}
                    for m in list_bulan:
                        db[thn][kat][cbg]['r'][m] = row.get(m, 0)
            return db
        except:
            return None

    # --- FUNGSI SIMPAN KE GSHEETS ---
    def save_data_to_gsheets():
        rows = []
        for thn, kats in st.session_state.db_kyc_v37.items():
            for kat, cbgs in kats.items():
                for cbg, data in cbgs.items():
                    row = {
                        'Tahun': thn, 'Kategori': kat, 'Cabang': cbg,
                        'T_High': data['t']['High'], 'T_Med': data['t']['Medium'], 'T_Low': data['t']['Low']
                    }
                    row.update(data['r']) # Masukkan data realisasi bulanan
                    rows.append(row)
        df_save = pd.DataFrame(rows)
        conn.update(worksheet="KYC_Data", data=df_save)

    # Inisialisasi Data
    if 'db_kyc_v37' not in st.session_state:
        data_gsheet = load_data_from_gsheets()
        if data_gsheet:
            st.session_state.db_kyc_v37 = data_gsheet
        else:
            st.session_state.db_kyc_v37 = {str(thn): {kat: {c: {'t': {r: 0 for r in risk_cats}, 'r': {m: 0 for m in list_bulan}} 
                                          for c in list_cabang} for kat in ["Perorangan", "Korporasi"]} for thn in list_tahun}

    # --- FILTER (Sama seperti kodinganmu) ---
    st.markdown("<h1 style='text-align: center;'>📊 PENGKINIAN DATA NASABAH</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        thn_v = str(f1.selectbox("📅 Pilih Tahun", list_tahun, index=2))
        kat_v = f2.selectbox("📂 Pilih Kategori", ["Perorangan", "Korporasi"])
        bln_v = f3.selectbox("📆 Posisi Bulan s/d", list_bulan, index=0)

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard Utama", "✍️ Update Progres", "⚙️ Setup Target Risk"])

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.markdown("### ✍️ Input Realisasi")
        c1, c2 = st.columns(2)
        u_cbg = c1.selectbox("Pilih Cabang", list_cabang, key="sb_cbg")
        old_val = st.session_state.db_kyc_v37[thn_v][kat_v][u_cbg]['r'][bln_v]
        u_val = c2.number_input(f"Total Selesai {bln_v}:", min_value=0, value=int(old_val))
        
        if st.button("💾 Simpan ke GSheets", use_container_width=True):
            st.session_state.db_kyc_v37[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val)
            save_data_to_gsheets()
            st.success("Data Sinkron ke Google Sheets!")
            time.sleep(1)
            st.rerun()

    # --- TAB 3: TARGET RISK ---
    with tab_t:
        st.markdown("### 🎯 Setup Target Risiko")
        # ... (Logika data_editor sama seperti sebelumnya) ...
        # Tambahkan save_data_to_gsheets() di tombol simpan targetnya
        if st.button("💾 Simpan Target ke GSheets", use_container_width=True):
            # ... (Logika loop update session state kamu) ...
            save_data_to_gsheets()
            st.success("Target Permanen Tersimpan!")
            st.rerun()
