import streamlit as st
import pandas as pd
from auth_utils import load_user_db

def run_user_management():
    st.header("👥 Daftar Pengguna Terdaftar")
    st.markdown("Halaman ini menampilkan daftar user yang ada dalam database sistem.")
    
    # Memanggil data dari CSV melalui auth_utils
    df_users = load_user_db()

    if not df_users.empty:
        # Menghapus kolom Password dari tampilan agar lebih rapi dan aman
        if 'Password' in df_users.columns:
            display_df = df_users.drop(columns=['Password'])
        else:
            display_df = df_users

        # Menampilkan tabel data user
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True
        )
        
        # Informasi tambahan di bawah tabel
        st.info(f"💡 Saat ini terdapat **{len(df_users)}** user yang terdata.")
    else:
        st.warning("⚠️ Belum ada data user yang terdeteksi di file `users.csv`.")

    # Tombol refresh manual untuk menarik data terbaru
    if st.button("🔄 Perbarui Tampilan Data"):
        st.rerun()
