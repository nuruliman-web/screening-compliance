import streamlit as st
import pandas as pd
from thefuzz import fuzz
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
    # --- UI FILTER PENCARIAN ---
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    metode = c1.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    query = c2.text_input("Cari Data:", placeholder="Masukkan nama atau nomor...")
    
    # INI ADALAH SLIDE FUZZY LOGIC YANG DIMAKSUD
    threshold = c3.slider("Ambang Batas Akurasi (Similarity %):", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    if query:
        q_strip = query.replace(" ", "").replace(".", "").replace("-", "")
        
        # Validasi Input NIK
        if metode == "NIK" and len(q_strip) < 16:
            st.error(f"❌ NIK minimal 16 digit! (Input Anda: {len(q_strip)} digit)")
        else:
            log_activity(user_email, f"Cari {metode}: {query} (Acc: {threshold}%)")
            q_clean = " ".join(query.split()).lower()
            found = False
            res_dict = {} 

            for name, df in db.items():
                # --- LOGIKA FUZZY UNTUK MENGHASILKAN PERSENTASE ---
                def fuzzy_identify(row):
                    best_score = 0
                    match_details = []
                    # Tentukan kolom mana yang akan dicek
                    target_cols = df.columns if metode != "Nama" else [c for c in df.columns if 'nama' in c.lower()]
                    
                    for col in target_cols:
                        val = str(row[col]).lower()
                        # Hitung skor kemiripan fuzzy
                        score = fuzz.token_sort_ratio(q_clean, val)
                        if score >= threshold:
                            match_details.append(f"{col} ({score}%)")
                            if score > best_score: best_score = score
                    
                    if best_score > 0:
                        return pd.Series([best_score, "MATCH: " + ", ".join(match_details)])
                    else:
                        return pd.Series([0, None])

                df_c = df.copy()
                # Jalankan Fuzzy Logic
                df_c[['_score', 'HASIL IDENTIFIKASI']] = df_c.apply(fuzzy_identify, axis=1)
                
                # Filter data yang di atas threshold
                matches = df_c[df_c['_score'] >= threshold].copy()
                
                if not matches.empty:
                    found = True
                    # Sorting berdasarkan skor tertinggi
                    matches = matches.sort_values('_score', ascending=False).drop(columns=['_score'])
                    
                    # Pindahkan HASIL IDENTIFIKASI (yang ada skor % nya) ke paling kiri
                    cols = matches.columns.tolist()
                    cols.insert(0, cols.pop(cols.index('HASIL IDENTIFIKASI')))
                    matches = matches[cols]
                    
                    res_dict[name] = matches 
                    
                    with st.expander(f"🚩 Ditemukan di Database: {name}", expanded=True):
                        st.dataframe(matches, hide_index=True, use_container_width=True)

            # --- FITUR DOWNLOAD MULTI-SHEET ---
            if found and is_admin:
                st.divider()
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, data_frame in res_dict.items():
                        data_frame.to_excel(writer, index=False, sheet_name=sheet_name)
                
                st.download_button(
                    label=f"📥 Download Temuan '{query}' (Excel Multi-Sheet)",
                    data=output.getvalue(),
                    file_name=f"Screening_Fuzzy_{query}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            elif not found:
                st.warning("Data tidak ditemukan dengan akurasi tersebut. Coba turunkan slider akurasi.")
