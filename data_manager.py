import json
import os
from datetime import datetime
import requests
import logging
import  shutil

# =========================
# KONFIGURASI FILE
# =========================
FILE_PATH = "data_promo.json"

logging.basicConfig(
    filename="activity.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 🔗 API CONFIG
API_URL = "https://script.google.com/macros/s/AKfycbyYXsTk2KoKliez2uFMdOfMC5Lc3jbyWYb2lt_1M5AX9jS1NYcoZvHb0JxAngD2jIkTkA/exec?sheet=Promo"
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

    # backup file lama
    if os.path.exists(FILE_PATH):
        shutil.copy(FILE_PATH, "data_promo_backup.json")

    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=2)

    logging.info("Data lokal berhasil ditulis")    
# =========================
# GENERATE ID
# =========================
def generate_id(retailer_brand, branch_name, item_name):
    return f"{retailer_brand.lower()}|{branch_name.lower().replace(' ', '_')}|{item_name.lower().replace(' ', '_')}"


# =========================
# ADD PROMO
# =========================
def add_promo(
    item_name,
    retailer_brand,
    branch_name,
    category,
    area_tags,
    price_int,

    harga_promo,
    diskon_persen,
    perubahan_harga,
    jenis_harga,
    periode_promo
):
    data = read_local_data()

    new_id = generate_id(retailer_brand, branch_name, item_name)

    # cek duplikat
    for promo in data:
        if promo["id"] == new_id:
            print("❌ Promo sudah ada!")
            return

    new_promo = {
        "id": new_id,
        "timestamp_scrape": datetime.now().isoformat(),
        "nama_produk": item_name,
        "brand_toko": retailer_brand,
        "nama_cabang": branch_name,
        "kategori": category,
        "area_tags": area_tags,
        "harga_normal": price_int,
        "harga_promo": harga_promo,
        "diskon_persen": diskon_persen,
        "perubahan_harga": perubahan_harga,
        "jenis_harga": jenis_harga,
        "periode_promo": periode_promo,
        "display_harga": f"Rp {harga_promo:,}".replace(",", "."),
        "image_url": "https://placehold.co/200x200?text=Promo",
        "logo_url": "",
        "search_vector": f"{item_name} {retailer_brand} {branch_name}".lower()
    }

    data.append(new_promo)
    write_local_data(data)
    logging.info(f"Promo ditambahkan: {new_id}")

    print("✅ Promo berhasil ditambahkan!")
# =========================
# FETCH FROM GOOGLE SHEET
# =========================
def fetch_cloud_data():
    try:
        response = requests.get(API_URL)

        response.raise_for_status()

        data = response.json()

        logging.info(f"Fetch cloud sukses ({len(data)} data)")
        return data

    except Exception as e:
        logging.error(f"Fetch cloud gagal: {e}")
        return []
# =========================
# PUSH TO GOOGLE SHEET
# =========================
def push_promo_to_cloud(data):
    try:
        response = requests.post(API_URL, json={
    "data": data
    })

        print(response.text)

        response.raise_for_status()

        logging.info(f"Push cloud sukses ({len(data)} data)")
        return True

    except Exception as e:
        logging.error(f"Push cloud gagal: {e}")
        print(e)
        return False
# =========================
# SYNC LOCAL → CLOUD
# =========================
def sync_to_cloud():
    data = read_local_data()
    return push_promo_to_cloud(data)


# =========================
# SYNC CLOUD → LOCAL
# =========================
def sync_from_cloud():
    data = fetch_cloud_data()

    if data:
        write_local_data(data)
        logging.info("Sync from cloud berhasil")
    else:
        logging.warning("Cloud kosong, sync dibatalkan")