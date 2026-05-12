import streamlit as st
import pandas as pd
from auth_utils import load_user_db

# Import modul tab
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

# KONFIGURASI LAYAR
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

def main_interface():
    # Menetapkan Identitas Default karena login ditiadakan
    if 'user' not in st.session_state:
        st.session_state['user'] = "Administrator"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"

    # Header Atas
    c1, c2 = st.columns([10, 2])
    c1.markdown(f"👤 **Mode:** Akses Langsung | 🏷️ **Otoritas:** {st.session_state['role']}")
    
    # Tombol Reset Aplikasi (Jika diperlukan refresh total)
    if c2.button("🔄 Reset Aplikasi", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Load data utama dari modul screening
    db_p, stats, total = sc.fetch_all_data()

    # Navigasi Tab
    tabs = st.tabs(["🔍 Single", "🚀 Bulk", "📊 KYC Dashboard", "📝 Log Kegiatan", "👥 Users", "🕒 Admin Log"])
    
    with tabs[0]: sc.run_pencarian(st.session_state['user'], db_p, True)
    with tabs[1]: bat.run_bulk_screening()
    with tabs[2]: kyc.run_kyc_dashboard()
    with tabs[3]: kt.run_kegiatan_tracker()
    with tabs[4]: ut.run_user_management() # Menampilkan daftar user
    with tabs[5]: lt.run_log_admin(stats, total)

def main():
    # Langsung jalankan antarmuka utama
    main_interface()

if __name__ == "__main__":
    main()
