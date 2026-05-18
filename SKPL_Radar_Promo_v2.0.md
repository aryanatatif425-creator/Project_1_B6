# Spesifikasi Kebutuhan Perangkat Lunak Radar Promo v2.0

### Aplikasi Desktop Agregator Diskon Kebutuhan Pokok Berbasis Web Scraping untuk Optimalisasi Anggaran Mahasiswa di Kawasan Ciwaruga dan Sekitarnya

---

## Daftar Isi

* [BAB 1: Pendahuluan](#bab 1--pendahuluan)
* [1.1 Tujuan Dokumen](https://www.google.com/search?q=%2311-tujuan-dokumen)
* [1.2 Ruang Lingkup Produk](https://www.google.com/search?q=%2312-ruang-lingkup-produk)
* [1.3 Perbedaan Utama dengan Website Hemat.id](https://www.google.com/search?q=%2313-perbedaan-utama-dengan-website-hematid)


* [BAB 2: Deskripsi Umum](https://www.google.com/search?q=%23bab-2--deskripsi-umum)
* [2.1 Arsitektur Sistem](https://www.google.com/search?q=%2321-arsitektur-sistem)
* [2.2 Fungsi Produk Utama](https://www.google.com/search?q=%2322-fungsi-produk-utama)
* [2.3 Karakteristik Pengguna](https://www.google.com/search?q=%2323-karakteristik-pengguna)


* [BAB 3: Persyaratan Fungsional](https://www.google.com/search?q=%23bab-3--persyaratan-fungsional-user-stories--acceptance-criteria)
* [BAB 4: Persyaratan Antarmuka Eksternal](https://www.google.com/search?q=%23bab-4--persyaratan-antarmuka-eksternal)
* [4.1 Antarmuka Perangkat Lunak (Sumber Data)](https://www.google.com/search?q=%2341-antarmuka-perangkat-lunak-sumber-data)
* [4.2 Antarmuka Pengguna (UI)](https://www.google.com/search?q=%2342-antarmuka-pengguna-ui)


* [BAB 5: Persyaratan Data (Model Data)](https://www.google.com/search?q=%23bab-5--persyaratan-data-model-data)
* [5.1 Skema data_promo.json](https://www.google.com/search?q=%2351-skema-data_promojson-list-of-dictionary)
* [5.2 Skema rekomendasi.json](https://www.google.com/search?q=%2352-skema-rekomendasijson-list-of-dictionary)


* [BAB 6: Atribut Kualitas](https://www.google.com/search?q=%23bab-6--atribut-kualitas)
* [BAB 7: Asumsi dan Batasan](https://www.google.com/search?q=%23bab-7--asumsi-dan-batasan)
* [7.1 Asumsi](https://www.google.com/search?q=%2371-asumsi)
* [7.2 Batasan](https://www.google.com/search?q=%2372-batasan)


* [Pembagian Role dan Deskripsi Tugas](https://www.google.com/search?q=%23pembagian-role-dan-deskripsi-tugas)

---

## BAB 1 : Pendahuluan

### 1.1 Tujuan Dokumen

Dokumen ini mendefinisikan persyaratan fungsional dan non-fungsional untuk aplikasi desktop Radar Promo v2.0. Dokumen ini menjadi kontrak antara tim pengembang dan pemangku kepentingan (dosen penguji) tentang apa yang akan dibangun.

### 1.2 Ruang Lingkup Produk

**Radar Promo** adalah aplikasi desktop *offline-first* dengan *cloud sync* yang berfungsi sebagai agregator informasi promo kebutuhan pokok dan rekomendasi tempat makan berbasis korespondensi khusus untuk mahasiswa di Kawasan Politeknik Negeri Bandung. Aplikasi ini dibangun dengan **PySide6** untuk antarmuka modernnya, dan memiliki dua mode operasi:

* **Mode User (Frontend):** Berfungsi sebagai agregator informasi promo kebutuhan pokok dan platform *crowdsourcing* rekomendasi tempat makan hemat di sekitar kawasan Politeknik Negeri Bandung (Ciwaruga, Sarijadi, Gegerkalong).
* **Mode Admin (Backend):** Program yang hanya digunakan oleh administrator untuk memperbarui database promo dari internet dan memantau log aktivitas. Mode ini diakses melalui halaman Pengaturan, bukan melalui dialog saat aplikasi dimulai.

### 1.3 Perbedaan Utama dengan Website Hemat.id

| Fitur | Website Hemat.id | Radar Promo |
| --- | --- | --- |
| **Konteks Data** | Data mentah nasional | Data terkurasi khusus area Polban (Ciwaruga, Sarijadi, Gegerkalong) |
| **Filter Utama** | Kategori & Nama Produk | Area Spesifik (Cabang terdekat) |
| **Fitur Tambahan** | Tidak ada | Peta interaktif, *Crowdsourcing* rekomendasi (+foto), Visualisasi data, Simulasi Anggaran |
| **Koneksi** | Harus online | *Offline-First* (bekerja tanpa internet setelah sync) |

---

## BAB 2 : Deskripsi Umum

### 2.1 Arsitektur Sistem

Aplikasi menganut arsitektur *Offline-First* dengan *Eager Loading* serta pemisahan tanggung jawab yang ketat (*Separation of Concerns*).

#### Komponen Cloud (Serverless Backend)

* **Google Sheets:** Bertindak sebagai database pusat yang menyimpan `data_promo` dan `rekomendasi`.
* **Google Apps Script Web App:** Berfungsi sebagai API endpoint yang menerima data dari aplikasi (Viewer dan Admin Tool), menuliskannya ke Google Sheets, serta melayani permintaan baca data.
* **ImgBB API:** Layanan hosting gambar gratis yang digunakan untuk menyimpan foto rekomendasi yang diunggah pengguna.

#### Aliran Data

* **Upload Rekomendasi (Otomatis dari User):** Aplikasi Viewer mengunggah foto ke ImgBB $\rightarrow$ Menerima URL dari ImgBB $\rightarrow$ Mengirim data rekomendasi (termasuk URL foto) ke Google Apps Script $\rightarrow$ Google Sheets (Sheet `Rekomendasi`) diperbarui.
* **Sinkronisasi Promo (Manual oleh Admin):** Admin membuka Dashboard Admin (Tkinter) $\rightarrow$ Menekan tombol "Sinkronisasi Sekarang" $\rightarrow$ `scraper.py` menarik data dari hemat.id $\rightarrow$ Data disimpan ke `data_promo.json` lokal $\rightarrow$ Admin menekan "Upload Promo ke Cloud" $\rightarrow$ Data dikirim ke Google Sheets (Sheet `Promo`) dengan strategi *Replace* (timpa total).
* **Unduh Data (User):** Aplikasi Viewer saat dibuka atau saat pengguna menekan tombol Refresh akan menarik data terbaru dari Google Sheets (maksimal 100 entri rekomendasi terbaru) dan menyimpannya sebagai cache lokal (file JSON).

#### Komponen Aplikasi Lokal

* `scraper.py`: Modul untuk menarik data mentah dari situs hemat.id. Hanya digunakan oleh Admin Tool.
* `data_manager.py`: Modul pengelola data. Menangani operasi baca/tulis file JSON, operasi *Replace* Database, pemetaan cabang toko (*Address Book*), pengayaan data (*data enrichment*) menggunakan *Address Book*, dan pembuatan `search_vector`. Juga menangani komunikasi API dengan Google Sheets dan ImgBB.
* `engine.py`: Mesin logika. Menangani filter area, kategori, toko, pencarian teks cepat (`search_vector`), pengurutan menggunakan algoritma Timsort bawaan Python, dan fungsi statistik.
* `gui_pyqt.py` (MainWindow): Antarmuka Mode Pengguna berbasis PySide6 modern, dengan *threading* (`QThread`) untuk menjaga responsivitas UI. Menggunakan `QWebEngineView` untuk menampilkan peta Leaflet.js.
* `admin_tool.py`: Dashboard Admin berbasis Tkinter (aplikasi terpisah). Hanya berisi tombol sinkronisasi, upload cloud, dan log viewer.
* `main.py`: Entry point aplikasi. Langsung membuka Mode Pengguna tanpa dialog. Menyediakan fungsi `show_admin_login()` yang dipanggil dari halaman Pengaturan.
* `image_loader.py`: Pengunduhan dan caching gambar (produk & foto rekomendasi).

### 2.2 Fungsi Produk Utama

* **F-1:** Akses Admin melalui Halaman Pengaturan
* **F-2:** Pencarian & Filter Promo Groceries (Mode User)
* **F-3:** Peta Interaktif & Crowdsourcing Rekomendasi (Mode User)
* **F-4:** Visualisasi Data Statistik (Mode User)
* **F-5:** Simulasi Anggaran & Keranjang Belanja (Mode User)
* **F-6:** Dashboard Admin (Scraping, Upload, Log)

### 2.3 Karakteristik Pengguna

| Pengguna | Mode | Aktivitas |
| --- | --- | --- |
| **Mahasiswa Polban** | User | Mencari promo, melihat peta, menambah rekomendasi, melihat statistik, simulasi belanja |
| **Administrator** | Admin | Scraping data promo, upload ke cloud, melihat log aktivitas scraping dan kontribusi rekomendasi |

---

## BAB 3 : Persyaratan Fungsional (User Stories & Acceptance Criteria)

| ID | Aktor (sebagai) | Keinginan (Saya ingin) | Manfaat (Sehingga) | Kriteria Penerimaan Utama |
| --- | --- | --- | --- | --- |
| **F-1** | Administrator | mengakses alat pemeliharaan data melalui halaman pengaturan setelah masuk ke aplikasi, tanpa mengganggu pengguna biasa. | keamanan data dan fokus kerja masing-masing peran dapat terjaga. | 1. Aplikasi langsung terbuka dalam Mode Pengguna tanpa dialog awal.<br>

<br>2. Pada halaman Pengaturan, terdapat tombol "Masuk sebagai Admin".<br>

<br>3. Memilih Admin akan meminta kata sandi. Jika benar, antarmuka berubah menjadi Dashboard Admin (Tkinter).<br>

<br>4. Dashboard Admin hanya berisi alat sinkronisasi, upload, dan log. |
| **F-2** | Mahasiswa | mencari dan menyaring informasi promo kebutuhan pokok berdasarkan area, kategori, dan kata kunci tertentu. | proses pencarian barang dengan harga terbaik dapat dilakukan secara cepat dan tepat sasaran. | 1. Tab Home menyediakan bilah pencarian, filter area, filter toko, dan tombol kategori.<br>

<br>2. Hasil pencarian muncul dalam bentuk kartu produk (foto, nama, cabang, harga).<br>

<br>3. Pencarian teks memanfaatkan atribut `search_vector`. <br>

<br>4. Hasil diurutkan menggunakan algoritma Timsort (`list.sort()`).<br>

<br>5. Harga normal tercoret jika ada harga promo. Label khusus untuk status PROMO. |
| **F-3** | Mahasiswa | menjelajahi peta interaktif yang menunjukkan lokasi toko resmi serta tempat rekomendasi komunitas, sekaligus berkontribusi menambahkan rekomendasi baru. | saya dapat mempertimbangkan jarak, melihat rekomendasi teman, dan berbagi informasi tempat makan hemat. | 1. Tab Jelajah menampilkan peta penuh OpenStreetMap (via `QWebEngineView`).<br>

<br>2. Pin Biru (toko resmi) dan Pin Hijau (rekomendasi).<br>

<br>3. Animasi radar pada pin toko dengan promo aktif.<br>

<br>4. Tombol "Tambah Tempat" dengan form input (foto via ImgBB, rating bintang, pin drop lokasi).<br>

<br>5. Data otomatis tersinkronisasi ke cloud. Tersedia tombol Refresh. |
| **F-4** | Mahasiswa | melihat ringkasan statistik dan visualisasi data dari promo yang sedang berlangsung. | pengguna dapat mengidentifikasi toko dengan promo terbanyak dan komposisi kategori diskon. | 1. Tab Statistik menampilkan diagram batang "3 Toko dengan Promo Terbanyak".<br>

<br>2. Menampilkan diagram lingkaran komposisi kategori promo. |
| **F-5** | Mahasiswa | menyusun rencana belanja dalam keranjang virtual dan memantau sisa anggaran bulanan. | pengeluaran dapat terkontrol dan tidak melebihi batas anggaran yang telah ditentukan. | 1. Ikon Keranjang di header kanan atas sebagai pintasan ke halaman Keranjang.<br>

<br>2. Halaman Keranjang menampilkan kartu saldo (dengan fitur sembunyikan).<br>

<br>3. Item dengan kontrol kuantitas, total biaya real-time.<br>

<br>4. Saldo otomatis bertambah/berkurang. |
| **F-6** | Administrator | mengelola pembaruan data promo melalui proses penarikan data (scraping) dan mengunggahnya ke cloud. | data yang diakses pengguna selalu akurat dan terbebas dari informasi usang atau duplikat. | 1. Dashboard Admin (Tkinter) tidak menampilkan antarmuka belanja.<br>

<br>2. Tombol "Sinkronisasi Sekarang" (dengan progress bar).<br>

<br>3. Tombol "Upload Promo ke Cloud" (strategi *Replace*).<br>

<br>4. Tersedia Log Viewer untuk memantau aktivitas. |

---

## BAB 4 : Persyaratan Antarmuka Eksternal

### 4.1 Antarmuka Perangkat Lunak (Sumber Data)

| Sumber | Tujuan | Metode |
| --- | --- | --- |
| **hemat.id** | Data promo groceries | Web Scraping (`requests`, `BeautifulSoup`) |
| **OpenStreetMap** | Ubin peta (*tiles*) | HTTP Request (via Leaflet.js di `QWebEngineView`) |
| **Nominatim** | Pencarian koordinat toko (opsional) | HTTP Request (dengan rate limit) |
| **ImgBB** | Hosting foto rekomendasi | HTTP POST |

### 4.2 Antarmuka Pengguna (UI)

#### 4.2.1 Tata Letak Sisi Pengguna

Antarmuka utama untuk mahasiswa terdiri dari elemen-elemen berikut:

| Elemen | Posisi | Keterangan |
| --- | --- | --- |
| **Header** | Atas | Menampilkan Logo & Nama Aplikasi di sisi kiri, serta Ikon Keranjang di sisi kanan bersamaan dengan bilah pencarian. Ikon keranjang menjadi pintasan untuk membuka halaman keranjang. |
| **Area Konten Utama** | Tengah (Dinamis) | Menampilkan konten sesuai tab yang sedang aktif (Home, Jelajah, Statistik, Pengaturan). |
| **Navigasi Bawah** | Bawah | Empat tab permanen: Home, Jelajah, Statistik, Pengaturan. |

#### 4.2.2 Deskripsi Halaman

* **Halaman Home:** Berisi bilah pencarian, filter area/toko/kategori, dan tampilan grid kartu produk promo.
* **Halaman Jelajah:** Berisi peta interaktif penuh (via `QWebEngineView`) dengan pin lokasi toko dan rekomendasi. Tombol "Tambah Tempat" berada di pojok tengah bawah peta.
* **Halaman Statistik:** Berisi visualisasi data, terutama diagram batang "Top 3 Toko dengan Promo Terbanyak" dan diagram lingkaran komposisi kategori promo.
* **Halaman Keranjang:** Halaman ini tidak muncul sebagai tab di navigasi bawah. Hanya dapat diakses dengan mengeklik Ikon Keranjang di Header. Menampilkan Kartu Saldo dan daftar item belanja.
* **Halaman Pengaturan:** Berisi pengaturan personalisasi (Mode Gelap/Terang, Ukuran Font), informasi "About", dan tombol "Masuk sebagai Admin".

---

## BAB 5 : Persyaratan Data (Model Data)

### 5.1 Skema data_promo.json (List of Dictionary)

File `data_promo.json` berisi array dari objek-objek dengan struktur sebagai berikut:

```json
[
  {
    "id": "superindo|superindo_pasteur|beras_365_5kg",
    "timestamp_scrape": "2026-04-19T10:00:00",
    "nama_produk": "Beras 365 Pulen Wangi 5kg",
    "brand_toko": "Superindo",
    "nama_cabang": "Superindo Pasteur",
    "kategori": "Sembako",
    "area_tags": ["Sarijadi", "Gegerkalong"],
    "harga_normal": 85000,
    "harga_promo": 72900,
    "diskon_persen": 14.1,
    "perubahan_harga": -5,
    "jenis_harga": "PROMO",
    "periode_promo": "14-20 April 2026",
    "display_harga": "Rp 72.900",
    "image_url": "https://example.com/images/beras.jpg",
    "logo_url": "https://example.com/logos/superindo.png",
    "search_vector": "beras 365 pulen wangi 5kg superindo superindo pasteur"
  }
]

```

| Field | Tipe Data | Wajib | Deskripsi |
| --- | --- | --- | --- |
| `id` | String | Ya | ID unik produk. |
| `timestamp_scrape` | String (ISO 8601) | Ya | Waktu terakhir data di-scrape. |
| `nama_produk` | String | Ya | Nama lengkap produk. |
| `brand_toko` | String | Ya | Nama brand retailer. |
| `nama_cabang` | String | Ya | Nama cabang toko. |
| `kategori` | String | Ya | Kategori produk. |
| `area_tags` | Array of String | Ya | Tag wilayah yang dilayani cabang. Diisi melalui proses data enrichment di `data_manager.py` menggunakan Address Book. |
| `harga_normal` | Integer | Opsional | Harga sebelum diskon. |
| `harga_promo` | Integer | Ya | Harga setelah diskon. |
| `diskon_persen` | Float | Opsional | Persentase diskon. |
| `perubahan_harga` | Integer | Opsional | Persentase perubahan harga dari minggu lalu. |
| `jenis_harga` | String | Ya | Status: `"PROMO"` atau `"REGULER"`. |
| `periode_promo` | String | Opsional | Periode berlakunya promo. |
| `display_harga` | String | Ya | Harga dalam format tampilan. |
| `image_url` | String | Opsional | URL gambar produk. |
| `logo_url` | String | Opsional | URL logo retailer. |
| `search_vector` | String | Ya | String gabungan untuk pencarian cepat. |

### 5.2 Skema rekomendasi.json (List of Dictionary)

File `rekomendasi.json` berisi array dari objek-objek dengan struktur sebagai berikut:

```json
[
  {
    "id": "R_1713523200",
    "nama": "Nasi Goreng Mang Ujang",
    "lokasi_teks": "Ciwaruga, samping Indomaret",
    "menu": "Nasi Goreng Spesial",
    "harga": 15000,
    "rating": 5,
    "deskripsi": "Porsi banyak, bisa request telur dadar!",
    "penambah": "Budi",
    "timestamp": "2026-04-19T14:30:00",
    "latitude": -6.8721,
    "longitude": 107.5952,
    "foto_url": "https://i.ibb.co/xxxxx/nasi-goreng.jpg",
    "reaksi": {
      "enak": 12,
      "murah": 8
    }
  }
]

```

| Field | Tipe Data | Wajib | Deskripsi |
| --- | --- | --- | --- |
| `id` | String | Ya | ID unik rekomendasi. |
| `nama` | String | Ya | Nama tempat. |
| `lokasi_teks` | String | Opsional | Deskripsi lokasi dalam teks. |
| `menu` | String | Opsional | Menu andalan. |
| `harga` | Integer | Ya | Kisaran harga. |
| `rating` | Integer (1–5) | Ya | Rating bintang. |
| `deskripsi` | String | Opsional | Deskripsi singkat. |
| `penambah` | String | Ya | Nama kontributor. |
| `timestamp` | String (ISO 8601) | Ya | Waktu penambahan. |
| `latitude` | Float | Opsional | Koordinat lintang. |
| `longitude` | Float | Opsional | Koordinat bujur. |
| `foto_url` | String | Opsional | URL foto dari ImgBB. |
| `reaksi` | Object | Opsional | `{"enak": int, "murah": int}` |

---

## BAB 6 : Atribut Kualitas

| Atribut | Persyaratan |
| --- | --- |
| **Performa** | Waktu pencarian < 100ms untuk 1.000 item di RAM. GUI tetap responsif saat sync berkat threading (`QThread`). |
| **Keandalan** | Aplikasi otomatis membuat data demo jika `data_promo.json` tidak ada. Jika sinkronisasi gagal, aplikasi tetap berjalan dengan cache lokal terakhir. |
| **Portabilitas** | Dapat dijalankan di Windows, macOS, dan Linux dengan Python 3.10+. Peta (OSM) dapat di-cache untuk penggunaan offline. |
| **Keamanan** | Tidak ada data pengguna yang dikirim ke server eksternal (kecuali foto ke ImgBB publik). Mode Admin diproteksi kata sandi. |
| **Skalabilitas** | Data rekomendasi yang diunduh dibatasi 100 entri terbaru untuk mencegah cache lokal membengkak. |

---

## BAB 7 : Asumsi dan Batasan

### 7.1 Asumsi

1. Pengguna aplikasi adalah mahasiswa Politeknik Negeri Bandung di area Ciwaruga, Sarijadi, dan Gegerkalong.
2. Koneksi internet tersedia saat Admin melakukan sinkronisasi dan saat Pengguna melakukan refresh data rekomendasi.
3. Data promo dari hemat.id akurat dan sesuai dengan harga di toko fisik.
4. Data promo di aplikasi dianggap sebagai data minggu berjalan (Admin melakukan *Replace* database setiap minggu).
5. Volume pengguna dan data masih dalam batas wajar sehingga layanan gratis (Google Apps Script, ImgBB) tidak melampaui kuota.

### 7.2 Batasan

1. Fitur peta memerlukan caching ubin OpenStreetMap saat pertama kali dibuka dengan internet.
2. Akurasi pin rekomendasi bergantung pada ketelitian pengguna saat *pin drop*.
3. Tidak ada fitur autentikasi pengguna (login/register) di Mode Pengguna. Identitas hanya berdasarkan input nama.
4. Sinkronisasi data rekomendasi bersifat *pull-based* (pengguna menekan tombol Refresh).
5. Kuota dan batasan layanan gratis (Google Apps Script, ImgBB) dapat memengaruhi performa jika data melonjak drastis.

---

## Pembagian Role dan Deskripsi Tugas

| Anggota | Peran Utama | Tanggung Jawab | Deliverables |
| --- | --- | --- | --- |
| **Alpedro Simanjorang**<br>

<br>(251524037) | Data Manager | 1. Implementasi `data_manager.py` (skema final: `data_promo.json`, `rekomendasi.json`).<br>

<br>2. Mengelola Address Book toko.<br>

<br>3. Integrasi Google Apps Script API.<br>

<br>4. Integrasi ImgBB API.<br>

<br>5. Sistem logging (`activity.log`).<br>

<br>6. Strategi *Replace* database. | Modul `data_manager.py` final, File `activity.log`, Dokumentasi API |
| **Arya Nata Adidjaya**<br>

<br>(251524039) | Integrator & Dokumentasi | 1. `main.py`: inisialisasi *Eager Loading*, fungsi `show_admin_login()`.<br>

<br>2. Integrasi seluruh modul (`gui_pyqt.py`, `engine.py`, `data_manager.py`).<br>

<br>3. Mengatur alur Mode Admin vs Mode User.<br>

<br>4. Menyusun dokumen SKPL final, diagram (Arsitektur, Flowchart, Use Case).<br>

<br>5. Pengujian integrasi dan skenario demo. | `main.py` final, Dokumen SKPL + Lampiran, Skenario demo |
| **Hilman Alfarisi Kurniadi**<br>

<br>(251524052) | Scraper & Admin Tool | 1. `scraper.py`: ekstrak `harga_normal`, `harga_promo`, `periode_promo`, `jenis_harga` dari hemat.id.<br>

<br>2. `admin_tool.py` (berbasis Tkinter): tombol "Sinkronisasi Sekarang" (progress bar), "Upload Promo ke Cloud", Log Viewer.<br>

<br>3. Fallback `get_demo_data()`.<br>

<br>4. Strategi *Replace* saat upload. | Modul `scraper.py` final, Modul `admin_tool.py` final |
| **Raden Muhammad Zehan Fadillah**<br>

<br>(251524061) | Algorithm Engine | 1. `engine.py`: filter area, kategori, toko, `jenis_harga`.<br>

<br>2. Pencarian teks (`search_vector`).<br>

<br>3. Pengurutan Timsort (`list.sort()`).<br>

<br>4. Fungsi Statistik (Top 3 Toko, Komposisi Kategori).<br>

<br>5. Fungsi `perubahan_harga`.<br>

<br>6. Validasi data rekomendasi. | Modul `engine.py` final, Fungsi statistik |
| **Shahnaz Saskia Putri**<br>

<br>(251524062) | GUI Developer (PySide6) | 1. `gui_pyqt.py`: Antarmuka Mode Pengguna berbasis PySide6.<br>

<br>2. Halaman Home (grid kartu, search bar, filter).<br>

<br>3. Halaman Keranjang (kartu saldo, toggle).<br>

<br>4. Halaman Pengaturan (tema, font, About).<br>

<br>5. Halaman Jelajah: Integrasi Leaflet.js via `QWebEngineView` (pin, animasi radar).<br>

<br>6. Form input rekomendasi (rating, upload, pin drop). | Modul `gui_pyqt.py` final, File HTML/JS Leaflet |
