import streamlit as st
import pandas as pd
from auth_utils import load_user_db

def run_user_management():
    st.subheader("👥 Manajemen Pengguna")
    
    # Ambil data dari auth_utils
    df_users = load_user_db()

    if df_users is not None and not df_users.empty:
        # Filter kolom agar password tidak tampil
        display_cols = [c for c in df_users.columns if 'pass' not in c.lower()]
        
        st.dataframe(
            df_users[display_cols], 
            use_container_width=True, 
            hide_index=True
        )
        st.caption(f"Menampilkan {len(df_users)} pengguna terdaftar.")
    else:
        st.info("💡 Belum ada data pengguna. Pastikan file 'users.csv' tersedia.")

    if st.button("🔄 Refresh Data"):
        st.rerun()
