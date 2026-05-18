"""
scraper.py — Web Scraper hemat.id
==================================
Menarik data promo groceries dari hemat.id.
"""

import re
import time
import requests
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional, Tuple, List, Dict

BASE_URL = "https://www.hemat.id"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
}

TARGET_RETAILERS = {
    "borma": "Borma",
    "superindo": "Superindo",
    "yogya": "Yogya",
    "griya": "Griya",
    "alfamart": "Alfamart",
    "indomaret": "Indomaret",
    "yomart": "Yomart",
}

# Kategori asli dari hemat.id untuk filter di URL
NATIVE_CATEGORIES = [
    "makanan-minuman",
    "makanan-segar",
    "bahan-masakan",
    "kesehatan-kecantikan",
    "perawatan-kulit-tubuh",
    "bayi-anak"
]

EXCLUDE_KEYWORDS = [
    # Elektronik & Gadget
    "laptop", "tablet", "charger", "headset", "speaker", "earphone", "powerbank", "kamera", "smartwatch", "drone", "handphone", "hp", "samsung", "vivo", "oppo", "tv", "led",
    # Peralatan Rumah Tangga & Dapur
    "kompor", "oven", "mixer", "dispenser", "magic com", "air fryer", "juicer", "toaster", "chopper", "cooker", "kulkas", "mesin cuci", "setrika", "kipas", "panci", "wajan", "blender",
    # Furniture & Dekorasi
    "lemari", "kasur", "sofa", "meja", "kursi", "rak", "springbed", "lampu", "hiasan",
    # Fashion & Aksesoris
    "jaket", "kemeja", "kaos", "celana", "sepatu", "sandal", "tas", "dompet", "jam tangan", "topi", "baju",
    # Peralatan Bangunan & Pertukangan
    "palu", "obeng", "tang", "bor", "gergaji", "kunci", "cat", "kuas", "sekop", "kabel",
    # Mainan & Hobi
    "mainan", "boneka", "action figure", "puzzle", "board game",
    # Otomotif
    "helm", "oli", "ban", "aki", "spion", "sepeda", "motor"
]

CATEGORY_MAP = {
    "Sembako": ["beras", "minyak", "gula", "tepung", "garam", "telur", "kecap", "sambal", "saus", "margarin", "mentega", "santan", "royco", "masako", "totole", "maggi", "ajinomoto", "racik", "bumbu", "kaldu", "ladaku", "ayam", "daging", "sapi", "ikan", "sayur", "buah", "bawang", "cabe", "tomat", "jeruk", "apel", "mangga", "pisang", "anggur", "melon", "semangka"],
    "Makanan Instan": ["mie", "noodle", "indomie", "sedaap", "sarimi", "pop mie", "sarden", "kornet", "nugget", "fiesta", "so good", "sosis", "dimsum", "seblak", "roti", "bakso", "abon", "la fonte", "spaghetti", "macaroni"],
    "Minuman": ["susu", "ultra", "indomilk", "cimory", "bear brand", "yakult", "dancow", "kopi", "teh", "air", "aqua", "minerale", "sirup", "coca-cola", "sprite", "fanta", "minuman", "jus", "buavita", "hydro", "pocari", "galon", "vit", "le minerale", "nestle"],
    "Kamar & Kebersihan": ["sabun", "lifebuoy", "lux", "biore", "dettol", "shampo", "pantene", "clear", "sunsilk", "pasta gigi", "pepsodent", "deterjen", "rinso", "pewangi", "molto", "sunlight", "pembersih", "wipol", "vixal", "stella", "bayclean", "soklin", "daia", "downy", "sikat", "odol", "kamper", "bagus", "deodorant", "rexona", "body wash", "sabun mandi"],
    "Kesehatan": ["nyamuk", "hit", "baygon", "vape", "autan", "tisu", "paseo", "nice", "telon", "kayu putih", "vitamin", "enervon", "tolak angin", "bodrex", "panadol", "promag", "betadine", "diapers", "pembalut", "charm", "laurier", "masker", "handsanitizer", "sweety", "mamypoko", "merries", "popok", "lotion", "cleanser", "serum", "body mist", "hair color", "skincare", "pomade", "parfum", "cologne", "sunscreen", "facial wash", "micellar", "toner", "moisturizer", "bedak", "lipstik", "lip balm"],
    "Snack": ["biskuit", "roma", "khong guan", "keripik", "chitato", "japota", "kusuka", "qtela", "kacang", "garuda", "cokelat", "coklat", "silverqueen", "beng beng", "oreo", "pocky", "tango", "snack", "wafer", "permen", "kopiko", "yupi", "choki", "taro", "lays", "es krim", "ice cream", "walls", "campina", "aice", "kuaci"]
}


def clean_price(raw: str) -> Optional[int]:
    if not raw:
        return None
        
    # Hapus harga satuan (contoh: "Rp 1.000 / Liter" atau "Rp 1.200 / 100 gr")
    raw = re.sub(r'Rp\s*[\d\.]+\s*/\s*\d*\s*(?:liter|l|ml|gr|g|pcs|kg|m)\b', '', raw, flags=re.IGNORECASE)
    
    # 1. Cari pola "Harga Promo RpX.XXX" atau "Promo RpX.XXX"
    m_promo = re.search(r'(?:Promo)\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_promo:
        cleaned = re.sub(r'[^\d]', '', m_promo.group(1))
        if cleaned: return int(cleaned)
        
    # 2. Jika tidak ada kata promo, cari kemunculan pertama "RpX.XXX"
    m_rp = re.search(r'Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_rp:
        cleaned = re.sub(r'[^\d]', '', m_rp.group(1))
        if cleaned: return int(cleaned)
        
    # 3. Fallback: ambil semua angka, hindari jika merupakan diskon
    # Hapus kata "Diskon XX%" agar angkanya tidak terambil
    raw_no_disc = re.sub(r'Diskon\s*\d+\s*%', '', raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^\d]", "", raw_no_disc)
    
    if not cleaned:
        return None
        
    price = int(cleaned)
    if price > 10000000:
        for i in [5, 6, 7]:
            if len(cleaned) >= i:
                possible_price = int(cleaned[-i:])
                if 1000 <= possible_price <= 10000000:
                    return possible_price
        if len(cleaned) >= 6:
            return int(cleaned[-6:])
            
    if 0 < price < 1000:
        return price * 1000
        
    return price


def format_price(price_int: int) -> str:
    return f"Rp {price_int:,.0f}".replace(",", ".")


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception:
            time.sleep(2)
    return None


def classify_product(name: str) -> Optional[str]:
    lower = name.lower()
    
    # 0. Cek Blacklist (Jika masuk blacklist, langsung buang)
    for bad_word in EXCLUDE_KEYWORDS:
        if re.search(rf"\b{re.escape(bad_word)}\b", lower):
            return None
            
    # 1. Exact word boundary match menggunakan Regex
    for cat, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            # Gunakan word boundary untuk kecocokan kata persis.
            # re.escape() memastikan spasi atau karakter spesial ditangani dengan benar.
            if re.search(rf"\b{re.escape(kw)}\b", lower):
                return cat
                
    # Jika tidak ada yang cocok secara utuh, kembalikan None (buang produk dari hasil)
    return None


def scrape_retailer(slug: str, label: str, max_pages: int = 5) -> List[Dict]:
    results = []
    progress_log = f"[{label}]"
    
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}/katalog/{slug}/"
        else:
            url = f"{BASE_URL}/katalog/{slug}/?page={page}"
            
        soup = fetch_page(url)
        if not soup:
            progress_log += f" | Halaman {page}: 0 item (gagal fetch)"
            break

        cards = soup.select("div.item") or soup.select("div.product-card") or soup.select(".product-item")
        
        if not cards:
            progress_log += f" | Halaman {page}: 0 item (berhenti)"
            break
            
        page_results = []
        for card in cards:
            try:
                # Nama
                title_div = card.select_one("div.title") or card.select_one(".product-title")
                if not title_div: continue
                brand_tag = title_div.select_one("div.brand")
                item_name = title_div.get_text(strip=True)
                if brand_tag:
                    item_name = item_name.replace(brand_tag.get_text(strip=True), "").strip()

                # Harga
                desc_tag = card.select_one("div.desc") or card.select_one(".price")
                raw_price = desc_tag.get_text(strip=True) if desc_tag else ""
                price_int = clean_price(raw_price)
                if not item_name or price_int is None: continue

                # Gambar
                img_div = card.select_one("div.img") or card.select_one(".product-image")
                image_url = ""
                if img_div:
                    img_tag = img_div.select_one("img")
                    if img_tag:
                        image_url = img_tag.get("data-src") or img_tag.get("src", "")
                        if image_url.startswith("/"):
                            image_url = BASE_URL + image_url

                category = classify_product(item_name)
                is_promo = "promo" in raw_price.lower() or "hemat" in raw_price.lower()
                ts_scrape = datetime.now().isoformat()
                
                str_to_hash = image_url if image_url else item_name
                img_hash = hashlib.md5(str_to_hash.encode()).hexdigest()[:8]
                safe_name = re.sub(r'[^a-z0-9]', '_', item_name.lower())[:20]
                prod_id = f"{label.lower()}|{safe_name}|{img_hash}"
                area_tags = ["Ciwaruga", "Sarijadi", "Gegerkalong"]
                search_vector = f"{item_name} {label} {' '.join(area_tags)}".lower()

                page_results.append({
                    "id": prod_id, "timestamp_scrape": ts_scrape,
                    "nama_produk": item_name.strip().title(), "brand_toko": label,
                    "nama_cabang": f"{label} ", "kategori": category,
                    "area_tags": area_tags, "harga_normal": price_int,
                    "harga_promo": price_int, "diskon_persen": 0.0,
                    "perubahan_harga": 0, "jenis_harga": "PROMO" if is_promo else "REGULER",
                    "periode_promo": "", "display_harga": format_price(price_int),
                    "image_url": image_url, "logo_url": "", "search_vector": search_vector
                })
            except Exception:
                continue
                
        results.extend(page_results)
        progress_log += f" | Halaman {page}: {len(page_results)} item"
        
        # Stop if no valid products found on this page
        if len(page_results) == 0:
            progress_log += " (berhenti)"
            break
            
        # Delay before next page (unless it's the last page)
        if page < max_pages:
            time.sleep(1)
            
    print(progress_log)
    return results


def run_scraper() -> Tuple[List[Dict], List[str]]:
    all_items = []
    errors = []
    for ret_slug, label in TARGET_RETAILERS.items():
        for cat_slug in NATIVE_CATEGORIES:
            # Format URL slug di hemat.id untuk filter silang: kategori.retailer
            combined_slug = f"{cat_slug}.{ret_slug}"
            try:
                # Kita kurangi max_pages menjadi 3 karena sekarang kita melakukan filter
                # lebih spesifik dan ada banyak kategori per retailer.
                items = scrape_retailer(combined_slug, label, max_pages=3)
                all_items.extend(items)
            except Exception as e:
                err_msg = f"Error scraping {label} ({cat_slug}): {e}"
                print(err_msg)
                errors.append(err_msg)
    return all_items, errors


def get_demo_data() -> List[Dict]:
    return [
        {"id": "superindo|beras_365|demo1", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Beras 365 Pulen Wangi 5kg", "brand_toko": "Superindo", "nama_cabang": "Superindo ", "kategori": "Sembako", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 85000, "harga_promo": 72900, "diskon_persen": 14.1, "perubahan_harga": 0, "jenis_harga": "PROMO", "periode_promo": "", "display_harga": "Rp 72.900", "image_url": "", "logo_url": "", "search_vector": "beras 365 pulen wangi 5kg superindo ciwaruga sarijadi gegerkalong"},
        {"id": "alfamart|minyak_sania|demo2", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Minyak Goreng Sania 2L", "brand_toko": "Alfamart", "nama_cabang": "Alfamart ", "kategori": "Sembako", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 38000, "harga_promo": 35500, "diskon_persen": 6.6, "perubahan_harga": 0, "jenis_harga": "PROMO", "periode_promo": "", "display_harga": "Rp 35.500", "image_url": "", "logo_url": "", "search_vector": "minyak goreng sania 2l alfamart ciwaruga sarijadi gegerkalong"},
        {"id": "indomaret|gula_pasir|demo3", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Gula Pasir Gulaku 1kg", "brand_toko": "Indomaret", "nama_cabang": "Indomaret ", "kategori": "Sembako", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 16500, "harga_promo": 16500, "diskon_persen": 0, "perubahan_harga": 0, "jenis_harga": "REGULER", "periode_promo": "", "display_harga": "Rp 16.500", "image_url": "", "logo_url": "", "search_vector": "gula pasir gulaku 1kg indomaret ciwaruga sarijadi gegerkalong"},
        {"id": "indomaret|indomie_goreng|demo4", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Indomie Mi Goreng Spesial 5x85g", "brand_toko": "Indomaret", "nama_cabang": "Indomaret ", "kategori": "Makanan Instan", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 14800, "harga_promo": 14800, "diskon_persen": 0, "perubahan_harga": 0, "jenis_harga": "REGULER", "periode_promo": "", "display_harga": "Rp 14.800", "image_url": "", "logo_url": "", "search_vector": "indomie mi goreng spesial 5x85g indomaret ciwaruga sarijadi gegerkalong"},
        {"id": "alfamart|teh_pucuk|demo5", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Teh Pucuk Harum 350ml", "brand_toko": "Alfamart", "nama_cabang": "Alfamart ", "kategori": "Minuman", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 3500, "harga_promo": 3500, "diskon_persen": 0, "perubahan_harga": 0, "jenis_harga": "REGULER", "periode_promo": "", "display_harga": "Rp 3.500", "image_url": "", "logo_url": "", "search_vector": "teh pucuk harum 350ml alfamart ciwaruga sarijadi gegerkalong"},
        {"id": "alfamart|stella_matic|demo6", "timestamp_scrape": datetime.now().isoformat(), "nama_produk": "Stella Matic Refill 225ml", "brand_toko": "Alfamart", "nama_cabang": "Alfamart ", "kategori": "Kamar & Kebersihan", "area_tags": ["Ciwaruga", "Sarijadi", "Gegerkalong"], "harga_normal": 35000, "harga_promo": 32000, "diskon_persen": 8.6, "perubahan_harga": 0, "jenis_harga": "PROMO", "periode_promo": "", "display_harga": "Rp 32.000", "image_url": "", "logo_url": "", "search_vector": "stella matic refill 225ml alfamart ciwaruga sarijadi gegerkalong"},
    ]


if __name__ == "__main__":
    data, errors = run_scraper()
    if not data:
        print("Scraping gagal, pakai demo data.")
        data = get_demo_data()
    print(f"Total: {len(data)} item")
    if errors:
        print(f"Errors occurred: {errors}")
