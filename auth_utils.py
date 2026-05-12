import os
import pandas as pd
import hashlib

USER_DB_FILE = "users_db.csv"

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        try:
            df = pd.read_csv(USER_DB_FILE)
            # Pastikan kolom standar ada
            for col in ["Email", "Password", "Role", "Status"]:
                if col not in df.columns:
                    df[col] = "Active" if col == "Status" else ("User" if col == "Role" else "")
            return df
        except:
            pass
            
    # Default Admin jika file hilang/rusak
    df_default = pd.DataFrame([{
        "Email": "imanmuhamad9@gmail.com", 
        "Password": "", 
        "Role": "Admin", 
        "Status": "Active"
    }])
    df_default.to_csv(USER_DB_FILE, index=False)
    return df_default

def log_activity(user, activity):
    log_file = "admin_activity_log.csv" # Samakan dengan log_tab.py
    now = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    new_log = pd.DataFrame([{"Timestamp": now, "User": user, "Aksi": activity, "Keterangan": "-"}])
    if os.path.exists(log_file):
        try:
            df_log = pd.read_csv(log_file)
            pd.concat([df_log, new_log], ignore_index=True).to_csv(log_file, index=False)
        except:
            new_log.to_csv(log_file, index=False)
    else:
        new_log.to_csv(log_file, index=False)
