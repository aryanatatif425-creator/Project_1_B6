import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class NewsScraper:
    """
    ADAPTASI: Scraper untuk produk hemat.id
    """

    def __init__(self, headless=True):
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--disable-gpu")

        self.driver = None

    def start_driver(self):
        if not self.driver:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
        self.driver = None

    def scrape_products(self, url, limit=10):
        """
        Ambil produk dari hemat.id (versi awal)
        """
        self.start_driver()
        self.driver.get(url)

        time.sleep(5)  # tunggu JS render

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        products = []

        # DEBUG: cek isi HTML
        print("Halaman berhasil di-load")

        # Ambil semua div (sementara)
        items = soup.find_all("div")

        for item in items:
            text = item.get_text(" ", strip=True)

            # Ambil hanya yang ada harga (Rp)
            if "Rp" not in text:
                continue

            try:
                # Ambil harga pakai regex
                match = re.search(r'Rp[\d\.\,]+', text)
                price = match.group(0) if match else "Tidak ditemukan"
            except:
                price = "Tidak ditemukan"

            try:
                # Nama (sementara ambil sebagian teks)
                name = text[:80]
            except:
                name = "Tidak ditemukan"

            try:
                img_tag = item.find("img")
                img = img_tag["src"] if img_tag else "Tidak ditemukan"
            except:
                img = "Tidak ditemukan"

            products.append({
                "nama": name,
                "harga": price,
                "gambar": img,
                "promo": "Belum tersedia"
            })

            if len(products) >= limit:
                break

        return products


# =========================
# BAGIAN UJI COBA (WAJIB)
# =========================
if __name__ == "__main__":
    scraper = NewsScraper(headless=False)

    url = "https://www.hemat.id/katalog-superindo/#goog_rewarded"

    data = scraper.scrape_products(url)

    print("\nHASIL SCRAPING:\n")
    for p in data:
        print(p)

    scraper.stop_driver()