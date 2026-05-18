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


# ─── 1. FILTER ───────────────────────────────────────────────────

def filter_by_area(records: List[Dict], area: Optional[str]) -> List[Dict]:
    if not area or area.strip().lower() in ("", "semua area", "all"):
        return records
    area_norm = area.strip()
    return [r for r in records if area_norm in r.get("area_tags", [])]


def filter_by_category(records: List[Dict], category: Optional[str]) -> List[Dict]:
    if not category or category.strip().lower() in ("", "semua kategori"):
        return records
    cat_norm = category.strip()
    return [r for r in records if r.get("kategori") == cat_norm]


def filter_by_brand(records: List[Dict], brand: Optional[str]) -> List[Dict]:
    if not brand or brand.strip().lower() in ("", "semua toko"):
        return records
    brand_norm = brand.strip().lower()
    return [r for r in records if r.get("brand_toko", "").lower() == brand_norm]


def filter_by_jenis_harga(records: List[Dict], jenis: Optional[str]) -> List[Dict]:
    if not jenis or jenis.strip().lower() in ("", "semua jenis"):
        return records
    jenis_norm = jenis.strip()
    return [r for r in records if r.get("jenis_harga") == jenis_norm]


# ─── 2. SEARCH ──────────────────────────────────────────────────

def search_by_keyword(records: List[Dict], keyword: Optional[str]) -> List[Dict]:
    if not keyword or not keyword.strip():
        return records
    tokens = keyword.strip().lower().split()

    def match(r):
        hv = r.get("search_vector", "")
        return all(tok in hv for tok in tokens)

    return list(filter(match, records))


# ─── 3. SORT (Timsort) ──────────────────────────────────────────

def sort_by_price(records: List[Dict], reverse: bool = False) -> List[Dict]:
    return sorted(records, key=lambda r: r.get("harga_promo", 0), reverse=reverse)


# ─── 4. STATISTIK ───────────────────────────────────────────────

def get_statistics(records: List[Dict]) -> Dict:
    if not records:
        return {"top_3_toko": [], "komposisi_kategori": {}}

    toko_counter = Counter()
    kat_counter = Counter()

    for r in records:
        toko_counter[r.get("nama_cabang", r.get("brand_toko", "?"))] += 1
        kat_counter[r.get("kategori", "Lainnya")] += 1

    return {
        "top_3_toko": toko_counter.most_common(3),
        "komposisi_kategori": dict(kat_counter),
    }


# ─── 5. VALIDASI ────────────────────────────────────────────────

def validate_data(records: List[Dict]) -> List[Dict]:
    valid = []
    for r in records:
        nama = r.get("nama_produk", "").strip()
        harga = r.get("harga_promo")
        if not nama:
            continue
        if not isinstance(harga, (int, float)) or harga <= 0:
            continue
        if not r.get("id"):
            continue
        if not r.get("search_vector"):
            r["search_vector"] = (
                f"{nama} {r.get('brand_toko', '')} {r.get('nama_cabang', '')}".lower()
            )
        valid.append(r)
    return valid


# ─── 6. PERUBAHAN HARGA ─────────────────────────────────────────

def apply_price_changes(records: List[Dict]) -> List[Dict]:
    for r in records:
        normal = r.get("harga_normal", 0) or 0
        promo = r.get("harga_promo", 0) or 0
        r["perubahan_harga"] = max(0, normal - promo)
    return records


# ─── 7. PIPELINE ────────────────────────────────────────────────

def run_pipeline(
    records: List[Dict],
    area: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    jenis_harga: Optional[str] = None,
    keyword: Optional[str] = None,
    reverse: bool = False,
) -> Tuple[List[Dict], Dict]:
    if not records:
        return [], {"top_3_toko": [], "komposisi_kategori": {}}

    step1 = filter_by_area(records, area)
    step2 = filter_by_category(step1, category)
    step3 = filter_by_brand(step2, brand)
    step4 = filter_by_jenis_harga(step3, jenis_harga)
    step5 = search_by_keyword(step4, keyword)
    step6 = validate_data(step5)
    step7 = apply_price_changes(step6)
    step8 = sort_by_price(step7, reverse=reverse)
    stats = get_statistics(step8)

    return step8, stats