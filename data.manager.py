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


# =========================
# TEST FUNCTION (OPSIONAL)
# =========================
if __name__ == "__main__":
    # Test baca lokal
    local_data = read_local_data()
    print("Data lokal:", local_data)

    # Test tulis lokal
    write_local_data([
        {"id": 1, "nama": "Promo Baru", "aktif": True}
    ])

    # Test fetch cloud
    cloud_data = fetch_cloud_data()
    print("Data cloud:", cloud_data)

    # Test push cloud
    push_promo_to_cloud(cloud_data)