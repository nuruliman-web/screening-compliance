import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # --- 1. MASTER DATA TARGET (DIKUNCI) ---
    target_perorangan = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    
    # Update Data Korporasi Sesuai Instruksi Terbaru (Total: 46)
    target_korporasi = {
        'KPO': 32, 'Tangerang': 3, 'Kelapa Gading': 1, 'Bogor': 2, 
        'Jambi': 1, 'Pontianak': 7, 'Depok': 0, 'Bekasi': 0, 
        'Pekanbaru': 0, 'Pangkalan Kerinci': 0, 'Siantan': 0
    }

    list_cabang = list(target_perorangan.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # --- 2. INISIALISASI DATABASE (V8 - Data Terkunci) ---
    if 'db_kyc_v8' not in st.session_state:
        st.session_state.db_kyc_v8 = {
            'Perorangan': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang},
            'Korporasi': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
        }

    # --- 3. SIDEBAR NAVIGASI ---
    with st.sidebar:
        st.title("⚙️ Menu Dashboard")
        kategori_view = st.radio("Pilih Kategori Nasabah:", ["Perorangan", "Korporasi"])
        st.divider()
        st.info(f"Target {kategori_view} Nasional: {sum(target_perorangan.values()) if kategori_view == 'Perorangan' else sum(target_korporasi.values())}")

    st.markdown(f"<h2 style='text-align: center; color: #1E293B;'>📊 Monitoring KYC {kategori_view} 2026</h2>", unsafe_allow_html=True)
    
    tab_view, tab_input = st.tabs([f"📈 View {kategori_view}", "✍️ Input Data"])

    # --- 4. TAB INPUT DATA ---
    with tab_input:
        st.subheader(f"Input Realisasi - {kategori_view}")
        with st.form("form_input_v8"):
            c1, c2, c3 = st.columns(3)
            bln_in = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg_in = c2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = c3.number_input("Jumlah Realisasi (Menambah data lama):", min_value=0, step=1)
            
            # Form otomatis mengikuti kategori yang sedang dilihat
            kat_in = st.radio("Kategori Nasabah:", ["Perorangan", "Korporasi"], index=0 if kategori_view == "Perorangan" else 1, horizontal=True)
            
            if st.form_submit_button("Simpan & Update"):
                st.session_state.db_kyc_v8[kat_in][cbg_in][bln_in] += int(jml_in)
                st.success(f"Berhasil menambahkan data {kat_in} - {cbg_in}")
        
        if st.button("🗑️ Reset Semua Data"):
            st.session_state.db_kyc_v8 = {
                'Perorangan': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang},
                'Korporasi': {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
            }
            st.rerun()

    # --- 5. TAB VIEW DASHBOARD ---
    with tab_view:
        # Pilihan Bulan
        filter_bln = st.selectbox("📅 Lihat Progres s/d Bulan:", list_bulan)

        # Logic Filter & Akumulasi
        active_target = target_perorangan if kategori_view == "Perorangan" else target_korporasi
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = active_target.get(cbg, 0)
            realisasi_raw = sum(st.session_state.db_kyc_v8[kategori_view][cbg][m] for m in bulan_terpilih)
            
            # Capping & Calculation
            sudah = min(realisasi_raw, target) if target > 0 else realisasi_raw
            belum = max(0, target - sudah)
            p_sudah = int(round((sudah / target) * 100)) if target > 0 else (100 if sudah > 0 else 0)
            
            rows.append({
                'Cabang': cbg, 'Target': int(target), 'Sudah': int(sudah),
                '% Sudah': f"{p_sudah}%", 'Belum': int(belum), '% Belum': f"{100 - p_sudah}%",
                'Val_Sudah': sudah, 'Val_Belum': belum
            })
        
        df_final = pd.DataFrame(rows)

        # A. DIAGRAM BATANG (Di Atas)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Progres {kategori_view} s/d {filter_bln}</p>", unsafe_allow_html=True)
        chart_data = df_final.set_index('Cabang')[['Val_Sudah', 'Val_Belum']]
        chart_data.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_data, color=["#3498db" if kategori_view == "Korporasi" else "#2ecc71", "#e74c3c"])

        # B. METRICS (Angka Gede)
        t_target = sum(active_target.values())
        t_sudah = df_final['Sudah'].sum()
        total_p = int(round((t_sudah / t_target) * 100)) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target", f"{t_target}")
        m2.metric("✅ Pencapaian", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Sisa", f"{t_target - t_sudah}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # C. TABEL DETAIL (Paling Bawah - Rata Tengah)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📋 Tabel Detail Monitoring {kategori_view}</p>", unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='stDataFrame'] td {text-align: center !important;}</style>", unsafe_allow_html=True)
        
        df_display = df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.caption("Fokus Data Perorangan & Korporasi 2026")
