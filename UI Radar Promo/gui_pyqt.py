import os
import sys
import logging
import time
import urllib.request
import threading
import math
from datetime import datetime
from io import BytesIO
import requests
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QGridLayout,
    QFrame, QStackedWidget, QSizePolicy, QComboBox, QDialog,
    QGraphicsDropShadowEffect, QMessageBox, QSlider, QTextEdit,
    QListWidget, QListWidgetItem, QCheckBox, QRadioButton,
    QButtonGroup, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal as Signal, QThread, QObject, QRect, QUrl, pyqtSlot, QPointF
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QColor, QLinearGradient, QBrush,
    QPen, QPainterPath, QImage, QFontMetrics
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineProfile
from PyQt6.QtWebChannel import QWebChannel

import data_manager
import engine

PRODUCTS = [

    {"id":"2",  "name":"Minyak Goreng 2L",          "category":"Sembako",        "price":32000, "harga_normal":40000, "effective_price":32000, "diskon_persen":20, "is_promo":True,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=400&fit=crop"},
    {"id":"3",  "name":"Gula Pasir 1kg",            "category":"Sembako",        "price":14000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1582381804013-81e8e2b82146?w=400&h=400&fit=crop"},

    {"id":"5",  "name":"Indomie Goreng (5 pcs)",    "category":"Makanan Instan", "price":12500, "harga_normal":16000, "effective_price":12500, "diskon_persen":22, "is_promo":True,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=400&fit=crop"},
    {"id":"6",  "name":"Pop Mie Ayam Bawang",       "category":"Makanan Instan", "price":6500,  "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=400&h=400&fit=crop"},

    {"id":"8",  "name":"Susu Kental Manis 380g",    "category":"Makanan Instan", "price":13000, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop"},
    {"id":"9",  "name":"Sabun Mandi Lifebuoy 3pcs", "category":"Mandi",          "price":15000, "harga_normal":19000, "effective_price":15000, "diskon_persen":21, "is_promo":True,  "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1585828923118-587afa12bcc5?w=400&h=400&fit=crop"},

    {"id":"11", "name":"Pasta Gigi Pepsodent",      "category":"Mandi",          "price":9500,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1622286346003-c44d93e0cc47?w=400&h=400&fit=crop"},
    {"id":"12", "name":"Sabun Cuci Piring 800ml",   "category":"Mandi",          "price":12000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1608042314453-ae338d5053d2?w=400&h=400&fit=crop"},

    {"id":"14", "name":"Vitamin C 100 tablet",      "category":"Kesehatan",      "price":35000, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1550572017-4c0f2e5e8f6c?w=400&h=400&fit=crop"},
    {"id":"15", "name":"Hand Sanitizer 500ml",      "category":"Kesehatan",      "price":28000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1584744982334-e8d2f7947871?w=400&h=400&fit=crop"},

    {"id":"17", "name":"Chitato Sapi Panggang",     "category":"Snack",          "price":9500,  "harga_normal":12500, "effective_price":9500, "diskon_persen":24, "is_promo":True,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400&h=400&fit=crop"},
    {"id":"18", "name":"Oreo Chocolate 137g",       "category":"Snack",          "price":10500, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop"},

    {"id":"20", "name":"Tango Wafer Coklat",        "category":"Snack",          "price":7500,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1586526564426-a3242d4c7b4e?w=400&h=400&fit=crop"},
]

CATEGORIES  = ["Semua", "Sembako", "Makanan Instan", "Mandi", "Kesehatan", "Snack", "Minuman"]
CAT_EMOJI = {
    "Semua": "Semua",
    "Sembako": "🥬 Sembako",
    "Makanan Instan": "🍜 Makanan instan",
    "Mandi": "🧴 Mandi",
    "Kesehatan": "💊 Kesehatan",
    "Snack": "🍪 Snack",
    "Minuman": "🥤 Minuman",
}
AREAS       = ["Semua Area", "Ciwaruga", "Sarijadi", "Gegerkalong"]
PROMO_IDS   = {"2","5","9","13","17","19"}   # produk yang sedang promo

LIGHT = {
    "bg":"#FFFFFF","nav_bg":"#FFFFFF","nav_border":"#E5E7EB",
    "banner_from":"#25C799","banner_to":"#25C799",
    "filter_bg":"#FFFFFF","filter_border":"#E5E7EB",
    "pill_off_bg":"#F3F4F6","pill_off_fg":"#374151",
    "pill_on_bg":"#25C799","pill_on_fg":"#FFFFFF",
    "card_bg":"#FFFFFF","card_border":"#696868","card_img_bg":"#F3F4F6",
    "price_fg":"#25C799","store_fg":"#6B7280","dist_fg":"#25C799",
    "add_bg":"#25C799","add_fg":"#FFFFFF",
    "text1":"#1F2937","text2":"#6B7280",
    "badge_bg":"#D1FAE5","badge_fg":"#25C799",
    "promo_badge_bg":"#25C799","promo_badge_fg":"#FFFFFF",
    "search_bg":"#F3F4F6","search_border":"#E5E7EB","search_fg":"#374151",
    "btn_bg":"#F3F4F6","btn_fg":"#374151",
    "bottom_bg":"#FFFFFF","bottom_border":"#E5E7EB",
    "bottom_active_bg":"#25C799","bottom_active_fg":"#FFFFFF","bottom_fg":"#9CA3AF",
    "cart_bg":"#FFFFFF","cart_card_bg":"#FFFFFF","cart_item_bg":"#F3F4F6",
    "budget_bg":"#FFFFFF","budget_border":"#25C799",
    "total_bg":"#F3F4F6","remain_bg":"#D1FAE5","remain_fg":"#25C799",
    "over_bg":"#FEE2E2","over_fg":"#DC2626",
    "prog_bg":"#E5E5E5","divider":"#E5E7EB",
    "combo_bg":"#F3F4F6","combo_border":"#E5E7EB",
    "stat_bg":"#F3F4F6","stat_card_bg":"#FFFFFF",
    "chart_colors":["#25C799","#34D399","#6EE7B7","#A7F3D0","#D1FAE5"],
    "setting_bg":"#F3F4F6","setting_card_bg":"#FFFFFF",
    "input_bg":"#F3F4F6","input_border":"#E5E7EB",
    "loc_bg":"#F3F4F6","loc_card_bg":"#FFFFFF",
    "toast_bg":"#25C799","toast_fg":"#FFFFFF",
}

DARK = {
    "bg":"#2c2c2e","nav_bg":"#2c2c2e","nav_border":"#3c3c3e",
    "banner_from":"#0d9488","banner_to":"#0d9488",
    "filter_bg":"#2c2c2e","filter_border":"#3c3c3e",
    "pill_off_bg":"#3c3c3e","pill_off_fg":"#99f6e4",
    "pill_on_bg":"#0d9488","pill_on_fg":"#FFFFFF",
    "card_bg":"#3c3c3e","card_border":"#696868","card_img_bg":"#4c4c4e",
    "price_fg":"#0d9488","store_fg":"#86a895","dist_fg":"#5eead4",
    "add_bg":"#0d9488","add_fg":"#ffffff",
    "text1":"#FFFFFF","text2":"#a5a5a5",
    "badge_bg":"#1a3d3e","badge_fg":"#0d9488",
    "promo_badge_bg":"#0d9488","promo_badge_fg":"#FFFFFF",
    "search_bg":"#3c3c3e","search_border":"#4c4c4e","search_fg":"#FFFFFF",
    "btn_bg":"#3c3c3e","btn_fg":"#0d9488",
    "bottom_bg":"#3c3c3e","bottom_border":"#4c4c4e",
    "bottom_active_bg":"#0d9488","bottom_active_fg":"#FFFFFF","bottom_fg":"#9ca3af",
    "cart_bg":"#2c2c2e","cart_card_bg":"#3c3c3e","cart_item_bg":"#4c4c4e",
    "budget_bg":"#0d9488","budget_border":"#0d9488",
    "total_bg":"#3c3c3e","remain_bg":"#1a3d3e","remain_fg":"#0d9488",
    "over_bg":"#3d1515","over_fg":"#dc2626",
    "prog_bg":"#3c3c3e","divider":"#4c4c4e",
    "combo_bg":"#3c3c3e","combo_border":"#4c4c4e",
    "stat_bg":"#2c2c2e","stat_card_bg":"#3c3c3e",
    "chart_colors":["#0d9488","#14b8a6","#2dd4bf","#5eead4","#99f6e4"],
    "setting_bg":"#2c2c2e","setting_card_bg":"#3c3c3e",
    "input_bg":"#3c3c3e","input_border":"#4c4c4e",
    "loc_bg":"#2c2c2e","loc_card_bg":"#3c3c3e",
    "toast_bg":"#0d9488","toast_fg":"#FFFFFF",
}
# ═══════════════════════════════════════════════════════════════════════════════
# UTILS
# ═══════════════════════════════════════════════════════════════════════════════

def rp(n): return "Rp " + f"{int(n):,}".replace(",", ".")

def drop_shadow(w, blur=18, color="#00000020", dy=4):
    ef = QGraphicsDropShadowEffect()
    ef.setBlurRadius(blur)
    ef.setColor(QColor(color))
    ef.setOffset(0, dy)
    w.setGraphicsEffect(ef)

# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE LOADER
# ═══════════════════════════════════════════════════════════════════════════════

_cache, _lock = {}, threading.Lock()
_img_sem = threading.Semaphore(6)

class _Sig(QObject):
    done = Signal(str, QPixmap)

class ImgLoader(QThread):
    def __init__(self, url, pid, w, h, sig):
        super().__init__()
        self.url = url; self.pid = pid; self.w = w; self.h = h; self.sig = sig
    def run(self):
        _img_sem.acquire()
        try:
            with _lock:
                if self.pid in _cache:
                    self.sig.done.emit(self.pid, _cache[self.pid])
                    return
            try:
                req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=6) as r:
                    data = r.read()
                img = Image.open(BytesIO(data)).convert("RGBA")
                s = min(img.width, img.height)
                img = img.crop(((img.width-s)//2, (img.height-s)//2, (img.width+s)//2, (img.height+s)//2))
                img = img.resize((self.w, self.h), Image.Resampling.LANCZOS)
                mask = Image.new("L", img.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle([(0, 0), img.size], radius=14, fill=255)
                img.putalpha(mask)
                qimg = QImage(img.tobytes("raw", "RGBA"), img.width, img.height, QImage.Format.Format_RGBA8888)
                px = QPixmap.fromImage(qimg)
                with _lock: _cache[self.pid] = px
                self.sig.done.emit(self.pid, px)
            except Exception:
                self.sig.done.emit(self.pid, QPixmap())
        finally:
            _img_sem.release()

# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATION UPLOADER (QThread)
# ═══════════════════════════════════════════════════════════════════════════════

class RecUploadSignals(QObject):
    success = Signal(str)  # foto_url
    failure = Signal(str)  # error message

class RecommendationUploader(QThread):
    """Upload photo to ImgBB and sync recommendation to Google Sheets."""
    def __init__(self, photo, recommendation):
        super().__init__()
        self.photo = photo
        self.recommendation = recommendation
        self.signals = RecUploadSignals()

    def run(self):
        try:
            foto_url = data_manager.upload_photo(self.photo)
            if not foto_url:
                self.signals.failure.emit("Gagal mengunggah foto ke ImgBB")
                return

            entry = self.recommendation.copy()
            entry["foto_url"] = foto_url

            success = data_manager.add_rekomendasi(entry)
            if success:
                self.signals.success.emit(foto_url)
            else:
                self.signals.failure.emit("Gagal mengirim rekomendasi ke Google Sheets")
        except Exception as e:
            self.signals.failure.emit(str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# JS BRIDGE (QWebChannel)
# ═══════════════════════════════════════════════════════════════════════════════

class JSBridge(QObject):
    """Exposes Python methods to JavaScript in the map web view."""
    upload_success = Signal(str)
    upload_failure = Signal(str)

    def __init__(self, page, toast, t, parent=None):
        super().__init__(parent)
        self.page = page  # LokasiPage reference
        self.toast = toast
        self.t = t
        self._uploader = None

    @pyqtSlot(str)
    def submitRecommendation(self, json_data):
        import json as json_lib
        try:
            data = json_lib.loads(json_data)
        except Exception:
            self.upload_failure.emit("Format data tidak valid")
            return

        nama = data.get("nama", "")
        address = data.get("address", "")
        menu = data.get("menu", "")
        harga = data.get("harga", 0)
        description = data.get("description", "")
        contributor = data.get("contributor", "Anonim")
        rating = data.get("rating", 5)
        lat = data.get("lat", None)
        lon = data.get("lon", None)
        photo = data.get("photo", None)

        logging.info(f"Recommendation received: {nama}, {menu}, Rp{harga}, lat={lat}, lon={lon}, rating={rating}")
        if not nama or not menu or not harga or not lat or not lon:
            self.upload_failure.emit("Data tidak lengkap")
            return

        try:
            harga_val = int(harga) if isinstance(harga, int) else int(str(harga).replace(".", "").replace(",", ""))
            lat_val = float(lat)
            lon_val = float(lon)
            rating_val = float(rating) if rating else 0.0
        except ValueError:
            self.upload_failure.emit("Format data tidak valid")
            return

        recommendation = {
            "nama": nama,
            "menu": menu,
            "harga": harga_val,
            "latitude": lat_val,
            "longitude": lon_val,
            "rating": rating_val,
            "alamat": address,
            "description": description,
            "contributor": contributor,
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save locally first for persistence
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rekomendasi.json")
        try:
            local_recs = []
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8") as f:
                    local_recs = json_lib.load(f)
            local_recs.append(recommendation)
            with open(local_path, "w", encoding="utf-8") as f:
                json_lib.dump(local_recs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save recommendation locally: {e}")

        if self._uploader and self._uploader.isRunning():
            self._uploader.terminate()
            self._uploader.wait()

        self._last_recommendation = recommendation
        self._uploader = RecommendationUploader(photo, recommendation)
        self._uploader.signals.success.connect(self._on_upload_success)
        self._uploader.signals.failure.connect(self._on_upload_failure)
        self._uploader.start()

    def _on_upload_success(self, foto_url):
        self.toast.show_msg("Rekomendasi berhasil ditambahkan!", self.t)
        self.upload_success.emit(foto_url)
        rec = getattr(self, '_last_recommendation', None)
        if rec and hasattr(self.page, 'web_view'):
            rec_lat = rec.get('latitude', -6.8701)
            rec_lon = rec.get('longitude', 107.5954)
            popup_html = f"<div class='popup-title'>{rec.get('nama','')}</div>"
            menu = rec.get('menu', '')
            if menu:
                popup_html += f"<div>{menu}</div>"
            harga = rec.get('harga', 0)
            if harga:
                popup_html += f"<div>Rp {int(harga):,}</div>"
            rating = rec.get('rating', 0)
            if rating:
                popup_html += f"<span class='popup-badge badge-rating'>{rating}/5</span>"
            rec_name = rec.get('nama', '').replace("'", "\\'")
            rec_menu = menu.replace("'", "\\'") if menu else ''
            js = f"""
(function() {{
    var lat={rec_lat}, lon={rec_lon}, name='{rec_name}', rating={rating}, foto='{foto_url}', menu='{rec_menu}', harga={harga};
    var _greenIcon = L.divIcon({{
        className: 'custom-green-pin',
        html: '<div style="background:#22c55e;width:25px;height:25px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid white;box-shadow:0 0 10px rgba(34,197,94,0.6);"></div>',
        iconSize: [25, 25],
        iconAnchor: [12, 25],
        popupAnchor: [0, -20]
    }});
    var marker = L.marker([lat, lon], {{ icon: _greenIcon }}).addTo(map);
    window.recMarkers.push(marker);
    var ph = '<div class="popup-title">' + name + '</div>';
    if (menu) ph += '<div>' + menu + '</div>';
    if (harga) ph += '<div>Rp ' + Number(harga).toLocaleString('id-ID') + '</div>';
    if (rating) ph += '<span class="popup-badge badge-rating">' + rating + '/5</span>';
    ph += '<br><button onclick="window.removeRecommendation(' + lat + ', ' + lon + ')" style="margin-top:8px;padding:6px 12px;background:#ef4444;color:white;border:none;border-radius:6px;font-size:12px;cursor:pointer;">Hapus</button>';
    marker.bindPopup(ph).openPopup();
    var _circle = L.circle([lat, lon], {{ radius: 200, color: 'rgba(34,197,94,0.5)', fillColor: 'rgba(34,197,94,0.15)', fillOpacity: 0.15, weight: 2 }}).addTo(map);
    var _s = Date.now(), _d = 2000, _sr = 200, _er = 600;
    (function _a() {{ var p = Math.min((Date.now()-_s)/_d, 1); _circle.setRadius(_sr+(_er-_sr)*p); _circle.setStyle({{opacity:1-p, fillOpacity:0.15*(1-p)}}); if(p<1) {{requestAnimationFrame(_a);}} else {{map.removeLayer(_circle);}} }})();
}})();
"""
            self.page.web_view.page().runJavaScript(js)

    def _on_upload_failure(self, error_msg):
        self.toast.show_msg(f"Gagal: {error_msg}", self.t)
        self.upload_failure.emit(error_msg)

    @pyqtSlot(float, float)
    def deleteRecommendation(self, lat, lon):
        import json as json_lib
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rekomendasi.json")
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    local_recs = json_lib.load(f)
                local_recs = [r for r in local_recs if abs(r.get("latitude", 0) - lat) > 0.0001 or abs(r.get("longitude", 0) - lon) > 0.0001]
                with open(local_path, "w", encoding="utf-8") as f:
                    json_lib.dump(local_recs, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logging.warning(f"Failed to delete recommendation from local: {e}")

    @pyqtSlot(str, result=str)
    def geocode_address(self, address):
        """Search address using Nominatim (Layer 1) then LocationIQ (Layer 2). Returns 'lat,lon' or empty string."""
        import requests
        import time

        postal_codes = {
            "ciwaruga": "40559",
            "sarijadi": "40164",
            "gegerkalong": "40153",
            "sukasari": "40153",
            "cibaduyut": "40163",
            "ledeng": "40162",
        }

        bbox = {"min_lat": -6.95, "max_lat": -6.83, "min_lon": 107.55, "max_lon": 107.63}

        def in_bbox(lat, lon):
            try:
                la, lo = float(lat), float(lon)
                return bbox["min_lat"] <= la <= bbox["max_lat"] and bbox["min_lon"] <= lo <= bbox["max_lon"]
            except:
                return False

        informal_words = ["samping", "dekat", "belakang", "depan", "sekitar"]
        cleaned = address
        for word in informal_words:
            idx = cleaned.lower().find(word)
            if idx != -1:
                cleaned = cleaned[:idx].strip()
                break
        if not cleaned:
            cleaned = address.strip()

        postal_suffix = ""
        lower_addr = address.lower()
        for area, code in postal_codes.items():
            if area in lower_addr:
                postal_suffix = f", {code}"
                break

        search_query = f"{cleaned}{postal_suffix}, Bandung"

        headers = {'User-Agent': 'RadarPromo/2.0 (Polban-Student-App)'}

        def try_layer(url, params, headers, layer_name):
            print(f"[Geocoding] {layer_name}: Searching '{search_query}'...")
            time.sleep(0.6)
            try:
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                results = response.json()
                if not results:
                    print(f"[Geocoding] {layer_name}: No results for '{search_query}'")
                    return None
                lat, lon = results[0]['lat'], results[0]['lon']
                if not in_bbox(lat, lon):
                    print(f"[Geocoding] {layer_name}: REJECTED {lat},{lon} (outside Bandung bounds)")
                    return None
                print(f"[Geocoding] Success at {layer_name}: {address} -> {lat},{lon}")
                return f"{lat},{lon}"
            except Exception as e:
                print(f"[Geocoding] {layer_name} failed: {e}")
                return None

        result = try_layer(
            'https://nominatim.openstreetmap.org/search',
            {'q': search_query, 'format': 'json', 'limit': 1},
            headers, 'Layer 1 (Nominatim)'
        )
        if result:
            return result

        result = try_layer(
            'https://us1.locationiq.com/v1/search',
            {'key': 'pk.488a08e689af06b360008edf6da12813', 'q': search_query, 'format': 'json', 'limit': 1},
            {}, 'Layer 2 (LocationIQ)'
        )
        if result:
            return result

        print(f"[Geocoding] All layers failed for '{address}'")
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
# REUSABLE WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class Card(QWidget):
    def __init__(self, bg="#ffffff", border="#ececec", radius=20, parent=None):
        super().__init__(parent)
        self._bg = QColor(bg)
        self._border = QColor(border)
        self._r = radius
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    def set_colors(self, bg, border):
        self._bg = QColor(bg)
        self._border = QColor(border)
        self.update()
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(1, 1, self.width() - 2, self.height() - 2, self._r, self._r)
        p.fillPath(path, QBrush(self._bg))
        p.setPen(QPen(self._border, 1))
        p.drawPath(path)

class PillBtn(QPushButton):
    def __init__(self, text, active=False, t=None):
        super().__init__(text)
        self.active = active
        self.t = t or LIGHT
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Arial", 11))
        self._restyle()
    def set_active(self, v):
        print(f"[DEBUG] PillBtn.set_active({v}) called on {self.text()}")
        self.active = v
        self._restyle()
    def apply_theme(self, t):
        self.t = t
        self._restyle()
    def _restyle(self):
        if self.active:
            self.setStyleSheet(f"QPushButton{{background:{self.t['pill_on_bg']};color:{self.t['pill_on_fg']};border:none;border-radius:18px;padding:0 20px;font-weight:bold;}}QPushButton:hover{{background:{self.t['pill_on_bg']};color:{self.t['pill_on_fg']};}}")
        else:
            self.setStyleSheet(f"QPushButton{{background:{self.t['pill_off_bg']};color:{self.t['pill_off_fg']};border:none;border-radius:18px;padding:0 20px;}}QPushButton:hover{{background:{self.t['pill_on_bg']}55;color:{self.t['text1']};}}")

class BannerWidget(QWidget):
    def __init__(self, t):
        super().__init__()
        self.t = t
        self.setFixedHeight(146) # 130 height + 16 gap

        # Container with solid background color and corner radius 12px
        self.container = QWidget()
        self.container.setObjectName("bannerContainer")
        self.container.setFixedHeight(130)
        self.container.setStyleSheet("""
            QWidget#bannerContainer {
                background-color: #25C799;
                border-radius: 12px;
            }
        """)

        lay = QHBoxLayout(self.container)
        lay.setContentsMargins(36, 0, 0, 0)
        lay.setSpacing(8)

        # Text area (left side)
        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)
        text_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title = QLabel("🔥 Promo Terbaru untuk Mahasiswa")
        self.title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title.setStyleSheet("color:white;background:transparent;")
        self.title.setWordWrap(True)

        self.sub = QLabel("Dapatkan harga termurah hari ini di sekitar Polban!")
        self.sub.setFont(QFont("Arial", 11))
        self.sub.setStyleSheet("color:rgba(255,255,255,220);background:transparent;")
        self.sub.setWordWrap(True)

        text_lay.addWidget(self.title)
        text_lay.addWidget(self.sub)
        lay.addLayout(text_lay)

        # Illustration_3.png - people eating (center, left of Group_69)
        self.people_img = QLabel()
        px_people = QPixmap("UI/Home/Assets/Illustration_3.png")
        if not px_people.isNull():
            px_people = px_people.scaledToHeight(200, Qt.TransformationMode.SmoothTransformation)
            self.people_img.setPixmap(px_people)
            self.people_img.setFixedSize(px_people.width(), 155)
        self.people_img.setStyleSheet("background:transparent;")
        lay.addWidget(self.people_img, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Group_69 food illustration (far right)
        self.group_img = QLabel()
        px_group = QPixmap("UI/Home/Assets/Group_69.png")
        if not px_group.isNull():
            px_group = px_group.scaledToHeight(195, Qt.TransformationMode.SmoothTransformation)
            self.group_img.setPixmap(px_group)
            self.group_img.setFixedSize(px_group.width(), 120)
        self.group_img.setStyleSheet("background:transparent;")
        lay.addWidget(self.group_img, alignment=Qt.AlignmentFlag.AlignVCenter)

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(36, 16, 36, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(self.container)

    def apply_theme(self, t):
        self.t = t
        self.container.setStyleSheet("""
            QWidget#bannerContainer {
                background-color: #25C799;
                border-radius: 12px;
            }
        """)

class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(44)
        self.hide()
        self._tmr = QTimer(self)
        self._tmr.setSingleShot(True)
        self._tmr.timeout.connect(self.hide)
    def show_msg(self, msg, t):
        self.setText(f"  ✓  {msg}  ")
        self.setStyleSheet(f"background:{t['toast_bg']};color:{t['toast_fg']};border-radius:22px;padding:0 16px;")
        self.adjustSize()
        pw = self.parent().width()
        ph = self.parent().height()
        # Posisi di dekat keranjang (kanan atas) atau di tempat yang terlihat
        self.move(pw - self.width() - 24, 76) 
        self.show()
        self.raise_()
        self._tmr.start(2500)

# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT CARD
# ═══════════════════════════════════════════════════════════════════════════════

CARD_W, IMG_H = 220, 160

class ProductCard(Card):
    add_clicked = Signal(dict)
    def __init__(self, product, t, parent=None):
        super().__init__(t["card_bg"], t["card_border"], 12, parent)
        self.product = product
        self.t = t
        self.setFixedSize(CARD_W, 360)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._loaders = []
        self._build()
        drop_shadow(self, 10, "#00000015", 2)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(0)
        
        self.img_cont = QWidget()
        self.img_cont.setFixedSize(CARD_W - 4, IMG_H - 2)
        self.img_cont.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:10px 10px 0 0;")
        
        self.img_lbl = QLabel(self.img_cont)
        self.img_lbl.setGeometry(38, 9, 140, 140)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setText("⏳")
        self.img_lbl.setFont(QFont("Arial", 22))
        self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
        lay.addWidget(self.img_cont)
        
        jenis = self.product.get("jenis_harga", "")
        harga_normal = self.product.get("harga_normal", 0) or 0
        harga_promo = self.product.get("harga_promo", self.product.get("price", 0)) or 0

        diskon = self.product.get("diskon_persen", 0)
        if isinstance(diskon, str):
            diskon = float(diskon) if diskon.strip() else 0.0
        diskon = diskon or 0.0

        has_actual_discount = (diskon > 0) or (harga_normal > harga_promo)

        if has_actual_discount:
            if diskon <= 0:
                diskon = round(100 * (harga_normal - harga_promo) / harga_normal, 1)
            self.product["diskon_persen"] = diskon
            print(f"[BADGE] {self.product['name'][:30]} - diskon={diskon}%, normal={harga_normal}, promo={harga_promo}")
            badge_text = f"🔥 -{diskon:.0f}%"
            self.promo_overlay = QLabel(badge_text, self.img_cont)
            self.promo_overlay.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.promo_overlay.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:6px 14px;min-width:80px;")
            self.promo_overlay.move(8, 8)
        
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(14, 12, 14, 14)
        il.setSpacing(6)
        
        self.cat_badge = QLabel(self.product["category"])
        self.cat_badge.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.cat_badge.setStyleSheet(f"background:{self.t['badge_bg']};color:{self.t['badge_fg']};border-radius:4px;padding:2px 4px;")
        
        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        badge_row.addWidget(self.cat_badge)
        badge_row.addStretch()
        il.addLayout(badge_row)
        
        self.name_lbl = QLabel(self.product["name"])
        self.name_lbl.setObjectName("product_name")
        self.name_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        fm = QFontMetrics(self.name_lbl.font())
        self.name_lbl.setFixedHeight(fm.height() * 2 + 4)
        self.name_lbl.setStyleSheet(f"color:{self.t['text1']};")
        il.addWidget(self.name_lbl)
        
        price_col = QVBoxLayout()
        price_col.setSpacing(2)

        is_promo_card = (jenis == "PROMO") and has_actual_discount
        effective_price = harga_promo

        if is_promo_card:
            self.product["is_promo"] = True
            self.product["effective_price"] = effective_price

            if harga_normal > harga_promo:
                orig_price = QLabel(rp(harga_normal))
                orig_font = QFont("Arial", 9)
                orig_font.setStrikeOut(True)
                orig_price.setFont(orig_font)
                orig_price.setStyleSheet(f"color:{self.t['text2']};")

                if diskon > 0:
                    diskon_lbl = QLabel(f"-{diskon:.0f}%")
                    diskon_lbl.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                    diskon_lbl.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
                    orig_price_lay = QHBoxLayout()
                    orig_price_lay.addWidget(orig_price)
                    orig_price_lay.addWidget(diskon_lbl)
                    orig_price_lay.addStretch()
                    price_col.addLayout(orig_price_lay)
                else:
                    price_col.addWidget(orig_price)

                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Arial", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
            else:
                self.product["is_promo"] = False
                self.price_lbl = QLabel(rp(harga_promo))
                self.price_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
                self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(self.price_lbl)
        else:
            self.product["is_promo"] = False
            self.product["effective_price"] = harga_promo
            self.price_lbl = QLabel(rp(harga_promo))
            self.price_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
            price_col.addWidget(self.price_lbl)
        
        il.addLayout(price_col)

        self.store_lbl = QLabel(f"🏪 {self.product.get('store_base', self.product['store'])}")
        self.store_lbl.setFont(QFont("Arial", 9))
        self.store_lbl.setStyleSheet(f"color:{self.t['store_fg']};")
        il.addWidget(self.store_lbl)

        self.add_btn = QPushButton(" Tambah")
        cart_icon_px = QPixmap("UI/Home/Assets/Shopping cart.png")
        if not cart_icon_px.isNull():
            from PyQt6.QtGui import QIcon
            self.add_btn.setIcon(QIcon(cart_icon_px.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        self.add_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(30)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("QPushButton{background:transparent;color:#006550;border:1px solid #006550;border-radius:6px;}QPushButton:hover{background:#00655015;}")
        self.add_btn.clicked.connect(lambda: self.add_clicked.emit(self.product))
        il.addWidget(self.add_btn)
        
        lay.addWidget(info)
        
        sig = _Sig()
        sig.done.connect(self._on_img)
        ldr = ImgLoader(self.product["image"], self.product["id"], 140, 140, sig)
        self._loaders.append((ldr, sig))
        ldr.start()

    def _on_img(self, pid, px):
        if pid != self.product["id"] or not self.img_lbl.isVisible():
            return
        if not px.isNull():
            self.img_lbl.setPixmap(px)
            self.img_lbl.setText("")
        else:
            self.img_lbl.setText("🖼️")

    def enterEvent(self, event):
        drop_shadow(self, 14, "#00000025", 3)
        super().enterEvent(event)

    def leaveEvent(self, event):
        drop_shadow(self, 10, "#00000015", 2)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_detail()
        super().mousePressEvent(event)

    def _show_detail(self):
        overlay = QWidget(self.window())
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        overlay.setStyleSheet("background:rgba(0,0,0,0.35);")
        overlay.setGeometry(0, 0, self.window().width(), self.window().height())
        overlay.show()
        overlay.raise_()
        dlg = QDialog(self.window())
        dlg.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        dlg.setFixedSize(300, 480)
        dlg.setStyleSheet(f"QDialog {{ background:{self.t['card_bg']}; border:2px solid {self.t['card_border']}; border-radius:12px; }}")
        drop_shadow(dlg, 20, "#00000030", 4)
        
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        
        header = QHBoxLayout()
        ttl = QLabel("Detail Promo")
        ttl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"background:transparent;color:{self.t['text2']};border:none;font-weight:bold;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dlg.close)
        header.addWidget(ttl); header.addStretch(); header.addWidget(close_btn)
        lay.addLayout(header)
        
        # Product Image
        img_lbl = QLabel()
        img_lbl.setFixedSize(268, 130)
        img_lbl.setStyleSheet(f"background:{self.t['card_img_bg']}; border-radius:8px;")
        if hasattr(self, 'img_lbl') and self.img_lbl.pixmap():
            img_lbl.setPixmap(self.img_lbl.pixmap().scaled(268, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            img_lbl.setText("🖼️")
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diskon = self.product.get("diskon_persen", 0)
        if diskon > 0:
            badge = QLabel("🔥 Promo", img_lbl)
            badge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            badge.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:4px 10px;min-width:70px;")
            badge.move(8, 8)
            badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay.addWidget(img_lbl)

        pname = QLabel(self.product["name"])
        pname.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pname.setWordWrap(True)
        pname.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(pname)
        
        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        diskon = self.product.get("diskon_persen", 0)
        if diskon > 0:
            op = QLabel(rp(self.product.get("harga_normal", self.product["price"])))
            f = QFont("Arial", 10); f.setStrikeOut(True); op.setFont(f)
            op.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            pp = QLabel(rp(self.product["effective_price"]))
            pp.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(op)
            price_row.addWidget(pp)
            dk = QLabel(f"-{diskon:.0f}%")
            dk.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            dk.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
            price_row.addWidget(dk)
        else:
            pp = QLabel(rp(self.product["price"]))
            pp.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(pp)
        price_row.addStretch()
        lay.addLayout(price_row)
        
        lbl_cabang = QLabel("Tersedia di:")
        lbl_cabang.setFont(QFont("Arial", 10))
        lbl_cabang.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(lbl_cabang)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;background:transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        c_wid = QWidget()
        c_wid.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(c_wid)
        c_lay.setContentsMargins(0,0,0,0)
        c_lay.setSpacing(8)
        
        branches = self.product.get("branches", [{"store": self.product["store"], "distance": self.product["distance"]}])
        for b in branches:
            bw = QFrame()
            bw.setStyleSheet(f"background:{self.t['cart_item_bg']};border-radius:8px;")
            bl = QVBoxLayout(bw)
            bl.setContentsMargins(12, 8, 12, 8)
            sn = QLabel(f"🏪 {b['store']}")
            sn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            sn.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            sd = QLabel(f"📍 {b['distance']}")
            sd.setFont(QFont("Arial", 9))
            sd.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            bl.addWidget(sn); bl.addWidget(sd)
            c_lay.addWidget(bw)
            
        c_lay.addStretch()
        scroll.setWidget(c_wid)
        lay.addWidget(scroll)

        add_cart_btn = QPushButton("+ Tambah ke Keranjang")
        add_cart_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        add_cart_btn.setFixedHeight(38)
        add_cart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_cart_btn.setStyleSheet(f"QPushButton{{background:{self.t['add_bg']};color:{self.t['add_fg']};border:none;border-radius:8px;}}QPushButton:hover{{background:{self.t['price_fg']};}}")
        add_cart_btn.clicked.connect(lambda: self.window()._add_to_cart(self.product))
        lay.addWidget(add_cart_btn)

        def onDlgClose():
            overlay.hide()
        dlg.finished.connect(onDlgClose)
        dlg.exec()
        overlay.hide()


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT LIST ITEM (for QListWidget viewport culling)
# ═══════════════════════════════════════════════════════════════════════════════

class ProductListItem(Card):
    add_clicked = Signal(dict)
    def __init__(self, product, t, parent=None):
        super().__init__(t["card_bg"], t["card_border"], 12, parent)
        self.product = product
        self.t = t
        self.setFixedSize(CARD_W, 360)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._loaders = []
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(0)

        self.img_cont = QWidget()
        self.img_cont.setFixedSize(CARD_W - 4, IMG_H - 2)
        self.img_cont.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:10px 10px 0 0;")

        self.img_lbl = QLabel(self.img_cont)
        self.img_lbl.setGeometry(38, 9, 140, 140)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setText("⏳")
        self.img_lbl.setFont(QFont("Arial", 22))
        self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
        lay.addWidget(self.img_cont)

        jenis = self.product.get("jenis_harga", "")
        diskon = self.product.get("diskon_persen", 0)
        is_promo = (jenis == "PROMO")
        if is_promo:
            badge_text = "🔥 Promo"
            self.promo_overlay = QLabel(badge_text, self.img_cont)
            self.promo_overlay.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            self.promo_overlay.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:6px 14px;min-width:80px;")
            self.promo_overlay.move(8, 8)
        
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(14, 12, 14, 14)
        il.setSpacing(6)
        
        self.cat_badge = QLabel(self.product["category"])
        self.cat_badge.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        self.cat_badge.setStyleSheet(f"background:{self.t['badge_bg']};color:{self.t['badge_fg']};border-radius:4px;padding:2px 4px;")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        badge_row.addWidget(self.cat_badge)
        badge_row.addStretch()
        il.addLayout(badge_row)

        self.name_lbl = QLabel(self.product["name"])
        self.name_lbl.setObjectName("product_name")
        self.name_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        fm = QFontMetrics(self.name_lbl.font())
        self.name_lbl.setFixedHeight(fm.height() * 2 + 4)
        self.name_lbl.setStyleSheet(f"color:{self.t['text1']};")
        il.addWidget(self.name_lbl)

        price_col = QVBoxLayout()
        price_col.setSpacing(2)
        diskon = self.product.get("diskon_persen", 0)
        jenis = self.product.get("jenis_harga", "")
        harga_normal = self.product.get("harga_normal", 0) or 0
        harga_promo = self.product.get("harga_promo", self.product["price"])

        is_promo_card = jenis == "PROMO"
        effective_price = harga_promo

        if is_promo_card:
            self.product["is_promo"] = True
            self.product["effective_price"] = effective_price

            if harga_normal > harga_promo:
                orig_price = QLabel(rp(harga_normal))
                orig_font = QFont("Arial", 9)
                orig_font.setStrikeOut(True)
                orig_price.setFont(orig_font)
                orig_price.setStyleSheet(f"color:{self.t['text2']};")

                if diskon > 0:
                    diskon_lbl = QLabel(f"-{diskon:.0f}%")
                    diskon_lbl.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                    diskon_lbl.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
                    orig_price_lay = QHBoxLayout()
                    orig_price_lay.addWidget(orig_price)
                    orig_price_lay.addWidget(diskon_lbl)
                    orig_price_lay.addStretch()
                    price_col.addLayout(orig_price_lay)
                else:
                    price_col.addWidget(orig_price)

                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Arial", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
            else:
                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Arial", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
        else:
            self.product["is_promo"] = False
            self.product["effective_price"] = harga_promo
            self.price_lbl = QLabel(rp(harga_promo))
            self.price_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
            price_col.addWidget(self.price_lbl)

        il.addLayout(price_col)

        self.store_lbl = QLabel(f"🏪 {self.product.get('store_base', self.product['store'])}")
        self.store_lbl.setFont(QFont("Arial", 9))
        self.store_lbl.setStyleSheet(f"color:{self.t['store_fg']};")
        il.addWidget(self.store_lbl)

        self.add_btn = QPushButton(" Tambah")
        cart_icon_px = QPixmap("UI/Home/Assets/Shopping cart.png")
        if not cart_icon_px.isNull():
            from PyQt6.QtGui import QIcon
            self.add_btn.setIcon(QIcon(cart_icon_px.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        self.add_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(30)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("QPushButton{background:transparent;color:#006550;border:1px solid #006550;border-radius:6px;}QPushButton:hover{background:#00655015;}")
        self.add_btn.clicked.connect(lambda: self.add_clicked.emit(self.product))
        il.addWidget(self.add_btn)

        lay.addWidget(info)

        sig = _Sig()
        sig.done.connect(self._on_img)
        ldr = ImgLoader(self.product["image"], self.product["id"], 140, 140, sig)
        self._loaders.append((ldr, sig))
        ldr.start()

    def _on_img(self, pid, px):
        if pid != self.product["id"] or not self.img_lbl.isVisible():
            return
        if not px.isNull():
            self.img_lbl.setPixmap(px)
            self.img_lbl.setText("")
        else:
            self.img_lbl.setText("🖼️")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_detail()
        super().mousePressEvent(event)

    def _show_detail(self):
        overlay = QWidget(self.window())
        overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        overlay.setStyleSheet("background:rgba(0,0,0,0.35);")
        overlay.setGeometry(0, 0, self.window().width(), self.window().height())
        overlay.show()
        overlay.raise_()
        dlg = QDialog(self.window())
        dlg.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        dlg.setFixedSize(300, 480)
        dlg.setStyleSheet(f"QDialog {{ background:{self.t['card_bg']}; border:2px solid {self.t['card_border']}; border-radius:12px; }}")
        drop_shadow(dlg, 20, "#00000030", 4)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        header = QHBoxLayout()
        ttl = QLabel("Detail Promo")
        ttl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"background:transparent;color:{self.t['text2']};border:none;font-weight:bold;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dlg.close)
        header.addWidget(ttl); header.addStretch(); header.addWidget(close_btn)
        lay.addLayout(header)

        img_lbl = QLabel()
        img_lbl.setFixedSize(268, 130)
        img_lbl.setStyleSheet(f"background:{self.t['card_img_bg']}; border-radius:8px;")
        if hasattr(self, 'img_lbl') and self.img_lbl.pixmap():
            img_lbl.setPixmap(self.img_lbl.pixmap().scaled(268, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            img_lbl.setText("🖼️")
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diskon = self.product.get("diskon_persen", 0)
        if diskon > 0:
            badge = QLabel("🔥 Promo", img_lbl)
            badge.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            badge.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:4px 10px;min-width:70px;")
            badge.move(8, 8)
            badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay.addWidget(img_lbl)

        pname = QLabel(self.product["name"])
        pname.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pname.setWordWrap(True)
        pname.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(pname)

        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        if diskon > 0:
            normal_price = self.product.get("harga_normal", self.product["price"])
            op = QLabel(rp(normal_price))
            op.setFont(QFont("Arial", 10))
            op.setStyleSheet(f"color:{self.t['text2']};text-decoration:line-through;")
            pp = QLabel(rp(self.product["effective_price"]))
            pp.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(op); price_row.addWidget(pp)
        else:
            pp = QLabel(rp(self.product["price"]))
            pp.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(pp)
        price_row.addStretch()
        lay.addLayout(price_row)

        lbl_cabang = QLabel("Tersedia di:")
        lbl_cabang.setFont(QFont("Arial", 10))
        lbl_cabang.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(lbl_cabang)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;background:transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        c_wid = QWidget()
        c_wid.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(c_wid)
        c_lay.setContentsMargins(0,0,0,0)
        c_lay.setSpacing(8)

        branches = self.product.get("branches", [{"store": self.product["store"], "distance": self.product["distance"]}])
        for b in branches:
            bw = QFrame()
            bw.setStyleSheet(f"background:{self.t['cart_item_bg']};border-radius:8px;")
            bl = QVBoxLayout(bw)
            bl.setContentsMargins(12, 8, 12, 8)
            sn = QLabel(f"🏪 {b['store']}")
            sn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            sn.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            sd = QLabel(f"📍 {b['distance']}")
            sd.setFont(QFont("Arial", 9))
            sd.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            bl.addWidget(sn); bl.addWidget(sd)
            c_lay.addWidget(bw)

        c_lay.addStretch()
        scroll.setWidget(c_wid)
        lay.addWidget(scroll)

        add_cart_btn = QPushButton("+ Tambah ke Keranjang")
        add_cart_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        add_cart_btn.setFixedHeight(38)
        add_cart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_cart_btn.setStyleSheet(f"QPushButton{{background:{self.t['add_bg']};color:{self.t['add_fg']};border:none;border-radius:8px;}}QPushButton:hover{{background:{self.t['price_fg']};}}")
        add_cart_btn.clicked.connect(lambda: self.window()._add_to_cart(self.product))
        lay.addWidget(add_cart_btn)

        def onDlgClose():
            overlay.hide()
        dlg.finished.connect(onDlgClose)
        dlg.exec()
        overlay.hide()

    def update_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['card_bg']}; border:1px solid {t['card_border']};")
        self._build()


# ═══════════════════════════════════════════════════════════════════════════════
# CART PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class ProgressBar(QWidget):
    def __init__(self, t):
        super().__init__()
        self.t = t; self.pct = 0; self.setFixedHeight(11)
    def set_pct(self, v):
        self.pct = max(0, min(v, 100))
        self.update()
    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg = QPainterPath()
        bg.addRoundedRect(0, 0, self.width(), self.height(), 5, 5)
        p.fillPath(bg, QColor(self.t["prog_bg"]))
        fw = int(self.width() * self.pct / 100)
        if fw > 4:
            fp = QPainterPath()
            fp.addRoundedRect(0, 0, fw, self.height(), 5, 5)
            col = QColor("#21C083" if self.pct < 70 else "#f59e0b" if self.pct < 90 else "#ef4444")
            p.fillPath(fp, col)

class CartPage(QWidget):
    back = Signal()
    def __init__(self, app, t):
        super().__init__()
        self.app = app; self.t = t; self.budget = 100000; self._build()

    def _build(self):
        self.setStyleSheet(f"background:{self.t['cart_bg']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{self.t['cart_bg']};border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        cont = QWidget()
        cont.setStyleSheet(f"background:{self.t['cart_bg']};")
        scroll.setWidget(cont)
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(40, 28, 40, 40)
        lay.setSpacing(16)
        back = QPushButton("← Kembali ke Beranda")
        back.setFont(QFont("Arial", 11))
        back.setFixedSize(220, 40)
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.setStyleSheet(f"QPushButton{{background:{self.t['btn_bg']};color:{self.t['text1']};border:1px solid {self.t['nav_border']};border-radius:20px;padding:0 14px;}}QPushButton:hover{{background:{self.t['cart_item_bg']};}}")
        back.clicked.connect(self.back.emit)
        lay.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)
        self.card_widget = Card(self.t["cart_card_bg"], self.t["card_border"], 26)
        drop_shadow(self.card_widget, 28, "#00000012", 6)
        self.card_lay = QVBoxLayout(self.card_widget)
        self.card_lay.setContentsMargins(32, 28, 32, 32)
        self.card_lay.setSpacing(14)
        lay.addWidget(self.card_widget)
        lay.addStretch()
        self._populate()

    def _populate(self):
        while self.card_lay.count():
            it = self.card_lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        t = self.t
        title = QLabel("Keranjang Belanja")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        self.card_lay.addWidget(title)
        if not self.app.cart_items:
            e = QLabel("🛒\n\nKeranjang kamu masih kosong\nMulai tambahkan produk dari halaman utama")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e.setFont(QFont("Arial", 13))
            e.setStyleSheet(f"color:{t['text2']};background:transparent;padding:32px;")
            self.card_lay.addWidget(e)
        else:
            for ci in self.app.cart_items:
                self.card_lay.addWidget(self._make_item_row(ci))
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"color:{t['divider']};")
        self.card_lay.addWidget(div)
        total = sum(ci["product"].get("effective_price", ci["product"].get("price", 0)) * ci["quantity"] for ci in self.app.cart_items)
        pct = min(int(total / self.budget * 100), 100) if self.budget > 0 else 0
        remaining = self.budget - total
        
        # budget box
        bb = Card(t["budget_bg"], t["budget_border"], 18)
        bl = QVBoxLayout(bb)
        bl.setContentsMargins(18, 14, 18, 14)
        bl.setSpacing(8)
        br = QHBoxLayout()
        bl2 = QLabel("Anggaran")
        bl2.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        bl2.setStyleSheet(f"color:{t['text1']};background:transparent;")
        br.addWidget(bl2)
        br.addStretch()
        bv = QLabel(rp(self.budget))
        bv.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        bv.setStyleSheet(f"color:{t['text1']};background:transparent;")
        br.addWidget(bv)
        eb = QPushButton("✏️")
        eb.setFixedSize(28, 28)
        eb.setFlat(True)
        eb.setCursor(Qt.CursorShape.PointingHandCursor)
        eb.setStyleSheet("background:transparent;border:none;font-size:13px;")
        eb.clicked.connect(self._edit_budget)
        br.addWidget(eb)
        bl.addLayout(br)
        prog = ProgressBar(t)
        prog.set_pct(pct)
        bl.addWidget(prog)
        pl = QLabel(f"{pct}% dari anggaran terpakai")
        pl.setFont(QFont("Arial", 10))
        pl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.setStyleSheet(f"color:{t['text2']};background:transparent;")
        bl.addWidget(pl)
        self.card_lay.addWidget(bb)
        
        # total
        tb = Card(t["total_bg"], t["total_bg"], 16)
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(18, 12, 18, 12)
        tl1 = QLabel("Total")
        tl1.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        tl1.setStyleSheet(f"color:{t['text1']};background:transparent;")
        tv = QLabel(rp(total))
        tv.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        tv.setStyleSheet(f"color:{t['text1']};background:transparent;")
        tl.addWidget(tl1)
        tl.addStretch()
        tl.addWidget(tv)
        self.card_lay.addWidget(tb)
        
        # remaining
        over = remaining < 0
        rb = Card(t["over_bg"] if over else t["remain_bg"], t["budget_border"], 18)
        rl = QVBoxLayout(rb)
        rl.setContentsMargins(18, 14, 18, 14)
        rl.setSpacing(4)
        rl1 = QLabel("Sisa Anggaran")
        rl1.setFont(QFont("Arial", 12))
        rl1.setStyleSheet(f"color:{t['text1']};background:transparent;")
        rv = QLabel(rp(remaining))
        rv.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        rv.setStyleSheet(f"color:{t['over_fg'] if over else t['remain_fg']};background:transparent;")
        rl.addWidget(rl1)
        rl.addWidget(rv)
        if over:
            w = QLabel("⚠️ Anggaran tidak cukup! Kurangi beberapa item.")
            w.setFont(QFont("Arial", 10))
            w.setStyleSheet(f"color:{t['over_fg']};background:transparent;")
            rl.addWidget(w)
        self.card_lay.addWidget(rb)

    def _make_item_row(self, ci):
        p = ci["product"]; q = ci["quantity"]
        row = Card(self.t["cart_item_bg"], self.t["cart_item_bg"], 16)
        rl = QHBoxLayout(row)
        rl.setContentsMargins(14, 12, 14, 12)
        rl.setSpacing(12)
        ic = QLabel("🛒")
        ic.setFont(QFont("Arial", 22))
        ic.setFixedSize(48, 48)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:12px;")
        rl.addWidget(ic)
        inf = QVBoxLayout()
        inf.setSpacing(3)
        n = QLabel(p["name"])
        n.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        n.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        s = QLabel(p["store"])
        s.setFont(QFont("Arial", 10))
        s.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        inf.addWidget(n)
        inf.addWidget(s)
        rl.addLayout(inf)
        rl.addStretch()
        prc = QVBoxLayout()
        prc.setAlignment(Qt.AlignmentFlag.AlignRight)
        tv = QLabel(rp(p.get("effective_price", p.get("price", 0)) * q))
        tv.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        tv.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        tv.setAlignment(Qt.AlignmentFlag.AlignRight)
        dv = QLabel(f"{q} x {rp(p.get('effective_price', p.get('price', 0)))}")
        dv.setFont(QFont("Arial", 9))
        dv.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        dv.setAlignment(Qt.AlignmentFlag.AlignRight)
        prc.addWidget(tv)
        prc.addWidget(dv)
        rl.addLayout(prc)
        db = QPushButton("🗑️")
        db.setFixedSize(34, 34)
        db.setFont(QFont("Arial", 14))
        db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.setStyleSheet("QPushButton{background:transparent;border:none;}QPushButton:hover{background:rgba(220,50,50,0.12);border-radius:8px;}")
        db.clicked.connect(lambda _, pid=p["id"]: self._remove(pid))
        rl.addWidget(db)
        return row

    def _remove(self, pid):
        self.app.cart_items = [ci for ci in self.app.cart_items if ci["product"].get("id", "") != pid]
        self.app.update_badge()
        self.app.update_balance_display()
        self._populate()

    def _edit_budget(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Set Anggaran")
        dlg.setFixedSize(300, 120)
        dlg.setStyleSheet(f"background:{self.t['cart_card_bg']};")
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(20, 20, 20, 20)
        dl.setSpacing(10)
        inp = QLineEdit(str(self.budget))
        inp.setFont(QFont("Arial", 14))
        inp.setStyleSheet(f"background:{self.t['search_bg']};color:{self.t['search_fg']};border:1px solid {self.t['search_border']};border-radius:10px;padding:6px 12px;")
        dl.addWidget(inp)
        ok = QPushButton("Simpan")
        ok.setStyleSheet(f"background:{self.t['pill_on_bg']};color:white;border-radius:10px;padding:8px;")
        ok.setCursor(Qt.CursorShape.PointingHandCursor)
        ok.clicked.connect(dlg.accept)
        dl.addWidget(ok)
        if dlg.exec():
            try:
                v = int(inp.text().replace(".", "").replace(",", ""))
                if v >= 0:
                    self.budget = v
                    self._populate()
            except Exception:
                pass

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['cart_bg']};")
        self._populate()

# ═══════════════════════════════════════════════════════════════════════════════
# STATISTIK PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class BarChart(QWidget):
    def __init__(self, data, t):
        super().__init__()
        self.data = data; self.t = t; self.setMinimumHeight(280)
    def paintEvent(self, e):
        if not self.data: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(self.t["stat_card_bg"]))
        W, H = self.width(), self.height()
        pad_l, pad_r, pad_t, pad_b = 48, 20, 20, 56
        chart_w = W - pad_l - pad_r; chart_h = H - pad_t - pad_b
        max_v = max(v for _, v in self.data)
        n = len(self.data)
        bar_w = max(20, int(chart_w / n * 0.5))
        gap = (chart_w - bar_w * n) // (n + 1)
        color = QColor(self.t["chart_colors"][0])
        p.setPen(QPen(QColor(self.t["text2"]), 1))
        p.setFont(QFont("Arial", 9))
        if max_v < 4:
            ticks = list(range(max_v + 1))
        else:
            step = max(1, int(math.ceil(max_v / 4.0)))
            ticks = [step * i for i in range(5) if step * i <= max_v * 1.2]
            if not ticks: ticks = [0]
            max_tick = ticks[-1]
            max_v = max_tick if max_tick > 0 else 1
            
        for yv in ticks:
            y = pad_t + chart_h - int(chart_h * yv / max_v) if max_v else pad_t + chart_h
            p.drawText(0, y + 4, pad_l - 6, 12, Qt.AlignmentFlag.AlignRight, str(int(yv)))
            p.drawLine(pad_l, y, W - pad_r, y)
        for i, (label, val) in enumerate(self.data):
            x = pad_l + gap * (i + 1) + bar_w * i
            bh = int(chart_h * val / max_v) if max_v else 0
            y = pad_t + chart_h - bh
            path = QPainterPath()
            path.addRoundedRect(x, y, bar_w, bh, 6, 6)
            grad = QLinearGradient(x, y + bh, x, y)
            grad.setColorAt(0, QColor("#10b981"))
            grad.setColorAt(1, QColor("#14b8a6"))
            p.fillPath(path, QBrush(grad))
            fm = QFontMetrics(QFont("Arial", 8))
            lbl = fm.elidedText(label, Qt.TextElideMode.ElideRight, bar_w * 2 + gap * 2)
            p.drawText(x - gap // 2, H - pad_b + 8, bar_w + gap, 40,
                       Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, lbl)
    def apply_theme(self, t):
        self.t = t; self.update()

class PieChart(QWidget):
    def __init__(self, data, t):
        super().__init__()
        self.data = data; self.t = t; self.setMinimumHeight(280)
    def paintEvent(self, e):
        if not self.data: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(self.t["stat_card_bg"]))
        W, H = self.width(), self.height()
        total = sum(v for _, v in self.data)
        r = min(W // 3, H // 2 - 40)
        cx = W // 2; cy = H // 2 - 10
        colors = [QColor(c) for c in self.t["chart_colors"]]
        start = 0; slices = []
        for i, (label, val) in enumerate(self.data):
            span = int(val / total * 5760) if total else 0
            slices.append((label, val, start, span, colors[i % len(colors)]))
            start += span
        for label, val, s, sp, col in slices:
            p.setBrush(QBrush(col))
            p.setPen(QPen(QColor(self.t["stat_card_bg"]), 2))
            p.drawPie(cx - r, cy - r, r * 2, r * 2, s, sp)
        p.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        label_rects = []
        for label, val, s, sp, col in slices:
            angle = math.radians(-(s + sp // 2) / 16)
            tx = cx + int((r + 30) * math.cos(angle))
            ty = cy + int((r + 30) * math.sin(angle))
            pct = int(val / total * 100) if total else 0
            text = f"{label} {pct}%"
            fm = QFontMetrics(p.font())
            elided_text = fm.elidedText(text, Qt.TextElideMode.ElideRight, 120)
            tw = fm.horizontalAdvance(elided_text)
            th = fm.height()
            
            if math.cos(angle) > 0:
                rect = QRect(tx, ty - th//2, tw, th)
            else:
                rect = QRect(tx - tw, ty - th//2, tw, th)
                
            for pr in label_rects:
                if rect.intersects(pr):
                    if rect.y() >= pr.y():
                        rect.moveTop(pr.bottom() + 2)
                    else:
                        rect.moveBottom(pr.top() - 2)
            
            label_rects.append(rect)
            p.setPen(col)
            p.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, elided_text)
        # legend
        lx = W // 2 - len(self.data) * 55 // 2; ly = H - 28
        p.setFont(QFont("Arial", 9))
        for i, (label, val, s, sp, col) in enumerate(slices):
            p.fillRect(lx + i * 90, ly, 12, 12, col)
            p.setPen(QColor(self.t["text2"]))
            lbl_elided = QFontMetrics(p.font()).elidedText(label, Qt.TextElideMode.ElideRight, 120)
            p.drawText(lx + i * 110 + 16, ly, 120, 12, Qt.AlignmentFlag.AlignLeft, lbl_elided)
    def apply_theme(self, t):
        self.t = t; self.update()

class StatistikPage(QWidget):
    def __init__(self, t, app=None):
        super().__init__()
        self.t = t
        self.app = app
        self._build()
        
    def _build(self):
        self.setStyleSheet(f"background:{self.t['stat_bg']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{self.t['stat_bg']};border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        cont = QWidget()
        cont.setStyleSheet(f"background:{self.t['stat_bg']};")
        scroll.setWidget(cont)
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(40, 32, 40, 40)
        lay.setSpacing(24)
        
        # header
        ttl = QLabel("Statistik Promo")
        ttl.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        
        # Last updated label synced with app
        if self.app:
            months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            m_idx = self.app.last_sync.month - 1
            formatted_date = f"{self.app.last_sync.day} {months[m_idx]} {self.app.last_sync.year}"
            self.sub = QLabel(f"Terakhir diperbarui: {formatted_date}")
        else:
            self.sub = QLabel("Terakhir diperbarui: -")
        self.sub.setFont(QFont("Arial", 12))
        self.sub.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(ttl); lay.addWidget(self.sub)
        
        # bar chart card
        store_count = {}
        for p in PRODUCTS:
            store_count[p["store"]] = store_count.get(p["store"], 0) + 1
        top3 = sorted(store_count.items(), key=lambda x: -x[1])[:3]
        self.bar_chart = BarChart(top3, self.t)
        bc = self._make_chart_card("Top 3 Toko dengan Promo Terbanyak", self.bar_chart)
        lay.addWidget(bc)
        
        # pie chart card
        cat_count = {}
        for p in PRODUCTS:
            if p["id"] in PROMO_IDS:
                cat_count[p["category"]] = cat_count.get(p["category"], 0) + 1
        pie_data = list(cat_count.items())
        self.pie_chart = PieChart(pie_data, self.t)
        pc = self._make_chart_card("Distribusi Kategori Produk Promo", self.pie_chart)
        lay.addWidget(pc)
        
        # summary cards
        total_promo = len(PROMO_IDS)
        total_stores = len(set(p["store"] for p in PRODUCTS))
        total_cats = len(set(p["category"] for p in PRODUCTS))
        sum_row = QHBoxLayout()
        sum_row.setSpacing(16)
        for num, label, color in [
            (total_promo, "Total Produk Promo", self.t["chart_colors"][0]),
            (total_stores, "Toko dengan Promo", self.t["chart_colors"][1]),
            (total_cats, "Kategori Tersedia", self.t["chart_colors"][2]),
        ]:
            sc = Card(self.t["stat_card_bg"], self.t["card_border"], 18)
            drop_shadow(sc, 12, "#00000010", 3)
            sl = QVBoxLayout(sc)
            sl.setContentsMargins(24, 24, 24, 24)
            sl.setSpacing(8)
            nl = QLabel(str(num))
            nl.setFont(QFont("Arial", 38, QFont.Weight.Bold))
            nl.setStyleSheet(f"color:{color};background:transparent;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ll = QLabel(label)
            ll.setFont(QFont("Arial", 12))
            ll.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(nl)
            sl.addWidget(ll)
            sum_row.addWidget(sc)
        lay.addLayout(sum_row)
        lay.addStretch()

    def update_sync_date(self):
        if self.app:
            months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            m_idx = self.app.last_sync.month - 1
            formatted_date = f"{self.app.last_sync.day} {months[m_idx]} {self.app.last_sync.year}"
            self.sub.setText(f"Terakhir diperbarui: {formatted_date}")

    def _make_chart_card(self, title, chart_widget):
        card = Card(self.t["stat_card_bg"], self.t["card_border"], 18)
        drop_shadow(card, 14, "#00000010", 3)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(12)
        tl = QLabel(title)
        tl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        tl.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        tl.setWordWrap(True)
        cl.addWidget(tl)
        if hasattr(chart_widget, 'setMinimumHeight'):
            chart_widget.setMinimumHeight(280)
        cl.addWidget(chart_widget)
        return card

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['stat_bg']};")
        if hasattr(self, 'sub'):
            self.sub.setStyleSheet(f"color:{t['text2']};background:transparent;")
        if hasattr(self, 'bar_chart'):
            self.bar_chart.apply_theme(t)
        if hasattr(self, 'pie_chart'):
            self.pie_chart.apply_theme(t)


# ═══════════════════════════════════════════════════════════════════════════════
# LOKASI PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class LokasiPage(QWidget):
    def __init__(self, t, toast=None):
        super().__init__()
        self.t = t
        self.toast = toast
        self._js_bridge = None
        self._build()
        
    def _build(self):
        self.setStyleSheet(f"background:{self.t['loc_bg']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{self.t['loc_bg']};border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        cont = QWidget()
        cont.setStyleSheet(f"background:{self.t['loc_bg']};")
        scroll.setWidget(cont)
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(40, 32, 40, 40)
        lay.setSpacing(20)
        ttl = QLabel("Lokasi Toko")
        ttl.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        sub = QLabel("Supermarket dengan promo di sekitar area kamu")
        sub.setFont(QFont("Arial", 12))
        sub.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(ttl); lay.addWidget(sub)
        stores = [

            {"name":"Indomaret Sarijadi 01", "area":"Sarijadi", "address":"Jl. Sarijadi No. 45, Bandung Utara", "lat": -6.8731, "lon": 107.5768, "items":len([p for p in PRODUCTS if p["store"]=="Indomaret Sarijadi 01"]), "open":"07.00 - 23.00"},
            {"name":"Alfamart Waruga Jaya", "area":"Gegerkalong", "address":"Jl. Gegerkalong No. 88, Bandung Utara", "lat": -6.8680, "lon": 107.5890, "items":len([p for p in PRODUCTS if p["store"]=="Alfamart Waruga Jaya"]), "open":"24 Jam"},
        ]
        
        # Folium Interactive Map
        map_card = Card(self.t["loc_card_bg"], self.t["card_border"], 18)
        ml = QVBoxLayout(map_card)
        ml.setContentsMargins(24, 20, 24, 20)
        ml.setSpacing(8)
        mtl = QLabel("Peta Area Interaktif")
        mtl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        mtl.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")

        from PyQt6.QtWebEngineCore import QWebEnginePage
        class ConsoleLoggingPage(QWebEnginePage):
            def javaScriptConsoleMessage(self, level, msg, line, src):
                print(f"[JS] {msg} (line {line}, {src})")
        self.web_view = QWebEngineView()
        self.web_view.setPage(ConsoleLoggingPage(self.web_view))
        self.web_view.setMinimumHeight(400)
        self.web_view.setStyleSheet("border: 3px solid red;")
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)
        self._tile_interceptor = TileInterceptor()
        self.web_view.page().profile().setUrlRequestInterceptor(self._tile_interceptor)
        map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map.html")
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath(map_path)))
        self.web_view.loadFinished.connect(self._on_map_loaded)

        map_inner = QWidget()
        inner_layout = QGridLayout(map_inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(self.web_view, 0, 0)

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(48, 48)
        self.add_btn.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{self.t['add_bg']};
                color:{self.t['add_fg']};
                border-radius:24px;
                border:2px solid {self.t['budget_border']};
            }}
            QPushButton:hover {{
                background:{self.t['budget_border']};
            }}
        """)
        self.add_btn.clicked.connect(self._on_add_recommendation)
        inner_layout.addWidget(self.add_btn, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        inner_layout.setRowStretch(0, 1)
        inner_layout.setColumnStretch(0, 1)

        ml.addWidget(mtl)
        ml.addWidget(map_inner)
        lay.addWidget(map_card)
        
        for st in stores:
            card = Card(self.t["loc_card_bg"], self.t["card_border"], 18)
            drop_shadow(card, 14, "#00000010", 3)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(24, 20, 24, 20)
            cl.setSpacing(20)
            icon_lbl = QLabel("🏪")
            icon_lbl.setFont(QFont("Arial", 32))
            icon_lbl.setFixedSize(60, 60)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"background:{self.t['budget_bg']};border-radius:30px;")
            cl.addWidget(icon_lbl)
            info = QVBoxLayout()
            info.setSpacing(4)
            nm = QLabel(st["name"])
            nm.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            nm.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            ar = QLabel(f"📍 {st['area']} · {st['address']}")
            ar.setFont(QFont("Arial", 11))
            ar.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            hr = QLabel(f"🕐 {st['open']}")
            hr.setFont(QFont("Arial", 11))
            hr.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            info.addWidget(nm); info.addWidget(ar); info.addWidget(hr)
            cl.addLayout(info)
            cl.addStretch()
            badge = QLabel(f"{st['items']} promo")
            badge.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            badge.setStyleSheet(f"background:{self.t['budget_bg']};color:{self.t['price_fg']};border-radius:12px;padding:6px 14px;")
            cl.addWidget(badge)
            lay.addWidget(card)
            
        lay.addStretch()

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['loc_bg']};")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{t['add_bg']};
                color:{t['add_fg']};
                border-radius:24px;
                border:2px solid {t['budget_border']};
            }}
            QPushButton:hover {{
                background:{t['budget_border']};
            }}
        """)

    def _on_map_loaded(self, ok):
        if not ok:
            print("Map page failed to load")
            return

        # Setup QWebChannel AFTER page load is confirmed
        channel = QWebChannel(self.web_view.page())
        self.web_view.page().setWebChannel(channel)
        self._js_bridge = JSBridge(self, self.toast, self.t)
        channel.registerObject("pyBridge", self._js_bridge)

        import json
        from data_manager import fetch_cloud_data, get_demo_recommendations
        raw = data_manager.read_local_data()
        product_counts = {}
        for r in raw:
            nc = r.get("nama_cabang", "").strip()
            product_counts[nc] = product_counts.get(nc, 0) + 1
        stores = []
        skipped_invalid_coords = 0
        for brand_key, brand_data in data_manager.ADDRESS_BOOK.items():
            for branch in brand_data["branches"]:
                nc = branch["nama_cabang"]
                area = branch["area_tags"][0] if branch["area_tags"] else ""
                items = product_counts.get(nc, 0)
                lat = -6.8620 + (hash(nc) % 100) * 0.0001
                lon = 107.5750 + (hash(nc) % 100) * 0.0001
                if lat is None or lat == 0 or lon is None or lon == 0:
                    skipped_invalid_coords += 1
                    continue
                print(f"[STORE PIN] {nc} | lat={lat:.6f} | lon={lon:.6f} | address={branch.get('address', 'N/A')[:50]}")
                if brand_key == "Alfamart":
                    open_hours = "24 Jam" if "Waruga" in nc or "Ciwaruga" in nc else "07.00 - 22.00"
                elif brand_key == "Indomaret":
                    open_hours = "24 Jam" if items > 5 else "07.00 - 23.00"
                elif brand_key == "Yomart":
                    open_hours = "08.00 - 21.00"
                else:
                    open_hours = "08.00 - 21.00"
                stores.append({
                    "name": nc,
                    "area": area,
                    "address": branch.get("address", f"Area {area}"),
                    "lat": lat,
                    "lon": lon,
                    "items": items,
                    "open": open_hours
                })
        invalid_stores = [s for s in stores if not s.get('lat') or not s.get('lon') or s.get('lat') == 0 or s.get('lon') == 0]
        if invalid_stores:
            print(f"[WARNING] {len(invalid_stores)} stores have invalid coordinates:")
            for s in invalid_stores:
                print(f"  - {s.get('name', 'Unknown')}: lat={s.get('lat')}, lon={s.get('lon')}")
        print(f"[MAP SUMMARY] Total stores prepared: {len(stores)}")
        print(f"[MAP SUMMARY] Valid coordinates: {len(stores) - len(invalid_stores)}")
        print(f"[MAP SUMMARY] Invalid coordinates (skipped): {skipped_invalid_coords}")
        recs = fetch_cloud_data("Rekomendasi") or get_demo_recommendations()
        promo_ids_list = list(PROMO_IDS)

        init_js = f"""
            var _stores = {json.dumps(stores)};
            var _recs = {json.dumps(recs)};
            var _promo_ids = {json.dumps(promo_ids_list)};
            if (typeof QWebChannel !== 'undefined') {{
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.pyBridge = channel.objects.pyBridge;
                    if (window.initMap) {{
                        window.initMap(_stores, _recs, _promo_ids);
                    }}
                }});
            }} else {{
                if (window.initMap) {{
                    window.initMap(_stores, _recs, _promo_ids);
                }}
            }}
        """
        self._map_ready = True
        qwebchannel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "qwebchannel.js")
        with open(qwebchannel_path, "r", encoding="utf-8") as f:
            qwebchannel_js = f.read()
        self.web_view.page().runJavaScript(qwebchannel_js)
        self.web_view.page().runJavaScript(init_js)
        QTimer.singleShot(5000, lambda: self._check_map_loaded())

    def _check_map_loaded(self):
        if getattr(self, '_map_ready', False) and not getattr(self, '_map_fix_attempted', False):
            self._map_fix_attempted = True
            self.web_view.page().runJavaScript("""
                if (typeof map !== 'undefined' && map.getContainer().offsetWidth === 0) {
                    console.log('Map still blank after 5s, reloading...');
                    window.location.reload();
                } else if (typeof map !== 'undefined') {
                    map.invalidateSize(true);
                }
            """)

    def _on_add_recommendation(self):
        self.web_view.page().runJavaScript("if (window.openPanel) window.openPanel();")

    def _refresh_map_recommendations(self):
        import json
        from data_manager import fetch_cloud_data, get_demo_recommendations
        recs = []
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rekomendasi.json")
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    recs = json.load(f) or []
                print(f"[MAP] Loaded {len(recs)} recommendations from local rekomendasi.json")
            except Exception as e:
                print(f"[MAP] Failed to load local rekomendasi.json: {e}")
        # Also try to fetch from cloud and merge (avoid duplicates by lat/lon)
        try:
            cloud_recs = fetch_cloud_data("Rekomendasi") or []
            if cloud_recs:
                existing_coords = set((r.get('latitude'), r.get('longitude')) for r in recs)
                for cr in cloud_recs:
                    coord = (cr.get('latitude'), cr.get('longitude'))
                    if coord not in existing_coords and coord[0] and coord[1]:
                        recs.append(cr)
                print(f"[MAP] Merged cloud recommendations, total: {len(recs)}")
        except Exception as e:
            print(f"[MAP] Failed to fetch cloud recommendations: {e}")
        if not recs:
            recs = get_demo_recommendations()
            print(f"[MAP] Using demo recommendations: {len(recs)} items")
        if recs:
            print(f"[MAP] Total recommendations to display on map: {len(recs)}")
        raw = data_manager.read_local_data()
        product_counts = {}
        for r in raw:
            nc = r.get("nama_cabang", "").strip()
            product_counts[nc] = product_counts.get(nc, 0) + 1
        stores = []
        invalid_stores = []
        for brand_key, brand_data in data_manager.ADDRESS_BOOK.items():
            for branch in brand_data["branches"]:
                nc = branch["nama_cabang"]
                area = branch["area_tags"][0] if branch["area_tags"] else ""
                items = product_counts.get(nc, 0)
                lat = -6.8620 + (hash(nc) % 100) * 0.0001
                lon = 107.5750 + (hash(nc) % 100) * 0.0001
                if brand_key == "Alfamart":
                    open_hours = "24 Jam" if "Waruga" in nc or "Ciwaruga" in nc else "07.00 - 22.00"
                elif brand_key == "Indomaret":
                    open_hours = "24 Jam" if items > 5 else "07.00 - 23.00"
                elif brand_key == "Yomart":
                    open_hours = "08.00 - 21.00"
                else:
                    open_hours = "08.00 - 21.00"
                stores.append({
                    "name": nc,
                    "area": area,
                    "address": branch.get("address", f"Area {area}"),
                    "lat": lat,
                    "lon": lon,
                    "items": items,
                    "open": open_hours
                })
                print(f"[STORE PIN] {nc} | lat={lat:.6f} | lon={lon:.6f} | address={branch.get('address', 'N/A')[:50]}")
        print(f"[MAP SUMMARY] Total stores prepared: {len(stores)}")
        print(f"[MAP SUMMARY] Valid coordinates: {len(stores) - len(invalid_stores)}")
        print(f"[MAP SUMMARY] Invalid coordinates (skipped): 0")
        promo_ids_list = list(PROMO_IDS)
        refresh_js = f"""
            var _stores = {json.dumps(stores)};
            var _recs = {json.dumps(recs)};
            var _promo_ids = {json.dumps(promo_ids_list)};
            if (typeof QWebChannel !== 'undefined') {{
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.pyBridge = channel.objects.pyBridge;
                    if (window.initMap) {{
                        window.initMap(_stores, _recs, _promo_ids);
                    }}
                }});
            }} else {{
                if (window.initMap) {{
                    window.initMap(_stores, _recs, _promo_ids);
                }}
            }}
        """
        self.web_view.page().runJavaScript(refresh_js)

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['loc_bg']};")


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

# [DEPRECATED] class AdminDashboard(QDialog):
#     """Dashboard Admin berbasis PyQt6 — DIGANTI oleh admin_tool.py (Tkinter subprocess)."""
#     def __init__(self, parent=None, t=None):
#         super().__init__(parent)
#         self.t = t or LIGHT
#         self.setWindowTitle("Radar Promo Admin Dashboard")
#         self.setFixedSize(600, 500)
#         self.setStyleSheet(f"background:{self.t['setting_bg']};")
#         
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(24, 24, 24, 24)
#         lay.setSpacing(16)
#         
#         hdr = QLabel("Radar Promo Admin Dashboard")
#         hdr.setFont(QFont("Arial", 16, QFont.Weight.Bold))
#         hdr.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
#         lay.addWidget(hdr)
#         
#         c1 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
#         cl1 = QVBoxLayout(c1)
#         l1 = QLabel("Sinkronisasi Data")
#         l1.setFont(QFont("Arial", 11, QFont.Weight.Bold))
#         l1.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
#         b1 = QPushButton("Sinkronisasi Sekarang")
#         b1.setFixedHeight(36)
#         b1.setCursor(Qt.CursorShape.PointingHandCursor)
#         b1.setStyleSheet(f"background:#6FB8AD;color:white;border-radius:8px;font-weight:bold;")
#         cl1.addWidget(l1); cl1.addWidget(b1)
#         lay.addWidget(c1)
#         
#         c2 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
#         cl2 = QVBoxLayout(c2)
#         l2 = QLabel("Upload ke Cloud")
#         l2.setFont(QFont("Arial", 11, QFont.Weight.Bold))
#         l2.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
#         b2 = QPushButton("Upload Promo ke Cloud")
#         b2.setFixedHeight(36)
#         b2.setCursor(Qt.CursorShape.PointingHandCursor)
#         b2.setStyleSheet(f"background:#F1C0CC;color:white;border-radius:8px;font-weight:bold;")
#         cl2.addWidget(l2); cl2.addWidget(b2)
#         lay.addWidget(c2)
#         
#         c3 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
#         cl3 = QVBoxLayout(c3)
#         l3 = QLabel("Log Aktivitas")
#         l3.setFont(QFont("Arial", 11, QFont.Weight.Bold))
#         l3.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
#         
#         log_text = QTextEdit()
#         log_text.setReadOnly(True)
#         log_text.setStyleSheet(f"background:{self.t['input_bg']};color:{self.t['text2']};border:1px solid {self.t['input_border']};border-radius:8px;")
#         log_text.setPlainText("[UPLOAD] upload berhasil\n[SYNC] sinkronisasi selesai\n[INFO] Data dimuat dari data_promo.json (6742 item)")
#         cl3.addWidget(l3); cl3.addWidget(log_text)
#         lay.addWidget(c3)

# ═══════════════════════════════════════════════════════════════════════════════
# PENGATURAN PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class PengaturanPage(QWidget):
    def __init__(self, app, t):
        super().__init__()
        self.app = app; self.t = t
        self.is_admin = False
        self.font_size = "Normal"
        self._build()
        
    def _build(self):
        self.setStyleSheet(f"background:{self.t['setting_bg']};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"background:{self.t['setting_bg']};border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)
        cont = QWidget()
        cont.setStyleSheet(f"background:{self.t['setting_bg']};")
        scroll.setWidget(cont)
        self.main_lay = QVBoxLayout(cont)
        self.main_lay.setContentsMargins(40, 32, 40, 40)
        self.main_lay.setSpacing(20)
        self._populate()

    def _populate(self):
        while self.main_lay.count():
            it = self.main_lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        t = self.t
        ttl = QLabel("Pengaturan")
        ttl.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{t['text1']};background:transparent;")
        sub = QLabel("Kelola preferensi dan akses admin")
        sub.setFont(QFont("Arial", 12))
        sub.setStyleSheet(f"color:{t['text2']};background:transparent;")
        self.main_lay.addWidget(ttl); self.main_lay.addWidget(sub)
        
        # Admin card
        admin_card = Card(t["setting_card_bg"], t["card_border"], 18)
        drop_shadow(admin_card, 14, "#00000010", 3)
        al = QVBoxLayout(admin_card)
        al.setContentsMargins(28, 24, 28, 24)
        al.setSpacing(16)
        ah = QHBoxLayout()
        ali = QLabel("🔒")
        ali.setFont(QFont("Arial", 18))
        ali.setStyleSheet("background:transparent;")
        aht = QLabel("Mode Admin")
        aht.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        aht.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        ah.addWidget(ali); ah.addWidget(aht); ah.addStretch(); al.addLayout(ah)
        if not self.is_admin:
            login_btn = QPushButton("Login sebagai Admin")
            login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            login_btn.setFixedSize(200, 44)
            login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            login_btn.setStyleSheet(f"QPushButton{{background:{t['price_fg']};color:white;border:none;border-radius:14px;}}QPushButton:hover{{background:{t['banner_from']};}}")
            login_btn.clicked.connect(self._show_login)
            al.addWidget(login_btn)
        else:
            status = QLabel("✅ Login sebagai Admin")
            status.setFont(QFont("Arial", 12))
            status.setStyleSheet(f"color:#22c55e;background:transparent;")
            logout = QPushButton("Logout")
            logout.setFont(QFont("Arial", 11))
            logout.setFixedSize(100, 36)
            logout.setCursor(Qt.CursorShape.PointingHandCursor)
            logout.setStyleSheet(f"QPushButton{{background:{t['btn_bg']};color:{t['text1']};border:1px solid {t['nav_border']};border-radius:12px;}}QPushButton:hover{{background:{t['cart_item_bg']};}}")
            logout.clicked.connect(self._logout)
            al.addWidget(status); al.addWidget(logout)
        self.main_lay.addWidget(admin_card)

        refresh_card = Card(t["setting_card_bg"], t["card_border"], 18)
        drop_shadow(refresh_card, 14, "#00000010", 3)
        rl = QVBoxLayout(refresh_card)
        rl.setContentsMargins(28, 24, 28, 24)
        rl.setSpacing(16)
        rh = QHBoxLayout()
        rhi = QLabel("📥")
        rhi.setFont(QFont("Arial", 18))
        rhi.setStyleSheet("background:transparent;")
        rht = QLabel("Sinkronisasi Data")
        rht.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        rht.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        rh.addWidget(rhi); rh.addWidget(rht); rh.addStretch(); rl.addLayout(rh)
        refresh_btn = QPushButton("↻ Perbarui Data Promo")
        refresh_btn.setFixedHeight(44)
        refresh_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet(f"QPushButton{{background:{t['add_bg']};color:{t['add_fg']};border:none;border-radius:12px;}}QPushButton:hover{{background:{t['price_fg']};}}")
        refresh_btn.clicked.connect(self.app._sync)
        rl.addWidget(refresh_btn)
        self.main_lay.addWidget(refresh_card)

        font_card = Card(t["setting_card_bg"], t["card_border"], 18)
        drop_shadow(font_card, 14, "#00000010", 3)
        fl = QVBoxLayout(font_card)
        fl.setContentsMargins(28, 24, 28, 24)
        fl.setSpacing(16)
        fh = QHBoxLayout()
        fhi = QLabel("T")
        fhi.setFont(QFont("Arial", 18))
        fhi.setStyleSheet("background:transparent;")
        fht = QLabel("Ukuran Font Aplikasi")
        fht.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        fht.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        fh.addWidget(fhi); fh.addWidget(fht); fh.addStretch(); fl.addLayout(fh)
        
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setMinimum(0)
        self.font_slider.setMaximum(4)
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_slider.setTickInterval(1)
        sizes = ["Sangat Kecil", "Kecil", "Normal", "Besar", "Sangat Besar"]
        if self.font_size in sizes:
            self.font_slider.setValue(sizes.index(self.font_size))
        else:
            self.font_slider.setValue(2)
            
        self.font_slider.valueChanged.connect(self._on_font_slider)
        
        sl_lay = QHBoxLayout()
        sl_lay.addWidget(QLabel("A", font=QFont("Arial", 8)))
        sl_lay.addWidget(self.font_slider)
        sl_lay.addWidget(QLabel("A", font=QFont("Arial", 16)))
        fl.addLayout(sl_lay)
        
        self.font_lbl = QLabel(f"Terpilih: {self.font_size}")
        self.font_lbl.setFont(QFont("Arial", 10))
        self.font_lbl.setStyleSheet(f"color:{t['text2']};background:transparent;")
        self.font_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(self.font_lbl)
        
        self.main_lay.addWidget(font_card)
        
        
        # About card
        about_card = Card(t["setting_card_bg"], t["card_border"], 18)
        drop_shadow(about_card, 14, "#00000010", 3)
        abl = QVBoxLayout(about_card)
        abl.setContentsMargins(28, 24, 28, 24)
        abl.setSpacing(12)
        abh = QHBoxLayout()
        abi = QLabel("ℹ️")
        abi.setFont(QFont("Arial", 18))
        abi.setStyleSheet("background:transparent;")
        abt = QLabel("Tentang Aplikasi")
        abt.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        abt.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        abh.addWidget(abi); abh.addWidget(abt); abh.addStretch(); abl.addLayout(abh)
        for label, val in [
            ("Radar Promo", "Aplikasi pencari promo supermarket untuk mahasiswa di area Bandung Barat"),
            ("Versi", "1.0.0"),
            ("Developer", "Tim Radar Promo\nMahasiswa D4 Teknik Informatika Politek Negeri Bandung 2025"),
            ("Cakupan Area", "Ciwaruga, Sarijadi, Gegerkalong (Bandung Utara)"),
        ]:
            div = QFrame()
            div.setFrameShape(QFrame.Shape.HLine)
            div.setStyleSheet(f"color:{t['divider']};")
            abl.addWidget(div)
            lbl = QLabel(label)
            lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{t['text1']};background:transparent;")
            vl = QLabel(val)
            vl.setFont(QFont("Arial", 11))
            vl.setWordWrap(True)
            vl.setStyleSheet(f"color:{t['text2']};background:transparent;")
            abl.addWidget(lbl)
            abl.addWidget(vl)
        self.main_lay.addWidget(about_card)
        self.main_lay.addStretch()

    def _show_login(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Login Admin")
        dlg.setFixedSize(360, 240)
        dlg.setStyleSheet(f"background:{self.t['setting_card_bg']};")
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(24, 24, 24, 24)
        dl.setSpacing(14)
        QLabel_style = f"color:{self.t['text1']};background:transparent;font-size:12px;"
        ul = QLabel("Username")
        ul.setStyleSheet(QLabel_style)
        dl.addWidget(ul)
        user = QLineEdit()
        user.setPlaceholderText("Masukkan username")
        user.setStyleSheet(f"background:{self.t['input_bg']};color:{self.t['search_fg']};border:1px solid {self.t['input_border']};border-radius:10px;padding:8px 12px;font-size:12px;")
        dl.addWidget(user)
        pl = QLabel("Password")
        pl.setStyleSheet(QLabel_style)
        dl.addWidget(pl)
        pwd = QLineEdit()
        pwd.setPlaceholderText("Masukkan password")
        pwd.setEchoMode(QLineEdit.EchoMode.Password)
        pwd.setStyleSheet(f"background:{self.t['input_bg']};color:{self.t['search_fg']};border:1px solid {self.t['input_border']};border-radius:10px;padding:8px 12px;font-size:12px;")
        dl.addWidget(pwd)
        btn_row = QHBoxLayout()
        login_b = QPushButton("Login")
        login_b.setFixedSize(100, 38)
        login_b.setCursor(Qt.CursorShape.PointingHandCursor)
        login_b.setStyleSheet(f"background:{self.t['pill_on_bg']};color:white;border-radius:12px;font-weight:bold;")
        login_b.clicked.connect(dlg.accept)
        cancel_b = QPushButton("Batal")
        cancel_b.setFixedSize(100, 38)
        cancel_b.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_b.setStyleSheet(f"background:{self.t['btn_bg']};color:{self.t['text1']};border-radius:12px;border:1px solid {self.t['nav_border']};")
        cancel_b.clicked.connect(dlg.reject)
        btn_row.addWidget(login_b)
        btn_row.addWidget(cancel_b)
        btn_row.addStretch()
        dl.addLayout(btn_row)
        if dlg.exec():
            if user.text() == "admin" and pwd.text() == "admin123":
                self.is_admin = True
                self._populate()
                QMessageBox.information(self, "Berhasil", "Login berhasil! Membuka Dashboard Admin...")
                import subprocess, sys, os
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                else:
                    base_path = os.path.dirname(os.path.abspath(__file__))
                script_path = os.path.join(base_path, "admin_tool.py")
                for python_cmd in [sys.executable, "python", "python3", "py"]:
                    try:
                        subprocess.Popen([python_cmd, script_path])
                        break
                    except FileNotFoundError:
                        continue
            else:
                QMessageBox.warning(self, "Login Gagal", "Username atau password salah!\n(Hint: admin / admin123)")

    def _logout(self):
        self.is_admin = False
        self._populate()

    def _on_font_slider(self, val):
        sizes = ["Sangat Kecil", "Kecil", "Normal", "Besar", "Sangat Besar"]
        fs = sizes[val]
        self.font_size = fs
        if hasattr(self, 'font_lbl'):
            self.font_lbl.setText(f"Terpilih: {fs}")
        if self.app:
            self.app.change_global_font_size(fs)

    def _set_font(self, fs):
        self.font_size = fs
        if self.app:
            self.app.change_global_font_size(fs)
        self._populate()

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['setting_bg']};")
        self._populate()

class SearchWorker(QThread):
    finishedSignal = Signal(list)

    def __init__(self, keyword, selected_cat, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.selected_cat = selected_cat
        self.results = []

    def run(self):
        try:
            if self.isInterruptionRequested():
                return
            raw_records = data_manager.read_local_data() if data_manager else []
            if self.isInterruptionRequested():
                return
            records = []
            for r in raw_records:
                harga_normal = r.get("harga_normal") or 0
                harga_promo = r.get("harga_promo") or 0
                records.append({
                    "id": r.get("id", ""),
                    "nama_produk": r.get("nama_produk", ""),
                    "name": r.get("nama_produk", ""),
                    "category": r.get("kategori") or "Lainnya",
                    "price": harga_promo,
                    "harga_normal": harga_normal,
                    "harga_promo": harga_promo,
                    "diskon_persen": r.get("diskon_persen") or 0,
                    "store": r.get("nama_cabang", r.get("brand_toko", "")),
                    "area": (r.get("area_tags", [""])[0] if r.get("area_tags") else ""),
                    "distance": "",
                    "image": r.get("image_url", ""),
                    "jenis_harga": r.get("jenis_harga", ""),
                    "search_vector": r.get("search_vector", ""),
                })
            if self.isInterruptionRequested():
                return
            category_for_pipeline = self.selected_cat if self.selected_cat not in ("Semua", "Promo") else None
            filtered, _ = engine.run_pipeline(
                records,
                area=None,
                category=category_for_pipeline,
                brand=None,
                jenis_harga=None,
                keyword=self.keyword if self.keyword and self.keyword.strip() else None,
                reverse=False,
            )
            if self.isInterruptionRequested():
                return
            self.results = filtered
            self.finishedSignal.emit(self.results)
        except Exception as e:
            print(f"SearchWorker error: {e}")
            self.finishedSignal.emit([])

