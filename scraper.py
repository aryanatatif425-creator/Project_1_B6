import time
import requests
import json
from bs4 import BeautifulSoup

BASE_URL = 'https://hemat.id'

# Daftar retailer target sesuai dengan SKPL & dokumen tugas
TARGET_RETAILERS = {
    'superindo': 'Superindo',
    'alfamart': 'Alfamart',
    'indomaret': 'Indomaret',
    'borma': 'Borma'
}

def get_soup(url):
    """Ambil HTML dari URL dan kembalikan sebagai objek BeautifulSoup."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def ekstrak_satu_produk(tag_produk, label_retailer):
    """Ekstrak semua field dari satu elemen produk HTML secara aman."""
    data = {}
    
    el_nama = tag_produk.find('p', class_='product-name') or tag_produk.find('div', class_='title')
    data['item_name'] = el_nama.get_text(strip=True) if el_nama else "Produk Tanpa Nama"
    data['retailer_brand'] = label_retailer
    data['category'] = "Kebutuhan Harian"
    
    el_promo = tag_produk.find('span', class_='sale-price') or tag_produk.find('span', class_='price')
    if el_promo:
        teks_promo = el_promo.get_text(strip=True)
        angka_promo = teks_promo.replace('Rp', '').replace('.', '').replace(',', '').strip()
        data['harga_promo'] = int(angka_promo) if angka_promo.isdigit() else 0
    else:
        data['harga_promo'] = 0
    
    data['price_int'] = data['harga_promo']

    el_normal = tag_produk.find('span', class_='original-price') or tag_produk.find('span', class_='old-price')
    if el_normal:
        teks = el_normal.get_text(strip=True)
        angka = teks.replace('Rp', '').replace('.', '').replace(',', '').strip()
        data['harga_normal'] = int(angka) if angka.isdigit() else data['harga_promo']
    else:
        data['harga_normal'] = data['harga_promo'] # Jika tidak ada harga coret, samakan dengan harga promo

    if data['harga_normal'] > 0 and data['harga_normal'] > data['harga_promo']:
        selisih = data['harga_normal'] - data['harga_promo']
        data['diskon_persen'] = round((selisih / data['harga_normal']) * 100, 1)
    else:
        data['diskon_persen'] = 0.0

    el_periode = tag_produk.find('p', class_='promo-period') or tag_produk.find('div', class_='period')
    if el_periode:
        data['periode_promo'] = el_periode.get_text(strip=True)
    else:
        data['periode_promo'] = "Periode tidak tersedia"

    el_jenis = tag_produk.find('span', class_='price-type') or tag_produk.find('span', class_='label')
    if el_jenis:
        data['jenis_harga'] = el_jenis.get_text(strip=True).upper()
    else:
       
        data['jenis_harga'] = "PROMO" if data['diskon_persen'] > 0 else "REGULER"
        
    data['display_harga'] = f"Rp {data['harga_promo']:,}".replace(',', '.')
    data['image_url'] = "https://placehold.co/200x200?text=" + data['item_name'].split()[0]
    
    return data

def scrape_retailer(slug, label):
    """Mengeksplor halaman daftar katalog berdasarkan retailer slug."""
    url = f"{BASE_URL}/katalog/{slug}/"
    soup = get_soup(url)
    
    products = []
    
    items = soup.find_all("div", class_="product-card") or soup.find_all("div", class_="item")
    
    
    if not items:
        div_items = soup.find_all("div")
        for item in div_items:
            if "Rp" in item.get_text():
    
                if len(item.get_text()) < 300 and item.find('span'):
                    items.append(item)
                    
    for item in items[:10]: 
        try:
            produk = ekstrak_satu_produk(item, label)
            if produk['harga_promo'] > 0:
                products.append(produk)
        except Exception:
            continue
            
    return products

def run_scraper():
    """Fungsi Utama: Menjalankan scraping untuk semua retailer (Digunakan oleh Admin Tool)."""
    all_items = []
    errors = []
    
    print("\n" + "="*50)
    print("Mengeksekusi Radar Promo Core Scraper Engine...")
    print("="*50)
    
    for slug, label in TARGET_RETAILERS.items():
        try:
            print(f"- Menscraping data katalog: {label}...")
            items = scrape_retailer(slug, label)
            all_items.extend(items)
            print(f"  --> Berhasil mengambil {len(items)} item dari {label}.")
        except requests.exceptions.ConnectionError:
            msg = f"{label}: Gagal terhubung ke internet (Connection Error)."
            print(f"  X {msg}")
            errors.append(msg)
        except requests.exceptions.Timeout:
            msg = f"{label}: Koneksi timeout (Server terlalu lama merespon)."
            print(f"  X {msg}")
            errors.append(msg)
        except requests.exceptions.HTTPError as e:
            msg = f"{label}: HTTP Error ({e.response.status_code})."
            print(f"  X {msg}")
            errors.append(msg)
        except Exception as e:
            msg = f"{label}: Error tidak dikenal ({str(e)})."
            print(f"  X {msg}")
            errors.append(msg)
            
    
    print("\n" + "="*50)
    print(f"Hasil Akhir Scraping: {len(all_items)} item sukses dikumpulkan.")
    if errors:
        print(f"Terjadi Kendala! {len(errors)} Retailer Gagal Diproses:")
        for err in errors:
            print(f"  ! {err}")
    print("="*50)
    
    return all_items, errors

def get_demo_data():
    """Mengembalikan data demo terstruktur (Fallback Data) jika scraping gagal total."""
    return [
        {
            "item_name": "Beras 365 Pulen Wangi 5kg",
            "retailer_brand": "Superindo",
            "category": "Sembako",
            "price_int": 72900,
            "harga_normal": 85000,
            "harga_promo": 72900,
            "diskon_percent": 14.1,
            "jenis_harga": "PROMO",
            "periode_promo": "14-20 Mei 2026",
            "display_harga": "Rp 72.900",
            "image_url": "https://placehold.co/200x200?text=Beras"
        },
        {
            "item_name": "Minyak Goreng Sania 2L",
            "retailer_brand": "Alfamart",
            "category": "Sembako",
            "price_int": 35500,
            "harga_normal": 38000,
            "harga_promo": 35500,
            "diskon_percent": 6.6,
            "jenis_harga": "PROMO",
            "periode_promo": "14-20 Mei 2026",
            "display_harga": "Rp 35.500",
            "image_url": "https://placehold.co/200x200?text=Minyak"
        },
        {
            "item_name": "Gula Pasir Gulaku 1kg",
            "retailer_brand": "Indomaret",
            "category": "Sembako",
            "price_int": 16500,
            "harga_normal": 16500,
            "harga_promo": 16500,
            "diskon_percent": 0.0,
            "jenis_harga": "REGULER",
            "periode_promo": "14-20 Mei 2026",
            "display_harga": "Rp 16.500",
            "image_url": "https://placehold.co/200x200?text=Gula"
        },
        {
            "item_name": "Susu UHT Ultra Milk 1L",
            "retailer_brand": "Borma",
            "category": "Susu & Olahan",
            "price_int": 17400,
            "harga_normal": 19500,
            "harga_promo": 17400,
            "diskon_percent": 10.7,
            "jenis_harga": "PROMO",
            "periode_promo": "12-25 Mei 2026",
            "display_harga": "Rp 17.400",
            "image_url": "https://placehold.co/200x200?text=Susu"
        },
        {
            "item_name": "Indomie Goreng Spesial 85g",
            "retailer_brand": "Indomaret",
            "category": "Mie Instan",
            "price_int": 3100,
            "harga_normal": 3500,
            "harga_promo": 3100,
            "diskon_percent": 11.4,
            "jenis_harga": "PROMO",
            "periode_promo": "14-20 Mei 2026",
            "display_harga": "Rp 3.100",
            "image_url": "https://placehold.co/200x200?text=Indomie"
        }
    ]

if __name__ == "__main__":
    
    hasil, errs = run_scraper()
    if not hasil:
        print("\nMenggunakan Fallback Data Demo...")
        hasil = get_demo_data()
        
    with open("data_promo.json", "w", encoding="utf-8") as f:
        json.dump(hasil, f, ensure_ascii=False, indent=2)
    print(f"\nUji Coba Berhasil. {len(hasil)} produk tersimpan di 'data_promo.json'.")