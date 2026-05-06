import streamlit as st
import pandas as pd
import os
from auth_utils import load_whitelist, save_whitelist, load_user_db, USER_DB_FILE

def run_user_management():
    st.subheader("👥 Manajemen Akses User")
    whitelist = load_whitelist()
    user_db = load_user_db()

    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    new_m = c1.text_input("Tambah Email Baru:")
    if c2.button("➕ Tambah"):
        if new_m and "@" in new_m and new_m not in whitelist:
            whitelist.append(new_m.lower().strip())
            save_whitelist(whitelist); st.rerun()

    st.divider()
    for email in whitelist:
        registered = not user_db[user_db['Email'] == email].empty
        col_m, col_s, col_a = st.columns([2, 1, 2])
        col_m.write(email)
        col_s.write("✅ Verified" if registered else "⏳ Pending")
        
        b_res, b_del = col_a.columns(2)
        if registered and b_res.button("🔄 Reset", key=f"rs_{email}"):
            user_db[user_db['Email'] != email].to_csv(USER_DB_FILE, index=False); st.rerun()
        if email != "imanmuhamad9@gmail.com" and b_del.button("🗑️ Hapus", key=f"del_{email}"):
            whitelist.remove(email); save_whitelist(whitelist)
            user_db[user_db['Email'] != email].to_csv(USER_DB_FILE, index=False); st.rerun()
