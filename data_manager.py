"""
data_manager.py — Pengelola Data Radar Promo v2.0
==================================================
Menangani baca/tulis JSON lokal, komunikasi dengan Google Sheets API,
upload foto ke ImgBB, dan logging aktivitas.
"""

import json
import os
import logging
import requests
from datetime import datetime

import copy

# ═══════════════ KONFIGURASI ═══════════════
ADDRESS_BOOK = {
    "Borma": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Logo_Borma_Toserba.png/200px-Logo_Borma_Toserba.png",
        "branches": [
            {"nama_cabang": "Borma Setiabudi", "area_tags": ["Gegerkalong"]},
            {"nama_cabang": "Borma Dakota", "area_tags": ["Sarijadi"]} 
        ]
    },
    "Griya": {
        "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/3/30/Logo_Yogya_Group.svg/200px-Logo_Yogya_Group.svg.png",
        "branches": [
            {"nama_cabang": "Griya Setrasari", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Griya Pasteur", "area_tags": ["Sarijadi"]}
        ]
    },
    "Alfamart": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Alfamart_logo.svg/200px-Alfamart_logo.svg.png",
        "branches": [
            {"nama_cabang": "Alfamart Warugajaya", "area_tags": ["Ciwaruga"]},
            {"nama_cabang": "Alfamart Ciwaruga", "area_tags": ["Ciwaruga"]},
            {"nama_cabang": "Alfamart Gegerkalong", "area_tags": ["Gegerkalong"]},
            {"nama_cabang": "Alfamart Sarimanah", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Alfamart Sariwangi", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Alfamart Terusan Sutami", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Alfamart Sarijadi Baru", "area_tags": ["Sarijadi"]}
        ]
    },
    "Indomaret": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Indomaret_logo.svg/200px-Indomaret_logo.svg.png",
        "branches": [
            {"nama_cabang": "Indomaret Warugajaya", "area_tags": ["Ciwaruga"]},
            {"nama_cabang": "Indomaret Sarijadi 10", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Indomaret Perintis 2", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Indomaret Sarimanah 58", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Indomaret Sari Asih", "area_tags": ["Sarijadi"]},
            {"nama_cabang": "Indomaret Sarimanis 21", "area_tags": ["Sarijadi"]}
        ]
    },
    "Yomart": {
        "logo": "https://static.wikia.nocookie.net/logopedia/images/4/4c/Yomart_logo.png",
        "branches": [
            {"nama_cabang": "Yomart Ciwaruga", "area_tags": ["Ciwaruga"]},
            {"nama_cabang": "Yomart Sarimanah", "area_tags": ["Sarijadi"]}
        ]
    }
}
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_promo.json")

# Ganti dengan URL Web App Google Apps Script milikmu
API_URL = "https://script.google.com/macros/s/AKfycbxFSJpo9FTQ0iapFUBj52RDJWFMrhpNyp926sk2JBs8elJ2rmxdR1W6Jleyn-zT5xep/exec"

# Ganti dengan API Key ImgBB milikmu
IMGBB_API_KEY = "2a81f5f79259fea5132713e10543c668"

# Setup logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "activity.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ═══════════════ BACA/TULIS LOKAL ═══════════════
def read_local_data():
    """Membaca data dari file data_promo.json"""
    if not os.path.exists(FILE_PATH):
        logging.warning(f"File {FILE_PATH} tidak ditemukan. Mengembalikan list kosong.")
        return []
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logging.warning(f"Format {FILE_PATH} tidak valid. Mengembalikan list kosong.")
            return []
        return data
    except json.JSONDecodeError:
        logging.error(f"File {FILE_PATH} rusak. Mengembalikan list kosong.")
        return []
    except Exception as e:
        logging.error(f"Gagal membaca {FILE_PATH}: {e}")
        return []

def write_local_data(data):
    """Menulis data ke file data_promo.json"""
    if not isinstance(data, list):
        logging.error("Data yang akan ditulis bukan list. Operasi dibatalkan.")
        return False
    try:
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"Data lokal berhasil ditulis ({len(data)} item).")
        return True
    except Exception as e:
        logging.error(f"Gagal menulis {FILE_PATH}: {e}")
        return False

# ═══════════════ ENRICH DATA ═══════════════
def enrich_data(raw_data):
    """
    Memperkaya data mentah dari scraper dengan data cabang spesifik dan area_tags
    berdasarkan ADDRESS_BOOK. Jika brand tidak ditemukan di ADDRESS_BOOK, data asli
    tetap dipertahankan.
    """
    if not isinstance(raw_data, list):
        return []
        
    enriched_data = []
    
    for item in raw_data:
        brand = item.get("brand_toko", item.get("retailer_brand", "Unknown")).strip()
        
        # Cari data brand di ADDRESS_BOOK (case-insensitive)
        matched_brand_key = None
        for key in ADDRESS_BOOK:
            if key.lower() == brand.lower():
                matched_brand_key = key
                break
                
        if matched_brand_key:
            brand_config = ADDRESS_BOOK[matched_brand_key]
            branches = brand_config.get("branches", [])
            logo_url = brand_config.get("logo", "")
            
            for branch in branches:
                new_item = copy.deepcopy(item)
                cabang_name = branch.get("nama_cabang", "")
                areas = branch.get("area_tags", [])
                
                new_item["nama_cabang"] = cabang_name
                new_item["area_tags"] = areas
                new_item["logo_url"] = logo_url
                
                # Buat ID yang unik untuk setiap cabang
                base_id = item.get("id", f"{brand}|{item.get('nama_produk','')}".replace(" ", "_").lower())
                safe_cabang = cabang_name.replace(" ", "_").lower()
                new_item["id"] = f"{base_id}|{safe_cabang}"
                
                # Perbarui search_vector agar mengandung nama cabang & area
                item_name = item.get("nama_produk", "")
                new_item["search_vector"] = f"{item_name} {cabang_name} {' '.join(areas)}".lower()
                
                enriched_data.append(new_item)
        else:
            # Jika brand tidak dikenali, biarkan seperti apa adanya
            enriched_data.append(item)
            
    logging.info(f"Enrichment selesai: {len(raw_data)} raw data menjadi {len(enriched_data)} item spesifik.")
    return enriched_data

# ═══════════════ FETCH DARI GOOGLE SHEETS ═══════════════
def fetch_cloud_data(sheet_name="Promo"):
    """Mengambil data dari Google Sheets (Sheet Promo atau Rekomendasi)"""
    try:
        response = requests.get(API_URL, params={"sheet": sheet_name}, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            logging.info(f"Fetch cloud sukses ({len(data)} data dari sheet {sheet_name})")
            return data
        else:
            logging.error("Data dari cloud bukan format list.")
            return []
    except requests.exceptions.ConnectionError:
        logging.error("Fetch cloud gagal: Tidak ada koneksi internet.")
        return []
    except requests.exceptions.Timeout:
        logging.error("Fetch cloud gagal: Request timeout.")
        return []
    except requests.exceptions.HTTPError as e:
        logging.error(f"Fetch cloud gagal: HTTP Error {e.response.status_code}")
        return []
    except Exception as e:
        logging.error(f"Fetch cloud gagal: {e}")
        return []

# ═══════════════ PUSH KE GOOGLE SHEETS ═══════════════
def push_promo_to_cloud(data):
    """Mengirim data promo ke Google Sheets (Sheet Promo) dengan strategi Replace"""
    if not data or not isinstance(data, list):
        logging.error("Push dibatalkan: data kosong atau bukan list.")
        return False
    try:
        response = requests.post(
            API_URL,
            params={"sheet": "Promo"},
            json=data,
            timeout=90
        )
        response.raise_for_status()
        logging.info(f"Push cloud sukses ({len(data)} data)")
        return True
    except requests.exceptions.ConnectionError:
        logging.error("Push cloud gagal: Tidak ada koneksi internet.")
        return False
    except requests.exceptions.Timeout:
        logging.error("Push cloud gagal: Request timeout.")
        return False
    except Exception as e:
        logging.error(f"Push cloud gagal: {e}")
        return False

def add_rekomendasi(entry):
    """Menambahkan satu rekomendasi baru ke Google Sheets (Sheet Rekomendasi)"""
    try:
        response = requests.post(
            API_URL,
            params={"sheet": "Rekomendasi"},
            json=entry,
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Rekomendasi baru dikirim: {entry.get('nama', 'N/A')}")
        return True
    except Exception as e:
        logging.error(f"Gagal kirim rekomendasi: {e}")
        return False

# ═══════════════ UPLOAD FOTO KE IMGBB ═══════════════
def upload_photo(file_path):
    """Mengunggah foto ke ImgBB API dan mengembalikan URL gambar"""
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                files={"image": f},
                timeout=30
            )
        response.raise_for_status()
        url = response.json()["data"]["url"]
        logging.info(f"Foto berhasil diunggah: {url}")
        return url
    except FileNotFoundError:
        logging.error(f"Upload foto gagal: File tidak ditemukan di {file_path}")
        return None
    except Exception as e:
        logging.error(f"Upload foto gagal: {e}")
        return None

# ═══════════════ SYNC ═══════════════
def sync_to_cloud():
    """Sinkronisasi data lokal → cloud"""
    data = read_local_data()
    if not data:
        logging.warning("Sync ke cloud dibatalkan: data lokal kosong.")
        return False
    return push_promo_to_cloud(data)

def sync_from_cloud():
    """Sinkronisasi cloud → lokal (dengan cache 100 entri)"""
    data = fetch_cloud_data()
    if not data:
        logging.warning("Sync dari cloud dibatalkan: cloud kosong.")
        return
    # Batasi maksimal 100 entri
    if len(data) > 100:
        logging.info(f"Membatasi data dari {len(data)} menjadi 100 entri terbaru")
        data = data[-100:]
    write_local_data(data)
    logging.info(f"Sync dari cloud berhasil ({len(data)} item)")