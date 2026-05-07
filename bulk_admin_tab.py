import streamlit as st
import pandas as pd
from thefuzz import fuzz
import time
import re
from io import BytesIO # Tambahkan ini untuk handle download Excel

# ... (fungsi clean_number_string tetap sama seperti sebelumnya)

def run_bulk_screening():
    # ... (bagian upload dan screening tetap sama sampai bagian hasil)

    if st.button("🚀 Jalankan Screening Otomatis"):
        # ... (proses screening looping tetap sama)
        
        # --- BAGIAN TAMPILKAN & DOWNLOAD HASIL ---
        if results:
            df_res = pd.DataFrame(results)
            st.warning(f"⚠️ Terdeteksi {len(df_res)} data yang cocok!")
            st.dataframe(df_res, use_container_width=True)
            
            # LOGIKA DOWNLOAD EXCEL (.xlsx)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_res.to_excel(writer, index=False, sheet_name='Hasil_Screening')
                # writer.save() # Untuk versi pandas lama, jika versi baru tidak perlu
            
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Laporan Match (.xlsx)",
                data=processed_data,
                file_name="Hasil_Bulk_Screening.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.success("✅ Bersih! Tidak ada data nasabah yang cocok.")
