# ```markdown

# Spesifikasi Kebutuhan Perangkat Lunak Radar Promo v2.0

# Aplikasi Desktop Agregator Diskon Kebutuhan Pokok Berbasis Web Scraping untuk Optimalisasi Anggaran Mahasiswa di Kawasan Ciwaruga dan Sekitarnya

# \---

# Daftar Isi

# BAB 1 : Pendahuluan

# 1.1 Tujuan Dokumen

# 1.2 Ruang Lingkup Produk

# 1.3 Perbedaan Utama dengan Website Hemat.id

# BAB 2 : Deskripsi Umum

# 2.1 Arsitektur Sistem

# 2.2 Fungsi Produk Utama

# 2.3 Karakteristik Pengguna

# BAB 3 : Persyaratan Fungsional

# BAB 4 : Persyaratan Antarmuka Eksternal

# 4.1 Antarmuka Perangkat Lunak (Sumber Data)

# 4.2 Antarmuka Pengguna (UI)

# 4.2.1 Tata Letak Sisi Pengguna

# 4.2.2 Deskripsi Halaman

# BAB 5 : Persyaratan Data (Model Data)

# 5.1 Skema data\_promo.json

# 5.2 Skema Rekomendasi

# BAB 6 : Atribut Kualitas

# BAB 7 : Asumsi dan Batasan

# 7.1 Asumsi

# 7.2 Batasan

# Pembagian Role dan Deskripsi Tugas

# \---

# BAB 1 : Pendahuluan

# 1.1 Tujuan Dokumen

# Dokumen ini mendefinisikan persyaratan fungsional dan non-fungsional untuk aplikasi desktop Radar Promo v2.0. Dokumen ini menjadi kontrak antara tim pengembang dan pemangku kepentingan (dosen penguji) tentang apa yang akan dibangun.

# 1.2 Ruang Lingkup Produk

# Radar Promo adalah aplikasi desktop offline-first dengan cloud sync yang berfungsi sebagai agregator informasi promo kebutuhan pokok dan rekomendasi tempat makan berbasis korespondensi khusus untuk mahasiswa di Kawasan Politeknik Negeri Bandung. Aplikasi ini dibangun dengan PySide6 untuk antarmuka modernnya, dan memiliki dua mode operasi:

# Mode User (Frontend): Berfungsi sebagai agregator informasi promo kebutuhan pokok dan platform crowdsourcing rekomendasi tempat makan hemat di sekitar kawasan Politeknik Negeri Bandung (Ciwaruga, Sarijadi, Gegerkalong).

# Mode Admin (Backend): Program yang hanya digunakan oleh administrator untuk memperbarui database promo dari internet dan memantau log aktivitas. Mode ini diakses melalui halaman Pengaturan, bukan melalui dialog saat aplikasi dimulai.

# 1.3 Perbedaan Utama dengan Website Hemat.id

# Fitur	Website Hemat.id	Radar Promo

# Konteks Data	Data mentah nasional	Data terkurasi khusus area Polban (Ciwaruga, Sarijadi, Gegerkalong)

# Filter Utama	Kategori \& Nama Produk	Area Spesifik (Cabang terdekat)

# Fitur Tambahan	Tidak ada	Peta interaktif, Crowdsourcing rekomendasi (+foto), Visualisasi data, Simulasi Anggaran

# Koneksi	Harus online	Offline-First (bekerja tanpa internet setelah sync)

# \---

# BAB 2 : Deskripsi Umum

# 2.1 Arsitektur Sistem

# Aplikasi menganut arsitektur Offline-First dengan Eager Loading serta pemisahan tanggung jawab yang ketat (Separation of Concerns).

# Komponen Cloud (Serverless Backend):

# Google Sheets: Bertindak sebagai database pusat yang menyimpan `data\\\_promo` dan `rekomendasi`.

# Google Apps Script Web App: Berfungsi sebagai API endpoint yang menerima data dari aplikasi (Viewer dan Admin Tool) dan menuliskannya ke Google Sheets, serta melayani permintaan baca data.

# ImgBB API: Layanan hosting gambar gratis yang digunakan untuk menyimpan foto rekomendasi yang diunggah pengguna.

# Aliran Data:

# Upload Rekomendasi (Otomatis dari User): Aplikasi Viewer mengunggah foto ke ImgBB → Menerima URL dari ImgBB → Mengirim data rekomendasi (termasuk URL foto) ke Google Apps Script → Google Sheets (Sheet `Rekomendasi`) diperbarui.

# Sinkronisasi Promo (Manual oleh Admin): Admin membuka Dashboard Admin (Tkinter) → Menekan tombol "Sinkronisasi Sekarang" → `scraper.py` menarik data dari hemat.id Rx → Data disimpan ke `data\\\_promo.json` lokal → Admin menekan "Upload Promo ke Cloud" → Data dikirim ke Google Sheets (Sheet `Promo`) dengan strategi Replace (timpa total).

# Unduh Data (User): Aplikasi Viewer saat dibuka atau saat pengguna menekan tombol Refresh akan menarik data terbaru dari Google Sheets (maksimal 100 entri rekomendasi terbaru) dan menyimpannya sebagai cache lokal (file JSON).

# Komponen Aplikasi Lokal:

# `scraper.py`: Modul untuk menarik data mentah dari situs hemat.id. Hanya digunakan oleh Admin Tool.

# `data\\\_manager.py`: Modul pengelola data. Menangani operasi baca/tulis file JSON, operasi Replace Database, pemetaan cabang toko (Address Book), pengayaan data (data enrichment) menggunakan Address Book, dan pembuatan `search\\\_vector`. Juga menangani komunikasi API dengan Google Sheets dan ImgBB.

# `engine.py`: Mesin logika. Menangani filter area, kategori, toko, pencarian teks cepat (`search\\\_vector`), pengurutan menggunakan algoritma Timsort bawaan Python, dan fungsi statistik.

# `gui\\\_pyqt.py` (MainWindow): Antarmuka Mode Pengguna berbasis PySide6 modern, dengan threading (QThread) untuk menjaga responsivitas UI. Menggunakan `QWebEngineView` untuk menampilkan peta Leaflet.js.

# `admin\\\_tool.py`: Dashboard Admin berbasis Tkinter (aplikasi terpisah). Hanya berisi tombol sinkronisasi, upload cloud, dan log viewer.

# `main.py`: Entry point aplikasi. Langsung membuka Mode Pengguna tanpa dialog. Menyediakan fungsi `show\\\_admin\\\_login()` yang dipanggil dari halaman Pengaturan.

# `image\\\_loader.py`: Pengunduhan dan caching gambar (produk \& foto rekomendasi).

# 2.2 Fungsi Produk Utama

# F-1: Akses Admin melalui Halaman Pengaturan

# F-2: Pencarian \& Filter Promo Groceries (Mode User)

# F-3: Peta Interaktif \& Crowdsourcing Rekomendasi (Mode User)

# F-4: Visualisasi Data Statistik (Mode User)

# F-5: Simulasi Anggaran \& Keranjang Belanja (Mode User)

# F-6: Dashboard Admin (Scraping, Upload, Log)

# 2.3 Karakteristik Pengguna

# Pengguna	Mode	Aktivitas

# Mahasiswa Polban	User	Mencari promo, melihat peta, menambah rekomendasi, melihat statistik, simulasi belanja

# Administrator	Admin	Scraping data promo, upload ke cloud, melihat log aktivitas scraping dan kontribusi rekomendasi

# \---

# BAB 3 : Persyaratan Fungsional (User Stories \& Acceptance Criteria)

# 

# | ID | Aktor (sebagai) | Keinginan (Saya ingin) | Manfaat (Sehingga) | Kriteria Penerimaan Utama |

# | :--- | :--- | :--- | :--- | :--- |

# | F-1 | Administrator | mengakses alat pemeliharaan data melalui halaman pengaturan setelah masuk ke aplikasi, tanpa mengganggu pengguna biasa. | keamanan data dan fokus kerja masing-masing peran dapat terjaga. | 1. Aplikasi langsung terbuka dalam Mode Pengguna tanpa dialog awal. <br>2. Pada halaman Pengaturan, terdapat tombol "Masuk sebagai Admin". <br>3. Memilih Admin akan meminta kata sandi. Jika benar, antarmuka berubah menjadi Dashboard Admin (Tkinter). <br>4. Dashboard Admin hanya berisi alat sinkronisasi, upload, dan log. |

# | F-2 | Mahasiswa | mencari dan menyaring informasi promo kebutuhan pokok berdasarkan area, kategori, dan kata kunci tertentu. | proses pencarian barang dengan harga terbaik dapat dilakukan secara cepat dan tepat sasaran. | 1. Tab Home menyediakan bilah pencarian, filter area, filter toko, dan tombol kategori. <br>2. Hasil pencarian muncul dalam bentuk kartu produk (foto, nama, cabang, harga). <br>3. Pencarian teks memanfaatkan atribut `search\\\_vector`. <br>4. Hasil diurutkan menggunakan algoritma Timsort (`list.sort()`). <br>5. Harga normal tercoret jika ada harga promo. Label khusus untuk status PROMO. |

# | F-3 | Mahasiswa | menjelajahi peta interaktif yang menunjukkan lokasi toko resmi serta tempat rekomendasi komunitas, sekaligus berkontribusi menambahkan rekomendasi baru. | saya dapat mempertimbangkan jarak, melihat rekomendasi teman, dan berbagi informasi tempat makan hemat. | 1. Tab Jelajah menampilkan peta penuh OpenStreetMap (via `QWebEngineView`). <br>2. Pin Biru (toko resmi) dan Pin Hijau (rekomendasi). <br>3. Animasi radar pada pin toko dengan promo aktif. <br>4. Tombol "Tambah Tempat" dengan form input (foto via ImgBB, rating bintang, pin drop lokasi). <br>5. Data otomatis tersinkronisasi ke cloud. Tersedia tombol Refresh. |

# | F-4 | Mahasiswa | melihat ringkasan statistik dan visualisasi data dari promo yang sedang berlangsung. | pengguna dapat mengidentifikasi toko dengan promo terbanyak dan komposisi kategori diskon. | 1. Tab Statistik menampilkan diagram batang "3 Toko dengan Promo Terbanyak". <br>2. Menampilkan diagram lingkaran komposisi kategori promo. |

# | F-5 | Mahasiswa | menyusun rencana belanja dalam keranjang virtual dan memantau sisa anggaran bulanan. | pengeluaran dapat terkontrol dan tidak melebihi batas anggaran yang telah ditentukan. | 1. Ikon Keranjang di header kanan atas sebagai pintasan ke halaman Keranjang. <br>2. Halaman Keranjang menampilkan kartu saldo (dengan fitur sembunyikan). <br>3. Item dengan kontrol kuantitas, total biaya real-time. <br>4. Saldo otomatis bertambah/berkurang. |

# | F-6 | Administrator | mengelola pembaruan data promo melalui proses penarikan data (scraping) dan mengunggahnya ke cloud. | data yang diakses pengguna selalu akurat dan terbebas dari informasi usang atau duplikat. | 1. Dashboard Admin (Tkinter) tidak menampilkan antarmuka belanja. <br>2. Tombol "Sinkronisasi Sekarang" (dengan progress bar). <br>3. Tombol "Upload Promo ke Cloud" (strategi Replace). <br>4. Tersedia Log Viewer untuk memantau aktivitas. |

# 

# \---

# BAB 4 : Persyaratan Antarmuka Eksternal

# 4.1 Antarmuka Perangkat Lunak (Sumber Data)

# Sumber	Tujuan	Metode

# hemat.id	Data promo groceries	Web Scraping (`requests`, `BeautifulSoup`)

# OpenStreetMap	Ubin peta (tiles)	HTTP Request (via Leaflet.js di `QWebEngineView`)

# Nominatim	Pencarian koordinat toko (opsional)	HTTP Request (dengan rate limit)

# ImgBB	Hosting foto rekomendasi	HTTP POST

# 4.2 Antarmuka Pengguna (UI)

# 4.2.1 Tata Letak Sisi Pengguna

# Antarmuka utama untuk mahasiswa terdiri dari elemen-elemen berikut:

# Elemen	Posisi	Keterangan

# Header	Atas	Menampilkan Logo \& Nama Aplikasi di sisi kiri, serta Ikon Keranjang di sisi kanan bersamaan dengan bilah pencarian. Ikon keranjang menjadi pintasan untuk membuka halaman keranjang.

# Area Konten Utama	Tengah (Dinamis)	Menampilkan konten sesuai tab yang sedang aktif (Home, Jelajah, Statistik, Pengaturan).

# Navigasi Bawah	Bawah	Empat tab permanen: Home, Jelajah, Statistik, Pengaturan.

# 4.2.2 Deskripsi Halaman

# Halaman Home: Berisi bilah pencarian, filter area/toko/kategori, dan tampilan grid kartu produk promo.

# Halaman Jelajah: Berisi peta interaktif penuh (via `QWebEngineView`) dengan pin lokasi toko dan rekomendasi. Tombol "Tambah Tempat" berada di pojok tengah bawah peta.

# Halaman Statistik: Berisi visualisasi data, terutama diagram batang "Top 3 Toko dengan Promo Terbanyak" dan diagram lingkaran komposisi kategori promo.

# Halaman Keranjang: Halaman ini tidak muncul sebagai tab di navigasi bawah. Hanya dapat diakses dengan mengeklik Ikon Keranjang di Header. Menampilkan Kartu Saldo dan daftar item belanja.

# Halaman Pengaturan: Berisi pengaturan personalisasi (Mode Gelap/Terang, Ukuran Font), informasi "About", dan tombol "Masuk sebagai Admin".

# \---

# BAB 5 : Persyaratan Data (Model Data)

# 5.1 Skema data\_promo.json (List of Dictionary)

# File `data\\\_promo.json` berisi array dari objek-objek (List of Dictionary) dengan struktur sebagai berikut:

# ```json

# {

# &#x20; "id": "superindo|superindo\\\_pasteur|beras\\\_365\\\_5kg",

# &#x20; "timestamp\\\_scrape": "2026-04-19T10:00:00",

# &#x20; "nama\\\_produk": "Beras 365 Pulen Wangi 5kg",

# &#x20; "brand\\\_toko": "Superindo",

# &#x20; "nama\\\_cabang": "Superindo Pasteur",

# &#x20; "kategori": "Sembako",

# &#x20; "area\\\_tags": \\\["Sarijadi", "Gegerkalong"],

# &#x20; "harga\\\_normal": 85000,

# &#x20; "harga\\\_promo": 72900,

# &#x20; "diskon\\\_persen": 14.1,

# &#x20; "perubahan\\\_harga": -5,

# &#x20; "jenis\\\_harga": "PROMO",

# &#x20; "periode\\\_promo": "14-20 April 2026",

# &#x20; "display\\\_harga": "Rp 72.900",

# &#x20; "image\\\_url": "...",

# &#x20; "logo\\\_url": "...",

# &#x20; "search\\\_vector": "beras 365 pulen wangi 5kg superindo superindo pasteur"

# }

# 

# ```

# 

# Field	Tipe Data	Wajib	Deskripsi

# `id`	String	Ya	ID unik produk.

# `timestamp\\\_scrape`	String (ISO 8601)	Ya	Waktu terakhir data di-scrape.

# `nama\\\_produk`	String	Ya	Nama lengkap produk.

# `brand\\\_toko`	String	Ya	Nama brand retailer.

# `nama\\\_cabang`	String	Ya	Nama cabang toko.

# `kategori`	String	Ya	Kategori produk.

# `area\\\_tags`	Array of String	Ya	Tag wilayah yang dilayani cabang. Diisi melalui proses data enrichment di data\_manager.py menggunakan Address Book.

# `harga\\\_normal`	Integer	Opsional	Harga sebelum diskon.

# `harga\\\_promo`	Integer	Ya	Harga setelah diskon.

# `diskon\\\_persen`	Float	Opsional	Persentase diskon.

# `perubahan\\\_harga`	Integer	Opsional	Persentase perubahan harga dari minggu lalu.

# `jenis\\\_harga`	String	Ya	Status: `"PROMO"` atau `"REGULER"`.

# `periode\\\_promo`	String	Opsional	Periode berlakunya promo.

# `display\\\_harga`	String	Ya	Harga dalam format tampilan.

# `image\\\_url`	String	Opsional	URL gambar produk.

# `logo\\\_url`	String	Opsional	URL logo retailer.

# `search\\\_vector`	String	Ya	String gabungan untuk pencarian cepat.

# 5.2 Skema rekomendasi.json (List of Dictionary)

# File `rekomendasi.json` berisi array dari objek-objek (List of Dictionary) with struktur sebagai berikut:

# 

# ```json

# {

# &#x20; "id": "R\\\_1713523200",

# &#x20; "nama": "Nasi Goreng Mang Ujang",

# &#x20; "lokasi\\\_teks": "Ciwaruga, samping Indomaret",

# &#x20; "menu": "Nasi Goreng Spesial",

# &#x20; "harga": 15000,

# &#x20; "rating": 5,

# &#x20; "deskripsi": "Porsi banyak, bisa request telur dadar!",

# &#x20; "penambah": "Budi",

# &#x20; "timestamp": "2026-04-19T14:30:00",

# &#x20; "latitude": -6.8721,

# &#x20; "longitude": 107.5952,

# &#x20; "foto\\\_url": "\[https://i.ibb.co/xxxxx/nasi-goreng.jpg](https://i.ibb.co/xxxxx/nasi-goreng.jpg)",

# &#x20; "reaksi": {

# &#x20;   "enak": 12,

# &#x20;   "murah": 8

# &#x20; }

# }

# 

# ```

# 

# \## Field	Tipe Data	Wajib	Deskripsi

# `id`	String	Ya	ID unik rekomendasi.

# `nama`	String	Ya	Nama tempat.

# `lokasi\\\_teks`	String	Opsional	Deskripsi lokasi dalam teks.

# `menu`	String	Opsional	Menu andalan.

# `harga`	Integer	Ya	Kisaran harga.

# `rating`	Integer (1–5)	Ya	Rating bintang.

# `deskripsi`	String	Opsional	Deskripsi singkat.

# `penambah`	String	Ya	Nama kontributor.

# `timestamp`	String (ISO 8601)	Ya	Waktu penambahan.

# `latitude`	Float	Opsional	Koordinat lintang.

# `longitude`	Float	Opsional	Koordinat bujur.

# `foto\\\_url`	String	Opsional	URL foto dari ImgBB.

# `reaksi`	Object	Opsional	`{"enak": int, "murah": int}`

# 

# \## BAB 6 : Atribut Kualitas

# Atribut	Persyaratan

# Performa	Waktu pencarian < 100ms untuk 1.000 item di RAM. GUI tetap responsif saat sync berkat threading (QThread).

# Keandalan	Aplikasi otomatis membuat data demo jika `data\\\_promo.json` tidak ada. Jika sinkronisasi gagal, aplikasi tetap berjalan dengan cache lokal terakhir.

# Portabilitas	Dapat dijalankan di Windows, macOS, dan Linux dengan Python 3.10+. Peta (OSM) dapat di-cache untuk penggunaan offline.

# Keamanan	Tidak ada data pengguna yang dikirim ke server eksternal (kecuali foto ke ImgBB publik). Mode Admin diproteksi kata sandi.

# Skalabilitas	Data rekomendasi yang diunduh dibatasi 100 entri terbaru untuk mencegah cache lokal membengkak.

# 

# BAB 7 : Asumsi dan Batasan

# 7.1 Asumsi

# No	Asumsi

# 

# 1\. Pengguna aplikasi adalah mahasiswa Politeknik Negeri Bandung di area Ciwaruga, Sarijadi, dan Gegerkalong.

# 2\. Koneksi internet tersedia saat Admin melakukan sinkronisasi dan saat Pengguna melakukan refresh data rekomendasi.

# 3\. Data promo dari hemat.id akurat dan sesuai dengan harga di toko fisik.

# 4\. Data promo di aplikasi dianggap sebagai data minggu berjalan (Admin melakukan Replace database setiap minggu).

# 5\. Volume pengguna dan data masih dalam batas wajar sehingga layanan gratis (Google Apps Script, ImgBB) tidak melampaui kuota.

# 7.2 Batasan

# No	Batasan

# 6\. Fitur peta memerlukan caching ubin OpenStreetMap saat pertama kali dibuka dengan internet.

# 7\. Akurasi pin rekomendasi bergantung pada ketelitian pengguna saat pin drop.

# 8\. Tidak ada fitur autentikasi pengguna (login/register) di Mode Pengguna. Identitas hanya berdasarkan input nama.

# 9\. Sinkronisasi data rekomendasi bersifat pull-based (pengguna menekan tombol Refresh).

# 10\. Kuota dan batasan layanan gratis (Google Apps Script, ImgBB) dapat memengaruhi performa jika data melonjak drastis.

# 

# \---

# 

# Pembagian Role dan Deskripsi Tugas

# Anggota	Peran Utama	Tanggung Jawab	Deliverables

# Alpedro Simanjorang (251524037)	Data Manager	1. Implementasi `data\\\_manager.py` (skema final: `data\\\_promo.json`, `rekomendasi.json`). 2. Mengelola Address Book toko. 3. Integrasi Google Apps Script API. 4. Integrasi ImgBB API. 5. Sistem logging (`activity.log`). 6. Strategi Replace database.	Modul `data\\\_manager.py` final, File `activity.log`, Dokumentasi API

# Arya Nata Adidjaya (251524039)	Integrator \& Dokumentasi	1. `main.py`: inisialisasi Eager Loading, fungsi `show\\\_admin\\\_login()`. 2. Integrasi seluruh modul (`gui\\\_pyqt.py`, `engine.py`, `data\\\_manager.py`). 3. Mengatur alur Mode Admin vs Mode User. 4. Menyusun dokumen SKPL final, diagram (Arsitektur, Flowchart, Use Case). 5. Pengujian integrasi dan skenario demo.	`main.py` final, Dokumen SKPL + Lampiran, Skenario demo

# Hilman Alfarisi Kurniadi (251524052)	Scraper \& Admin Tool	1. `scraper.py`: ekstrak `harga\\\_normal`, `harga\\\_promo`, `periode\\\_promo`, `jenis\\\_harga` dari hemat.id. 2. `admin\\\_tool.py` (berbasis Tkinter): tombol "Sinkronisasi Sekarang" (progress bar), "Upload Promo ke Cloud", Log Viewer. 3. Fallback `get\\\_demo\\\_data()`. 4. Strategi Replace saat upload.	Modul `scraper.py` final, Modul `admin\\\_tool.py` final

# Raden Muhammad Zehan Fadillah (251524061)	Algorithm Engine	1. `engine.py`: filter area, kategori, toko, `jenis\\\_harga`. 2. Pencarian teks (`search\\\_vector`). 3. Pengurutan Timsort (`list.sort()`). 4. Fungsi Statistik (Top 3 Toko, Komposisi Kategori). 5. Fungsi `perubahan\\\_harga`. 6. Validasi data rekomendasi.	Modul `engine.py` final, Fungsi statistik

# Shahnaz Saskia Putri (251524062)	GUI Developer (PySide6)	1. `gui\\\_pyqt.py`: Antarmuka Mode Pengguna berbasis PySide6. 2. Halaman Home (grid kartu, search bar, filter). 3. Halaman Keranjang (kartu saldo, toggle). 4. Halaman Pengaturan (tema, font, About). 5. Halaman Jelajah: Integrasi Leaflet.js via `QWebEngineView` (pin, animasi radar). 6. Form input rekomendasi (rating, upload, pin drop).	Modul `gui\\\_pyqt.py` final, File HTML/JS Leaflet

# 

# ```

# 

# ```

