# Blackbox Test Cases – Radar Promo 

## 1. Test Case Overview

| Total Test Cases | Features Covered | Priority |
|-----------------|-------------------|----------|
| 48 | 8 features | High/Medium/Low |

---

## 2. Test Case Table

### 2.1 Home Tab – Search & Filter (F-2)

---

#### TC-001: Filter Promo by Area – Ciwaruga
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `area_tags` including "Ciwaruga", "Sarijadi", "Gegerkalong" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click area filter dropdown<br>4. Select "Ciwaruga" |
| **Input Data** | Selected area = "Ciwaruga" |
| **Expected Result** | Only products with `area_tags` containing "Ciwaruga" are displayed. Count matches filtered data. |
| **Actual Result** | |
| **Status** | |

---

#### TC-002: Filter Promo by Area – Sarijadi
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `area_tags` including "Sarijadi" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click area filter dropdown<br>4. Select "Sarijadi" |
| **Input Data** | Selected area = "Sarijadi" |
| **Expected Result** | Only products with `area_tags` containing "Sarijadi" are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-003: Filter Promo by Area – Gegerkalong
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `area_tags` including "Gegerkalong" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click area filter dropdown<br>4. Select "Gegerkalong" |
| **Input Data** | Selected area = "Gegerkalong" |
| **Expected Result** | Only products with `area_tags` containing "Gegerkalong" are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-004: Filter Promo by Category – Sembako
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `kategori` = "Sembako" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click category button "🥬 Sembako" |
| **Input Data** | Selected category = "Sembako" |
| **Expected Result** | Only products with `kategori` = "Sembako" are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-005: Filter Promo by Category – Makanan Instan
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `kategori` = "Makanan Instan" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click category button "🍜 Makanan instan" |
| **Input Data** | Selected category = "Makanan Instan" |
| **Expected Result** | Only products with `kategori` = "Makanan Instan" are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-006: Text Search by Product Name
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `search_vector` including "minyak goreng" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Type "minyak goreng" in search bar<br>4. Observe results |
| **Input Data** | Search query = "minyak goreng" |
| **Expected Result** | Products with `search_vector` containing "minyak goreng" are displayed (case-insensitive). |
| **Actual Result** | |
| **Status** | |

---

#### TC-007: Text Search by Store Name
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products from "Alfamart Warugajaya" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Type "Alfamart Warugajaya" in search bar<br>4. Observe results |
| **Input Data** | Search query = "Alfamart Warugajaya" |
| **Expected Result** | Products from Alfamart Warugajaya branch are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-008: Combined Area and Category Filter
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products from multiple areas and categories |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Select area = "Ciwaruga"<br>4. Select category = "Makanan Instan" |
| **Input Data** | Area = "Ciwaruga", Category = "Makanan Instan" |
| **Expected Result** | Only products matching BOTH area AND category filters are displayed. |
| **Actual Result** | |
| **Status** | |

---

#### TC-009: Sort by Cheapest Price (Termurah)
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with varying `harga_promo` |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click sort dropdown<br>4. Select "Termurah" |
| **Input Data** | Sort option = "termurah" |
| **Expected Result** | Products are sorted by `harga_promo` ascending (lowest first). |
| **Actual Result** | |
| **Status** | |

---

#### TC-010: Sort by Most Expensive (Termahal)
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with varying `harga_promo` |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Click sort dropdown<br>4. Select "Termahal" |
| **Input Data** | Sort option = "termahal" |
| **Expected Result** | Products are sorted by `harga_promo` descending (highest first). |
| **Actual Result** | |
| **Status** | |

---

#### TC-011: PROMO Badge Display
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | `data_promo.json` contains products with `jenis_harga` = "PROMO" |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Observe product cards |
| **Input Data** | None |
| **Expected Result** | Products with `jenis_harga` = "PROMO" show green "PROMO" badge. Original price shown with strikethrough. |
| **Actual Result** | |
| **Status** | |

---

#### TC-012: No Results Found Display
| Aspect | Description |
|--------|-------------|
| **Feature** | F-2: Pencarian & Filter Promo |
| **Preconditions** | None |
| **Steps** | 1. Launch application<br>2. Go to Home tab<br>3. Type "xyzabc123notexist" in search bar |
| **Input Data** | Search query = "xyzabc123notexist" |
| **Expected Result** | Empty state is displayed with message "Tidak ada hasil" or similar. |
| **Actual Result** | |
| **Status** | |

---

### 2.2 Home Tab – Shopping Cart (F-5)

---

#### TC-013: Add Product to Cart
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | Application is on Home tab with products displayed |
| **Steps** | 1. Find a product card<br>2. Click "+" button on the product card<br>3. Observe cart icon in header |
| **Input Data** | None |
| **Expected Result** | Cart counter increments. Toast notification "Item ditambahkan" appears. |
| **Actual Result** | |
| **Status** | |

---

#### TC-014: View Cart Page
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | At least 1 item in cart |
| **Steps** | 1. Click cart icon in header (top right) |
| **Input Data** | None |
| **Expected Result** | Cart page opens showing list of items with quantities and subtotals. |
| **Actual Result** | |
| **Status** | |

---

#### TC-015: Increase Item Quantity in Cart
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | Cart page is open with at least 1 item |
| **Steps** | 1. Find an item in cart<br>2. Click "+" button next to quantity |
| **Input Data** | None |
| **Expected Result** | Quantity increments. Subtotal updates in real-time. |
| **Actual Result** | |
| **Status** | |

---

#### TC-016: Decrease Item Quantity in Cart
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | Cart page is open with item quantity > 1 |
| **Steps** | 1. Find an item in cart with quantity > 1<br>2. Click "-" button next to quantity |
| **Input Data** | None |
| **Expected Result** | Quantity decrements. Subtotal updates. |
| **Actual Result** | |
| **Status** | |

---

#### TC-017: Remove Item from Cart
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | Cart page is open with at least 1 item |
| **Steps** | 1. Find an item in cart<br>2. Click delete/trash icon |
| **Input Data** | None |
| **Expected Result** | Item is removed from cart. Total updates. |
| **Actual Result** | |
| **Status** | |

---

#### TC-018: Display Total Cost in Cart
| Aspect | Description |
|--------|-------------|
| **Feature** | F-5: Simulasi Anggaran & Keranjang Belanja |
| **Preconditions** | Cart page is open with multiple items |
| **Steps** | 1. Open cart page<br>2. Observe total cost display |
| **Input Data** | None |
| **Expected Result** | Total cost equals sum of (item price × quantity) for all items. Displayed as "Rp X.XXX". |
| **Actual Result** | |
| **Status** | |

---

### 2.3 Recommendations Tab – Map (F-3)

---

#### TC-019: Map Renders with Blue Store Pins
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Application is on Recommendations tab |
| **Steps** | 1. Go to Recommendations tab<br>2. Wait for map to load<br>3. Observe blue pins |
| **Input Data** | None |
| **Expected Result** | Map displays with blue pins for stores (Alfamart, Indomaret, Yomart). Tiles load from OpenStreetMap. |
| **Actual Result** | |
| **Status** | |

---

#### TC-020: Store Pin Popup Shows Details
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Map is loaded with blue store pins |
| **Steps** | 1. Click on a blue store pin<br>2. Observe popup |
| **Input Data** | None |
| **Expected Result** | Popup shows store name, branch, address, hours, and promo count if applicable. |
| **Actual Result** | |
| **Status** | |

---

#### TC-021: Radar Animation on Stores with Promos
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Map is loaded, stores have promo items |
| **Steps** | 1. Go to Recommendations tab<br>2. Look for blue pins with active promos |
| **Input Data** | None |
| **Expected Result** | Blue pins with active promos show animated radar pulse circles expanding outward. |
| **Actual Result** | |
| **Status** | |

---

#### TC-022: Green Recommendation Pins Display
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | `rekomendasi.json` contains recommendations OR demo recommendations exist |
| **Steps** | 1. Go to Recommendations tab<br>2. Observe green pins on map |
| **Input Data** | None |
| **Expected Result** | Green pins appear at recommendation locations. |
| **Actual Result** | |
| **Status** | |

---

#### TC-023: Click Green Pin Opens Detail Panel
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Map has green recommendation pins |
| **Steps** | 1. Click on a green pin<br>2. Observe right-side panel |
| **Input Data** | None |
| **Expected Result** | Detail panel slides in from right showing: name, rating (stars), menu, price, address, contributor, photo. |
| **Actual Result** | |
| **Status** | |

---

#### TC-024: Close Recommendation Detail Panel
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Recommendation detail panel is open |
| **Steps** | 1. Click "←" back button or "✕" close button |
| **Input Data** | None |
| **Expected Result** | Panel closes. Map is visible again. |
| **Actual Result** | |
| **Status** | |

---

#### TC-025: Reaction Buttons on Recommendation Detail
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Recommendation detail panel is open |
| **Steps** | 1. Open recommendation detail<br>2. Look for "Murah" and "Enak Banget" buttons |
| **Input Data** | None |
| **Expected Result** | Two reaction buttons visible: "Murah" and "Enak Banget" with current counts. |
| **Actual Result** | |
| **Status** | |

---

#### TC-026: Add New Recommendation – Open Form
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Application is on Recommendations tab |
| **Steps** | 1. Click green "+ Tambah Rekomendasi" floating button |
| **Input Data** | None |
| **Expected Result** | Right-side panel slides in with form fields: Nama Tempat, Alamat, Menu Andalan, Harga, Rating, Deskripsi, Foto, Kontributor. |
| **Actual Result** | |
| **Status** | |

---

#### TC-027: Add New Recommendation – Fill Form
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Recommendation form panel is open |
| **Steps** | 1. Fill in "Nama Tempat" = "Nasi Goreng Bude"<br>2. Fill in "Menu Andalan" = "Nasi Goreng Special"<br>3. Fill in "Harga" = 15000<br>4. Click rating stars to set 4 stars<br>5. Leave other fields optional |
| **Input Data** | name="Nasi Goreng Bude", menu="Nasi Goreng Special", harga=15000, rating=4 |
| **Expected Result** | Form accepts input. Fields show entered values. |
| **Actual Result** | |
| **Status** | |

---

#### TC-028: Pick Location from Map
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Recommendation form is open |
| **Steps** | 1. Click "📍 Pilih dari Peta" button<br>2. Click on map location<br>3. Observe lat/lon fields |
| **Input Data** | Click on map at approx. -6.8620, 107.5750 |
| **Expected Result** | Latitude and Longitude fields populate with selected coordinates. Red pin appears at location. |
| **Actual Result** | |
| **Status** | |

---

#### TC-029: Upload Photo for Recommendation
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Recommendation form is open |
| **Steps** | 1. Click "📷 Pilih Gambar" button<br>2. Select a JPG/PNG image file |
| **Input Data** | Image file (e.g., test_photo.jpg) |
| **Expected Result** | Photo preview appears in form. Image uploaded to Catbox after submission. |
| **Actual Result** | |
| **Status** | |

---

#### TC-030: Submit New Recommendation
| Aspect | Description |
|--------|-------------|
| **Feature** | F-3: Peta Interaktif & Crowdsourcing Rekomendasi |
| **Preconditions** | Form is filled with valid data |
| **Steps** | 1. Fill required fields<br>2. Click "Kirim Rekomendasi" button |
| **Input Data** | Valid recommendation data |
| **Expected Result** | Success dialog "Rekomendasi berhasil ditambahkan!". Panel closes. New green pin appears on map. |
| **Actual Result** | |
| **Status** | |

---

### 2.4 Statistics Tab (F-4)

---

#### TC-031: Bar Chart Displays Top 3 Stores
| Aspect | Description |
|--------|-------------|
| **Feature** | F-4: Visualisasi Data Statistik |
| **Preconditions** | Application is on Statistics tab |
| **Steps** | 1. Go to Statistics tab<br>2. Observe bar chart |
| **Input Data** | None |
| **Expected Result** | Bar chart shows "3 Toko dengan Promo Terbanyak" with 3 bars. Y-axis shows counts with thousand separators (e.g., "1,234"). |
| **Actual Result** | |
| **Status** | |

---

#### TC-032: Pie Chart Displays Category Distribution
| Aspect | Description |
|--------|-------------|
| **Feature** | F-4: Visualisasi Data Statistik |
| **Preconditions** | Application is on Statistics tab |
| **Steps** | 1. Go to Statistics tab<br>2. Observe pie/donut chart |
| **Input Data** | None |
| **Expected Result** | Donut chart shows category composition. Legend on right shows category names with percentages. Small slices (< 5%) grouped into "Lainnya". |
| **Actual Result** | |
| **Status** | |

---

#### TC-033: Statistics Summary Cards
| Aspect | Description |
|--------|-------------|
| **Feature** | F-4: Visualisasi Data Statistik |
| **Preconditions** | Application is on Statistics tab |
| **Steps** | 1. Go to Statistics tab<br>2. Observe summary cards at bottom |
| **Input Data** | None |
| **Expected Result** | Three cards show: Total Produk Promo, Toko dengan Promo, Kategori Tersedia. Numbers match actual data. |
| **Actual Result** | |
| **Status** | |

---

#### TC-034: Statistics Using Real Data (Not Demo)
| Aspect | Description |
|--------|-------------|
| **Feature** | F-4: Visualisasi Data Statistik |
| **Preconditions** | `data_promo.json` contains real promo data |
| **Steps** | 1. Go to Statistics tab<br>2. Note the store counts in bar chart<br>3. Compare with actual promo items per store in data_promo.json |
| **Input Data** | None |
| **Expected Result** | Bar chart reflects actual promo counts from data_promo.json, not hardcoded demo data (20 items). |
| **Actual Result** | |
| **Status** | |

---

### 2.5 Settings Tab

---

#### TC-035: Toggle Dark Mode
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Personalisasi (Theme) |
| **Preconditions** | Application is on Settings tab |
| **Steps** | 1. Go to Settings tab<br>2. Find dark mode toggle<br>3. Toggle dark mode on |
| **Input Data** | None |
| **Expected Result** | UI colors change to dark theme. Nav bar, cards, buttons update to dark palette. |
| **Actual Result** | |
| **Status** | |

---

#### TC-036: Toggle Back to Light Mode
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Personalisasi (Theme) |
| **Preconditions** | Dark mode is currently on |
| **Steps** | 1. Go to Settings tab<br>2. Toggle dark mode off |
| **Input Data** | None |
| **Expected Result** | UI colors revert to light theme. |
| **Actual Result** | |
| **Status** | |

---

#### TC-037: Font Size Adjustment
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Personalisasi (Font Size) |
| **Preconditions** | Application is on Settings tab |
| **Steps** | 1. Go to Settings tab<br>2. Find font size control<br>3. Adjust to larger size |
| **Input Data** | Font size = "Besar" |
| **Expected Result** | Text throughout the application increases in size. |
| **Actual Result** | |
| **Status** | |

---

#### TC-038: About Information Display
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Personalisasi (About) |
| **Preconditions** | Application is on Settings tab |
| **Steps** | 1. Go to Settings tab<br>2. Scroll to About section |
| **Input Data** | None |
| **Expected Result** | About section shows: App name "Radar Promo", version, team names. |
| **Actual Result** | |
| **Status** | |

---

#### TC-039: Admin Login – Correct Password
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Admin Access |
| **Preconditions** | Application is on Settings tab |
| **Steps** | 1. Click "Masuk sebagai Admin" button<br>2. Enter correct password<br>3. Click OK/Submit |
| **Input Data** | Password = "<ganti_dengan_password_admin>" (nilai dari environment RADAR_ADMIN_PASSWORD) |
| **Expected Result** | Admin Dashboard (Tkinter window) opens with sync, upload, and log viewer tools. |
| **Actual Result** | |
| **Status** | |

---

#### TC-040: Admin Login – Wrong Password
| Aspect | Description |
|--------|-------------|
| **Feature** | F-1: Admin Access |
| **Preconditions** | Application is on Settings tab |
| **Steps** | 1. Click "Masuk sebagai Admin" button<br>2. Enter wrong password<br>3. Click OK/Submit |
| **Input Data** | Password = "wrongpassword" |
| **Expected Result** | Error message "Password salah" or similar. Admin dashboard does not open. |
| **Actual Result** | |
| **Status** | |

---

### 2.6 Admin Tool (F-6)

---

#### TC-041: Scrape Data from hemat.id
| Aspect | Description |
|--------|-------------|
| **Feature** | F-6: Dashboard Admin (Scraping) |
| **Preconditions** | Admin dashboard is open |
| **Steps** | 1. Click "Sinkronisasi Sekarang" button<br>2. Wait for progress to complete |
| **Input Data** | None |
| **Expected Result** | Progress bar shows. Data is scraped and saved to `data_promo.json`. Success message appears. |
| **Actual Result** | |
| **Status** | |

---

#### TC-042: Upload Promo to Cloud
| Aspect | Description |
|--------|-------------|
| **Feature** | F-6: Dashboard Admin (Cloud Upload) |
| **Preconditions** | Admin dashboard is open, data_promo.json has data |
| **Steps** | 1. Click "Upload Promo ke Cloud" button<br>2. Wait for upload to complete |
| **Input Data** | None |
| **Expected Result** | Data is uploaded to Google Sheets (Replace strategy). Success message appears. |
| **Actual Result** | |
| **Status** | |

---

#### TC-043: View Activity Log
| Aspect | Description |
|--------|-------------|
| **Feature** | F-6: Dashboard Admin (Log Viewer) |
| **Preconditions** | Admin dashboard is open |
| **Steps** | 1. Scroll to Log Viewer section<br>2. Observe log entries |
| **Input Data** | None |
| **Expected Result** | Log entries show timestamp, action type (SCRAPE, UPLOAD, ERROR), and message. |
| **Actual Result** | |
| **Status** | |

---

### 2.7 Data Persistence & Edge Cases

---

#### TC-044: App Loads with Missing data_promo.json
| Aspect | Description |
|--------|-------------|
| **Feature** | Data Persistence |
| **Preconditions** | `data_promo.json` does not exist |
| **Steps** | 1. Delete `data_promo.json`<br>2. Launch application |
| **Input Data** | None |
| **Expected Result** | Application uses demo data and functions normally. Error is logged but user sees normal UI. |
| **Actual Result** | |
| **Status** | |

---

#### TC-045: App Loads with Corrupted JSON (BOM Issue)
| Aspect | Description |
|--------|-------------|
| **Feature** | Data Persistence |
| **Preconditions** | `rekomendasi.json` has UTF-8 BOM that causes JSON parse error |
| **Steps** | 1. Ensure `rekomendasi.json` has BOM (created by Windows Notepad)<br>2. Launch application<br>3. Go to Recommendations tab<br>4. Add new recommendation<br>5. Restart application |
| **Input Data** | Valid recommendation data |
| **Expected Result** | App reads file correctly with `utf-8-sig` encoding. Recommendations persist across restarts. |
| **Actual Result** | |
| **Status** | |

---

#### TC-046: Cloud Sync Failure – Offline Mode
| Aspect | Description |
|--------|-------------|
| **Feature** | Data Persistence |
| **Preconditions** | No internet connection |
| **Steps** | 1. Disconnect from internet<br>2. Launch application<br>3. Try to refresh recommendations |
| **Input Data** | None |
| **Expected Result** | App works offline with cached local data. Error logged but UI shows cached recommendations. |
| **Actual Result** | |
| **Status** | |

---

#### TC-047: Photo Upload Failure (Catbox)
| Aspect | Description |
|--------|-------------|
| **Feature** | Photo Upload |
| **Preconditions** | Form is open for new recommendation |
| **Steps** | 1. Fill recommendation form<br>2. Attach photo<br>3. Submit |
| **Input Data** | Photo that is too large or network timeout |
| **Expected Result** | Error toast "Gagal mengunggah foto" appears. User can retry or submit without photo. |
| **Actual Result** | |
| **Status** | |

---

#### TC-048: Google Sheets API Failure
| Aspect | Description |
|--------|-------------|
| **Feature** | Cloud Sync |
| **Preconditions** | App has internet but Google Apps Script is down |
| **Steps** | 1. Launch application<br>2. Go to Recommendations tab<br>3. Click refresh button |
| **Input Data** | None |
| **Expected Result** | App falls back to local `rekomendasi.json` or demo data. Error logged. UI remains functional. |
| **Actual Result** | |
| **Status** | |

---

## 3. Coverage Matrix

| Feature | Test Cases |
|---------|------------|
| **F-1: Admin Access** | TC-039, TC-040 |
| **F-2: Search & Filter Promo** | TC-001 to TC-012 |
| **F-3: Map & Recommendations** | TC-019 to TC-030 |
| **F-4: Statistics Visualization** | TC-031 to TC-034 |
| **F-5: Cart & Budget** | TC-013 to TC-018 |
| **F-6: Admin Dashboard** | TC-041 to TC-043 |
| **Data Persistence** | TC-044 to TC-048 |

---

## 4. Edge Cases Summary

| ID | Edge Case | Covered By |
|----|-----------|------------|
| E1 | Missing data_promo.json | TC-044 |
| E2 | Corrupted JSON with BOM | TC-045 |
| E3 | Offline mode | TC-046 |
| E4 | Photo upload failure | TC-047 |
| E5 | Cloud API failure | TC-048 |
| E6 | Empty search results | TC-012 |
| E7 | Invalid password | TC-040 |
| E8 | Very large numbers in statistics | TC-031 |
| E9 | Many small pie slices | TC-032 |
| E10 | Map tiles fail to load | (Manual verify – network dependent) |

---

## 5. Test Execution Notes

### Pre-Test Setup
1. Ensure `data_promo.json` contains at least 50 products across 3 areas
2. Ensure `rekomendasi.json` exists with at least 3 recommendations
3. Ensure internet connection is available for cloud tests

### Test Sequence Recommendation
1. Start with Home tab tests (TC-001 to TC-012)
2. Then Cart tests (TC-013 to TC-018)
3. Then Recommendations/Map tests (TC-019 to TC-030)
4. Then Statistics tests (TC-031 to TC-034)
5. Then Settings tests (TC-035 to TC-040)
6. Then Admin tests (TC-041 to TC-043)
7. Finally Edge cases (TC-044 to TC-048)

### Expected Time
- Full test suite: ~45-60 minutes
- Quick smoke test (priority tests only): ~15-20 minutes