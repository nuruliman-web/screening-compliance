import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Screening System", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Sidebar otomatis tertutup/hilang
)

# 2. CSS SAKTI: HAPUS HEADER & MENU TOTAL
st.markdown("""
    <style>
    /* Hilangkan Header atas (termasuk tombol sidebar dan menu 3 titik) */
    header[data-testid="stHeader"] {
        visibility: hidden;
        height: 0%;
    }
    
    /* Hilangkan Footer */
    footer {visibility: hidden;}

    /* Styling Teks User agar Hitam & Tidak Bisa Diklik */
    .user-info {
        color: black !important;
        font-weight: bold;
        pointer-events: none;
        cursor: default;
    }
    
    /* Atur jarak atas halaman karena header sudah hilang */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOGGING
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    if not os.path.isfile(log_file):
        new_data.to_csv(log_file, index=False)
    else:
        new_data.to_csv(log_file, mode='a', header=False, index=False)

# 4. TIMEOUT (10 Menit)
TIMEOUT_SECONDS = 600 
if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

if st.session_state.get("auth"):
    if (time.time() - st.session_state.last_activity) > TIMEOUT_SECONDS:
        log_activity(st.session_state.email_user, "Auto-Logout")
        st.session_state.auth = False
        st.rerun()

st.session_state.last_activity = time.time()

# 5. LOGIN SYSTEM
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com", "xxx@gmail.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    user_email = st.text_input("Masukkan Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            log_activity(user_email, "Login")
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# Role & Permissions
is_admin = st.session_state.email_user == "imanmuhamad9@gmail.com"
can_download = st.session_state.email_user != "xxx@gmail.com"

# 6. TAMPILAN ATAS (PENGGANTI SIDEBAR)
col_u, col_a, col_l = st.columns([2, 2, 1])
with col_u:
    st.markdown(f'<p class="user-info">👤 User: {st.session_state.email_user}</p>', unsafe_allow_html=True)

with col_a:
    # Slider Ak
