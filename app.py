import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io
import time
import uuid
import hashlib
from datetime import datetime, timedelta

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Screening System Multi-Database", layout="wide", initial_sidebar_state="collapsed")

# 2. DAFTAR LINK DATABASE
LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

# 3. CSS CUSTOM (SIDEBAR HIDE & LAYOUT PRESISI)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    footer { visibility: hidden; }
    
    /* Info User & Header */
    .user-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
    }
    .header-title { 
        color: #1f1f1f; 
        font-size: 28px; 
        font-weight: 800; 
        text-align: center;
        margin-top: 5px;
    }
    
    /* Kontainer Pencarian */
    .search-box {
        background-color: #f0f2f6; 
        padding: 20px; 
        border-radius: 12px;
        border-left: 6px solid #0068c9;
        margin-bottom: 20px;
    }
    
    /* Kartu Statistik */
    .stat-card {
        padding: 15px; 
        border-radius: 10px; 
        background-color: #ffffff; 
        border: 1px solid #e6e9ef; 
        text-align: center;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }

    /* Styling Button agar Presisi */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI LOGGING & SECURITY
def log_activity(email, action):
    log_file = "log_aktivitas.csv"
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    try:
        if not os.path.isfile(log_file): new_data.to_csv(log_file, index=False)
        else: new_data.to_csv(log_file, mode='a', header=False, index=False)
    except: pass

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

USER_DB_FILE = "users_db.csv"
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "x@gmail.com", "xx@gmail.com"]

def load_user_db():
    if os.path.exists(USER_DB_FILE): return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["Email", "PasswordHash"])

# 5. SESSION STATE
if "auth" not in st.session_state: st.session_state.auth = False
if "form_key" not in st.session_state: st.session_state.form_key = str(uuid.uuid4())
if "show_pw_form" not in st.session_state: st.session_state.show_pw_form = False

# 6. LOGIN SYSTEM
if not st.session_state.auth:
    st.title("🔐 Login Screening System")
    df_users = load_user_db()
    u_email = st.text_input("Email:", key=f"m_{st.session_state.form_key}").lower().strip()
    
    if u_email:
        if u_email not in ALLOWED_EMAILS:
            st.error("Email tidak terdaftar di sistem!")
        else:
            user_row = df_users[df_users['Email'] == u_email]
            if user_row.empty:
                st.info(f"Halo {u_email}, silakan buat password untuk akun Anda.")
                p1 = st.text_input("Password Baru:", type="password", key="p1")
                p2 = st.text_input("Konfirmasi Password:", type="password", key="p2")
                if st.button("Daftarkan Akun"):
                    if p1 == p2 and len(p1) >= 4:
                        new_u = pd.DataFrame([[u_email, hash_pass(p1)]], columns=["Email", "PasswordHash"])
                        pd.concat([df_users, new_u]).to_csv(USER_DB_FILE, index=False)
                        st.success("Berhasil! Silakan masukkan email kembali."); time.sleep(1); st.rerun()
                    else: st.error("Password tidak cocok atau terlalu pendek!")
            else:
                u_pass = st.text_input("Password:", type="password", key=f"p_{st.session_state.form_key}")
                if st.button("Masuk"):
                    if hash_pass(u_pass
