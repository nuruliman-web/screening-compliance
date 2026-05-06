import streamlit as st
import pandas as pd
import os
import io

def run_log_admin(stats, total):
    # --- Bagian Statistik (Cards) ---
    st.markdown("### 📊 Statistik Database")
    cols = st.columns(len(stats) + 1)
    
    for i, (name, val) in enumerate(stats.items()):
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <p style="margin: 0; color: #666; font-size: 12px; font-weight: bold;">{name.upper()}</p>
                    <p style="margin: 0; color: #0068c9; font-size: 20px; font-weight: 800;">{val:,}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with cols[-1]:
        st.markdown(f"""
            <div style="background-color: #0068c9; padding: 15px; border-radius: 10px; border: 1px solid #0068c9; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <p style="margin: 0; color: #ffffff; font-size: 12px; font-weight: bold;">TOTAL DATA</p>
                <p style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 800;">{total:,}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # --- Bagian Log Aktivitas ---
    st.markdown("### 🕒 Riwayat Aktivitas User")
    
    if os.path.exists("log_aktivitas.csv"):
        log_df = pd.read_csv("log_aktivitas.csv")
        
        # Tombol Aksi (Download & Reset)
        c1, c2, c3 = st.columns([3.5, 1, 1])
        
        # 1. Fitur Download Log
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            log_df.to_excel(writer, index=False, sheet_name='Log_Aktivitas')
        
        c2.download_button(
            label="📥 Download Log",
            data=output.getvalue(),
            file_name="Riwayat_Aktivitas_User.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # 2. Fitur Reset Log
        if c3.button("🔥 Reset Log", use_container_width=True):
            os.remove("log_aktivitas.csv")
            st.rerun()
            
        # Tampilkan Tabel
        st.dataframe(
            log_df.iloc[::-1], # Urutan dari yang paling baru
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Belum ada riwayat aktivitas yang tercatat.")
