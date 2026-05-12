import os
import pandas as pd
import hashlib

USER_DB_FILE = "users_db.csv"

def hash_pass(password):
    if not password: return ""
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        df = pd.read_csv(USER_DB_FILE)
        # Pastikan kolom standar tersedia agar tidak error saat dibaca app.py
        for col in ["Email", "Password", "Role", "Status"]:
            if col not in df.columns:
                df[col] = "Active" if col == "Status" else ("User" if col == "Role" else "")
        return df
    # Jika file tidak ada, buat admin default agar kamu bisa masuk pertama kali
    df_default = pd.DataFrame([{
        "Email": "imanmuhamad9@gmail.com", 
        "Password": "", # Kosong agar bisa registrasi awal
        "Role": "Admin", 
        "Status": "Active"
    }])
    df_default.to_csv(USER_DB_FILE, index=False)
    return df_default

def log_activity(user, activity):
    log_file = "log_aktivitas.csv"
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([[now, user, activity]], columns=["Waktu", "User", "Aktivitas"])
    if os.path.exists(log_file):
        df_log = pd.read_csv(log_file)
        pd.concat([df_log, new_log], ignore_index=True).to_csv(log_file, index=False)
    else:
        new_log.to_csv(log_file, index=False)
