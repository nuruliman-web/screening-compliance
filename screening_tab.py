import streamlit as st
import pandas as pd
import io
from auth_utils import log_activity

# Konfigurasi Link Database
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
    c1, c2 = st.columns([1, 3])
    metode = c1.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    query = c2.text_input("Cari Data:", placeholder="Masukkan kata kunci...")
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        log_activity(user_email, f"Cari {metode}: {query}")
        found = False
        res_dict = {} # Menggunakan dictionary untuk memisahkan per Database (Sheet)

        for name, df in db.items():
            # Fungsi cek data (pencarian teks sederhana)
            def check(row):
                target_cols = df.columns if metode != "Nama" else [c for c in df.columns if 'nama' in c.lower()]
                for c in target_cols:
                    if str(query).lower() in str(row[c]).lower():
                        return f"MATCH di {c}"
                return None

            df_c = df.copy()
            df_c['HASIL IDENTIFIKASI'] = df_c.apply(check, axis=1)
            matches = df_c[df_c['HASIL IDENTIFIKASI'].notna()].copy()
            
            if not matches.empty:
                found = True
                # Pindahkan kolom HASIL IDENTIFIKASI ke paling kiri
                cols = matches.columns.tolist()
                cols.insert(0, cols.pop(cols.index('HASIL IDENTIFIKASI')))
                matches = matches[cols]
                
                res_dict[name] = matches # Simpan hasil berdasarkan nama database-nya
                
                with st.expander(f"🚩 Ditemukan di Database: {name}", expanded=True):
                    st.dataframe(matches, hide_index=True, use_container_width=True)

        # FITUR DOWNLOAD MULTI-SHEET
        if found and is_admin:
            st.divider()
            output = io.BytesIO()
            # Gunakan ExcelWriter untuk membuat banyak sheet
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, data_frame in res_dict.items():
                    data_frame.to_excel(writer, index=False, sheet_name=sheet_name)
            
            st.download_button(
                label=f"📥 Download Hasil Screening '{query}' (Excel Multi-Sheet)",
                data=output.getvalue(),
                file_name=f"Screening_{query}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        elif not found:
            st.warning("Data tidak ditemukan di database manapun.")
