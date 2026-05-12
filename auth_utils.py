import pandas as pd
import hashlib
import os

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
