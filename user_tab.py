import streamlit as st
import pandas as pd
import os

def load_user_db():
    # Menyesuaikan dengan nama file database Anda, umumnya users.csv
    file_path = 'users.csv' 
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip() # Bersihkan spasi di nama kolom
            return df
        except:
            return pd.DataFrame(columns=['Email', 'Role', 'Status'])
    return pd.DataFrame(columns=['Email', 'Role', 'Status'])

def run_user_management():
    st.subheader("👥 Manajemen Pengguna")
    
    # Ambil data terbaru
    df_users = load_user_db()

    if not df_users.empty:
        # Menampilkan tabel (tanpa kolom password demi keamanan tampilan)
        cols_to_show = [c for c in df_users.columns if 'pass' not in c.lower()]
        
        st.dataframe(
            df_users[cols_to_show], 
            use_container_width=True, 
            hide_index=True
        )
        
        st.caption(f"Total user terdaftar: {len(df_users)}")
    else:
        st.warning("⚠️ Tidak ada data user yang ditemukan di database.")

    # Tetap sediakan expander untuk kontrol (opsional)
    with st.expander("Opsi Tambahan"):
        if st.button("Refresh Data User"):
            st.rerun()
