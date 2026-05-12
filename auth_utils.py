import os
import pandas as pd
import hashlib

USER_DB_FILE = "users_db.csv"

def hash_pass(password):
    """Mengubah password teks biasa menjadi kode rahasia (hash)"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_user_db():
    """Memuat database user dari CSV lokal"""
    if os.path.exists(USER_DB_FILE):
        return pd.read_csv(USER_DB_FILE)
    # Jika file tidak ada, buat admin default
    df = pd.DataFrame([{"Email": "imanmuhamad9@gmail.com", "Password": hash_pass("admin123"), "Role": "Admin", "Status": "Active"}])
    df.to_csv(USER_DB_FILE, index=False)
    return df

def log_activity(user, activity):
    """Mencatat aktivitas ke log_aktivitas.csv"""
    log_file = "log_aktivitas.csv"
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([[now, user, activity]], columns=["Waktu", "User", "Aktivitas"])
    if os.path.exists(log_file):
        df_log = pd.read_csv(log_file)
        pd.concat([df_log, new_log], ignore_index=True).to_csv(log_file, index=False)
    else:
        new_log.to_csv(log_file, index=False)
