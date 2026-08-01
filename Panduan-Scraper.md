# Panduan Scraper — Radar Promo

> **Catatan Penting:** Scraper hanya dapat dijalankan dari **kode sumber** (source code), bukan dari file `.exe` yang didistribusikan. Jika Anda hanya menerima `RadarPromo.exe`, Anda tidak dapat menjalankan scraper sendiri — hubungi developer untuk update data.

---

## Login Admin (untuk Developer)

Jika Anda memiliki akses ke kode sumber:

```
Username: admin
Password:  <ganti_dengan_password_admin>
```

> Catatan: Nilai password diambil dari environment variable `RADAR_ADMIN_PASSWORD` (lihat .env.example).

Login melalui menu Admin di dalam aplikasi.

---

## Cara Kerja Scraper

File utama: `scraper.py`

Scraper menarik data promo dari **hemat.id** untuk retail berikut:
- Alfamart
- Indomaret
- Griya (ex Yomart)

### Alur Scraper

```
scraper.py
  └─> scrape_allRetailers()
        └─> scrape_retailer(retailer_name)
              └─> fetch_page(url) → BeautifulSoup
                    └─> extract_product_cards()
                          └─> extract_product_details(nama, harga, lokasi, foto_url)
                                └─> data_manager.add_product()
```

Data hasil scraper langsung disimpan ke `data_promo.json` via `data_manager.add_product()`.

---

## Menjalankan Scraper (Developer)

### Prasyarat

Pastikan semua dependency terinstall:

```bash
pip install -r requirements.txt
```

Dependencies yang dibutuhkan scraper:
- `requests`
- `beautifulsoup4`
- `Pillow` (untuk proses gambar)

### Menjalankan dari Terminal

```bash
cd D:\Ujicoba
python scraper.py
```

Scraper akan:
1. Iterasi semua kategori di `hemat.id`
2. Ambil data promo untuk setiap retailer
3. Simpan ke `data_promo.json`

### Menjalankan via Aplikasi (Admin Tool)

1. Buka aplikasi RadarPromo
2. Login ke menu Admin
3. Pilih menu **Scraping** atau **Update Data**
4. Klik tombol **Jalankan Scraper**

---

## Konfigurasi Scraper

### Target Retailer

Di `scraper.py` baris 25-29:

```python
TARGET_RETAILERS = {
    "alfamart": "Alfamart",
    "indomaret": "Indomaret",
    "yogya": "Griya",
}
```

Untuk menambahkan retailer baru, edit dictionary ini.

### Kategori yang Diambil

Di `scraper.py` baris 32-48:

```python
NATIVE_CATEGORIES = [
    "makanan-minuman",
    "makanan-segar",
    "bahan-masakan",
    "kesehatan-kecantikan",
    ...
]
```

Hapus atau tambahkan kategori sesuai kebutuhan.

---

## File Output

| File | Lokasi | Format |
|------|--------|--------|
| `data_promo.json` | `D:\Ujicoba\data_promo.json` | JSON array |

### Struktur Data `data_promo.json`

```json
[
  {
    "nama_produk": "Indomie Goreng",
    "harga_asal": 3500,
    "harga_promo": 2500,
    "nama_cabang": "Alfamart Jalan Sudirman",
    "latitude": -6.1234,
    "longitude": 106.5678,
    "foto_url": "https://...",
    "tanggal_promo": "2026-07-13",
    "sumber": "alfamart",
    "kategori": "makanan-minuman"
  }
]
```

---

## Troubleshooting

### Error: `ConnectionError` / timeout

- Cek koneksi internet
- hemat.id mungkin membatasi request terlalu banyak
- Scraper sudah ada jeda antar request (`time.sleep()`) untuk avoid rate limit

### Error: `BeautifulSoup` parse gagal

- Struktur HTML hemat.id mungkin berubah
- Update selector di fungsi `extract_product_cards()` dan `extract_product_details()`

### Data tidak muncul di aplikasi

- Pastikan `data_promo.json` di-refresh setelah scraping selesai
- Restart aplikasi atau klik tombol Refresh di aplikasi

---

## Scheduling Otomatis (Optional)

Untuk scrape otomatis setiap jam, gunakan Windows Task Scheduler:

```bash
# Buat file batch
echo python "D:\Ujicoba\scraper.py" >> scrape.bat

# Atau jalankan via Python langsung
python -m schedule --interval 3600 -- python scraper.py
```

> Gunakan library `schedule` atau `APScheduler` untuk scheduling dalam Python.
