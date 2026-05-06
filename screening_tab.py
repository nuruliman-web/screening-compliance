import streamlit as st
import pandas as pd
from thefuzz import fuzz
import io
from auth_utils import log_activity

LINK_SHEETS = {
    "JUDOL": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1397546375&single=true&output=csv",
    "DTTOT": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1229360429&single=true&output=csv",
    "DPPSPM": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=1059062603&single=true&output=csv",
    "SIPENDAR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTwj6BDBGvo9yWRYMkPGNxPi9KtLrbU8qT8zA5VdiogRlp1JoxBDADyh3xF2gWROuPS0pBujoYiKUn-/pub?gid=288835560&single=true&output=csv"
}

@st.cache_data(ttl=600)
def fetch_all_data():
    all_d, stats, total = {}, {}, 0
    for name, url in LINK_SHEETS.items():
        try:
            df = pd.read_csv(url)
            all_d[name], stats[name], total = df, len(df), total + len(df)
        except: continue
    return all_d, stats, total

def run_pencarian(user_email, db, is_admin):
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    metode = c1.radio("Metode Pencarian:", ["Nama", "NIK", "Paspor"], horizontal=True)
    query = c2.text_input("Input Data:", placeholder="Ketik nama/nomor...", key="q_in")
    threshold = c3.slider("Akurasi (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
        if metode == "Nama" and any(char.isdigit() for char in query):
            st.error("❌ Nama tidak boleh angka!")
        elif metode == "NIK" and len(q_strip) < 16:
            st.error(f"❌ NIK minimal 16 digit!")
        else:
            log_activity(user_email, f"Cari {metode}: {query}")
            q_clean = " ".join(query.split()).lower()
            found, res_list = False, []
            for name, df in db.items():
                def check(row):
                    cols = df.columns if metode != "Nama" else [c for c in df.columns if 'nama' in c.lower()]
                    s = max([fuzz.token_sort_ratio(q_clean, str(row[c]).lower()) for c in cols])
                    return s if s >= threshold else 0
                df_c = df.copy()
                df_c['_s'] = df_c.apply(check, axis=1)
                matches = df_c[df_c['_s'] > 0].drop(columns=['_s'])
                if not matches.empty:
                    found = True; res_list.append(matches)
                    with st.expander(f"🚩 Database: {name}", expanded=True): st.dataframe(matches, hide_index=True)
            if found and is_admin:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: pd.concat(res_list).to_excel(w, index=False)
                st.download_button("📥 Download Hasil", buf.getvalue(), "Hasil.xlsx")
