import json
import os
from datetime import datetime
import requests

# =========================
# KONFIGURASI FILE
# =========================
FILE_PATH = "data_promo.json"

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
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=2)

# =========================
# GENERATE ID
# =========================
def generate_id(retailer_brand, branch_name, item_name):
    return f"{retailer_brand.lower()}|{branch_name.lower().replace(' ', '_')}|{item_name.lower().replace(' ', '_')}"


# =========================
# ADD PROMO
# =========================
def add_promo(item_name, retailer_brand, branch_name, category, area_tags, price_int):
    data = read_local_data()

    new_id = generate_id(retailer_brand, branch_name, item_name)

    for promo in data:
        if promo["id"] == new_id:
            print("❌ Promo sudah ada!")
            return

    new_promo = {
        "id": new_id,
        "timestamp": datetime.now().isoformat(),
        "item_name": item_name,
        "retailer_brand": retailer_brand,
        "branch_name": branch_name,
        "category": category,
        "area_tags": area_tags,
        "price_int": price_int,
        "price_display": f"Rp {price_int:,}".replace(",", "."),
        "image_url": "https://placehold.co/200x200?text=Promo",
        "logo_url": "",
        "search_vector": f"{item_name} {retailer_brand} {branch_name}".lower()
    }

    data.append(new_promo)
    write_local_data(data)

    print("✅ Promo berhasil ditambahkan!")



# =========================
# FETCH FROM GOOGLE SHEET
# =========================
def fetch_cloud_data():
    try:
        response = requests.get(API_URL, params={
            "sheet": "Promo",
            "api_key": API_KEY
        })

        response.raise_for_status()
        data = response.json()

        print(f"☁️ Fetch sukses: {len(data)} data")
        return data

    except Exception as e:
        print("❌ Gagal fetch:", e)
        return []

# =========================
# PUSH TO GOOGLE SHEET
# =========================
def push_promo_to_cloud(data):
    try:
        response = requests.post(API_URL, json={
            "api_key": API_KEY,
            "sheet": "Promo",
            "data": data
        })

        response.raise_for_status()

        print("☁️ Push sukses!")
        return True

    except Exception as e:
        print("❌ Gagal push:", e)
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

    if not data:
        print("❌ Cloud kosong, batal overwrite local")
        return

    write_local_data(data)
    print("✅ Local updated dari cloud")
