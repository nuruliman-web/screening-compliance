import streamlit as st
import pandas as pd
import os

def run_log_admin(stats, total):
    # Bagian Statistik (Database Info)
    st.markdown("### 📊 Statistik Database")
    cols = st.columns(len(stats) + 1)
    
    # Loop untuk membuat card statistik tiap database
    for i, (name, val) in enumerate(stats.items()):
        with cols[i]:
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e6e9ef; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <p style="margin: 0; color: #666; font-size: 12px; font-weight: bold;">{name.upper()}</p>
                    <p style="margin: 0; color: #0068c9; font-size: 20px; font-weight: 800;">{val:,}</p>
                </div>
            """, unsafe_allow_html=True)
            
    # Card untuk TOTAL
    with cols[-1]:
        st.markdown(f"""
            <div style="background-color: #0068c9; padding: 15px; border-radius: 10px; border: 1px solid #0068c9; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <p style="margin: 0; color: #ffffff; font-size: 12px; font-weight: bold;">TOTAL DATA</p>
                <p style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 800;">{total:,}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Bagian Log Aktivitas
    st.markdown("### 🕒 Riwayat Aktivitas User")
    
    if os.path.exists("log_aktivitas.csv"):
        log_df = pd.read_csv("log_aktivitas.csv")
        
        # Tombol Reset Log di pojok kanan
        c1, c2 = st.columns([5, 1])
        if c2.button("🔥 Reset Log", use_container_width=True):
            os.remove("log_aktivitas.csv")
            st.rerun()
            
        # Tampilkan tabel log dengan desain full width
        st.dataframe(
            log_df.iloc[::-1], # Data terbaru di paling atas
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("Belum ada riwayat aktivitas.")
