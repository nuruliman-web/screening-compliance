import streamlit as st
import pandas as pd
from auth_utils import load_user_db, hash_pass

# Import semua tab modul
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt

# KONFIGURASI LAYAR LEBAR (WIDE)
st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")

def main_interface():
    # Inisialisasi session state jika belum ada karena login dihapus
    if 'user' not in st.session_state:
        st.session_state['user'] = "Admin_User"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"

    # Header & Tombol Reset
    c1, c2 = st.columns([10, 2])
    c1.markdown(f"👤 **User:** {st.session_state['user']} | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🔄 Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    
    # Ambil Data Utama
    db_p, stats, total = sc.fetch_all_data()

    # Menu Tabs Horizontal
    if st.session_state['role'] == "Admin":
        tabs = st.tabs(["🔍 Single", "🚀 Bulk", "📊 KYC Dashboard", "📝 Log Kegiatan", "👥 Users", "🕒 Admin Log"])
        with tabs[0]: sc.run_pencarian(st.session_state['user'], db_p, True)
        with tabs[1]: bat.run_bulk_screening()
        with tabs[2]: kyc.run_kyc_dashboard()
        with tabs[3]: kt.run_kegiatan_tracker()
        with tabs[4]: ut.run_user_management() # Memanggil tab user
        with tabs[5]: lt.run_log_admin(stats, total)
    else:
        tabs = st.tabs(["🔍 Single", "🚀 Bulk", "📊 KYC Dashboard", "📝 Log Kegiatan"])
        with tabs[0]: sc.run_pencarian(st.session_state['user'], db_p, False)
        with tabs[1]: bat.run_bulk_screening()
        with tabs[2]: kyc.run_kyc_dashboard()
        with tabs[3]: kt.run_kegiatan_tracker()

def main():
    # Langsung ke interface utama
    main_interface()

if __name__ == "__main__":
    main()
