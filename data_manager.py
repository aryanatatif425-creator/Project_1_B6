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
    "Alfamart": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Alfamart_logo.svg/200px-Alfamart_logo.svg.png",
        "branches": [
            {"nama_cabang": "Alfamart Warugajaya", "area_tags": ["Ciwaruga"], "address": "Jl. Warugajaya No. 5, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559"},
            {"nama_cabang": "Alfamart Ciwaruga", "area_tags": ["Ciwaruga"], "address": "Jl. Ciwaruga No. 120, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559"},
            {"nama_cabang": "Alfamart Gegerkalong", "area_tags": ["Gegerkalong"], "address": "Jl. Gegerkalong Hilir No. 75, Gegerkalong, Kec. Sukasari, Kota Bandung 40153"},
            {"nama_cabang": "Alfamart Sarimanah", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanah No. 33, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Alfamart Sariwangi", "area_tags": ["Sarijadi"], "address": "Jl. Sariwangi No. 18, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Alfamart Terusan Sutami", "area_tags": ["Sarijadi"], "address": "Jl. Terusan Sutami No. 45, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Alfamart Sarijadi Baru", "area_tags": ["Sarijadi"], "address": "Jl. Sarijadi Baru No. 7, Sarijadi, Kec. Sukasari, Kota Bandung 40151"}
        ]
    },
    "Indomaret": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Indomaret_logo.svg/200px-Indomaret_logo.svg.png",
        "branches": [
            {"nama_cabang": "Indomaret Warugajaya", "area_tags": ["Ciwaruga"], "address": "Jl. Warugajaya No. 12, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559"},
            {"nama_cabang": "Indomaret Sarijadi 10", "area_tags": ["Sarijadi"], "address": "Jl. Sarijadi Raya No. 10, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Indomaret Perintis 2", "area_tags": ["Sarijadi"], "address": "Jl. Perintis Kemerdekaan No. 2, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Indomaret Sarimanah 58", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanah No. 58, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Indomaret Sari Asih", "area_tags": ["Sarijadi"], "address": "Jl. Sari Asih No. 22, Sarijadi, Kec. Sukasari, Kota Bandung 40151"},
            {"nama_cabang": "Indomaret Sarimanis 21", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanis No. 21, Sarijadi, Kec. Sukasari, Kota Bandung 40151"}
        ]
    },
    "Yomart": {
        "logo": "https://static.wikia.nocookie.net/logopedia/images/4/4c/Yomart_logo.png",
        "branches": [
            {"nama_cabang": "Yomart Ciwaruga", "area_tags": ["Ciwaruga"], "address": "Jl. Ciwaruga No. 55, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559"},
            {"nama_cabang": "Yomart Sarimanah", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanah No. 15, Sarijadi, Kec. Sukasari, Kota Bandung 40151"}
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
    matched_count = 0
    unmatched_count = 0
    
    for item in raw_data:
        brand = item.get("brand_toko", item.get("retailer_brand", "Unknown")).strip()
        
        # Cari data brand di ADDRESS_BOOK (case-insensitive)
        matched_brand_key = None
        for key in ADDRESS_BOOK:
            if key.lower() == brand.lower():
                matched_brand_key = key
                break
                
        if matched_brand_key:
            matched_count += 1
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
            unmatched_count += 1
            # Jika brand tidak dikenali, biarkan seperti apa adanya
            enriched_data.append(item)
            
    logging.info(f"Enrichment selesai: {len(raw_data)} raw data menjadi {len(enriched_data)} item spesifik ({matched_count} matched, {unmatched_count} unmatched).")
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
            raise ValueError("Cloud data is not a list")
    except requests.exceptions.ConnectionError:
        logging.error("Fetch cloud gagal: Tidak ada koneksi internet.")
        raise
    except requests.exceptions.Timeout:
        logging.error("Fetch cloud gagal: Request timeout.")
        raise
    except requests.exceptions.HTTPError as e:
        logging.error(f"Fetch cloud gagal: HTTP Error {e.response.status_code}")
        raise
    except Exception as e:
        logging.error(f"Fetch cloud gagal: {e}")
        raise

def get_demo_recommendations():
    return [
        {
            "nama": "Warung Nasi Ibu Imas",
            "menu": "Nasi Timbel, Ayam Goreng, Sambal Terasi",
            "harga": 25000,
            "rating": 4.5,
            "latitude": -6.8620,
            "longitude": 107.5750,
            "foto": "",
            "area": "Ciwaruga",
            "jam_buka": "08:00 - 21:00"
        },
        {
            "nama": "Bakso Akpol Ciwaruga",
            "menu": "Bakso Urat, Mie Ayam, Tahu Goreng",
            "harga": 18000,
            "rating": 4.3,
            "latitude": -6.8640,
            "longitude": 107.5770,
            "foto": "",
            "area": "Ciwaruga",
            "jam_buka": "09:00 - 22:00"
        },
        {
            "nama": "Sate Maranggi H. Iming",
            "menu": "Sate Maranggi Daging Sapi, Nasi, Lontong",
            "harga": 35000,
            "rating": 4.7,
            "latitude": -6.8600,
            "longitude": 107.5730,
            "foto": "",
            "area": "Ciwaruga",
            "jam_buka": "10:00 - 20:00"
        },
        {
            "nama": "Mie Gacoan Sarijadi",
            "menu": "Mie Gacoan Level 1-8, Siomay, Pangsit",
            "harga": 15000,
            "rating": 4.2,
            "latitude": -6.8680,
            "longitude": 107.5800,
            "foto": "",
            "area": "Sarijadi",
            "jam_buka": "10:00 - 22:00"
        },
        {
            "nama": "RM Padang Sederhana Gegerkalong",
            "menu": "Rendang, Ayam Pop, Gulai Tunjang, Sayur Nangka",
            "harga": 30000,
            "rating": 4.4,
            "latitude": -6.8660,
            "longitude": 107.5780,
            "foto": "",
            "area": "Gegerkalong",
            "jam_buka": "08:00 - 21:00"
        }
    ]

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
def upload_photo(photo_data):
    """Mengunggah foto ke ImgBB API dan mengembalikan URL gambar. photo_data can be a file path or a base64 data URL."""
    try:
        if photo_data and isinstance(photo_data, str) and photo_data.startswith("data:"):
            import base64
            header, b64 = photo_data.split(",", 1)
            image_bytes = base64.b64decode(b64)
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                params={"key": IMGBB_API_KEY},
                files={"image": ("photo.jpg", image_bytes, "image/jpeg")},
                timeout=30
            )
        else:
            with open(photo_data, "rb") as f:
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
        logging.error(f"Upload foto gagal: File tidak ditemukan di {photo_data}")
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
    """Sinkronisasi cloud → lokal"""
    try:
        data = fetch_cloud_data()
    except Exception:
        logging.error("Sync dari cloud dibatalkan: fetch cloud gagal dengan exception.")
        return
    if not data:
        logging.warning("Sync dari cloud dibatalkan: cloud kosong.")
        return
    write_local_data(data)
    logging.info(f"Sync dari cloud berhasil ({len(data)} item)")