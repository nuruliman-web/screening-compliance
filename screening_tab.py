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
    query = c2.text_input("Input Data:", placeholder="Ketik nama atau nomor...", key="q_in")
    threshold = c3.slider("Ambang Batas Akurasi (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
        
        # Validasi Input
        if metode == "Nama" and any(char.isdigit() for char in query):
            st.error("❌ Pencarian Nama tidak boleh mengandung angka!")
        elif metode == "NIK" and len(q_strip) < 16:
            st.error(f"❌ NIK harus minimal 16 digit! (Input: {len(q_strip)})")
        else:
            log_activity(user_email, f"Cari {metode}: {query}")
            q_clean = " ".join(query.split()).lower()
            found, res_list = False, []

            for name, df in db.items():
                # Logic Identifikasi Kolom & Skor
                def identify_match(row):
                    best_score = 0
                    matched_info = []
                    # Tentukan kolom target
                    target_cols = df.columns if metode != "Nama" else [c for c in df.columns if 'nama' in c.lower()]
                    
                    for col in target_cols:
                        val = str(row[col]).lower()
                        score = fuzz.token_sort_ratio(q_clean, val)
                        if score >= threshold:
                            matched_info.append(f"{col} ({score}%)")
                            if score > best_score: best_score = score
                    
                    status = "MATCH: " + ", ".join(matched_info) if best_score > 0 else "-"
                    return pd.Series([best_score, status])

                df_c = df.copy()
                # Jalankan fungsi dan simpan ke kolom sementara
                df_c[['_score', 'HASIL IDENTIFIKASI']] = df_c.apply(identify_match, axis=1)
                
                # Filter hanya yang match
                matches = df_c[df_c['_score'] > 0].copy()
                
                if not matches.empty:
                    found = True
                    # Hapus skor internal dan pindahkan HASIL IDENTIFIKASI ke paling kiri
                    matches = matches.sort_values('_score', ascending=False).drop(columns=['_score'])
                    cols = matches.columns.tolist()
                    cols.insert(0, cols.pop(cols.index('HASIL IDENTIFIKASI')))
                    matches = matches[cols]
                    
                    res_list.append(matches)
                    with st.expander(f"🚩 Ditemukan di Database: {name}", expanded=True):
                        st.dataframe(matches, hide_index=True, use_container_width=True)
            
            if found and is_admin:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf) as w: pd.concat(res_list).to_excel(w, index=False)
                st.download_button("📥 Download Semua Temuan (Excel)", buf.getvalue(), "Hasil_Screening.xlsx", use_container_width=True)
            elif not found:
                st.warning("Data tidak ditemukan di database manapun.")
