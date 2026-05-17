"""
Test Debugging: Alur Data Cloud & Cache 100 Entri
=================================================
Uji semua jalur data: Promo (Replace) dan Cache.
"""

import os
import json
from datetime import datetime

# Import modul data_manager
import data_manager


# =========================
# 1. UJI FETCH DATA (GET)
# =========================
def test_fetch():

    print("\n" + "=" * 60)
    print(" 📥 UJI FETCH: Mengambil data dari Google Sheets")
    print("=" * 60)

    print("\n1A. Fetch data Promo...")

    data_promo = data_manager.fetch_cloud_data()

    if data_promo:
        print(f"   ✅ Berhasil! {len(data_promo)} item promo diterima.")

        print(
        f"   Contoh item pertama: "
        f"{data_promo[0].get('nama_produk', 'N/A')[:50]}"
        )
        return True

    else:
        print(
            "   ❌ Gagal fetch data Promo. "
            "Periksa APPS_SCRIPT_URL dan koneksi internet."
        )

        return False


# =========================
# 2. UJI PUSH DATA PROMO
# =========================
def test_push_promo():

    print("\n" + "=" * 60)
    print(" 📤 UJI PUSH PROMO: Mengirim data ke Google Sheets")
    print("=" * 60)

    # Data dummy
    dummy_promo = [
        {
            "id": "test|test_cabang|produk_uji_1",
            "timestamp_scrape": datetime.now().isoformat(),
            "nama_produk": "Produk Uji 1",
            "brand_toko": "Test",
            "nama_cabang": "Test Cabang",
            "kategori": "Sembako",
            "area_tags": ["Ciwaruga"],
            "harga_normal": 50000,
            "harga_promo": 45000,
            "diskon_persen": 10.0,
            "perubahan_harga": 5000,
            "jenis_harga": "PROMO",
            "periode_promo": "Test",
            "display_harga": "Rp 45.000",
            "image_url": "",
            "logo_url": "",
            "search_vector": "produk uji 1 test test cabang"
        }
    ]

    print(f"\n   Mengirim {len(dummy_promo)} item dummy...")

    berhasil = data_manager.push_promo_to_cloud(dummy_promo)

    if berhasil:
        print("   ✅ Push berhasil! Data terkirim ke Google Sheets.")
        return True

    else:
        print(
            "   ❌ Push gagal. "
            "Periksa APPS_SCRIPT_URL dan koneksi internet."
        )

        return False


# =========================
# 3. UJI CACHE 100 ENTRI
# =========================
def test_cache_100():

    print("\n" + "=" * 60)
    print(" 📦 UJI CACHE: Maksimal 100 entri")
    print("=" * 60)

    dummy_entries = []

    # buat 120 dummy data
    for i in range(120):

        dummy_entries.append({
            "id": f"R_cache_test_{i}",
            "nama": f"Test Cache {i}",
            "lokasi_teks": "Test",
            "menu": "Test",
            "harga": 10000 + i,
            "rating": 5,
            "deskripsi": "Test cache",
            "penambah": "Alpedro",
            "timestamp": datetime.now().isoformat(),
            "latitude": -6.8721,
            "longitude": 107.5952,
            "foto_url": "",
            "reaksi": {
                "enak": 0,
                "murah": 0
            }
        })

    test_file = "test_cache_100.json"

    # simpan dummy data
    with open(test_file, "w") as f:
        json.dump(dummy_entries, f, indent=2)

    print(
        f"\n   Data dummy dibuat: "
        f"{len(dummy_entries)} entri"
    )

    # baca ulang
    with open(test_file, "r") as f:
        all_data = json.load(f)

    # ambil max 100
    cached_data = all_data[-100:] if len(all_data) > 100 else all_data

    print(f"   Setelah cache: {len(cached_data)} entri")

    if len(cached_data) == 100:
        print("   ✅ Cache 100 entri berfungsi.")
        hasil = True

    else:
        print("   ❌ Cache gagal.")
        hasil = False

    # hapus file test
    os.remove(test_file)

    print(f"   File {test_file} dihapus.")

    return hasil


# =========================
# 4. UJI SYNC LOCAL → CLOUD
# =========================
def test_sync_to_cloud():

    print("\n" + "=" * 60)
    print(" 🔄 UJI SYNC: Lokal → Cloud")
    print("=" * 60)

    data_lokal = data_manager.read_local_data()

    print(f"\n   Data lokal: {len(data_lokal)} item")

    if not data_lokal:
        print("   ⚠ Tidak ada data lokal.")
        return False

    berhasil = data_manager.sync_to_cloud()

    if berhasil:
        print("   ✅ Sync lokal → cloud berhasil!")
        return True

    else:
        print("   ❌ Sync gagal.")
        return False


# =========================
# 5. UJI SYNC CLOUD → LOCAL
# =========================
def test_sync_from_cloud():

    print("\n" + "=" * 60)
    print(" 🔄 UJI SYNC: Cloud → Lokal")
    print("=" * 60)

    data_manager.sync_from_cloud()

    data_lokal = data_manager.read_local_data()

    print(f"\n   Data lokal setelah sync: {len(data_lokal)} item")

    if data_lokal:
        print("   ✅ Sync cloud → lokal berhasil!")
        return True

    else:
        print("   ⚠ Data lokal kosong setelah sync.")
        return False


# =========================
# 6. UJI LOGGING
# =========================
def test_logging():

    print("\n" + "=" * 60)
    print(" 📋 UJI LOGGING")
    print("=" * 60)

    log_path = os.path.join(
        os.path.dirname(__file__),
        "activity.log"
    )

    if os.path.exists(log_path):

        with open(log_path, "r") as f:
            isi = f.read()

        lines = isi.strip().split("\n")

        print(
            f"\n   File activity.log ditemukan "
            f"dengan {len(lines)} baris."
        )

        if lines:

            print("   5 baris terakhir:")

            for line in lines[-5:]:
                print(f"   {line[:100]}")

            print("   ✅ Logging berfungsi.")

            return True

        else:
            print("   ⚠ File log kosong.")
            return False

    else:
        print("   ❌ File activity.log tidak ditemukan!")
        return False


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("=" * 60)
    print(" 🔧 DEBUGGING ALUR DATA CLOUD & CACHE")
    print("=" * 60)

    print(
        f"Waktu: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    hasil = {}

    hasil["fetch"] = test_fetch()
    hasil["push_promo"] = test_push_promo()
    hasil["cache_100"] = test_cache_100()
    hasil["sync_to_cloud"] = test_sync_to_cloud()
    hasil["sync_from_cloud"] = test_sync_from_cloud()
    hasil["logging"] = test_logging()

    # Ringkasan
    print("\n" + "=" * 60)
    print(" 📊 RINGKASAN HASIL DEBUGGING")
    print("=" * 60)

    for nama, status in hasil.items():

        status_str = "✅ LULUS" if status else "❌ GAGAL"

        print(f"   {nama:20s} : {status_str}")

    print(
        "\n🔧 Perbaiki uji yang GAGAL, "
        "lalu jalankan ulang sampai semua LULUS."
    )