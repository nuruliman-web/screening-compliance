import os
import pandas as pd
import hashlib

USER_DB_FILE = "users_db.csv"

def hash_pass(password):
    """Hashing SHA256 agar password aman"""
    return hashlib.sha256(str.encode(str(password))).hexdigest()

def load_user_db():
    """Memuat database lokal dan memastikan akun abang terdaftar"""
    admin_email = "imanmuhamad9@gmail.com"
    admin_pass_raw = "1111" 
    
    if os.path.exists(USER_DB_FILE):
        df = pd.read_csv(USER_DB_FILE)
    else:
        df = pd.DataFrame(columns=["Email", "Password", "Role", "Status"])

    # Normalisasi Data
    df['Email'] = df['Email'].astype(str).str.lower().str.strip()

    # Pastikan akun abang ada di CSV
    if admin_email not in df['Email'].values:
        new_admin = pd.DataFrame([{
            "Email": admin_email,
            "Password": hash_pass(admin_pass_raw),
            "Role": "Admin",
            "Status": "Active"
        }])
        df = pd.concat([df, new_admin], ignore_index=True)
        df.to_csv(USER_DB_FILE, index=False)
    
    return df

def log_activity(user, activity):
    log_file = "log_aktivitas.csv"
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([[now, user, activity]], columns=["Waktu", "User", "Aktivitas"])
    if os.path.exists(log_file):
        df_log = pd.read_csv(log_file)
        pd.concat([df_log, new_log], ignore_index=True).to_csv(log_file, index=False)
    else:
        new_log.to_csv(log_file, index=False)
