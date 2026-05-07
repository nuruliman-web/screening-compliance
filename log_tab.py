import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import io

def run_log_admin(stats, total):
    # 1. KONEKSI GSHEETS
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    st.markdown("### 📊 Statistik Database")
    # (Bagian UI Statistik tetap sama menggunakan variabel stats dan total yang dikirim)
    cols = st.columns(len(stats) + 1)
    for i, (name, val) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label=name.upper(), value=f"{val:,}".replace(",", "."))
    with cols[-1]:
        st.metric(label="TOTAL DATA", value=f"{total:,}".replace(",", "."))

    st.divider()

    # 2. BAGIAN LOG AKTIVITAS (GSHEETS)
    st.markdown("### 🕒 Riwayat Aktivitas User (Sync to GSheets)")
    
    try:
        # Baca riwayat dari GSheets
        log_df = conn.read(worksheet="Admin_Log", ttl=0)
    except:
        log_df = pd.DataFrame(columns=["Timestamp", "User", "Aksi", "Keterangan"])

    if not log_df.empty:
        # Tombol Aksi
        c1, c2 = st.columns([4, 1])
        
        # Download Log (Excel)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            log_df.to_excel(writer, index=False, sheet_name='Log_Aktivitas')
        
        c2.download_button(
            label="📥 Download Log",
            data=output.getvalue(),
            file_name="Riwayat_Aktivitas_GSheets.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Tampilkan Tabel (Urutan terbaru di atas)
        st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada riwayat aktivitas di Google Sheets.")
