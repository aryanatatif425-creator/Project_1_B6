\# Spesifikasi Kebutuhan Perangkat Lunak Radar Promo v2.0  

\*\*Aplikasi Desktop Agregator Diskon Kebutuhan Pokok Berbasis Web Scraping untuk Optimalisasi Anggaran Mahasiswa di Kawasan Ciwaruga dan Sekitarnya\*\*



\---



\## Daftar Isi

\- \[BAB 1 : Pendahuluan](#bab-1--pendahuluan)

&#x20; - \[1.1 Tujuan Dokumen](#11-tujuan-dokumen)

&#x20; - \[1.2 Ruang Lingkup Produk](#12-ruang-lingkup-produk)

&#x20; - \[1.3 Perbedaan Utama dengan Website Hemat.id](#13-perbedaan-utama-dengan-website-hematid)

\- \[BAB 2 : Deskripsi Umum](#bab-2--deskripsi-umum)

&#x20; - \[2.1 Arsitektur Sistem](#21-arsitektur-sistem)

&#x20; - \[2.2 Fungsi Produk Utama](#22-fungsi-produk-utama)

&#x20; - \[2.3 Karakteristik Pengguna](#23-karakteristik-pengguna)

\- \[BAB 3 : Persyaratan Fungsional](#bab-3--persyaratan-fungsional-user-stories--acceptance-criteria)

\- \[BAB 4 : Persyaratan Antarmuka Eksternal](#bab-4--persyaratan-antarmuka-eksternal)

&#x20; - \[4.1 Antarmuka Perangkat Lunak (Sumber Data)](#41-antarmuka-perangkat-lunak-sumber-data)

&#x20; - \[4.2 Antarmuka Pengguna (UI)](#42-antarmuka-pengguna-ui)

&#x20;   - \[4.2.1 Tata Letak Sisi Pengguna](#421-tata-letak-sisi-pengguna)

&#x20;   - \[4.2.2 Deskripsi Halaman](#422-deskripsi-halaman)

\- \[BAB 5 : Persyaratan Data (Model Data)](#bab-5--persyaratan-data-model-data)

&#x20; - \[5.1 Skema data\_promo.json](#51-skema-data\_promojson-list-of-dictionary)

&#x20; - \[5.2 Skema rekomendasi.json](#52-skema-rekomendasijson-list-of-dictionary)

\- \[BAB 6 : Atribut Kualitas](#bab-6--atribut-kualitas)

\- \[BAB 7 : Asumsi dan Batasan](#bab-7--asumsi-dan-batasan)

&#x20; - \[7.1 Asumsi](#71-asumsi)

&#x20; - \[7.2 Batasan](#72-batasan)

\- \[Pembagian Role dan Deskripsi Tugas](#pembagian-role-dan-deskripsi-tugas)



\---



\## BAB 1 : Pendahuluan



\### 1.1 Tujuan Dokumen

Dokumen ini mendefinisikan persyaratan fungsional dan non-fungsional untuk aplikasi desktop Radar Promo v2.0. Dokumen ini menjadi kontrak antara tim pengembang dan pemangku kepentingan (dosen penguji) tentang apa yang akan dibangun.



\### 1.2 Ruang Lingkup Produk

Radar Promo adalah aplikasi desktop offline-first dengan cloud sync yang berfungsi sebagai agregator informasi promo kebutuhan pokok dan rekomendasi tempat makan berbasis crowdsourcing khusus untuk mahasiswa di Kawasan Politeknik Negeri Bandung. Aplikasi ini dibangun dengan PySide6 untuk antarmuka modern, dan memiliki dua mode operasi:



\- \*\*Mode User (Frontend):\*\* Agregator promo kebutuhan pokok dan platform crowdsourcing rekomendasi tempat makan hemat di sekitar kawasan Ciwaruga, Sarijadi, dan Gegerkalong.

\- \*\*Mode Admin (Backend):\*\* Program terpisah yang hanya digunakan oleh administrator untuk memperbarui database promo dari internet dan memantau log aktivitas. Mode ini diakses melalui halaman Pengaturan, bukan melalui dialog saat aplikasi dimulai.



\### 1.3 Perbedaan Utama dengan Website Hemat.id

| Fitur            | Website Hemat.id                | Radar Promo                                                                          |

| ---------------- | ------------------------------- | ------------------------------------------------------------------------------------ |

| Konteks Data     | Data mentah nasional            | Data terkurasi khusus area Polban (Ciwaruga, Sarijadi, Gegerkalong)                  |

| Filter Utama     | Kategori \& Nama Produk          | Area Spesifik (Cabang terdekat)                                                      |

| Fitur Tambahan   | Tidak ada                       | Peta interaktif, Crowdsourcing rekomendasi (+foto), Visualisasi data, Simulasi Anggaran |

| Koneksi          | Harus online                    | Offline-First (bekerja tanpa internet setelah sync)                                  |



\---



\## BAB 2 : Deskripsi Umum



\### 2.1 Arsitektur Sistem

Aplikasi menganut arsitektur \*\*Offline-First\*\* dengan \*Eager Loading\* serta pemisahan tanggung jawab yang ketat (\*Separation of Concerns\*).



\*\*Komponen Cloud (Serverless Backend):\*\*

\- \*\*Google Sheets:\*\* Database pusat yang menyimpan `data\_promo` dan `rekomendasi`.

\- \*\*Google Apps Script Web App:\*\* API endpoint yang menerima data dari aplikasi dan menuliskannya ke Google Sheets, serta melayani permintaan baca data.

\- \*\*ImgBB API:\*\* Layanan hosting gambar gratis untuk menyimpan foto rekomendasi yang diunggah pengguna.



\*\*Aliran Data:\*\*

1\. \*\*Upload Rekomendasi (User):\*\* Aplikasi Viewer mengunggah foto ke ImgBB → Menerima URL dari ImgBB → Mengirim data rekomendasi (termasuk URL foto) ke Google Apps Script → Google Sheets (Sheet `Rekomendasi`) diperbarui.

2\. \*\*Sinkronisasi Promo (Admin):\*\* Admin membuka Dashboard Admin (Tkinter) → Menekan "Sinkronisasi Sekarang" → `scraper.py` menarik data dari hemat.id → Data disimpan ke `data\_promo.json` lokal → Admin menekan "Upload Promo ke Cloud" → Data dikirim ke Google Sheets (Sheet `Promo`) dengan strategi Replace (timpa total).

3\. \*\*Unduh Data (User):\*\* Aplikasi Viewer saat dibuka atau saat pengguna menekan tombol Refresh menarik data terbaru dari Google Sheets (maksimal 100 entri rekomendasi terbaru) dan menyimpannya sebagai cache lokal (file JSON).



\*\*Komponen Aplikasi Lokal:\*\*

\- `scraper.py` – Modul penarik data mentah dari hemat.id (hanya digunakan Admin).

\- `data\_manager.py` – Pengelola data: baca/tulis JSON, Replace Database, pemetaan cabang (Address Book), pengayaan data (`area\_tags`, `search\_vector`), serta komunikasi API dengan Google Sheets dan ImgBB.

\- `engine.py` – Mesin logika: filter area/kategori/toko, pencarian teks (`search\_vector`), pengurutan Timsort, dan fungsi statistik.

\- `gui\_pyqt.py` (MainWindow) – Antarmuka Mode Pengguna berbasis PySide6 dengan QThread, menampilkan peta Leaflet.js melalui `QWebEngineView`.

\- `admin\_tool.py` – Dashboard Admin berbasis Tkinter (sinkronisasi, upload cloud, log viewer).

\- `main.py` – Entry point, langsung membuka Mode Pengguna; menyediakan fungsi `show\_admin\_login()` dari halaman Pengaturan.

\- `image\_loader.py` – Pengunduhan dan caching gambar (produk \& foto rekomendasi).



\### 2.2 Fungsi Produk Utama

| ID  | Fungsi                                                |

| --- | ----------------------------------------------------- |

| F-1 | Akses Admin melalui Halaman Pengaturan                |

| F-2 | Pencarian \& Filter Promo Groceries (Mode User)        |

| F-3 | Peta Interaktif \& Crowdsourcing Rekomendasi (Mode User) |

| F-4 | Visualisasi Data Statistik (Mode User)                |

| F-5 | Simulasi Anggaran \& Keranjang Belanja (Mode User)     |

| F-6 | Dashboard Admin (Scraping, Upload, Log)                |



\### 2.3 Karakteristik Pengguna

| Pengguna           | Mode  | Aktivitas                                                                                   |

| ------------------ | ----- | ------------------------------------------------------------------------------------------- |

| Mahasiswa Polban   | User  | Mencari promo, melihat peta, menambah rekomendasi, melihat statistik, simulasi belanja     |

| Administrator      | Admin | Scraping data promo, upload ke cloud, melihat log aktivitas scraping dan kontribusi rekomendasi |



\---



\## BAB 3 : Persyaratan Fungsional (User Stories \& Acceptance Criteria)



| ID  | Aktor (sebagai) | Keinginan (Saya ingin)                                                                                                         | Manfaat (Sehingga)                                                                                 | Kriteria Penerimaan Utama                                                                                                                                                                                                                                                                                                                                              |

|:----|:---------------|:-------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| F-1 | Administrator  | mengakses alat pemeliharaan data melalui halaman pengaturan setelah masuk ke aplikasi, tanpa mengganggu pengguna biasa.       | keamanan data dan fokus kerja masing-masing peran dapat terjaga.                                   | 1. Aplikasi langsung terbuka dalam Mode Pengguna tanpa dialog awal.<br>2. Pada halaman Pengaturan, terdapat tombol "Masuk sebagai Admin".<br>3. Memilih Admin akan meminta kata sandi. Jika benar, antarmuka berubah menjadi Dashboard Admin (Tkinter).<br>4. Dashboard Admin hanya berisi alat sinkronisasi, upload, dan log.                 |

| F-2 | Mahasiswa      | mencari dan menyaring informasi promo kebutuhan pokok berdasarkan area, kategori, dan kata kunci tertentu.                    | proses pencarian barang dengan harga terbaik dapat dilakukan secara cepat dan tepat sasaran.       | 1. Tab Home menyediakan bilah pencarian, filter area, filter toko, dan tombol kategori.<br>2. Hasil pencarian muncul dalam bentuk kartu produk (foto, nama, cabang, harga).<br>3. Pencarian teks memanfaatkan atribut `search\_vector`.<br>4. Hasil diurutkan menggunakan algoritma Timsort (`list.sort()`).<br>5. Harga normal tercoret jika ada harga promo. Label khusus untuk status PROMO. |

| F-3 | Mahasiswa      | menjelajahi peta interaktif yang menunjukkan lokasi toko resmi serta tempat rekomendasi komunitas, sekaligus berkontribusi menambahkan rekomendasi baru. | saya dapat mempertimbangkan jarak, melihat rekomendasi teman, dan berbagi informasi tempat makan hemat. | 1. Tab Jelajah menampilkan peta penuh OpenStreetMap (via `QWebEngineView`).<br>2. Pin Biru (toko resmi) dan Pin Hijau (rekomendasi) — pin toko yang memiliki promo aktif diberi animasi radar.<br>3. Tombol "+" (Tambah Tempat) di pojok kanan bawah peta membuka \*\*panel samping kanan\*\* (lebar \~350px) berisi form input:<br>\&nbsp;\&nbsp;- Nama Tempat\\\*<br>\&nbsp;\&nbsp;- Alamat (teks lokasi, misal "Ciwaruga, samping Indomaret")\\\* opsional<br>\&nbsp;\&nbsp;- Menu Andalan (opsional)<br>\&nbsp;\&nbsp;- Kisaran Harga\\\*<br>\&nbsp;\&nbsp;- Rating bintang (1-5)\\\*<br>\&nbsp;\&nbsp;- Deskripsi Singkat (opsional)<br>\&nbsp;\&nbsp;- Upload Foto (via ImgBB, dengan pratinjau)<br>\&nbsp;\&nbsp;- Nama Kontributor\\\* (default "Anonim")<br>\&nbsp;\&nbsp;- Koordinat (Latitude/Longitude) yang dapat diisi dengan dua cara: \*\*mengetik manual\*\* atau menggunakan tombol \*\*"Pilih dari Peta"\*\* untuk menjatuhkan pin di peta.<br>4. Data yang dikirim langsung tersinkronisasi ke cloud; pengguna dapat menekan tombol Refresh untuk melihat rekomendasi terbaru. |

| F-4 | Mahasiswa      | melihat ringkasan statistik dan visualisasi data dari promo yang sedang berlangsung.                                         | pengguna dapat mengidentifikasi toko dengan promo terbanyak dan komposisi kategori diskon.         | 1. Tab Statistik menampilkan diagram batang "3 Toko dengan Promo Terbanyak".<br>2. Menampilkan diagram lingkaran komposisi kategori promo.                                                                                                                                                                                                            |

| F-5 | Mahasiswa      | menyusun rencana belanja dalam keranjang virtual dan memantau sisa anggaran bulanan.                                         | pengeluaran dapat terkontrol dan tidak melebihi batas anggaran yang telah ditentukan.              | 1. Ikon Keranjang di header kanan atas sebagai pintasan ke halaman Keranjang.<br>2. Halaman Keranjang menampilkan kartu saldo (dengan fitur sembunyikan).<br>3. Item dengan kontrol kuantitas, total biaya real-time.<br>4. Saldo otomatis bertambah/berkurang.                                                                                          |

| F-6 | Administrator  | mengelola pembaruan data promo melalui proses penarikan data (scraping) dan mengunggahnya ke cloud.                          | data yang diakses pengguna selalu akurat dan terbebas dari informasi usang atau duplikat.          | 1. Dashboard Admin (Tkinter) tidak menampilkan antarmuka belanja.<br>2. Tombol "Sinkronisasi Sekarang" (dengan progress bar).<br>3. Tombol "Upload Promo ke Cloud" (strategi Replace).<br>4. Tersedia Log Viewer untuk memantau aktivitas.                                                                                                              |



\---



\## BAB 4 : Persyaratan Antarmuka Eksternal



\### 4.1 Antarmuka Perangkat Lunak (Sumber Data)

| Sumber         | Tujuan                           | Metode                                              |

| -------------- | -------------------------------- | --------------------------------------------------- |

| hemat.id       | Data promo groceries             | Web Scraping (`requests`, `BeautifulSoup`)          |

| OpenStreetMap  | Ubin peta (tiles)                | HTTP Request (via Leaflet.js di `QWebEngineView`)   |

| Nominatim      | Pencarian koordinat toko (opsional) | HTTP Request (dengan rate limit)                 |

| ImgBB          | Hosting foto rekomendasi         | HTTP POST                                           |



\### 4.2 Antarmuka Pengguna (UI)



\#### 4.2.1 Tata Letak Sisi Pengguna

| Elemen            | Posisi           | Keterangan                                                                                                                                             |

| ----------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |

| Header            | Atas             | Logo \& Nama Aplikasi (kiri), Ikon Keranjang \& bilah pencarian (kanan). Ikon keranjang menjadi pintasan ke halaman Keranjang.                           |

| Area Konten Utama | Tengah (Dinamis) | Menampilkan konten sesuai tab yang sedang aktif: Home, Jelajah, Statistik, Pengaturan.                                                                 |

| Navigasi Bawah    | Bawah            | Empat tab permanen: \*\*Home\*\*, \*\*Jelajah\*\*, \*\*Statistik\*\*, \*\*Pengaturan\*\*.                                                                              |



\#### 4.2.2 Deskripsi Halaman

\- \*\*Halaman Home:\*\* Bilah pencarian, filter area (Ciwaruga, Sarijadi, Gegerkalong), filter toko, tombol kategori, dan grid kartu produk promo (foto, nama, cabang, harga normal tercoret, harga promo, label PROMO).

\- \*\*Halaman Jelajah:\*\* Peta interaktif penuh (via `QWebEngineView`). Menampilkan:

&#x20; - \*\*Pin Biru\*\* untuk toko resmi (dengan animasi radar jika ada promo aktif).

&#x20; - \*\*Pin Hijau\*\* untuk rekomendasi tempat makan dari komunitas.

&#x20; - Tombol \*\*"+"\*\* di pojok kanan bawah peta yang membuka \*\*panel samping kanan\*\* (lebar ±350px) berisi form "Tambah Tempat Rekomendasi". Form menyediakan field: Nama Tempat, Alamat (teks lokasi), Menu Andalan, Kisaran Harga, Rating bintang, Deskripsi Singkat, Upload Foto (dengan pratinjau), Nama Kontributor, serta koordinat (Latitude/Longitude) yang dapat diisi manual atau dengan tombol \*\*"Pilih dari Peta"\*\* (mengaktifkan mode drop pin di peta). Setelah data terkirim, rekomendasi langsung tersimpan di cloud dan muncul setelah Refresh.

\- \*\*Halaman Statistik:\*\* Diagram batang "Top 3 Toko dengan Promo Terbanyak" dan diagram lingkaran komposisi kategori promo.

\- \*\*Halaman Keranjang:\*\* Tidak muncul di navigasi bawah; diakses melalui ikon Keranjang di Header. Menampilkan Kartu Saldo (dengan toggle sembunyikan), daftar item belanja (kuantitas, subtotal), dan total biaya real-time.

\- \*\*Halaman Pengaturan:\*\* Pengaturan personalisasi (Mode Gelap/Terang, Ukuran Font), informasi "About" (nama aplikasi, versi, tim pengembang), dan tombol \*\*"Masuk sebagai Admin"\*\* (meminta kata sandi untuk membuka Dashboard Admin Tkinter).



\---



\## BAB 5 : Persyaratan Data (Model Data)



\### 5.1 Skema data\_promo.json (List of Dictionary)

File `data\_promo.json` berisi array dari objek-objek dengan struktur sebagai berikut:



```json

{

&#x20; "id": "superindo|superindo\_pasteur|beras\_365\_5kg",

&#x20; "timestamp\_scrape": "2026-04-19T10:00:00",

&#x20; "nama\_produk": "Beras 365 Pulen Wangi 5kg",

&#x20; "brand\_toko": "Superindo",

&#x20; "nama\_cabang": "Superindo Pasteur",

&#x20; "kategori": "Sembako",

&#x20; "area\_tags": \["Sarijadi", "Gegerkalong"],

&#x20; "harga\_normal": 85000,

&#x20; "harga\_promo": 72900,

&#x20; "diskon\_persen": 14.1,

&#x20; "perubahan\_harga": -5,

&#x20; "jenis\_harga": "PROMO",

&#x20; "periode\_promo": "14-20 April 2026",

&#x20; "display\_harga": "Rp 72.900",

&#x20; "image\_url": "...",

&#x20; "logo\_url": "...",

&#x20; "search\_vector": "beras 365 pulen wangi 5kg superindo superindo pasteur"

}

```



| Field               | Tipe Data         | Wajib     | Deskripsi                                                                                               |

| ------------------- | ----------------- | --------- | ------------------------------------------------------------------------------------------------------- |

| `id`                | String            | Ya        | ID unik produk.                                                                                         |

| `timestamp\_scrape`  | String (ISO 8601) | Ya        | Waktu terakhir data di-scrape.                                                                          |

| `nama\_produk`       | String            | Ya        | Nama lengkap produk.                                                                                    |

| `brand\_toko`        | String            | Ya        | Nama brand retailer.                                                                                    |

| `nama\_cabang`       | String            | Ya        | Nama cabang toko.                                                                                       |

| `kategori`          | String            | Ya        | Kategori produk.                                                                                        |

| `area\_tags`         | Array of String   | Ya        | Tag wilayah yang dilayani cabang, diisi melalui data enrichment menggunakan Address Book.               |

| `harga\_normal`      | Integer           | Opsional  | Harga sebelum diskon.                                                                                   |

| `harga\_promo`       | Integer           | Ya        | Harga setelah diskon.                                                                                   |

| `diskon\_persen`     | Float             | Opsional  | Persentase diskon.                                                                                      |

| `perubahan\_harga`   | Integer           | Opsional  | Persentase perubahan harga dari minggu lalu.                                                            |

| `jenis\_harga`       | String            | Ya        | Status: `"PROMO"` atau `"REGULER"`.                                                                     |

| `periode\_promo`     | String            | Opsional  | Periode berlakunya promo.                                                                               |

| `display\_harga`     | String            | Ya        | Harga dalam format tampilan.                                                                            |

| `image\_url`         | String            | Opsional  | URL gambar produk.                                                                                      |

| `logo\_url`          | String            | Opsional  | URL logo retailer.                                                                                      |

| `search\_vector`     | String            | Ya        | String gabungan (`nama\_produk`, `brand\_toko`, `nama\_cabang`) untuk pencarian cepat.                     |



\### 5.2 Skema rekomendasi.json (List of Dictionary)

File `rekomendasi.json` berisi array dari objek-objek dengan struktur sebagai berikut:



```json

{

&#x20; "id": "R\_1713523200",

&#x20; "nama": "Nasi Goreng Mang Ujang",

&#x20; "lokasi\_teks": "Ciwaruga, samping Indomaret",

&#x20; "menu": "Nasi Goreng Spesial",

&#x20; "harga": 15000,

&#x20; "rating": 5,

&#x20; "deskripsi": "Porsi banyak, bisa request telur dadar!",

&#x20; "penambah": "Budi",

&#x20; "timestamp": "2026-04-19T14:30:00",

&#x20; "latitude": -6.8721,

&#x20; "longitude": 107.5952,

&#x20; "foto\_url": "https://i.ibb.co/xxxxx/nasi-goreng.jpg",

&#x20; "reaksi": {

&#x20;   "enak": 12,

&#x20;   "murah": 8

&#x20; }

}

```



| Field          | Tipe Data         | Wajib     | Deskripsi                                                                                   |

| -------------- | ----------------- | --------- | ------------------------------------------------------------------------------------------- |

| `id`           | String            | Ya        | ID unik rekomendasi.                                                                        |

| `nama`         | String            | Ya        | Nama tempat.                                                                                |

| `lokasi\_teks`  | String            | Opsional  | Deskripsi lokasi dalam teks (contoh: "Ciwaruga, samping Indomaret").                        |

| `menu`         | String            | Opsional  | Menu andalan.                                                                               |

| `harga`        | Integer           | Ya        | Kisaran harga.                                                                              |

| `rating`       | Integer (1–5)     | Ya        | Rating bintang.                                                                             |

| `deskripsi`    | String            | Opsional  | Deskripsi singkat.                                                                          |

| `penambah`     | String            | Ya        | Nama kontributor (default "Anonim").                                                        |

| `timestamp`    | String (ISO 8601) | Ya        | Waktu penambahan.                                                                           |

| `latitude`     | Float             | Opsional  | Koordinat lintang (dapat diisi manual atau lewat pin drop di peta).                         |

| `longitude`    | Float             | Opsional  | Koordinat bujur (dapat diisi manual atau lewat pin drop di peta).                           |

| `foto\_url`     | String            | Opsional  | URL foto dari ImgBB.                                                                        |

| `reaksi`       | Object            | Opsional  | Objek reaksi komunitas: `{"enak": int, "murah": int}` (tidak diisi saat penambahan, hanya ditampilkan). |



\---



\## BAB 6 : Atribut Kualitas



| Atribut       | Persyaratan                                                                                                                                                                         |

| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |

| \*\*Performa\*\*  | Waktu pencarian < 100ms untuk 1.000 item di RAM. GUI tetap responsif saat sinkronisasi berkat threading (QThread).                                                                 |

| \*\*Keandalan\*\* | Aplikasi otomatis membuat data demo jika `data\_promo.json` tidak ada. Jika sinkronisasi gagal, aplikasi tetap berjalan dengan cache lokal terakhir.                                  |

| \*\*Portabilitas\*\* | Dapat dijalankan di Windows, macOS, dan Linux dengan Python 3.10+. Peta (OSM) dapat di-cache untuk penggunaan offline.                                                           |

| \*\*Keamanan\*\*  | Tidak ada data pribadi pengguna yang dikirim ke server eksternal (kecuali foto ke ImgBB yang bersifat publik). Mode Admin diproteksi kata sandi. Tidak ada fitur login di Mode User. |

| \*\*Skalabilitas\*\* | Data rekomendasi yang diunduh dibatasi 100 entri terbaru untuk mencegah cache lokal membengkak.                                                                                |



\---



\## BAB 7 : Asumsi dan Batasan



\### 7.1 Asumsi

| No | Asumsi                                                                                                      |

| -- | ----------------------------------------------------------------------------------------------------------- |

| 1  | Pengguna aplikasi adalah mahasiswa Politeknik Negeri Bandung di area Ciwaruga, Sarijadi, dan Gegerkalong.   |

| 2  | Koneksi internet tersedia saat Admin melakukan sinkronisasi dan saat Pengguna melakukan refresh data rekomendasi. |

| 3  | Data promo dari hemat.id akurat dan sesuai dengan harga di toko fisik.                                      |

| 4  | Data promo di aplikasi dianggap sebagai data minggu berjalan (Admin melakukan Replace database setiap minggu). |

| 5  | Volume pengguna dan data masih dalam batas wajar sehingga layanan gratis (Google Apps Script, ImgBB) tidak melampaui kuota. |



\### 7.2 Batasan

| No | Batasan                                                                                                                           |

| -- | --------------------------------------------------------------------------------------------------------------------------------- |

| 1  | Fitur peta memerlukan caching ubin OpenStreetMap saat pertama kali dibuka dengan internet.                                        |

| 2  | Akurasi pin rekomendasi bergantung pada ketelitian pengguna saat pin drop.                                                        |

| 3  | Tidak ada fitur autentikasi pengguna (login/register) di Mode Pengguna. Identitas kontributor hanya berdasarkan input nama (field `penambah`). |

| 4  | Sinkronisasi data rekomendasi bersifat pull-based (pengguna menekan tombol Refresh).                                               |

| 5  | Kuota dan batasan layanan gratis (Google Apps Script, ImgBB) dapat memengaruhi performa jika data melonjak drastis.               |



\---



\## Pembagian Role dan Deskripsi Tugas



| Anggota                                    | Peran Utama               | Tanggung Jawab                                                                                                                                                                                                                                     | Deliverables                                      |

| ------------------------------------------ | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- |

| Alpedro Simanjorang (251524037)             | \*\*Data Manager\*\*          | 1. Implementasi `data\_manager.py` (skema final: `data\_promo.json`, `rekomendasi.json`). 2. Mengelola Address Book toko. 3. Integrasi Google Apps Script API. 4. Integrasi ImgBB API. 5. Sistem logging (`activity.log`). 6. Strategi Replace database. | Modul `data\_manager.py` final, `activity.log`, Dokumentasi API |

| Arya Nata Adidjaya (251524039)              | \*\*Integrator \& Dokumentasi\*\* | 1. `main.py`: inisialisasi Eager Loading, fungsi `show\_admin\_login()`. 2. Integrasi seluruh modul. 3. Mengatur alur Mode Admin vs Mode User. 4. Menyusun dokumen SKPL final, diagram (Arsitektur, Flowchart, Use Case). 5. Pengujian integrasi dan skenario demo. | `main.py` final, Dokumen SKPL + Lampiran, Skenario demo |

| Hilman Alfarisi Kurniadi (251524052)        | \*\*Scraper \& Admin Tool\*\*  | 1. `scraper.py`: ekstrak `harga\_normal`, `harga\_promo`, `periode\_promo`, `jenis\_harga` dari hemat.id. 2. `admin\_tool.py` (Tkinter): tombol sinkronisasi, upload cloud, log viewer. 3. Fallback `get\_demo\_data()`. 4. Strategi Replace saat upload.       | Modul `scraper.py` final, Modul `admin\_tool.py` final |

| Raden Muhammad Zehan Fadillah (251524061)   | \*\*Algorithm Engine\*\*      | 1. `engine.py`: filter area, kategori, toko, `jenis\_harga`. 2. Pencarian teks (`search\_vector`). 3. Pengurutan Timsort. 4. Fungsi statistik (Top 3 Toko, Komposisi Kategori). 5. Fungsi `perubahan\_harga`. 6. Validasi data rekomendasi.            | Modul `engine.py` final, Fungsi statistik         |

| Shahnaz Saskia Putri (251524062)            | \*\*GUI Developer (PySide6)\*\* | 1. `gui\_pyqt.py`: antarmuka Mode Pengguna. 2. Halaman Home (grid kartu, search bar, filter). 3. Halaman Keranjang (kartu saldo, toggle). 4. Halaman Pengaturan (tema, font, About). 5. Halaman Jelajah: integrasi Leaflet.js, pin, animasi radar. 6. Form input rekomendasi (rating, upload foto, pin drop lokasi). | Modul `gui\_pyqt.py` final, File HTML/JS Leaflet |

