"""
test_scraper.py — Test scrape untuk verify clean_price() fix
==============================================================
Scrape 1 page dari Superindo untuk verify harga normal vs promo.
"""

import json
import sys
sys.path.insert(0, r"D:\Ujicoba")

from scraper import scrape_retailer

def main():
    print("=" * 60)
    print("TEST SCRAPE: Verify clean_price() fix")
    print("=" * 60)

    # Run scrape for Superindo makanan-minuman category, 1 page only
    print("\nScraping makanan-minuman.superindo (1 page)...\n")
    results = scrape_retailer("makanan-minuman.superindo", "Superindo", max_pages=1)

    # Save results to JSON
    output_path = r"D:\Ujicoba\test_scrape_output.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Analyze results
    total = len(results)
    promo_items = [r for r in results if r.get('jenis_harga') == 'PROMO' and r.get('harga_normal', 0) > r.get('harga_promo', 0)]
    reguler_items = [r for r in results if r.get('jenis_harga') == 'REGULER' or r.get('harga_normal', 0) == r.get('harga_promo', 0)]

    print("\n" + "=" * 60)
    print("TEST SCRAPE RESULTS")
    print("=" * 60)
    print(f"Total products scraped: {total}")
    print(f"Products with price difference (PROMO): {len(promo_items)}")
    print(f"Products with same price (REGULER): {len(reguler_items)}")

    # Sample promo products
    if promo_items:
        print(f"\nSample PROMO products (showing 3):")
        for i, item in enumerate(promo_items[:3], 1):
            nama = item.get('nama_produk', 'Unknown')
            normal = item.get('harga_normal', 0)
            promo = item.get('harga_promo', 0)
            diskon = item.get('diskon_persen', 0)
            print(f"  {i}. {nama}")
            print(f"     Normal: Rp{normal:,}, Promo: Rp{promo:,}, Diskon: {diskon}%")
    else:
        print("\nNo PROMO products found.")

    # Sample reguler products
    if reguler_items:
        print(f"\nSample REGULER products (showing 2):")
        for i, item in enumerate(reguler_items[:2], 1):
            nama = item.get('nama_produk', 'Unknown')
            normal = item.get('harga_normal', 0)
            promo = item.get('harga_promo', 0)
            diskon = item.get('diskon_persen', 0)
            print(f"  {i}. {nama}")
            print(f"     Normal: Rp{normal:,}, Promo: Rp{promo:,}, Diskon: {diskon}%")

    print("\n" + "=" * 60)

    # Final verdict
    if len(promo_items) > 0:
        print("SUCCESS: Scraper fix WORKS - found products with harga_normal > harga_promo")
    else:
        print("ISSUE: No promo products found - scraper may not be extracting price differences correctly")
    print("=" * 60)

    return len(promo_items) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)