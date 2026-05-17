"""
engine.py — Radar Promo Algorithm Engine
=========================================
Implements the core data-processing pipeline:
  1. Filter: Area, Kategori, Toko, Jenis Harga
  2. Smart Search: Teks cepat (search_vector)
  3. Optimised Sort: Timsort bawaan Python
  4. Statistik: Top 3 Cabang, Komposisi Kategori
  5. Perubahan Harga: Kalkulasi selisih harga & persentase diskon
  6. Validasi: Memastikan kelayakan data (ID, Harga, Nama)
"""

import logging
from typing import Optional, Tuple
from collections import Counter  # Modul bawaan Python untuk menghitung jumlah data dengan cepat

log = logging.getLogger(__name__)


# ─── 1. Fungsi Filter (Area, Kategori, Toko, Jenis Harga) ─────────────

def filter_by_area(records: list[dict], area: Optional[str]) -> list[dict]:
    if not area or area.strip().lower() in ("", "semua area", "all"):
        return list(records)

    area_normalised = area.strip()
    return [r for r in records if area_normalised in r.get("area_tags", [])]


def filter_by_category(records: list[dict], category: Optional[str]) -> list[dict]:
    if not category or category.strip() in ("", "Semua Kategori"):
        return list(records)

    cat_normalised = category.strip()
    return [r for r in records if r.get("kategori") == cat_normalised]


def filter_by_shop(records: list[dict], shop: Optional[str]) -> list[dict]:
    """Menyaring data berdasarkan nama brand retailer."""
    if not shop or shop.strip() in ("", "Semua Toko"):
        return list(records)
    
    shop_normalised = shop.strip().lower()
    # Membandingkan nama toko dengan mengabaikan huruf besar/kecil
    return [r for r in records if r.get("brand_toko", "").lower() == shop_normalised]


def filter_by_price_type(records: list[dict], price_type: Optional[str]) -> list[dict]:
    """Menyaring data berdasarkan jenis harga (misal: PROMO, REGULER)."""
    if not price_type or price_type.strip() in ("", "Semua Jenis"):
        return list(records)
    
    pt_normalised = price_type.strip().lower()
    return [r for r in records if r.get("jenis_harga", "").lower() == pt_normalised]


# ─── 2. Smart Search (Eager Loading) ──────────────────────────────────

def search_by_keyword(records: list[dict], keyword: Optional[str]) -> list[dict]:
    """Pencarian substring super kilat menggunakan search_vector."""
    if not keyword or not keyword.strip():
        return list(records)

    tokens = keyword.strip().lower().split()
    matched = []

    for r in records:
        haystack = r.get("search_vector", "")
        # AND logic: semua kata kunci harus ada di dalam haystack
        if all(tok in haystack for tok in tokens):
            matched.append(r)

    return matched


# ─── 3. Optimised Sort (Timsort) ──────────────────────────────────────

def sort_by_price(records: list[dict]) -> list[dict]:
    """Mengurutkan harga dari yang termurah."""
    return sorted(records, key=lambda r: r.get("harga_promo", 0))


# ─── 4. Fungsi Statistik ──────────────────────────────────────────────

def get_statistics(records: list[dict]) -> dict:
    """Menghasilkan Top 3 Cabang Toko dan Komposisi Kategori dari data yang sedang ditampilkan."""
    if not records:
        return {"top_3_toko": [], "komposisi_kategori": {}}

    # Mengambil semua nama kategori dan nama cabang dari data
    categories = [r.get("kategori", "Lainnya") for r in records]
    shops = [r.get("nama_cabang", "Cabang Anonim") for r in records]

    # Menghitung komposisi kategori (misal: {'Sembako': 5, 'Elektronik': 2})
    komposisi_kategori = dict(Counter(categories))
    
    # Menghitung cabang paling sering muncul, ambil 3 teratas
    top_3_toko = Counter(shops).most_common(3)

    return {
        "top_3_toko": top_3_toko,
        "komposisi_kategori": komposisi_kategori
    }


# ─── 5. Fungsi Perubahan Harga ────────────────────────────────────────

def apply_price_changes(records: list[dict]) -> list[dict]:
    """
    Menghitung perubahan harga untuk setiap produk.
    - Membandingkan harga_normal dengan harga_promo.
    - Menyimpan selisih di field 'perubahan_harga' (rupiah).
    - Jika tidak ada harga_normal, perubahan_harga = 0.
    - Menghitung 'diskon_persen' (tambahan dari evaluasi sebelumnya).
    """
    for r in records:
        harga_normal = r.get('harga_normal', 0) or 0
        harga_promo  = r.get('harga_promo', 0) or 0
        
        if harga_normal > 0 and harga_promo > 0 and harga_normal > harga_promo:
            r['perubahan_harga'] = harga_normal - harga_promo
            r['diskon_persen'] = round((r['perubahan_harga'] / harga_normal) * 100, 2)
        else:
            r['perubahan_harga'] = 0
            r['diskon_persen'] = 0
            
    return records


# ─── 6. Validasi Data Rekomendasi ─────────────────────────────────────

def validate_recommendations(records: list[dict]) -> list[dict]:
    """Membuang data yang cacat (misalnya tidak ada ID, harga, atau nama produk)."""
    valid_records = []
    for r in records:
        # Cek apakah data memiliki id, harga_promo (angka), dan nama_produk tidak kosong
        if r.get("id") and r.get("harga_promo") is not None and r.get("nama_produk"):
            valid_records.append(r)
    return valid_records


# ─── Public Pipeline Entry Point ──────────────────────────────────────

def run_pipeline(
    records: list[dict],
    area: Optional[str] = None,
    category: Optional[str] = None,
    shop: Optional[str] = None,
    price_type: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Tuple[list[dict], dict]:
    """
    Menjalankan seluruh alur pemrosesan data dan mengembalikan 2 hal:
    1. Daftar rekomendasi promo yang sudah disaring & diurutkan.
    2. Data statistik (untuk ditampilkan di dashboard/grafik).
    """
    
    if not records:
        return [], {"top_3_toko": [], "komposisi_kategori": {}}

    # Tahap 1: Filtering berlapis
    step1 = filter_by_area(records, area)
    step2 = filter_by_category(step1, category)
    step3 = filter_by_shop(step2, shop)
    step4 = filter_by_price_type(step3, price_type)
    
    # Tahap 2: Pencarian teks cepat
    step5 = search_by_keyword(step4, keyword)
    
    # Tahap 3: Validasi kelayakan data
    step6 = validate_recommendations(step5)
    
    # Tahap 4: Kalkulasi perubahan harga (diskon)
    step7 = apply_price_changes(step6)
    
    # Tahap 5: Pengurutan menggunakan Timsort
    final_records = sort_by_price(step7)

    # Tahap 6: Generate Statistik berdasarkan hasil akhir
    stats = get_statistics(final_records)

    # Mengembalikan 2 nilai (Tuple): Data hasil saringan dan Data statistiknya
    return final_records, stats