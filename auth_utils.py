import os
import pandas as pd
import hashlib

USER_DB_FILE = "users_db.csv"
WHITELIST_FILE = "whitelist.csv"

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        return pd.read_csv(USER_DB_FILE)
    return pd.DataFrame(columns=["Email", "PasswordHash"])

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        # Tambah kolom Status: 'Active' atau 'Blocked'
        df = pd.DataFrame([{"Email": "imanmuhamad9@gmail.com", "Role": "Admin", "Status": "Active"}])
        df.to_csv(WHITELIST_FILE, index=False)
        return df
    
    try:
        df = pd.read_csv(WHITELIST_FILE)
        # Pastikan kolom Status ada, kalau gak ada buat default 'Active'
        if "Status" not in df.columns:
            df["Status"] = "Active"
            df.to_csv(WHITELIST_FILE, index=False)
        return df
    except:
        df = pd.DataFrame([{"Email": "imanmuhamad9@gmail.com", "Role": "Admin", "Status": "Active"}])
        df.to_csv(WHITELIST_FILE, index=False)
        return df

def save_whitelist(df):
    df.to_csv(WHITELIST_FILE, index=False)

def log_activity(user, activity):
    log_file = "log_aktivitas.csv"
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([[now, user, activity]], columns=["Waktu", "User", "Aktivitas"])
    if os.path.exists(log_file):
        df_log = pd.read_csv(log_file)
        pd.concat([df_log, new_log], ignore_index=True).to_csv(log_file, index=False)
    else:
        new_log.to_csv(log_file, index=False)

def update_password(email, new_password):
    db = load_user_db()
    if email in db['Email'].values:
        db.loc[db['Email'] == email, 'PasswordHash'] = hash_pass(new_password)
        db.to_csv(USER_DB_FILE, index=False)
        return True
    return False
