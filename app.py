# --- DI DALAM TAB SCREENING ---
with tabs[0]:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 2])
    with c1: 
        metode = st.radio("Metode:", ["Nama", "NIK", "Paspor"], horizontal=True)
    with c2: 
        query = st.text_input("Cari Data:", placeholder=f"Masukkan {metode}...", key="pencarian_utama")
    with c3: 
        threshold = st.slider("🎯 Akurasi Pencarian (%)", 50, 100, 85)
    st.markdown('</div>', unsafe_allow_html=True)

    # Validasi NIK
    valid_to_search = True
    if query and metode == "NIK" and len(query) != 16:
        st.warning(f"⚠️ NIK harus berjumlah 16 digit!")
        valid_to_search = False

    # --- BAGIAN LOGIKA LOGGING GLOBAL (DI SINI PERBAIKANNYA) ---
    if query and valid_to_search:
        # Kita buat ID unik per pencarian agar tidak mencatat log yang sama berulang kali saat geser slider
        search_id = f"{st.session_state.email_user}_{metode}_{query}"
        if "last_search_id" not in st.session_state or st.session_state.last_search_id != search_id:
            log_activity(st.session_state.email_user, f"Mencari {metode}: {query}")
            st.session_state.last_search_id = search_id
        
        # Lanjut proses cari data...
        q_clean = " ".join(query.split()).lower()
        found = False
        results_to_export = []
        
        for sn, df_data in db.items():
            def find_match(row):
                matches_info, max_score = [], 0
                check_cols = df_data.columns if metode in ["NIK", "Paspor"] else [c for c in df_data.columns if 'nama' in c.lower()]
                for c in check_cols:
                    val = " ".join(str(row[c]).split()).lower()
                    s = fuzz.token_sort_ratio(q_clean, val)
                    if s >= threshold:
                        matches_info.append(f"{c} ({s}%)")
                        if s > max_score: max_score = s
                return pd.Series([max_score, "Match: " + ", ".join(matches_info)]) if max_score > 0 else pd.Series([0, "-"])

            df_temp = df_data.copy()
            df_temp[['_score', 'ALASAN MATCH']] = df_temp.apply(find_match, axis=1)
            match = df_temp[df_temp['_score'] > 0].copy()
            
            if not match.empty:
                found = True
                display_df = match.sort_values('_score', ascending=False).drop(columns=['_score'])
                results_to_export.append(display_df)
                with st.expander(f"🚩 Database: {sn}", expanded=True):
                    st.dataframe(display_df, hide_index=True, use_container_width=True)

        # Download button tetep punya Super Admin aja
        if found and is_super_admin:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf) as w: pd.concat(results_to_export).to_excel(w, index=False)
            st.download_button("📥 Download Hasil", buf.getvalue(), "Hasil.xlsx", use_container_width=True)
        
        if not found:
            st.error("Data tidak ditemukan.")
