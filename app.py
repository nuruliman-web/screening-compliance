import streamlit as st

# 1. IMPORT SEMUA TAB/MODUL YANG KAMU MILIKI
from screening_tab import render_screening_tab
from kyc_dashboard_tab import render_kyc_dashboard_tab
from bulk_admin_tab import render_bulk_admin_tab
from user_tab import render_user_tab
from log_tab import render_log_tab
from kegiatan_tracker import render_kegiatan_tracker  # Sesuaikan jika nama fungsinya berbeda

# IMPORT TAB BARU YANG TADI KITA BUAT
from sipesat_tab import render_sipesat_tab 

# (Opsional) Jika kamu menggunakan file auth_utils untuk login
# from auth_utils import check_password

def main():
    # Pengaturan dasar halaman web Streamlit
    st.set_page_config(
        page_title="Screening & Compliance System",
        page_icon="🛡️",
        layout="wide"
    )

    # --- BAGIAN OTENTIKASI / LOGIN (Jika ada) ---
    # Jika web kamu membutuhkan login, biasanya kodenya ditaruh di sini.
    # Contoh:
    # if not check_password():
    #     st.stop()

    # --- BAGIAN SIDEBAR & NAVIGASI MENU ---
    st.sidebar.title("🧭 Navigasi Menu")
    
    # Menambahkan "SIPESAT" ke dalam daftar pilihan menu di Sidebar
    menu_options = [
        "Dashboard KYC", 
        "Screening", 
        "SIPESAT",           # <-- Menu Baru Kamu
        "Bulk Admin", 
        "User Management", 
        "Activity Log",
        "Kegiatan Tracker"
    ]
    
    # Membuat komponen selectbox di sidebar untuk memilih menu
    pilihan_menu = st.sidebar.selectbox("Pilih Halaman:", menu_options)

    st.sidebar.markdown("---")
    st.sidebar.caption("Screening Compliance App v1.1")

    # --- BAGIAN LOGIKAL PERCABANGAN MENU (ROUTING) ---
    # Di sini aplikasi akan mendeteksi menu apa yang sedang diklik oleh user
    
    if pilihan_menu == "Dashboard KYC":
        render_kyc_dashboard_tab()
        
    elif pilihan_menu == "Screening":
        render_screening_tab()
        
    elif pilihan_menu == "SIPESAT":
        # Menjalankan fungsi dari file sipesat_tab.py yang kita buat sebelumnya
        render_sipesat_tab()
        
    elif pilihan_menu == "Bulk Admin":
        render_bulk_admin_tab()
        
    elif pilihan_menu == "User Management":
        render_user_tab()
        
    elif pilihan_menu == "Activity Log":
        render_log_tab()
        
    elif pilihan_menu == "Kegiatan Tracker":
        render_kegiatan_tracker()

if __name__ == "__main__":
    main()
