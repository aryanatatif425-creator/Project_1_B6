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


