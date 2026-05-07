import streamlit as st
import pandas as pd

def run_kyc_dashboard():
    # Judul Rata Tengah
    st.markdown("<h3 style='text-align: center;'>📊 Dashboard Pengkinian Data Nasabah Perorangan 2026</h3>", unsafe_allow_html=True)
    
    # 1. MASTER DATA TARGET (DIKUNCI AGAR TIDAK SALAH HITUNG)
    # Pangkalan Kerinci diperbaiki jadi 21 (Total Target jadi 452)
    target_map = {
        'KPO': 182, 'Tangerang': 13, 'Depok': 30, 'Bekasi': 29, 'Kelapa Gading': 23,
        'Bogor': 5, 'Jambi': 80, 'Pekanbaru': 5, 'Pangkalan Kerinci': 21, 'Pontianak': 58, 'Siantan': 6
    }
    list_cabang = list(target_map.keys())
    list_bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # 2. INISIALISASI DATABASE (Ganti nama variabel agar data lama yang 'bug' terhapus)
    if 'db_kyc_v4_final' not in st.session_state:
        st.session_state.db_kyc_v4_final = {
            cbg: {m: 0 for m in list_bulan} for cbg in list_cabang
        }

    tab_view, tab_input = st.tabs(["📈 Tampilan Dashboard", "✍️ Input Data"])

    # --- TAB INPUT DATA ---
    with tab_input:
        st.info("Masukkan data realisasi per bulan. Sistem akan menjumlahkannya secara otomatis.")
        with st.form("form_kyc_v4"):
            c1, c2, c3 = st.columns(3)
            bln_in = c1.selectbox("Pilih Bulan:", list_bulan)
            cbg_in = c2.selectbox("Pilih Cabang:", list_cabang)
            jml_in = c3.number_input("Jumlah Realisasi Baru:", min_value=0, step=1)
            
            if st.form_submit_button("Simpan Data"):
                # Simpan angka ke bulan spesifik (Menggantikan nilai lama di bulan tersebut)
                st.session_state.db_kyc_v4_final[cbg_in][bln_in] = int(jml_in)
                st.success(f"Data {cbg_in} untuk bulan {bln_in} berhasil diperbarui!")
        
        if st.button("🗑️ Reset Semua Data (Kosongkan Dashboard)"):
            st.session_state.db_kyc_v4_final = {cbg: {m: 0 for m in list_bulan} for cbg in list_cabang}
            st.rerun()

    # --- TAB VIEW DASHBOARD ---
    with tab_view:
        # A. PILIHAN BULAN (Dropdown)
        filter_bln = st.selectbox("📅 Pilih Periode Laporan (Akumulatif s/d):", list_bulan)

        # B. LOGIKA PERHITUNGAN (Fixed & Accurate)
        idx_akhir = list_bulan.index(filter_bln) + 1
        bulan_terpilih = list_bulan[:idx_akhir]
        
        rows = []
        for cbg in list_cabang:
            target = target_map[cbg]
            # Menghitung akumulasi dari bulan pertama sampai bulan yang dipilih
            total_realisasi = sum(st.session_state.db_kyc_v4_final[cbg][m] for m in bulan_terpilih)
            
            # Capped 100% (Sesuai standar audit bank)
            sudah = min(total_realisasi, target)
            belum = max(0, target - sudah)
            
            # Persentase dibulatkan (round) agar lebih akurat dibanding int()
            p_sudah = round((sudah / target) * 100) if target > 0 else 0
            p_belum = 100 - p_sudah
            
            rows.append({
                'Cabang': cbg,
                'Target': target,
                'Sudah': sudah,
                '% Sudah': f"{p_sudah}%",
                'Belum': belum,
                '% Belum': f"{p_belum}%",
                'Progress_Val': sudah, # Untuk Grafik
                'Sisa_Val': belum      # Untuk Grafik
            })
        
        df_final = pd.DataFrame(rows)

        # C. TOTAL METRICS (Dashboard Utama)
        t_target = sum(target_map.values())
        t_sudah = df_final['Sudah'].sum()
        t_belum = t_target - t_sudah
        total_p = round((t_sudah / t_target) * 100) if t_target > 0 else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("🎯 Total Target Seluruhnya", f"{t_target}")
        m2.metric("✅ Total Sudah Dikinikan", f"{t_sudah}", f"{total_p}%")
        m3.metric("⏳ Total Belum Dikinikan", f"{t_belum}", f"{100-total_p}%", delta_color="inverse")

        st.divider()

        # D. TABEL DETAIL (NAIK KE ATAS & RATA TENGAH)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📋 Tabel Monitoring Per Cabang s/d {filter_bln}</p>", unsafe_allow_html=True)
        
        # CSS Fix untuk Teks Tengah
        st.markdown("""
            <style>
                div[data-testid="stDataFrame"] td {text-align: center !important;}
                div[data-testid="stDataFrame"] th {text-align: center !important;}
            </style>
        """, unsafe_allow_html=True)

        # Menampilkan kolom utama saja
        df_display = df_final[['Cabang', 'Target', 'Sudah', '% Sudah', 'Belum', '% Belum']]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # E. DIAGRAM BATANG (Stacked / Tumpuk)
        st.markdown(f"<p style='text-align: center; font-weight: bold;'>📊 Grafik Progress Realisasi (Sudah vs Belum)</p>", unsafe_allow_html=True)
        chart_data = df_final.set_index('Cabang')[['Progress_Val', 'Sisa_Val']]
        chart_data.columns = ['Sudah', 'Belum']
        st.bar_chart(chart_data, color=["#2ecc71", "#e74c3c"])

    st.caption("Fokus Data Perorangan 2026 | Data Akurat & Sinkron")
