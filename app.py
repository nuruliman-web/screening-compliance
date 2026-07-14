import streamlit as st
import pandas as pd
from auth_utils import load_user_db

# Import modul tab asli milikmu
import screening_tab as sc
import bulk_admin_tab as bat
import kyc_dashboard_tab as kyc
import kegiatan_tracker as kt
import user_tab as ut
import log_tab as lt
import chat_tab as chat

# IMPORT TAB BARU SIPESAT
import sipesat_tab as ss

st.set_page_config(page_title="Screening System", layout="wide", initial_sidebar_state="collapsed")


# --- Helper untuk popup chat via query param ---
def render_chat_popup_if_requested():
    params = st.experimental_get_query_params()
    chat_on = params.get("chat", [None])[0] == "1"

    # Floating chat icon (tampilan selalu)
    float_css = """
    <style>
    .floating-chat-button {
        position: fixed;
        right: 20px;
        bottom: 20px;
        z-index: 9999;
        background: #006ee6;
        color: white;
        padding: 12px 14px;
        border-radius: 50px;
        box-shadow: 0 4px 14px rgba(2,6,23,0.2);
        text-decoration: none;
        font-weight: 600;
    }
    .chat-popup-frame {
        position: fixed;
        right: 20px;
        bottom: 80px;
        width: 420px;
        max-width: calc(100% - 40px);
        height: 520px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(2,6,23,0.12);
        padding: 12px 16px;
        z-index: 10000;
        overflow: auto;
    }
    .chat-close-link { float: right; font-size: 13px; }
    </style>
    """
    st.markdown(float_css, unsafe_allow_html=True)

    # Tombol floating yang menambahkan query param ?chat=1
    params_no = st.experimental_get_query_params()
    # build url with chat=1
    base_url = st.experimental_get_query_params()

    # We cannot directly build URL easily; we'll use link that appends ?chat=1
    current_page = st.experimental_get_query_params()
    chat_open_url = "?chat=1"
    chat_close_url = "?"

    st.markdown(f"<a class=\"floating-chat-button\" href=\"{chat_open_url}\">💬 Chat</a>", unsafe_allow_html=True)

    if chat_on:
        # Render popup container and call chat.run_chat() inside
        st.markdown(f"<div class=\"chat-popup-frame\"> <a class=\"chat-close-link\" href=\"{chat_close_url}\">Tutup ✖</a></div>", unsafe_allow_html=True)
        # Use an empty container placed at bottom-right using CSS trick: we will render chat UI into it by absolute positioning
        # But Streamlit renders top-to-bottom; instead render the chat UI normally but it will visually overlay due to fixed-position CSS above
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        chat.run_chat()


def main_interface():
    # Identitas Default
    if 'user' not in st.session_state:
        st.session_state['user'] = "Admin_System"
    if 'role' not in st.session_state:
        st.session_state['role'] = "Admin"

    # Header
    c1, c2 = st.columns([10, 2])
    c1.markdown(f"👤 **Mode:** Direct Access | 🏷️ **Role:** {st.session_state['role']}")
    if c2.button("🔄 Refresh App", use_container_width=True):
        st.rerun()
    
    st.divider()
    
    # Load Data Utama
    db_p, stats, total = sc.fetch_all_data()

    # Navigasi Tab (menambahkan "📊 SIPESAT" dan tetap menyimpan Users/Admin Log)
    tabs = st.tabs([
        "🔍 Single",
        "🚀 Bulk",
        "📊 KYC Dashboard",
        "📝 Log Kegiatan",
        "📊 SIPESAT",
        "👥 Users",
        "🕒 Admin Log"
    ])

    # Jalankan fungsi sesuai tab masing-masing
    with tabs[0]:
        sc.run_pencarian(st.session_state.get('user', "Admin_System"), db_p, True)
    with tabs[1]:
        bat.run_bulk_screening()
    with tabs[2]:
        kyc.run_kyc_dashboard()
    with tabs[3]:
        kt.run_kegiatan_tracker()
    
    # JALANKAN TAB BARU SIPESAT DI SINI
    with tabs[4]:
        ss.run_sipesat()

    with tabs[5]:
        ut.run_user_management()
    with tabs[6]:
        lt.run_log_admin(stats, total)

    # Render floating chat button/popup if requested
    render_chat_popup_if_requested()

if __name__ == "__main__":
    main_interface()
