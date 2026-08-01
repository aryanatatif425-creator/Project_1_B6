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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

import copy

# ═══════════════ KONFIGURASI ═══════════════
ADDRESS_BOOK = {
    "Alfamart": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Alfamart_logo.svg/200px-Alfamart_logo.svg.png",
        "branches": [
            {"nama_cabang": "Alfamart Warugajaya", "area_tags": ["Ciwaruga"], "address": "Jl. Warugajaya No. 5, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559", "latitude": -6.8620, "longitude": 107.5900},
            {"nama_cabang": "Alfamart Ciwaruga", "area_tags": ["Ciwaruga"], "address": "Jl. Ciwaruga No. 120, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559", "latitude": -6.8645, "longitude": 107.5885},
            {"nama_cabang": "Alfamart Gegerkalong", "area_tags": ["Gegerkalong"], "address": "Jl. Gegerkalong Hilir No. 75, Gegerkalong, Kec. Sukasari, Kota Bandung 40153", "latitude": -6.8670, "longitude": 107.5840},
            {"nama_cabang": "Alfamart Sarimanah", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanah No. 33, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8715, "longitude": 107.5810},
            {"nama_cabang": "Alfamart Sariwangi", "area_tags": ["Sarijadi"], "address": "Jl. Sariwangi No. 18, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8730, "longitude": 107.5795},
            {"nama_cabang": "Alfamart Terusan Sutami", "area_tags": ["Sarijadi"], "address": "Jl. Terusan Sutami No. 45, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8695, "longitude": 107.5760},
            {"nama_cabang": "Alfamart Sarijadi Baru", "area_tags": ["Sarijadi"], "address": "Jl. Sarijadi Baru No. 7, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8700, "longitude": 107.5745}
        ]
    },
    "Indomaret": {
        "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Indomaret_logo.svg/200px-Indomaret_logo.svg.png",
        "branches": [
            {"nama_cabang": "Indomaret Warugajaya", "area_tags": ["Ciwaruga"], "address": "Jl. Warugajaya No. 12, Ciwaruga, Kec. Parongpong, Kab. Bandung Barat 40559", "latitude": -6.8615, "longitude": 107.5915},
            {"nama_cabang": "Indomaret Sarijadi 10", "area_tags": ["Sarijadi"], "address": "Jl. Sarijadi Raya No. 10, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8720, "longitude": 107.5780},
            {"nama_cabang": "Indomaret Perintis 2", "area_tags": ["Sarijadi"], "address": "Jl. Perintis Kemerdekaan No. 2, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8705, "longitude": 107.5775},
            {"nama_cabang": "Indomaret Sarimanah 58", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanah No. 58, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8725, "longitude": 107.5805},
            {"nama_cabang": "Indomaret Sari Asih", "area_tags": ["Sarijadi"], "address": "Jl. Sari Asih No. 22, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8735, "longitude": 107.5785},
            {"nama_cabang": "Indomaret Sarimanis 21", "area_tags": ["Sarijadi"], "address": "Jl. Sarimanis No. 21, Sarijadi, Kec. Sukasari, Kota Bandung 40151", "latitude": -6.8740, "longitude": 107.5765}
        ]
    },
    "Griya": {
        "logo": "",  # logo not used in GUI, leave blank
        "branches": [
            {"nama_cabang": "Griya Setiabudi", "area_tags": ["Gegerkalong"], "address": "Jl. Setiabudi No. 1, Gegerkalong, Bandung", "latitude": -6.8665, "longitude": 107.5850},
            {"nama_cabang": "Griya Setrasari", "area_tags": ["Sarijadi"], "address": "Jl. Setrasari, Sarijadi, Bandung", "latitude": -6.8710, "longitude": 107.5730}
        ]
    }
}
FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_promo.json")

# Credentials — baca dari environment variable, fallback ke nilai lama untuk development
API_URL = os.environ.get("RADAR_GOOGLE_SCRIPT_URL", "")
IMGBB_API_KEY = os.environ.get("RADAR_IMGBB_API_KEY", "")

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
            pass
            
    logging.info(f"Enrichment selesai: {len(raw_data)} raw data menjadi {len(enriched_data)} item spesifik ({matched_count} matched, {unmatched_count} unmatched).")
    return enriched_data

# ═══════════════ ERROR HANDLER TERPUSAT ═══════════════
def get_user_friendly_error(e, context="fitur"):
    """Return a user-friendly error message for network/API errors."""
    if isinstance(e, requests.exceptions.ConnectionError):
        return f"Tidak dapat terhubung ke server untuk {context}. Periksa koneksi internet Anda."
    elif isinstance(e, requests.exceptions.Timeout):
        return f"Koneksi timeout saat memuat {context}. Coba lagi nanti."
    elif isinstance(e, requests.exceptions.HTTPError):
        return f"Server mengembalikan kesalahan saat memuat {context}. Coba lagi nanti."
    elif isinstance(e, FileNotFoundError):
        return f"File tidak ditemukan untuk {context}."
    else:
        return f"Terjadi kesalahan saat memuat {context}. Periksa koneksi dan coba lagi."

# ═══════════════ FETCH DARI GOOGLE SHEETS ═══════════════
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_promo_cache.json")

def _save_cache(data):
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None

def fetch_cloud_data(sheet_name="Promo"):
    """Mengambil data dari Google Sheets (Sheet Promo atau Rekomendasi). Fallback ke cache jika offline."""
    print(f"[DEBUG] fetch_cloud_data called for sheet: {sheet_name}")
    if not API_URL:
        logging.warning("RADAR_GOOGLE_SCRIPT_URL belum diatur. Melewati fetch cloud.")
        cached = _load_cache()
        return cached if cached is not None else []
    try:
        response = requests.get(API_URL, params={"sheet": sheet_name}, timeout=10)
        print(f"[DEBUG] fetch_cloud_data response status: {response.status_code}")
        print(f"[DEBUG] fetch_cloud_data response headers: {dict(response.headers)}")
        print(f"[DEBUG] fetch_cloud_data response text (first 300 chars): {response.text[:300]}")
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            print(f"[DEBUG] fetch_cloud_data: Response is not JSON (Content-Type: {content_type}). Likely Apps Script error page.")
            logging.error(f"Fetch cloud gagal: Response bukan JSON (Content-Type: {content_type}). Cek URL Apps Script.")
            cached = _load_cache()
            return cached if cached is not None else []
        data = response.json()
        if isinstance(data, list):
            logging.info(f"Fetch cloud sukses ({len(data)} data dari sheet {sheet_name})")
            _save_cache(data)
            return data
        else:
            logging.error("Data dari cloud bukan format list.")
            raise ValueError("Cloud data is not a list")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logging.warning(f"Fetch cloud gagal: Tidak ada koneksi. Mencoba load dari cache...")
        cached = _load_cache()
        if cached is not None:
            logging.info(f"Berhasil load dari cache ({len(cached)} data)")
            return cached
        raise Exception(get_user_friendly_error(e, "mengambil data"))
    except requests.exceptions.HTTPError as e:
        logging.error(f"Fetch cloud gagal: HTTP Error {e.response.status_code}")
        raise Exception(get_user_friendly_error(e, "mengambil data"))
    except requests.exceptions.JSONDecodeError as je:
        logging.error(f"Fetch cloud gagal: Response bukan JSON yang valid - {je}")
        print(f"[DEBUG] fetch_cloud_data JSONDecodeError: {je}")
        raise Exception(get_user_friendly_error(je, "mengambil data"))
    except Exception as e:
        logging.error(f"Fetch cloud gagal: {e}")
        raise Exception(get_user_friendly_error(e, "mengambil data"))

def get_demo_recommendations():
    return [
        {
            "nama": "Warung Nasi Ibu Imas",
            "menu": "Nasi Timbel, Ayam Goreng, Sambal Terasi",
            "harga_min": 20000,
            "harga_max": 35000,
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
            "harga_min": 15000,
            "harga_max": 25000,
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
            "harga_min": 30000,
            "harga_max": 45000,
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
            "harga_min": 12000,
            "harga_max": 22000,
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
            "harga_min": 25000,
            "harga_max": 40000,
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
    print(f"[DEBUG] add_rekomendasi called with entry: nama={entry.get('nama')}, lat={entry.get('latitude')}, lon={entry.get('longitude')}")
    print(f"[DEBUG] Request payload: {json.dumps(entry, ensure_ascii=False)}")
    try:
        response = requests.post(
            API_URL,
            params={"sheet": "Rekomendasi"},
            json=entry,
            timeout=10
        )
        print(f"[DEBUG] add_rekomendasi response status: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        print(f"[DEBUG] Response text (first 500 chars): {response.text[:500]}")
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            print(f"[DEBUG] Response is not JSON (Content-Type: {content_type}). Cannot verify write success.")
            print("[DEBUG] Returning False to indicate uncertain write - fix Apps Script to return JSON")
            return False
        resp_json = response.json()
        print(f"[DEBUG] Response JSON: {resp_json}")
        if resp_json.get("success") is True:
            logging.info(f"Rekomendasi baru dikirim: {entry.get('nama', 'N/A')}")
            print("[DEBUG] add_rekomendasi returning True (server success=True)")
            return True
        else:
            print(f"[DEBUG] Server returned success=False or missing: {resp_json}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"[DEBUG] add_rekomendasi connection error: {e}")
        logging.error(f"Gagal kirim rekomendasi: Tidak ada koneksi internet.")
        raise Exception(get_user_friendly_error(e, "mengirim rekomendasi"))
    except requests.exceptions.Timeout as e:
        print(f"[DEBUG] add_rekomendasi timeout: {e}")
        logging.error(f"Gagal kirim rekomendasi: Koneksi timeout.")
        raise Exception(get_user_friendly_error(e, "mengirim rekomendasi"))
    except Exception as e:
        print(f"[DEBUG] add_rekomendasi exception: {e}")
        logging.error(f"Gagal kirim rekomendasi: {e}")
        raise Exception(get_user_friendly_error(e, "mengirim rekomendasi"))

def add_reaction(rekomen_id, reaction_type, delta=1):
    """Memperbarui reaksi (murah/enak) untuk rekomendasi yang ada di Google Sheets. delta=1 increment, delta=-1 decrement."""
    try:
        payload = {"id": rekomen_id, "reaksi": reaction_type, "delta": delta}
        response = requests.post(
            API_URL,
            params={"sheet": "Rekomendasi", "action": "reaction"},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json() if response.text else {}
        logging.info(f"Reaction '{reaction_type}' ({'+' if delta > 0 else ''}{delta}) for {rekomen_id}: {result}")
        return result
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Gagal add reaction: Tidak ada koneksi internet.")
        logging.warning(get_user_friendly_error(e, "menambahkan reaksi"))
        return None
    except requests.exceptions.Timeout as e:
        logging.error(f"Gagal add reaction: Koneksi timeout.")
        logging.warning(get_user_friendly_error(e, "menambahkan reaksi"))
        return None
    except Exception as e:
        logging.error(f"Gagal add reaction: {e}")
        logging.warning(get_user_friendly_error(e, "menambahkan reaksi"))
        return None

# ═══════════════ UPLOAD FOTO KE CATBOX (dengan fallback ImgBB) ═══════════════
def upload_photo(photo_data):
    """Mengunggah foto ke Catbox (catbox.moe) dengan fallback ke ImgBB. photo_data can be a file path or a base64 data URL."""
    try:
        import base64
        import os
        import tempfile

        # Create session with HTTPAdapter for faster failure (total=1 retries)
        session = requests.Session()
        retry_strategy = Retry(
            total=1,
            connect=1,
            read=0,
            allowed_methods=["POST"],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        catbox_url = "https://catbox.moe/user/api.php"

        if photo_data and isinstance(photo_data, str) and photo_data.startswith("data:"):
            header, b64 = photo_data.split(",", 1)
            image_bytes = base64.b64decode(b64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            file_to_upload = open(tmp_path, "rb")
            filename = os.path.basename(tmp_path)
        else:
            file_to_upload = open(photo_data, "rb")
            filename = os.path.basename(photo_data)

        files = {"fileToUpload": (filename, file_to_upload, "image/jpeg")}
        data = {"reqtype": "fileupload"}
        headers = {"User-Agent": "RadarPromo/2.0"}

        print(f"[DEBUG] Catbox upload starting...")
        response = session.post(catbox_url, files=files, data=data, headers=headers, timeout=(60, 30))
        file_to_upload.close()

        if photo_data and isinstance(photo_data, str) and photo_data.startswith("data:"):
            os.unlink(tmp_path)

        if response.status_code == 200 and "https://files.catbox.moe/" in response.text:
            img_url = response.text.strip()
            print(f"[DEBUG] Catbox upload success: {img_url}")
            logging.info(f"Foto berhasil diunggah ke Catbox: {img_url}")
            session.close()
            return img_url
        else:
            print(f"[DEBUG] Catbox upload failed: {response.status_code} - {response.text[:200]}")
            logging.error(f"Catbox upload failed: {response.text}")

        # Fallback to ImgBB if Catbox fails
        print(f"[DEBUG] Falling back to ImgBB...")
        try:
            import base64
            import os
            import tempfile

            imgbb_url = "https://api.imgbb.com/1/upload"

            if photo_data and isinstance(photo_data, str) and photo_data.startswith("data:"):
                header, b64_data = photo_data.split(",", 1)
                b64_payload = b64_data
            else:
                with open(photo_data, "rb") as f:
                    b64_payload = base64.b64encode(f.read()).decode("utf-8")

            imgbb_data = {
                "key": IMGBB_API_KEY,
                "image": b64_payload,
            }

            print(f"[DEBUG] ImgBB upload starting...")
            imgbb_response = session.post(imgbb_url, data=imgbb_data, timeout=(60, 30))
            imgbb_response.raise_for_status()
            imgbb_result = imgbb_response.json()

            if imgbb_result.get("success"):
                img_url = imgbb_result["data"]["url"]
                print(f"[DEBUG] ImgBB upload success: {img_url}")
                logging.info(f"Foto berhasil diunggah ke ImgBB (fallback): {img_url}")
                session.close()
                return img_url
            else:
                print(f"[DEBUG] ImgBB upload failed: {imgbb_result}")
                logging.error(f"ImgBB upload failed: {imgbb_result}")

        except Exception as e:
            print(f"[DEBUG] ImgBB fallback exception: {e}")
            logging.error(f"ImgBB fallback gagal: {e}")
            raise Exception(get_user_friendly_error(e, "upload foto"))

        session.close()
        raise Exception("Gagal upload foto. Kedua layanan (Catbox dan ImgBB) tidak tersedia.")

    except FileNotFoundError:
        logging.error(f"Upload foto gagal: File tidak ditemukan di {photo_data}")
        raise Exception(f"File foto tidak ditemukan.")
    except requests.exceptions.ConnectionError:
        logging.error(f"Upload foto gagal: Tidak ada koneksi internet.")
        raise Exception("Tidak dapat terhubung ke server upload. Periksa koneksi internet Anda.")
    except requests.exceptions.Timeout:
        logging.error(f"Upload foto gagal: Upload timeout.")
        raise Exception("Upload foto timeout. File terlalu besar atau koneksi lambat.")
    except Exception as e:
        logging.error(f"Upload foto gagal: {e}")
        print(f"[DEBUG] Upload foto exception: {e}")
        raise Exception(get_user_friendly_error(e, "upload foto"))

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