import hashlib
import os
import pandas as pd
from datetime import datetime, timedelta

USER_DB_FILE = "users_db.csv"
WHITELIST_FILE = "whitelist.csv"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def log_activity(email, action):
    now = (datetime.now() + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, email, action]], columns=["Waktu", "User", "Aktivitas"])
    new_data.to_csv("log_aktivitas.csv", mode='a', header=not os.path.exists("log_aktivitas.csv"), index=False)

def load_user_db():
    return pd.read_csv(USER_DB_FILE) if os.path.exists(USER_DB_FILE) else pd.DataFrame(columns=["Email", "PasswordHash"])

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        return pd.read_csv(WHITELIST_FILE)['Email'].tolist()
    return ["imanmuhamad9@gmail.com"]

def save_whitelist(email_list):
    pd.DataFrame(email_list, columns=['Email']).to_csv(WHITELIST_FILE, index=False)
# ... (kode sebelumnya tetap sama)

def update_password(email, new_password):
    df_u = load_user_db()
    if email in df_u['Email'].values:
        idx = df_u[df_u['Email'] == email].index
        df_u.loc[idx, 'PasswordHash'] = hash_pass(new_password)
        df_u.to_csv(USER_DB_FILE, index=False)
        return True
    return False
