# Panduan Pengguna — Radar Promo

## Requirement Sistem

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| OS | Windows 10 64-bit | Windows 11 |
| RAM | 4 GB | 8 GB |
| Storage | 300 MB | 500 MB |

> **Catatan:** Tidak perlu install Python, .NET, atau dependency lainnya. Ini adalah file `.exe` standalone.

---

## Installation

### Langkah 1: Salin File

Salin file `RadarPromo.exe` ke lokasi yang diinginkan, contoh:
- `Desktop\`
- `D:\Aplikasi\`
- `C:\Program Files\RadarPromo\`

### Langkah 2: Jalankan

Double-click `RadarPromo.exe`

> **Catatan:** Saat pertama kali dibuka, Windows Defender mungkin menampilkan peringatan. Klik **"Info selengkapnya"** → **"Tetap jalankan"**. Ini normal karena `.exe` tidak signed dengan certificate.

---

## Fitur Utama

### 1. Halaman Utama (Home)

Menampilkan daftar promo produk dengan filter:
- **Kategori** — filter berdasarkan kategori produk
- **Cari** — cari produk berdasarkan nama
- **Urutkan** — harga termurah, rating tertinggi, dll

### 2. Lokasi Promo (Peta)

Menampilkan lokasi retailer pada peta interaktif. Klik marker untuk melihat detail promo di lokasi tersebut.

### 3. Rekomendasi

Kartu-kartu promo yang dikurasi manual oleh admin. Setiap kartu menampilkan:
- Nama tempat
- Alamat
- Menu / promo utama
- Range harga
- Rating
- Foto

Klik kartu untuk melihat detail lengkap.

### 4. Form Crowdsourcing

Pengguna dapat menambahkan informasi promo baru melalui tab Crowdsourcing. Data yang dikirim akan diupload ke Google Sheets.

### 5. Admin Panel

Akses untuk admin:
- **Username:** `admin`
- **Password:** `<ganti_dengan_password_admin>`

Fitur admin:
- Tambah / edit / hapus promo
- Lihat statistik

---

## Cara Penggunaan

### Mencari Promo

1. Buka aplikasi → tab **Home**
2. Ketik nama produk di kolom **Cari**
3. Atau pilih **Filter** untuk membatasi kategori
4. Klik produk untuk melihat detail

### Melihat Lokasi Promo

1. Buka tab **Lokasi**
2. Klik marker di peta untuk melihat detail
3. Zoom in/out dengan scroll atau tombol +/- di peta

### Submit Promo Baru (Crowdsourcing)

1. Buka tab **Crowdsourcing** / **Kontributor**
2. Isi formulir:
   - Nama tempat
   - Alamat
   - Menu / promo
   - Range harga (min / max)
   - Rating
   - Deskripsi
   - Upload foto (opsional)
3. Klik **Kirim**
4. Toast "Berhasil" akan muncul jika submit sukses

### Login Admin

1. Klik tombol **Admin** di navbar
2. Masukkan username dan password
3. Setelah login, menu admin akan terlihat di navbar

---

## Sinkronisasi Cloud

Aplikasi mendukung sinkronisasi data ke **Google Sheets**:

- Data promo dibaca dari Google Sheets saat aplikasi start
- Data crowdsourcing dikirim ke Google Sheets saat user submit form
- Jika offline, aplikasi menggunakan **cache lokal** (`data_promo_cache.json`) — data tetap bisa dilihat

---

## Troubleshooting

### Aplikasi tidak mau terbuka

1. Pastikan Windows Defender mengizinkan `.exe` — klik **"Tetap jalankan"** jika ada peringatan
2. Disable antivirus sementara jika yakin file aman
3. Pastikan file `RadarPromo.exe` tidak di-renamed atau dipindahkan saat sedang berjalan

### Data promo kosong saat pertama buka

1. Pastikan koneksi internet aktif saat pertama kali buka aplikasi
2. Jika offline, aplikasi tetap bisa dibuka dan menampilkan data dari cache lokal
3. Buka **Admin** → jalankan **Scraper** untuk download data terbaru (memerlukan koneksi internet)

### Foto tidak muncul

1. Cek koneksi internet — foto dimuat dari URL eksternal
2. Matikan VPN jika ada

### Aplikasi terasa lambat

1. Pastikan RAM cukup (minimal 4GB)
2. Tutup aplikasi lain yang memakan banyak RAM

---

## Uninstall

Hapus file `RadarPromo.exe` dari lokasi penyimpanan.

Tidak ada registry entries atau file tersembunyi.

---

## Lisensi

Proyek ini adalah aplikasi interno. Hubungi admin untuk pertanyaan lebih lanjut.
