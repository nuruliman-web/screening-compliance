import pandas as pd
import hashlib
import os
from datetime import datetime

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def load_user_db():
    file_path = 'users.csv'
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            return pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])
    else:
        # Membuat file default jika belum ada
        df_default = pd.DataFrame(columns=['Email', 'Password', 'Role', 'Status'])
        return df_default

# FUNGSI INI HARUS ADA UNTUK MEMPERBAIKI ERROR
def log_activity(user, activity, detail):
    """Mencatat aktivitas user ke dalam log (opsional)"""
    # Jika Anda punya file log_kegiatan.csv, kode ini akan menyimpannya
    log_file = 'log_kegiatan.csv'
    new_log = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'User': user,
        'Activity': activity,
        'Detail': detail
    }
    
    try:
        if os.path.exists(log_file):
            df_log = pd.read_csv(log_file)
            df_log = pd.concat([df_log, pd.DataFrame([new_log])], ignore_index=True)
        else:
            df_log = pd.DataFrame([new_log])
        
        df_log.to_csv(log_file, index=False)
    except:
        pass # Mengabaikan error jika gagal menulis log agar aplikasi tetap jalan
