import streamlit as st
import pandas as pd
import os, io
from auth_utils import log_activity

def run_log_admin(stats, total):
    cols = st.columns(len(stats) + 1)
    for i, (name, val) in enumerate(stats.items()):
        cols[i].markdown(f'<div class="stat-card"><small>{name}</small><br><b>{val:,}</b></div>', unsafe_allow_html=True)
    cols[-1].markdown(f'<div style="background-color:#0068c9;color:white;" class="stat-card"><small>TOTAL</small><br><b>{total:,}</b></div>', unsafe_allow_html=True)
    
    st.write("")
    if os.path.exists("log_aktivitas.csv"):
        log_df = pd.read_csv("log_aktivitas.csv")
        c1, c2 = st.columns(2)
        if c2.button("🔥 Reset Log"):
            os.remove("log_aktivitas.csv"); st.rerun()
        st.dataframe(log_df.iloc[::-1], use_container_width=True, hide_index=True)
