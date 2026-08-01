"""
scraper.py — Web Scraper hemat.id
==================================
Menarik data promo groceries dari hemat.id.
"""

import re
import random
import traceback
import time
import requests
import hashlib
import data_manager
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
    "alfamart": "Alfamart",
    "indomaret": "Indomaret",
    "yogya": "Griya",  # was "yomart": "Yomart"
}

# Kategori asli dari hemat.id untuk filter di URL
NATIVE_CATEGORIES = [
    "makanan-minuman",
    "makanan-segar",
    "bahan-masakan",
    "kesehatan-kecantikan",
    "perawatan-kulit-tubuh",
    "bayi-anak",
    "sembako",
    "snack",
    "minuman",
    "kebersihan",
    "perawatan-rambut",
    "obat-obatan",
    "bumbu-dapur",
    "makanan-hewan",
    "perlengkapan-rumah",
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
    "helm", "oli", "ban", "aki", "spion", "sepeda", "motor",
    # E-commerce & Online Marketplace (campaign tag names — not actual grocery products)
    "shopee", "lazada", "tokopedia", "blibli", "gojek", "grab"
]

CATEGORY_MAP = {
    "Sembako": ["beras", "minyak", "gula", "tepung", "garam", "telur", "kecap", "sambal", "saus", "margarin", "mentega", "santan", "royco", "masako", "totole", "maggi", "ajinomoto", "racik", "bumbu", "kaldu", "ladaku", "ayam", "daging", "sapi", "ikan", "sayur", "buah", "bawang", "cabe", "tomat", "jeruk", "apel", "mangga", "pisang", "anggur", "melon", "semangka"],
    "Makanan Instan": ["mie", "noodle", "indomie", "sedaap", "sarimi", "pop mie", "sarden", "kornet", "nugget", "fiesta", "so good", "sosis", "dimsum", "seblak", "roti", "bakso", "abon", "la fonte", "spaghetti", "macaroni"],
    "Minuman": ["susu", "ultra", "indomilk", "cimory", "bear brand", "yakult", "dancow", "kopi", "teh", "air", "aqua", "minerale", "sirup", "coca-cola", "sprite", "fanta", "minuman", "jus", "buavita", "hydro", "pocari", "galon", "vit", "le minerale", "nestle", "hydrococo", "c1000", "point coffee", "sinde", "pristine", "extrajoss", "healthy shoot"],
    "Kamar & Kebersihan": ["sabun", "lifebuoy", "lux", "biore", "dettol", "shampo", "pantene", "clear", "sunsilk", "pasta gigi", "pepsodent", "deterjen", "rinso", "pewangi", "molto", "sunlight", "pembersih", "wipol", "vixal", "stella", "bayclean", "soklin", "daia", "downy", "sikat", "odol", "kamper", "bagus", "deodorant", "rexona", "body wash", "sabun mandi"],
    "Kesehatan": ["nyamuk", "hit", "baygon", "vape", "autan", "tisu", "paseo", "nice", "telon", "kayu putih", "vitamin", "enervon", "tolak angin", "bodrex", "panadol", "promag", "betadine", "diapers", "pembalut", "charm", "laurier", "masker", "handsanitizer", "sweety", "mamypoko", "merries", "popok", "lotion", "cleanser", "serum", "body mist", "hair color", "skincare", "pomade", "parfum", "cologne", "sunscreen", "facial wash", "micellar", "toner", "moisturizer", "bedak", "lipstik", "lip balm", "garnier"],
    "Snack": ["biskuit", "roma", "khong guan", "keripik", "chitato", "japota", "kusuka", "qtela", "kacang", "garuda", "cokelat", "coklat", "silverqueen", "beng beng", "oreo", "pocky", "tango", "snack", "wafer", "permen", "kopiko", "yupi", "choki", "taro", "lays", "es krim", "ice cream", "walls", "campina", "aice", "kuaci", "assorted legend", "mayasi", "kukis", "bagelen"],
}


def clean_price(raw: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Ekstrak harga dari raw text.
    Returns (normal_price, promo_price).
    - Jika ada pola "Rp X → Rp Y" atau "Rp X - Rp Y", returns (X, Y)
    - Jika ada "Promo Rp Y" tanpa harga normal, returns (None, Y)
    - Jika hanya satu harga, returns (None, price) atau (price, None)
    """
    if not raw:
        return None, None

    # Hapus harga satuan (contoh: "Rp 1.000 / Liter" atau "Rp 1.200 / 100 gr")
    raw = re.sub(r'Rp\s*[\d\.]+\s*/\s*\d*\s*(?:liter|l|ml|gr|g|pcs|kg|m)\b', '', raw, flags=re.IGNORECASE)

    # Cek apakah ini harga promo (ada kata "promo" atau "hemat")
    is_promo_text = "promo" in raw.lower() or "hemat" in raw.lower()

    # 0. Cari pola hemat.id dengan diskon: "Diskon X%, Harga Promo RpY, Harga Normal RpZ"
    m_hemat_disc = re.search(r'Diskon\s*(\d+)\s*%.*?Harga Promo\s*Rp\s*([\d\.]+).*?Harga Normal\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE | re.DOTALL)
    if m_hemat_disc:
        normal_clean = re.sub(r'[^\d]', '', m_hemat_disc.group(3))
        promo_clean = re.sub(r'[^\d]', '', m_hemat_disc.group(2))
        normal_int = int(normal_clean) if normal_clean else None
        promo_int = int(promo_clean) if promo_clean else None
        return normal_int, promo_int

    # 1. Cari pola dual-price: "Rp X → Rp Y" atau "Rp X - Rp Y" (harga normal → harga promo)
    m_dual = re.search(r'Rp\s*([\d\.]+)\s*[→\-]\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_dual:
        normal_clean = re.sub(r'[^\d]', '', m_dual.group(1))
        promo_clean = re.sub(r'[^\d]', '', m_dual.group(2))
        normal_int = int(normal_clean) if normal_clean else None
        promo_int = int(promo_clean) if promo_clean else None
        return normal_int, promo_int

    # 1b. Cari pola hemat.id: "Diskon X%, Harga Promo RpY, Harga Normal RpZ"
    m_hemat = re.search(r'Harga Promo\s*Rp\s*([\d\.]+).*?Harga Normal\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_hemat:
        promo_clean = re.sub(r'[^\d]', '', m_hemat.group(1))
        normal_clean = re.sub(r'[^\d]', '', m_hemat.group(2))
        promo_int = int(promo_clean) if promo_clean else None
        normal_int = int(normal_clean) if normal_clean else None
        return normal_int, promo_int

    # 1c. Cari pola "Harga Promo RpY, Harga Normal RpZ" (tanpa kata Diskon)
    m_hemat2 = re.search(r'Harga Promo\s*Rp\s*([\d\.]+).*?Harga Normal\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_hemat2:
        promo_clean = re.sub(r'[^\d]', '', m_hemat2.group(1))
        normal_clean = re.sub(r'[^\d]', '', m_hemat2.group(2))
        promo_int = int(promo_clean) if promo_clean else None
        normal_int = int(normal_clean) if normal_clean else None
        return normal_int, promo_int

    # 2. Cari pola "Promo RpX.XXX" atau "Harga Promo RpX.XXX"
    m_promo = re.search(r'(?:Promo)\s*Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_promo:
        promo_clean = re.sub(r'[^\d]', '', m_promo.group(1))
        if promo_clean:
            promo_int = int(promo_clean)
            return None, promo_int

    # 3. Cari satu harga "RpX.XXX" saja
    m_rp = re.search(r'Rp\s*([\d\.]+)', raw, re.IGNORECASE)
    if m_rp:
        cleaned = re.sub(r'[^\d]', '', m_rp.group(1))
        if cleaned:
            price = int(cleaned)
            if price > 10000000:
                for i in [5, 6, 7]:
                    if len(cleaned) >= i:
                        possible_price = int(cleaned[-i:])
                        if 1000 <= possible_price <= 10000000:
                            return None, possible_price
                if len(cleaned) >= 6:
                    return None, int(cleaned[-6:])
            if 0 < price < 1000:
                return None, price * 1000
            return None, price

    # 4. Fallback: ambil semua angka
    raw_no_disc = re.sub(r'Diskon\s*\d+\s*%', '', raw, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^\d]", "", raw_no_disc)

    if not cleaned:
        return None, None

    price = int(cleaned)
    if price > 10000000:
        for i in [5, 6, 7]:
            if len(cleaned) >= i:
                possible_price = int(cleaned[-i:])
                if 1000 <= possible_price <= 10000000:
                    return None, possible_price
        if len(cleaned) >= 6:
            return None, int(cleaned[-6:])
    if 0 < price < 1000:
        return None, price * 1000
    return None, price


def format_price(price_int: int) -> str:
    return f"Rp {price_int:,.0f}".replace(",", ".")


def fetch_page(url: str) -> Optional[BeautifulSoup]:
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception:
            time.sleep(1)
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


def scrape_product_detail(url: str, session: requests.Session) -> dict:
    import re
    result = {
        "promo_start_date": "",
        "promo_end_date": "",
        "area_exclusions": "",
        "unit_price_label": ""
    }
    if not url:
        return result
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        page_text = soup.get_text(" ", strip=True)

        mulai_m = re.search(r'Berlaku Mulai\s*[:\s]+(\d+\s+\w+\s+\d+)', page_text)
        sampai_m = re.search(r'Berlaku Sampai\s*[:\s]+(\d+\s+\w+\s+\d+)', page_text)
        if mulai_m:   result["promo_start_date"] = mulai_m.group(1).strip()
        if sampai_m:  result["promo_end_date"]   = sampai_m.group(1).strip()

        area_m = re.search(r'Berlaku di\s*[:\s]+(.+?)(?:\n|$)', page_text)
        if area_m: result["area_exclusions"] = area_m.group(1).strip()[:200]

        unit_m = re.search(r'Harga Promo\s*[:\s]*Rp[\d\.]+\s*\(([^)]+)\)', page_text)
        if unit_m: result["unit_price_label"] = unit_m.group(1).strip()
    except Exception:
        pass
    return result


def scrape_retailer(slug: str, label: str, max_pages: int = 30) -> List[Dict]:
    results = []
    prev_count = 0
    progress_log = f"[{label}]"
    
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}/katalog-{slug}/"
        else:
            url = f"{BASE_URL}/katalog-{slug}/?page={page}"
            
        soup = fetch_page(url)
        if not soup:
            progress_log += f" | Halaman {page}: 0 item (gagal fetch)"
            break

        time.sleep(random.uniform(0.5, 1.5))

        retailer_slug_bg = f"bg-{slug}"
        cards = soup.select(f"div.item.{retailer_slug_bg}")
        if not cards:
            cards = soup.select("div.item")
        
        if not cards:
            progress_log += f" | Halaman {page}: 0 item (berhenti)"
            break

        page_results = []
        area_tags = ["Ciwaruga", "Sarijadi", "Gegerkalong"]
        for card in cards:
            try:
                link_tag = card if card.name == "a" else card.select_one("a")
                if not link_tag:
                    continue

                title_el = link_tag.select_one("div.title")
                if not title_el:
                    title_el = link_tag.select_one(".title")
                if not title_el:
                    continue
                brand_el = title_el.select_one("div.brand")
                if brand_el:
                    brand_el.extract()
                item_name = title_el.get_text(strip=True)

                normal_price = None
                promo_price = None
                raw_price = ""
                desc_el = link_tag.select_one("div.desc")
                if not desc_el:
                    desc_el = link_tag.select_one(".desc")
                if desc_el:
                    raw_price = desc_el.get_text(" ", strip=True)
                    normal_price, promo_price = clean_price(raw_price)

                # Extract regional price (Luar Jawa)
                regional_match = re.search(r'Luar Jawa[,.]?\s*Rp\s*([\d\.]+)', raw_price, re.IGNORECASE)
                regional_price = int(re.sub(r'[^\d]', '', regional_match.group(1))) if regional_match else None

                # Extract multi-region price (Luar Jawa, Bali, Lombok)
                multi_match = re.search(r'Luar Jawa,\s*Bali,\s*Lombok[,.]?\s*Rp\s*([\d\.]+)', raw_price, re.IGNORECASE)
                multi_region_price = int(re.sub(r'[^\d]', '', multi_match.group(1))) if multi_match else None

                if not item_name or promo_price is None: continue

                image_url = ""
                img_el = link_tag.select_one("div.img img")
                if not img_el:
                    img_el = link_tag.select_one(".img img")
                if img_el:
                    image_url = img_el.get("data-src") or img_el.get("src", "")
                    if image_url.startswith("//"):
                        image_url = "https:" + image_url
                    elif image_url.startswith("/"):
                        image_url = BASE_URL + image_url

                category = classify_product(item_name)
                if category is None:
                    continue  # skip products that don't match any grocery category

                is_promo = (normal_price is not None and promo_price is not None and normal_price > promo_price)
                has_discount_badge = bool(link_tag.select_one('[class*="discount"], [class*="promo"], [class*="sale"]'))
                is_promo = is_promo or has_discount_badge
                ts_scrape = datetime.now().isoformat()

                str_to_hash = image_url if image_url else item_name
                img_hash = hashlib.md5(str_to_hash.encode()).hexdigest()[:8]
                safe_name = re.sub(r'[^a-z0-9]', '_', item_name.lower())[:20]
                prod_id = f"{label.lower()}|{safe_name}|{img_hash}"
                search_vector = f"{item_name} {label} {' '.join(area_tags)}".lower()

                if is_promo:
                    harga_normal = normal_price
                    harga_promo = promo_price
                    diskon_persen = round(100 * (normal_price - promo_price) / normal_price, 1)
                    perubahan_harga = max(0, normal_price - promo_price)
                else:
                    harga_normal = normal_price if normal_price is not None else promo_price
                    harga_promo = promo_price
                    diskon_persen = 0.0
                    perubahan_harga = 0

                jenis_harga = "PROMO" if diskon_persen > 0 else "REGULER"

                promo_date_el = link_tag.select_one('.promo-date')
                promo_end_date = promo_date_el.get_text(strip=True) if promo_date_el else ""

                area_el = link_tag.select_one('.deals-area-custom')
                area_berlaku = area_el.get_text(strip=True) if area_el else ""

                promo_type_el = link_tag.select_one('.deals-desc-custom.content-more')
                promo_type = promo_type_el.get_text(strip=True) if promo_type_el else ""

                req_el = link_tag.select_one('.deals-req')
                promo_requirements = req_el.get_text(strip=True) if req_el else ""

                detail_url = link_tag.get("href", "")
                if detail_url and not detail_url.startswith("http"):
                    detail_url = BASE_URL + detail_url

                unit_el = link_tag.select_one('.deals-unit-custom')
                unit_price = unit_el.get_text(strip=True) if unit_el else ""

                page_results.append({
                    "id": prod_id, "timestamp_scrape": ts_scrape,
                    "nama_produk": item_name.strip().title(), "brand_toko": label,
                    "nama_cabang": label, "kategori": category,
                    "area_tags": area_tags, "harga_normal": harga_normal,
                    "harga_promo": harga_promo, "diskon_persen": diskon_persen,
                    "perubahan_harga": perubahan_harga, "jenis_harga": jenis_harga,
                    "periode_promo": "", "display_harga": format_price(harga_promo),
                    "image_url": image_url, "logo_url": "", "search_vector": search_vector,
                    "promo_end_date": promo_end_date, "area_berlaku": area_berlaku,
                    "promo_type": promo_type, "promo_requirements": promo_requirements,
                    "unit_price": unit_price, "regional_price": regional_price,
                    "multi_region_price": multi_region_price, "detail_url": detail_url
                })
            except Exception as e:
                print(f"[ERROR] Card processing failed: {e}")
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                continue

        results.extend(page_results)
        progress_log += f" | Halaman {page}: {len(page_results)} item"
        if len(page_results) == 0:
            progress_log += " (berhenti)"
            break
        if prev_count > 0 and len(page_results) < 0.3 * prev_count:
            progress_log += f" (drop, berhenti - dari {prev_count} ke {len(page_results)})"
            break
        prev_count = len(page_results)

        if page < max_pages:
            time.sleep(1.0)
            
    print(progress_log)
    return results


def run_scraper() -> Tuple[List[Dict], List[str]]:
    all_items = []
    seen_products = {}  # key: (normalized_name, image_url) -> best product
    errors = []

    # Scrape each retailer
    for url_slug, label in TARGET_RETAILERS.items():
        try:
            items = scrape_retailer(url_slug, label, max_pages=30)
            if items:
                print(f"[DEBUG] {label}: got {len(items)} items")

            # Deduplicate: keep best price per unique product
            for item in items:
                norm_name = item.get("nama_produk", "").strip().lower()
                norm_name = " ".join(norm_name.split())
                key = (norm_name, item.get("image_url", ""))

                if key in seen_products:
                    existing = seen_products[key]
                    existing_promo = existing.get("harga_promo", 0) or 0
                    item_promo = item.get("harga_promo", 0) or 0
                    if item_promo < existing_promo:
                        seen_products[key] = item
                else:
                    seen_products[key] = item

        except Exception as e:
            err_msg = f"Error scraping {label}: {e}"
            print(err_msg)
            errors.append(err_msg)

    all_items = list(seen_products.values())
    print(f"[DEBUG] Unique products after dedup: {len(all_items)}")

    needs_detail = [
        (item["nama_produk"], item.get("detail_url", ""), item)
        for item in all_items
        if not item.get("promo_end_date") and item.get("detail_url")
    ]
    if needs_detail:
        detail_session = requests.Session()
        detail_session.headers.update({"User-Agent": "Mozilla/5.0"})
        enriched = 0
        for nama, url, item in needs_detail:
            d = scrape_product_detail(url, detail_session)
            if d["promo_start_date"]:  item["promo_start_date"]  = d["promo_start_date"]
            if d["promo_end_date"]:     item["promo_end_date"]     = d["promo_end_date"]
            if d["area_exclusions"]:    item["area_exclusions"]   = d["area_exclusions"]
            if d["unit_price_label"]:   item["unit_price_label"]  = d["unit_price_label"]
            if any(d.values()): enriched += 1
            time.sleep(random.uniform(0.4, 0.9))
        print(f"[DEBUG] Detail enrichment: {enriched}/{len(needs_detail)} items updated")

    return all_items, errors


def get_demo_data() -> List[Dict]:
    return []


if __name__ == "__main__":
    data, errors = run_scraper()
    if not data:
        print("Scraping gagal, pakai demo data.")
        data = get_demo_data()
    print(f"Total: {len(data)} item")
    if errors:
        print(f"Errors occurred: {errors}")
    saved = data_manager.write_local_data(data)
    print(f"[DEBUG] Saved to file: {saved}")
