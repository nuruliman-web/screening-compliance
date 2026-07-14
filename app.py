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


def render_chat_popup_if_requested():
    # Robustly get query params across Streamlit versions
    params = {}
    try:
        if hasattr(st, "experimental_get_query_params"):
            params = st.experimental_get_query_params()
        elif hasattr(st, "experimental_get_url_params"):
            params = st.experimental_get_url_params()
        else:
            # fallback: try calling and catch AttributeError
            params = st.experimental_get_query_params()
    except Exception:
        params = {}

    def _get_param_value(d, k):
        v = d.get(k)
        if v is None:
            return None
        if isinstance(v, list):
            return v[0]
        return v

    chat_on = _get_param_value(params, "chat") == "1"

    float_css = """
    <style>
    .floating-chat-button {
        position: fixed;
        right: 18px;
        bottom: 18px;
        z-index: 9999;
        background: #0b5fff;
        color: white;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 28px;
        box-shadow: 0 6px 20px rgba(2,6,23,0.2);
        text-decoration: none;
        font-weight: 700;
        font-size: 20px;
    }
    .chat-popup-frame {
        position: fixed;
        right: 18px;
        bottom: 86px;
        width: 420px;
        max-width: calc(100% - 36px);
        height: 520px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(2,6,23,0.12);
        padding: 12px 16px;
        z-index: 10000;
        overflow: auto;
    }
    .chat-close-link { float: right; font-size: 13px; color: #444; text-decoration: none; }
    @media (max-width: 480px) {
        .chat-popup-frame { right: 10px; left: 10px; bottom: 72px; width: auto; height: 60vh; }
    }
    </style>
    """
    st.markdown(float_css, unsafe_allow_html=True)

    # Floating chat icon (always visible). Use a full URL if your app is served under a path.
    st.markdown('<a class="floating-chat-button" href="?chat=1" title="Chat dengan AI">💬</a>', unsafe_allow_html=True)

    if chat_on:
        # Render popup container and call chat.run_chat() inside
        st.markdown('<div class="chat-popup-frame"><a class="chat-close-link" href="?">Tutup ✖</a></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        try:
            chat.run_chat()
        except Exception as e:
            st.error(f"Gagal merender chat popup: {e}")


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
