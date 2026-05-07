import streamlit as st
import pandas as pd
import time

def run_kyc_dashboard():
    # --- 1. DATA MASTER ---
    list_cabang = ['KPO', 'Tangerang', 'Depok', 'Bekasi', 'Kelapa Gading', 'Bogor', 'Jambi', 'Pekanbaru', 'Pangkalan Kerinci', 'Pontianak', 'Siantan']
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    list_tahun = [2024, 2025, 2026, 2027, 2028]

    # --- 2. DATABASE SESSION (V27) ---
    if 'db_kyc_v27' not in st.session_state:
        st.session_state.db_kyc_v27 = {
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
    with f3: bln_v = st.selectbox("📆 Lihat Posisi Bulan:", list_bulan, index=0) 
    st.markdown("---")

    tab_v, tab_p, tab_t = st.tabs(["📈 Dashboard", "✍️ Update Progres", "⚙️ Target Tahunan"])

    # --- TAB 1: VIEW DASHBOARD (LATEST STATUS LOGIC) ---
    with tab_v:
        db_ref = st.session_state.db_kyc_v27[thn_v][kat_v]
        idx_pilihan = list_bulan.index(bln_v)
        
        rows = []
        for cbg in list_cabang:
            target_t = db_ref[cbg]['t']
            
            # LOGIKA TERBAWA (LATEST DATA): 
            # Cek dari bulan pilihan mundur ke Januari, ambil angka pertama yang > 0
            real_tampil = 0
            for i in range(idx_pilihan, -1, -1):
                bulan_cek = list_bulan[i]
                nilai_cek = db_ref[cbg]['r'][bulan_cek]
                if nilai_cek > 0:
                    real_tampil = nilai_cek
                    break
            
            p_sudah = int(round((real_tampil / target_t) * 100)) if target_t > 0 else (100 if real_tampil > 0 else 0)
            sisa = max(0, target_t - real_tampil)
            
            rows.append({
                'Cabang': cbg, 'Target Tahunan': target_t, 'Realisasi': real_tampil, 
                '% Capaian': f"{p_sudah}%", 'Sisa': sisa, '% Belum': f"{100-p_sudah}%",
                'v_s': real_tampil, 'v_b': sisa
            })
        
        df = pd.DataFrame(rows)

        # Download CSV
        csv_out = "sep=;\n" + df[['Cabang', 'Target Tahunan', 'Realisasi', '% Capaian', 'Sisa', '% Belum']].to_csv(index=False, sep=';')
        st.download_button("📥 Download Report (CSV)", csv_out.encode('utf-8'), f"Report_{kat_v}_{bln_v}.csv", "text/csv")

        # Metrics & Visual
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>Posisi Data {kat_v} s/d {bln_v} {thn_v}</p>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        tt, tr = df['Target Tahunan'].sum(), df['Realisasi'].sum()
        tp = int(round((tr/tt)*100)) if tt > 0 else 0
        m1.metric("🎯 Total Target", f"{tt:,}".replace(",", "."))
        m2.metric(f"✅ Realisasi Terakhir", f"{tr:,}".replace(",", "."), f"{tp}%")
        m3.metric("⏳ Total Sisa", f"{(tt-tr):,}".replace(",", "."), f"{100-tp}%", delta_color="inverse")

        st.bar_chart(df.set_index('Cabang')[['v_s', 'v_b']].rename(columns={'v_s':'Realisasi','v_b':'Sisa'}), color=["#3498db", "#e74c3c"])
        st.dataframe(df[['Cabang', 'Target Tahunan', 'Realisasi', '% Capaian', 'Sisa', '% Belum']], use_container_width=True, hide_index=True)

    # --- TAB 2: UPDATE PROGRES ---
    with tab_p:
        st.subheader(f"✍️ Update Progres {bln_v}")
        st.info("Masukkan angka realisasi terbaru. Jika tidak ada perubahan dari bulan lalu, biarkan kosong atau 0.")
        c1, c2 = st.columns(2)
        u_cbg = c1.selectbox("Pilih Cabang:", list_cabang, key="up_cbg")
        
        # Tampilkan data bulan ini
        old_val = st.session_state.db_kyc_v27[thn_v][kat_v][u_cbg]['r'][bln_v]
        u_val = c2.number_input(f"Angka Realisasi {bln_v}:", min_value=0, value=None if old_val==0 else old_val)
        
        if st.button("💾 Simpan Data", use_container_width=True):
            st.session_state.db_kyc_v27[thn_v][kat_v][u_cbg]['r'][bln_v] = int(u_val) if u_val is not None else 0
            st.toast("Berhasil disimpan!")
            time.sleep(0.5)
            st.rerun()

    # --- TAB 3: TARGET ---
    with tab_t:
        with st.form("f_tar_v27"):
            t_cols = st.columns(4)
            nt = {}
            for i, c in enumerate(list_cabang):
                val_t = st.session_state.db_kyc_v27[thn_v][kat_v][c]['t']
                nt[c] = t_cols[i%4].number_input(f"Target {c}", min_value=0, value=None if val_t==0 else val_t)
            if st.form_submit_button("Simpan Target", use_container_width=True):
                for c, v in nt.items(): st.session_state.db_kyc_v27[thn_v][kat_v][c]['t'] = int(v) if v is not None else 0
                st.rerun()
