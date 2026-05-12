import streamlit as st
import pandas as pd
import io
import os

def run_log_admin(stats, total):
    # --- 1. SETUP PENYIMPANAN LOKAL ---
    LOG_FILE_LOKAL = "admin_activity_log.csv"
    
    st.markdown("### 📊 Statistik Database")
    
    # UI Statistik (Tetap sama, menggunakan data dari parameter stats & total)
    cols = st.columns(len(stats) + 1)
    for i, (name, val) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label=name.upper(), value=f"{val:,}".replace(",", "."))
    with cols[-1]:
        st.metric(label="TOTAL DATA", value=f"{total:,}".replace(",", "."))

    st.divider()

    # --- 2. BAGIAN LOG AKTIVITAS (LOKAL CSV) ---
    st.markdown("### 🕒 Riwayat Aktivitas User")
    
    # Fungsi untuk memuat data dari file lokal
    if os.path.exists(LOG_FILE_LOKAL):
        try:
            log_df = pd.read_csv(LOG_FILE_LOKAL)
        except:
            log_df = pd.DataFrame(columns=["Timestamp", "User", "Aksi", "Keterangan"])
    else:
        # Jika file belum ada, buat DataFrame kosong
        log_df = pd.DataFrame(columns=["Timestamp", "User", "Aksi", "Keterangan"])

    if not log_df.empty:
        # Layout tombol download
        c1, c2 = st.columns([4, 1])
        
        # Download Log dalam format Excel (.xlsx)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            log_df.to_excel(writer, index=False, sheet_name='Log_Aktivitas')
        
        c2.download_button(
            label="📥 Download Log",
            data=output.getvalue(),
            file_name="Riwayat_Aktivitas_Admin.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # Tampilkan Tabel (Urutan terbaru di atas menggunakan iloc[::-1])
        st.dataframe(
            log_df.sort_values(by="Timestamp", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Belum ada riwayat aktivitas yang tercatat di database lokal.")

    # --- 3. FITUR TAMBAHAN: CLEAR LOG (Opsional) ---
    if not log_df.empty:
        if st.button("🗑️ Kosongkan Riwayat Log"):
            os.remove(LOG_FILE_LOKAL)
            st.success("Log telah dibersihkan!")
            st.rerun()
