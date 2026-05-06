import streamlit as st
import pandas as pd
from thefuzz import fuzz
import os
import io

# 1. SETUP HALAMAN
st.set_page_config(page_title="Screening System", layout="wide")

# 2. LOGIN SYSTEM
ALLOWED_EMAILS = ["imanmuhamad9@gmail.com", "admin@perusahaan.com"]

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    user_email = st.text_input("Email:").lower().strip()
    if st.button("Masuk"):
        if user_email in ALLOWED_EMAILS:
            st.session_state.auth = True
            st.session_state.email_user = user_email
            st.rerun()
        else:
            st.error("Email tidak terdaftar!")
    st.stop()

# 3. SIDEBAR (Dibuat sederhana agar tombol '>' tidak hilang)
with st.sidebar:
    st.title("⚙️ Panel")
    st.info(f"User: {st.session_state.email_user}")
    threshold = st.slider("Kemiripan (%)", 50, 100, 85)
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# 4. MAIN APP
st.title("🔍 Screening APU, PPT, dan PPPSPM")

@st.cache_data
def load_db(path):
    if os.path.exists(path):
        data = pd.read_excel(path, sheet_name=None)
        for s in data:
            for c in data[s].columns:
                if pd.api.types.is_datetime64_any_dtype(data[s][c]):
                    data[s][c] = data[s][c].dt.strftime('%Y-%m-%d')
        return data
    return None

db = load_db("database.xlsx")

if db:
    metode = st.radio("Metode:", ["Nama", "NIK / Paspor"], horizontal=True)
    query = st.text_input("Cari Data:")

    if query:
        q_clean = " ".join(query.split()).lower()
        found = False
        results = []
        
        for sheet_name in ['JUDOL', 'DTTOT', 'DPPSPM', 'SIPENDAR']:
            if sheet_name in db:
                df = db[sheet_name].copy()
                
                def score_row(row):
                    top_score = 0
                    # Jika Nama: scan kolom yang ada kata 'nama'. Jika NIK: scan semua.
                    cols = [c for c in df.columns if 'nama' in c.lower()] if metode == "Nama" else df.columns
                    for c in cols:
                        val = " ".join(str(row[c]).split()).lower()
                        if metode == "Nama":
                            s = fuzz.token_sort_ratio(q_clean, val)
                            top_score = max(top_score, s)
                        else:
                            if q_clean == val: top_score = 100
                    return top_score

                df.insert(0, 'SKOR', df.apply(score_row, axis=1))
                match = df[df['SKOR'] >= (threshold if metode == "Nama" else 100)].copy()
                
                if not match.empty:
                    found = True
                    results.append(match)
                    with st.expander(f"🚩 {sheet_name}"):
                        st.dataframe(match.sort_values('SKOR', ascending=False), hide_index=True)

        if found:
            final_df = pd.concat(results)
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as w: final_df.to_excel(w, index=False)
            st.download_button("📥 Download Excel", buf.getvalue(), "hasil.xlsx")
        elif query:
            st.warning("Tidak ditemukan.")
else:
    st.error("File database.xlsx tidak ada.")
