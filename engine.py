"""
engine.py — Radar Promo Algorithm Engine
=========================================
Implements the core data-processing pipeline:
  Geofencing Filter  — keep items whose area_tags include the chosen area
  Smart Search       — case-insensitive keyword match (Eagerly Loaded)
  Optimised Sort     — Timsort (Python built-in) on price_int (ascending)
"""

import logging
from typing import Optional

log = logging.getLogger(__name__)


# ─── Geofencing Filter ────────────────────────────────────────────────

def filter_by_area(records: list[dict], area: Optional[str]) -> list[dict]:
    if not area or area.strip().lower() in ("", "semua area", "all"):
        return list(records)

    area_normalised = area.strip()
    filtered = [
        r for r in records
        if area_normalised in r.get("area_tags", [])
    ]
    return filtered


def filter_by_category(records: list[dict], category: Optional[str]) -> list[dict]:
    if not category or category.strip() in ("", "Semua Kategori"):
        return list(records)

    cat_normalised = category.strip()
    filtered = [
        r for r in records
        if r.get("category") == cat_normalised
    ]
    return filtered


# ─── Smart Search (Super Cepat berkat Eager Loading) ─────────────────

def search_by_keyword(records: list[dict], keyword: Optional[str]) -> list[dict]:
    """
    Pencarian super kilat karena data teks sudah dirakit di data_manager.py.
    Hanya perlu operasi pengecekan substring sederhana.
    """
    if not keyword or not keyword.strip():
        return list(records)

    tokens = keyword.strip().lower().split()
    matched = []

    for r in records:
        # Ambil teks rakitan yang sudah disiapkan sejak awal
        haystack = r.get("search_vector", "")
        
        # AND logic: pastikan semua kata yang diketik ada di dalam haystack
        if all(tok in haystack for tok in tokens):
            matched.append(r)

    return matched


# ─── Optimised Sort     — Timsort (Python built-in) on price_int (ascending) ──────────────────────────

def sort_by_price(records: list[dict]) -> list[dict]:
    """
    Sort by price_int ascending menggunakan Timsort bawaan Python (C-optimized).
    """
    # Menggunakan sorted() bawaan Python dengan key untuk mengambil price_int.
    # Default get("price_int", 0) agar aman, kalau ada data yang tidak memiliki key tersebut.
    return sorted(records, key=lambda r: r.get("price_int", 0))


# ─── Public Pipeline Entry Point ─────────────────────────────────────────────

def run_pipeline(
    records:  list[dict],
    area:     Optional[str] = None,
    category: Optional[str] = None,
    keyword:  Optional[str] = None,
) -> list[dict]:
    
    if not records:
        return []

    step1a = filter_by_area(records, area)
    step1b = filter_by_category(step1a, category)
    step2  = search_by_keyword(step1b, keyword)
    
    # Memanggil fungsi Timsort
    step3  = sort_by_price(step2)

    return step3