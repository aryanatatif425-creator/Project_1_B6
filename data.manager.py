import json
import os

# =========================
# KONFIGURASI FILE
# =========================
FILE_PATH = "data_promo.json"


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
        json.dump(data, file, indent=4)


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


