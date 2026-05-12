import os
import pandas as pd
import hashlib
from datetime import datetime

USER_DB_FILE = "users_db.csv"

def hash_pass(password):
    """Hashing SHA256 agar password aman"""
    return hashlib.sha256(str.encode(str(password))).hexdigest()

def load_user_db():
    """Memuat database lokal users_db.csv"""
    if os.path.exists(USER_DB_FILE):
        try:
            df = pd.read_csv(USER_DB_FILE)
            df.columns = df.columns.str.strip()
            return df
        except:
            return pd.DataFrame(columns=["Email", "Password", "Role", "Status"])
    else:
        df = pd.DataFrame(columns=["Email", "Password", "Role", "Status"])
        df.to_csv(USER_DB_FILE, index=False)
        return df

def log_activity(user, activity, detail=""):
    """Mencatat aktivitas agar modul lain (screening_tab) tidak error"""
    log_file = "admin_activity_log.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{"Timestamp": now, "User": user, "Aksi": activity, "Keterangan": detail}])
    
    try:
        if os.path.exists(log_file):
            df_l = pd.read_csv(log_file)
            pd.concat([df_l, new_log], ignore_index=True).to_csv(log_file, index=False)
        else:
            new_log.to_csv(log_file, index=False)
    except:
        pass
