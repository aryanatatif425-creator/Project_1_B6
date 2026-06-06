"""
engine.py — Radar Promo Algorithm Engine
=========================================
Mesin logika: filter, search, sort, statistik, validasi.
"""

from collections import Counter
from typing import Optional, List, Dict, Tuple


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
    result = [r for r in records if r.get("category", "").strip() == cat_norm]
    print(f"DEBUG filter_by_category: category='{cat_norm}', records_count={len(records)}, filtered_count={len(result)}")
    return result


def filter_by_brand(records: List[Dict], brand: Optional[str]) -> List[Dict]:
    if not brand or brand.strip().lower() in ("", "semua toko"):
        return records
    brand_norm = brand.strip().lower()
    return [r for r in records if r.get("brand_toko", "").lower() == brand_norm]


def filter_by_brand_multi(records: List[Dict], brands: List[str]) -> List[Dict]:
    if not brands:
        return records
    return [r for r in records if r.get("brand_toko", "") in brands]


def filter_by_jenis_harga(records: List[Dict], jenis: Optional[str]) -> List[Dict]:
    if not jenis or jenis.strip().lower() in ("", "semua jenis"):
        return records
    jenis_norm = jenis.strip()
    return [r for r in records if r.get("jenis_harga") == jenis_norm]


def normalize_promo_data(records: List[Dict]) -> List[Dict]:
    count = 0
    promo_count = 0
    for r in records:
        diskon = r.get("diskon_persen", 0)
        needs_recalc = False
        
        if isinstance(diskon, str):
            if diskon.strip():
                try:
                    diskon = float(diskon)
                except:
                    needs_recalc = True
            else:
                needs_recalc = True
        elif diskon is None or diskon <= 0:
            needs_recalc = True
        
        if needs_recalc:
            harga_normal = r.get("harga_normal", 0) or 0
            harga_promo = r.get("harga_promo", 0) or 0
            if harga_normal > 0 and harga_promo > 0 and harga_normal > harga_promo:
                diskon = round(100 * (harga_normal - harga_promo) / harga_normal, 1)
                r["diskon_persen"] = diskon
                r["jenis_harga"] = "PROMO"
                count += 1
                promo_count += 1
            else:
                r["diskon_persen"] = 0
                r["jenis_harga"] = "REGULER"
    
    print(f"[NORMALIZE] {count} products recalculated, {promo_count} confirmed as PROMO")
    return records


def filter_promo_items(records: List[Dict]) -> List[Dict]:
    """Filter to only promotional items with actual discount."""
    passed = 0
    total = len(records)
    result = []
    for r in records:
        diskon = r.get("diskon_persen", 0)
        jenis = r.get("jenis_harga", "")
        
        if isinstance(diskon, str):
            if diskon.strip():
                try:
                    diskon = float(diskon)
                except:
                    diskon = 0.0
            else:
                diskon = 0.0
        
        if diskon <= 0:
            harga_normal = r.get("harga_normal", 0) or 0
            harga_promo = r.get("harga_promo", 0) or 0
            if harga_normal > 0 and harga_promo > 0 and harga_normal > harga_promo:
                diskon = round(100 * (harga_normal - harga_promo) / harga_normal, 1)
        
        if diskon > 0 or jenis == "PROMO":
            passed += 1
            result.append(r)
    
    print(f"[FILTER] {passed}/{total} products pass promo filter")
    return result


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
    reverse: Optional[bool] = False,
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
    step8 = sort_by_price(step7, reverse=reverse) if reverse is not None else step7
    stats = get_statistics(step8)

    return step8, stats