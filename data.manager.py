import json
import os
from datetime import datetime
import requests

# =========================
# KONFIGURASI FILE
# =========================
FILE_PATH = "data_promo.json"

# 🔗 API CONFIG
API_URL = "https://script.google.com/macros/s/AKfycbwT2neKsWqdP09WgyOBotVXtw5K45qWa3fFj7zQ57EwsQB4HTG8htXKhPbI1ROwKiDB/exec"
API_KEY = "4dfa489bff8831a80b449061b8247204"

# =========================
# READ LOCAL JSON
# =========================
def read_local_data():
    """Membaca data dari file data_promo.json"""
    if not os.path.exists(FILE_PATH):
        return []

    try:
        with open(FILE_PATH, "r") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        return []

# =========================
# WRITE LOCAL JSON
# =========================
def write_local_data(data):
    """Menulis data ke file data_promo.json"""
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=2)

# =========================
# GENERATE ID
# =========================
def generate_id(retailer_brand, branch_name, item_name):
    return f"{retailer_brand.lower()}|{branch_name.lower().replace(' ', '_')}|{item_name.lower().replace(' ', '_')}"


# =========================
# FETCH DATA FROM CLOUD (DUMMY)
# =========================
def fetch_cloud_data():
    """
    Ambil data dari Google Sheet (sementara dummy)
    Nanti bisa diganti pakai API / requests
    """
    print("Mengambil data dari cloud...")

    # Dummy data
    dummy_data = [
        {"id": 1, "nama": "Promo Diskon 10%", "aktif": True},
        {"id": 2, "nama": "Promo Gratis Ongkir", "aktif": False}
    ]

    return dummy_data


# =========================
# PUSH DATA TO CLOUD (DUMMY)
# =========================
def push_promo_to_cloud(data):
    """
    Kirim data ke Google Sheet (sementara dummy)
    """
    print("Mengirim data ke cloud...")
    print("Data yang dikirim:")
    print(data)

    # Simulasi sukses
    return True
