import os
import sys
import logging
import time
import urllib.request
import qtawesome as qta
import threading
import math
import json
from datetime import datetime

APP_BASE = os.path.dirname(os.path.abspath(__file__))
from io import BytesIO
import requests
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QGridLayout,
    QFrame, QStackedWidget, QSizePolicy, QComboBox, QDialog,
    QGraphicsDropShadowEffect, QMessageBox, QSlider, QTextEdit,
    QListWidget, QListWidgetItem, QCheckBox, QRadioButton,
    QButtonGroup, QProgressBar, QGraphicsOpacityEffect,
    QFileDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal as Signal, QThread, QObject, QRect, QUrl, pyqtSlot, QPointF, QEvent, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QColor, QLinearGradient, QBrush,
    QPen, QPainterPath, QImage, QFontMetrics, QMovie, QIcon,
    QIntValidator
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWebChannel import QWebChannel

# ─── Environment (.env) ─────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass  # python-dotenv belum terpasang; fallback ke environment OS

import data_manager
import engine

def _svg_to_icon(path, size=24):
    renderer = QSvgRenderer(path)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

CART_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cart.json")

# ── Geolocation HTML (hidden WebView trick) ──────────────────────────
GEOHTML = """
<!DOCTYPE html><html><body>
<p id="status" style="font-family:sans-serif;font-size:14px;color:#666;">Mendeteksi lokasi...</p>
</body></html>
"""

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
    "chart_colors":["#25C799","#FF8C42","#4B9BFF","#F59E0B","#9C89B8","#F97316","#06B6D4","#84CC16"],
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
    "chart_colors":["#14B8A6","#FB923C","#60A5FA","#FBBF24","#C084FC","#F87171","#22D3EE","#A3E635"],
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
                with urllib.request.urlopen(req, timeout=15) as r:
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
    """Upload photo to Catbox and sync recommendation to Google Sheets."""
    def __init__(self, photo, recommendation):
        super().__init__()
        self.photo = photo
        self.recommendation = recommendation
        self.signals = RecUploadSignals()

    def run(self):
        print("[DEBUG] RecommendationUploader.run() started")
        try:
            print("[DEBUG] Uploading photo to Catbox...")
            foto_url = data_manager.upload_photo(self.photo)
            print(f"[DEBUG] Catbox returned foto_url: {foto_url}")
            if not foto_url:
                print("[DEBUG] Catbox upload failed - emitting failure")
                self.signals.failure.emit("Gagal mengunggah foto ke Catbox")
                return

            entry = self.recommendation.copy()
            entry["foto_url"] = foto_url

            print("[DEBUG] Sending recommendation to Google Sheets...")
            success = data_manager.add_rekomendasi(entry)
            print(f"[DEBUG] Google Sheets result: {success}")
            if success:
                print("[DEBUG] Upload success - emitting success signal")
                self.signals.success.emit(foto_url)
            else:
                print("[DEBUG] Google Sheets upload failed - emitting failure")
                self.signals.failure.emit("Gagal mengirim rekomendasi ke Google Sheets")
        except Exception as e:
            print(f"[DEBUG] Exception in uploader: {e}")
            self.signals.failure.emit(str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# JS BRIDGE (QWebChannel)
# ═══════════════════════════════════════════════════════════════════════════════

class JSBridge(QObject):
    """Exposes Python methods to JavaScript in the map web view."""
    upload_success = Signal(str)
    upload_failure = Signal(str)
    location_ready = Signal(float, float)
    location_error = Signal(str)

    def __init__(self, page, toast, t, parent=None):
        super().__init__(parent)
        self.page = page
        self.toast = toast
        self.t = t

    @pyqtSlot(float, float)
    def receiveUserLocation(self, lat, lon):
        self.user_lat = lat
        self.user_lon = lon
        print(f"[DEBUG] User location received: {lat}, {lon}")
        if hasattr(self.page, 'refresh_store_list'):
            self.page.refresh_store_list()
        self.location_ready.emit(lat, lon)

    @pyqtSlot(str)
    def receiveLocationError(self, msg):
        print(f"[DEBUG] Location error: {msg}")
        self.location_error.emit(msg)

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
        self.setFont(QFont("Google Sans", 11))
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
        self.setFixedHeight(146)

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

        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)
        text_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.title = QLabel("🔥 Promo Terbaru untuk Mahasiswa")
        self.title.setFont(QFont("Google Sans", 20, QFont.Weight.Bold))
        self.title.setStyleSheet("color:white;background:transparent;")
        self.title.setWordWrap(True)

        self.sub = QLabel("Dapatkan harga termurah hari ini di sekitar Polban!")
        self.sub.setFont(QFont("Google Sans", 11))
        self.sub.setStyleSheet("color:rgba(255,255,255,220);background:transparent;")
        self.sub.setWordWrap(True)

        text_lay.addWidget(self.title)
        text_lay.addWidget(self.sub)
        lay.addLayout(text_lay)

        self.people_img = QLabel()
        px_people = QPixmap(os.path.join(APP_BASE, "UI", "Home", "Assets", "Illustration_3.png"))
        if not px_people.isNull():
            px_people = px_people.scaledToHeight(200, Qt.TransformationMode.SmoothTransformation)
            self.people_img.setPixmap(px_people)
            self.people_img.setFixedSize(px_people.width(), 155)
        self.people_img.setStyleSheet("background:transparent;")
        lay.addWidget(self.people_img, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.group_img = QLabel()
        px_group = QPixmap(os.path.join(APP_BASE, "UI", "Home", "Assets", "Group_69.png"))
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

class RecommendationCard(Card):
    """Card widget for displaying a recommendation in a grid."""
    detail_requested = Signal(dict)

    def __init__(self, rec, t, parent=None, card_w=280):
        super().__init__(t["card_bg"], t["card_border"], 12, parent)
        self.rec = rec
        self.t = t
        self._card_w = card_w
        card_h = max(340, int(card_w * 1.15))
        self.setFixedSize(card_w, card_h)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._loaders = []
        self._build()
        drop_shadow(self, 10, "#00000015", 2)

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.setSpacing(4)

        # ── Photo container ──────────────────────────────────────────────────
        photo_h = max(140, int(self._card_w * 0.55))
        self.img_cont = QWidget()
        self.img_cont.setFixedSize(self._card_w - 20, photo_h)
        self.img_cont.setStyleSheet(f"background:#f3f4f6;border-radius:10px 10px 0 0;")
        self.img_lbl = QLabel(self.img_cont)
        self.img_lbl.setGeometry(0, 0, self._card_w - 20, photo_h)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setText("⏳")
        self.img_lbl.setFont(QFont("Google Sans", 22))
        self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
        lay.addWidget(self.img_cont)

        foto = self.rec.get("foto") or self.rec.get("foto_url") or self.rec.get("photo") or ""
        if foto and os.path.exists(foto):
            try:
                from PyQt6.QtGui import QPixmap as _QPixmap
                raw = _QPixmap(foto)
                if not raw.isNull():
                    scaled = raw.scaled(self._card_w - 20, photo_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.img_lbl.setPixmap(scaled)
                    self.img_lbl.setText("")
                else:
                    self.img_lbl.setText("🍽️")
                    self.img_lbl.setFont(QFont("Google Sans", 36))
            except Exception:
                self.img_lbl.setText("🍽️")
                self.img_lbl.setFont(QFont("Google Sans", 36))
        elif foto and (foto.startswith("data:") or foto.startswith("http://") or foto.startswith("https://")):
            sig = _Sig()
            sig.done.connect(self._on_img)
            if foto.startswith("data:"):
                try:
                    import base64 as _b64
                    header, data = foto.split(",", 1)
                    img_bytes = _b64.b64decode(data)
                    from PyQt6.QtGui import QImage, QPixmap as _QPixmap
                    qi = QImage.fromData(img_bytes)
                    if not qi.isNull():
                        qi_scaled = qi.scaled(self._card_w - 20, photo_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.img_lbl.setPixmap(_QPixmap.fromImage(qi_scaled))
                        self.img_lbl.setText("")
                    else:
                        self.img_lbl.setText("🍽️")
                        self.img_lbl.setFont(QFont("Google Sans", 36))
                except Exception:
                    self.img_lbl.setText("🍽️")
                    self.img_lbl.setFont(QFont("Google Sans", 36))
            else:
                foto_id = str(id(foto))
                sig.done.connect(lambda pid, px: self._on_img(pid, px))
                ldr = ImgLoader(foto, foto_id, self._card_w - 20, photo_h, sig)
                self._loaders.append((ldr, sig))
                ldr.start()
        elif foto:
            foto_id = str(id(foto))
            sig = _Sig()
            sig.done.connect(lambda pid, px: self._on_img(pid, px))
            ldr = ImgLoader(foto, foto_id, self._card_w - 20, photo_h, sig)
            self._loaders.append((ldr, sig))
            ldr.start()
        else:
            self.img_lbl.setText("🍽️")
            self.img_lbl.setFont(QFont("Google Sans", 36))
            self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")

        # ── Info section ────────────────────────────────────────────────────
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 8, 0, 0)
        il.setSpacing(4)

        # Rating row
        rating = self.rec.get("rating", 0)
        full_stars = int(round(rating)) if rating else 0
        empty_stars = 5 - full_stars
        stars_text = "★" * full_stars + "☆" * empty_stars
        self.rating_lbl = QLabel(stars_text)
        self.rating_lbl.setFont(QFont("Google Sans", 11))
        self.rating_lbl.setStyleSheet("color:#F59E0B;background:transparent;")
        il.addWidget(self.rating_lbl)

        # Nama Tempat
        self.name_lbl = QLabel(self.rec.get("nama", ""))
        self.name_lbl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setFixedHeight(self.name_lbl.fontMetrics().height() * 2 + 4)
        self.name_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        il.addWidget(self.name_lbl)

        # Alamat
        alamat = self.rec.get("alamat", "")
        self.alamat_lbl = QLabel(alamat if alamat else "")
        self.alamat_lbl.setFont(QFont("Google Sans", 10))
        self.alamat_lbl.setWordWrap(True)
        self.alamat_lbl.setFixedHeight(self.alamat_lbl.fontMetrics().height() * 2 + 4)
        self.alamat_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        if alamat:
            il.addWidget(self.alamat_lbl)

        # Menu
        menu = self.rec.get("menu", "")
        if menu:
            self.menu_lbl = QLabel(f"🍴 {menu}")
            self.menu_lbl.setFont(QFont("Google Sans", 10))
            self.menu_lbl.setWordWrap(True)
            self.menu_lbl.setFixedHeight(self.menu_lbl.fontMetrics().height() + 4)
            self.menu_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            il.addWidget(self.menu_lbl)

        # Harga
        harga_min = self.rec.get("harga_min", 0)
        harga_max = self.rec.get("harga_max", 0)
        if harga_min == 0 and harga_max == 0:
            harga_min = self.rec.get("harga", 0)
            harga_max = harga_min
        if harga_min == harga_max:
            harga_str = rp(harga_min)
        else:
            harga_str = f"{rp(harga_min)} - {rp(harga_max)}"
        self.harga_lbl = QLabel(harga_str)
        self.harga_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
        self.harga_lbl.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        il.addWidget(self.harga_lbl)

        # Deskripsi (optional)
        deskripsi = self.rec.get("deskripsi", "")
        if deskripsi:
            self.desc_lbl = QLabel(deskripsi)
            self.desc_lbl.setFont(QFont("Google Sans", 9))
            self.desc_lbl.setStyleSheet(f"color:{self.t['text2']};font-style:italic;background:transparent;")
            self.desc_lbl.setWordWrap(True)
            self.desc_lbl.setFixedHeight(self.desc_lbl.fontMetrics().height() + 4)
            il.addWidget(self.desc_lbl)

        # Contributor + tanggal
        contributor = self.rec.get("contributor", "Anonim")
        tanggal = self.rec.get("tanggal", "")
        if tanggal:
            # Normalize date to YYYY-MM-DD
            date_part = tanggal.split(" ")[0] if " " in tanggal else tanggal
        else:
            date_part = ""
        self.contributor_lbl = QLabel(
            f"👤 {contributor}" + (f" · {date_part}" if date_part else "")
        )
        self.contributor_lbl.setFont(QFont("Google Sans", 9))
        self.contributor_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        il.addWidget(self.contributor_lbl)

        lay.addWidget(info)

    def _on_img(self, pid, px):
        try:
            foto = self.rec.get("foto") or self.rec.get("foto_url") or self.rec.get("photo") or ""
            if pid != str(id(foto)) or not self.img_lbl.isVisible():
                return
            if not px.isNull():
                self.img_lbl.setPixmap(px)
                self.img_lbl.setText("")
            else:
                self.img_lbl.setText("🍽️")
                self.img_lbl.setFont(QFont("Google Sans", 36))
        except RuntimeError:
            pass

    def enterEvent(self, event):
        drop_shadow(self, 14, "#00000025", 3)
        super().enterEvent(event)

    def leaveEvent(self, event):
        drop_shadow(self, 10, "#00000015", 2)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.detail_requested.emit(self.rec)
        super().mousePressEvent(event)

# ─── StarRating widget ───────────────────────────────────────────────────────
class StarRating(QWidget):
    clicked = Signal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rating = 0
        self.stars = []
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        for i in range(5):
            lbl = QLabel("★")
            lbl.setFont(QFont("Google Sans", 18))
            lbl.setStyleSheet("color:#D1D5DB; cursor:pointer; background:transparent;")
            lbl.mousePressEvent = lambda e, idx=i+1: self._on_click(idx)
            self.stars.append(lbl)
            lay.addWidget(lbl)
    def _on_click(self, idx):
        self.rating = idx
        for i, lbl in enumerate(self.stars):
            lbl.setStyleSheet(f"color:{'#F59E0B' if i < idx else '#D1D5DB'}; cursor:pointer; background:transparent;")
        self.clicked.emit(idx)
    def getRating(self):
        return self.rating


# ─── RecommendationFormDialog ─────────────────────────────────────────────────
class RecommendationFormDialog(QDialog):
    submitted = Signal(dict)
    def __init__(self, t, parent=None):
        super().__init__(parent)
        self.t = t
        self.setWindowTitle("Tambah Rekomendasi")
        self.setModal(True)
        self.setFixedSize(440, 620)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self._photo_path = None

        # Main container with background
        container = QWidget(self)
        container.setFixedSize(440, 620)
        container.setStyleSheet("background:#ffffff; border-radius:16px;")

        lay = QVBoxLayout(container)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = QWidget()
        hdr.setFixedHeight(48)
        hdr.setStyleSheet("background:transparent;")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(8)

        back_btn = QPushButton("←")
        back_btn.setFixedSize(36, 36)
        back_btn.setFont(QFont("Google Sans", 16))
        back_btn.setStyleSheet("background:#F3F4F6; border:none; border-radius:18px; color:#374151;")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.reject)

        title_lbl = QLabel("Tambah Rekomendasi")
        title_lbl.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
        title_lbl.setStyleSheet("background:transparent; color:#1F2937;")
        hl.addWidget(back_btn)
        hl.addWidget(title_lbl)
        hl.addStretch()
        lay.addWidget(hdr)
        lay.addSpacing(6)

        # ── Scrollable form area ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(490)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}QScrollBar:vertical{width:4px;background:transparent;}QScrollBar::handle:vertical{background:#d1d5db;border-radius:2px;min-height:30px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        form_cont = QWidget()
        form_cont.setStyleSheet("background:transparent;")
        fl = QVBoxLayout(form_cont)
        fl.setContentsMargins(0, 0, 8, 0)
        fl.setSpacing(16)

        field_style = "QLineEdit, QTextEdit{background:#ffffff;border:1px solid #d1d5db;border-radius:8px;padding:10px;font-family:'Google Sans';font-size:11pt;color:#1F2937;}QLineEdit:focus, QTextEdit:focus{border-color:#0FB291;}QLineEdit::placeholder, QTextEdit::placeholder{color:#9ca3af;}"
        label_style = "QLabel{font-family:'Google Sans';font-size:10pt;font-weight:bold;color:#374151;background:transparent;}"

        def make_field(label, widget):
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            wl = QVBoxLayout(w)
            wl.setContentsMargins(0, 0, 0, 0)
            wl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setStyleSheet(label_style)
            wl.addWidget(lbl)
            if isinstance(widget, QTextEdit):
                widget.setStyleSheet("background:#ffffff;border:1px solid #d1d5db;border-radius:8px;padding:10px;font-family:'Google Sans';font-size:11pt;color:#1F2937;")
                widget.setFixedHeight(72)
            else:
                widget.setStyleSheet("background:#ffffff;border:1px solid #d1d5db;border-radius:8px;padding:10px;font-family:'Google Sans';font-size:11pt;color:#1F2937;")
                widget.setFixedHeight(40)
            wl.addWidget(widget)
            return w

        # 1. Nama Tempat
        self.nama_inp = QLineEdit()
        self.nama_inp.setPlaceholderText("Warung Nasi Ibu Imas")
        fl.addWidget(make_field("NAMA TEMPAT *", self.nama_inp))

        # 2. Alamat
        self.alamat_inp = QLineEdit()
        self.alamat_inp.setPlaceholderText("Jl. Sarimanah Blok 10 No. 86, Sarijadi, Bandung")
        fl.addWidget(make_field("ALAMAT", self.alamat_inp))

        # 3. Menu Andalan
        self.menu_inp = QLineEdit()
        self.menu_inp.setPlaceholderText("Nasi Timbel, Ayam Goreng, Sambal Terasi")
        fl.addWidget(make_field("MENU ANDALAN *", self.menu_inp))

        # 4. Range Harga (two fields side by side)
        range_w = QWidget()
        range_w.setStyleSheet("background:transparent;")
        range_lay = QHBoxLayout(range_w)
        range_lay.setContentsMargins(0, 0, 0, 0)
        range_lay.setSpacing(10)

        harga_min_w = QWidget()
        harga_min_w.setStyleSheet("background:transparent;")
        harga_min_lay = QVBoxLayout(harga_min_w)
        harga_min_lay.setContentsMargins(0, 0, 0, 0)
        harga_min_lay.setSpacing(4)
        lbl_min = QLabel("MIN (Rp)")
        lbl_min.setStyleSheet(label_style)
        self.harga_min_inp = QLineEdit()
        self.harga_min_inp.setPlaceholderText("10000")
        self.harga_min_inp.setValidator(QIntValidator(0, 999999999, self))
        self.harga_min_inp.setStyleSheet(field_style)
        self.harga_min_inp.setFixedHeight(40)
        harga_min_lay.addWidget(lbl_min)
        harga_min_lay.addWidget(self.harga_min_inp)

        harga_max_w = QWidget()
        harga_max_w.setStyleSheet("background:transparent;")
        harga_max_lay = QVBoxLayout(harga_max_w)
        harga_max_lay.setContentsMargins(0, 0, 0, 0)
        harga_max_lay.setSpacing(4)
        lbl_max = QLabel("MAX (Rp)")
        lbl_max.setStyleSheet(label_style)
        self.harga_max_inp = QLineEdit()
        self.harga_max_inp.setPlaceholderText("25000")
        self.harga_max_inp.setValidator(QIntValidator(0, 999999999, self))
        self.harga_max_inp.setStyleSheet(field_style)
        self.harga_max_inp.setFixedHeight(40)
        harga_max_lay.addWidget(lbl_max)
        harga_max_lay.addWidget(self.harga_max_inp)

        range_lay.addWidget(harga_min_w, 1)
        range_lay.addWidget(harga_max_w, 1)
        range_label = QLabel("RANGE HARGA (Rp) *")
        range_label.setStyleSheet(label_style)
        fl.addWidget(range_label)
        fl.addWidget(range_w)

        # 5. Rating
        rating_w = QWidget()
        rating_w.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(rating_w)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)
        rl2 = QLabel("RATING")
        rl2.setStyleSheet(label_style)
        rl.addWidget(rl2)
        self.star_rating = StarRating()
        rl.addWidget(self.star_rating)
        fl.addWidget(rating_w)

        # 6. Deskripsi Singkat
        self.desc_inp = QTextEdit()
        self.desc_inp.setPlaceholderText("Deskripsi singkat...")
        fl.addWidget(make_field("DESKRIPSI SINGKAT", self.desc_inp))

        # 7. Foto
        foto_w = QWidget()
        foto_w.setStyleSheet("background:transparent;")
        fotol = QVBoxLayout(foto_w)
        fotol.setContentsMargins(0, 0, 0, 0)
        fotol.setSpacing(4)
        fotol2 = QLabel("FOTO")
        fotol2.setStyleSheet(label_style)
        fotol.addWidget(fotol2)
        foto_row = QHBoxLayout()
        foto_row.setSpacing(10)
        self.foto_btn = QPushButton("📷 Pilih Gambar")
        self.foto_btn.setFont(QFont("Google Sans", 11))
        self.foto_btn.setFixedHeight(40)
        self.foto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.foto_btn.setStyleSheet("QPushButton{background:#F3F4F6;border:1px solid #d1d5db;border-radius:8px;padding:0 16px;color:#374151;}QPushButton:hover{background:#E5E7EB;}")
        self.foto_btn.clicked.connect(self._on_pick_photo)
        self.foto_preview = QLabel()
        self.foto_preview.setFixedSize(80, 80)
        self.foto_preview.setStyleSheet("background:#F3F4F6;border:1px solid #d1d5db;border-radius:8px;")
        self.foto_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foto_preview.setText("Tidak ada\ngambar")
        self.foto_preview.setFont(QFont("Google Sans", 9))
        self.foto_preview.setStyleSheet("color:#9ca3af;background:#F3F4F6;border:1px solid #d1d5db;border-radius:8px;")
        foto_row.addWidget(self.foto_btn, 1)
        foto_row.addWidget(self.foto_preview)
        fotol.addLayout(foto_row)
        fl.addWidget(foto_w)

        # 8. Nama Kontributor
        self.kontributor_inp = QLineEdit()
        self.kontributor_inp.setPlaceholderText("Anonim")
        self.kontributor_inp.setText("Anonim")
        fl.addWidget(make_field("NAMA KONTRIBUTOR", self.kontributor_inp))

        fl.addStretch()
        scroll.setWidget(form_cont)
        lay.addWidget(scroll)

        # ── Footer buttons ───────────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(52)
        footer.setStyleSheet("background:transparent;")
        fr = QHBoxLayout(footer)
        fr.setContentsMargins(0, 0, 0, 0)
        fr.setSpacing(12)

        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Medium))
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("QPushButton{background:#F3F4F6;color:#374151;border:none;border-radius:10px;font-family:'Google Sans';}QPushButton:hover{background:#E5E7EB;}")
        self.cancel_btn.clicked.connect(self.reject)

        self.submit_btn = QPushButton("Kirim Rekomendasi")
        self.submit_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
        self.submit_btn.setFixedHeight(44)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setStyleSheet("QPushButton{background:#0FB291;color:white;border:none;border-radius:10px;font-family:'Google Sans';}QPushButton:hover{background:#0a8f79;}")
        self.submit_btn.clicked.connect(self._on_submit)

        fr.addWidget(self.cancel_btn, 1)
        fr.addWidget(self.submit_btn, 2)
        lay.addWidget(footer)

        drop_shadow(container, 20, "#00000020", 4)

        self._container = container

    def _on_pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar", "",
            "Gambar (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if path:
            self._photo_path = path
            pix = QPixmap(path).scaled(76, 76, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            if not pix.isNull():
                self.foto_preview.setPixmap(pix)
                self.foto_preview.setText("")
            else:
                self.foto_preview.setText("Tidak ada\ngambar")
                self.foto_preview.setFont(QFont("Google Sans", 9))
                self.foto_preview.setStyleSheet("color:#9ca3af;background:#F3F4F6;border:1px solid #d1d5db;border-radius:8px;")

    def _on_submit(self):
        nama = self.nama_inp.text().strip()
        menu = self.menu_inp.text().strip()
        harga_min_str = self.harga_min_inp.text().strip()
        harga_max_str = self.harga_max_inp.text().strip()
        kontributor = self.kontributor_inp.text().strip() or "Anonim"
        alamat = self.alamat_inp.text().strip()
        desc = self.desc_inp.toPlainText().strip()
        rating = self.star_rating.getRating()

        if not nama:
            QMessageBox.warning(self, "Validasi", "Nama tempat harus diisi.")
            self.nama_inp.setFocus()
            return
        if not menu:
            QMessageBox.warning(self, "Validasi", "Menu andalan harus diisi.")
            self.menu_inp.setFocus()
            return
        if not harga_min_str:
            QMessageBox.warning(self, "Validasi", "Harga min harus diisi.")
            self.harga_min_inp.setFocus()
            return
        if not harga_max_str:
            QMessageBox.warning(self, "Validasi", "Harga max harus diisi.")
            self.harga_max_inp.setFocus()
            return

        try:
            harga_min_val = int(harga_min_str)
            harga_max_val = int(harga_max_str)
        except ValueError:
            QMessageBox.warning(self, "Validasi", "Harga harus berupa angka.")
            return
        if harga_min_val > harga_max_val:
            QMessageBox.warning(self, "Validasi", "Harga min tidak boleh lebih dari harga max.")
            return

        import datetime
        rec = {
            "id": f"rec_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "nama": nama,
            "alamat": alamat,
            "menu": menu,
            "harga_min": harga_min_val,
            "harga_max": harga_max_val,
            "rating": rating,
            "deskripsi": desc,
            "foto": self._photo_path or "",
            "kontributor": kontributor,
            "tanggal": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
        }

        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rekomendasi.json")
        try:
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
            else:
                data = []
            data.append(rec)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menyimpan: {e}")
            return

        self.submitted.emit(rec)

        toast = self.parent().toast if self.parent() else None
        if self._photo_path and toast:
            uploader = RecommendationUploader(self._photo_path, rec)
            uploader.signals.success.connect(lambda _: toast.show_msg("Rekomendasi terkirim ke cloud!", self.t))
            uploader.signals.failure.connect(lambda err: toast.show_msg(f"Sync gagal: {err}", self.t))
            uploader.start()
            toast.show_msg("Rekomendasi disimpan! (sync ke cloud...)", self.t)
        else:
            if toast:
                toast.show_msg("Rekomendasi disimpan!", self.t)

        self.accept()


# ─── RecommendationDetailDialog ──────────────────────────────────────────────
class RecommendationDetailDialog(QDialog):
    def __init__(self, rec, t, parent=None):
        super().__init__(parent)
        self.rec = rec
        self.t = t
        self.setModal(True)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(480, 740)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            self.move(
                sg.x() + (sg.width() - 480) // 2,
                sg.y() + (sg.height() - 740) // 2
            )

        self.setStyleSheet("background:#ffffff;")
        drop_shadow(self, 24, "#00000025", 5)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Hero photo ────────────────────────────────────────────────────────
        self.hero = QWidget()
        self.hero.setFixedHeight(220)
        self.hero.setStyleSheet("background:#e8f5e9;border-radius:16px 16px 0 0;")
        hero_lay = QVBoxLayout(self.hero)
        hero_lay.setContentsMargins(0, 0, 0, 0)

        self.hero_lbl = QLabel("🍽️", self.hero)
        self.hero_lbl.setFixedSize(480, 220)
        self.hero_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hero_lbl.setFont(QFont("Google Sans", 48))
        self.hero_lbl.setStyleSheet("background:transparent;color:#9ca3af;")

        # Back button overlay
        self.back_btn = QPushButton("←", self.hero)
        self.back_btn.setFixedSize(36, 36)
        self.back_btn.move(12, 12)
        self.back_btn.setFont(QFont("Google Sans", 16))
        self.back_btn.setStyleSheet("QPushButton{background:rgba(255,255,255,0.9);border:none;border-radius:18px;color:#374151;font-size:16px;}QPushButton:hover{background:white;}")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.accept)

        # Load photo
        foto_url = rec.get("foto") or rec.get("foto_url") or rec.get("photo") or ""
        if foto_url and os.path.exists(foto_url):
            pix = QPixmap(foto_url).scaled(480, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            if not pix.isNull():
                self.hero_lbl.setPixmap(pix)
                self.hero_lbl.setText("")
        elif foto_url and (foto_url.startswith("http://") or foto_url.startswith("https://")):
            self._load_photo(foto_url)

        lay.addWidget(self.hero)

        # ── Scrollable info area ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea{border:none;background:white;}QScrollBar:vertical{width:4px;background:transparent;}QScrollBar::handle:vertical{background:#d1d5db;border-radius:2px;min-height:30px;}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}")
        cont = QWidget()
        cont.setStyleSheet("background:white;")
        cl = QVBoxLayout(cont)
        cl.setContentsMargins(24, 16, 24, 16)
        cl.setSpacing(0)

        # Title
        nama = rec.get("nama") or rec.get("name") or "Tanpa Nama"
        title_lbl = QLabel(nama)
        title_lbl.setFont(QFont("Google Sans", 17, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color:#1F2937;background:transparent;")
        title_lbl.setWordWrap(True)
        title_lbl.setFixedHeight(28)
        cl.addWidget(title_lbl)
        cl.addSpacing(16)

        # Rating stars
        rating_val = rec.get("rating", 0)
        if rating_val > 0:
            stars_lbl = QLabel("★" * int(rating_val) + "☆" * (5 - int(rating_val)))
            stars_lbl.setFont(QFont("Google Sans", 13))
            stars_lbl.setStyleSheet("color:#F59E0B;background:transparent;")
            cl.addWidget(stars_lbl)
            cl.addSpacing(12)

        # ── Info rows (re-use pattern from _show_recommendation_detail) ───────
        def add_info_row(icon_text, label_text, value_text):
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            row.setFixedHeight(52)
            row_lay = QHBoxLayout(row)
            row_lay.setContentsMargins(0, 8, 0, 8)
            row_lay.setSpacing(12)

            icon_lbl = QLabel(icon_text)
            icon_lbl.setFixedSize(28, 28)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setFont(QFont("Google Sans", 15))
            icon_lbl.setStyleSheet("background:transparent; color:#0D9488;")

            text_col = QWidget()
            text_col.setStyleSheet("background:transparent;")
            tc = QVBoxLayout(text_col)
            tc.setContentsMargins(0, 0, 0, 0)
            tc.setSpacing(1)

            lbl = QLabel(label_text)
            lbl.setFont(QFont("Google Sans", 10))
            lbl.setStyleSheet("color:#9ca3af; background:transparent;")

            val = QLabel(value_text)
            val.setFont(QFont("Google Sans", 12, QFont.Weight.Medium))
            val.setStyleSheet("color:#1f2937; background:transparent;")
            val.setWordWrap(True)

            tc.addWidget(lbl)
            tc.addWidget(val)
            row_lay.addWidget(icon_lbl)
            row_lay.addWidget(text_col, 1)
            cl.addWidget(row)

            sep = QWidget()
            sep.setFixedHeight(1)
            sep.setStyleSheet("background:#f3f4f6;")
            cl.addWidget(sep)

        # Menu Andalan
        menu = rec.get("menu") or rec.get("place") or ""
        if menu:
            add_info_row("🍴", "MENU ANDALAN", menu)

        # Harga
        harga_min = rec.get("harga_min", 0) or rec.get("harga", 0)
        harga_max = rec.get("harga_max", 0) or rec.get("harga", 0)
        if harga_min == 0 and harga_max == 0:
            harga_min = harga_max = 0
        if harga_min == harga_max:
            harga_str = rp(harga_min) if harga_min else "-"
        else:
            harga_str = f"{rp(harga_min)} - {rp(harga_max)}"
        add_info_row("💰", "HARGA", harga_str)

        # Alamat
        lokasi = rec.get("alamat") or rec.get("address") or rec.get("lokasi_teks") or "Tidak ada alamat"
        add_info_row("📍", "ALAMAT", lokasi)

        # Kontributor + Tanggal
        contributor = rec.get("kontributor") or rec.get("contributor") or "Anonim"
        tanggal = rec.get("tanggal") or ""
        kontributor_text = contributor + (f" · {tanggal}" if tanggal else "")
        add_info_row("👤", "KONTRIBUTOR", kontributor_text)

        # ── Description quote box ─────────────────────────────────────────────
        desc = rec.get("deskripsi") or rec.get("description") or rec.get("desc") or ""
        if desc:
            cl.addSpacing(10)
            quote_box = QWidget()
            quote_box.setStyleSheet("background:#f0fdf4; border-radius:10px; border:1px solid #bbf7d0;")
            qb_lay = QVBoxLayout(quote_box)
            qb_lay.setContentsMargins(16, 14, 16, 14)
            desc_lbl = QLabel(f'"{desc}"')
            desc_lbl.setFont(QFont("Google Sans", 11))
            desc_lbl.setStyleSheet("color:#374151; background:transparent; font-style:italic;")
            desc_lbl.setWordWrap(True)
            qb_lay.addWidget(desc_lbl)
            cl.addWidget(quote_box)

        # ── Reaction buttons ─────────────────────────────────────────────────
        cl.addSpacing(14)
        rekomen_id = rec.get("id") or rec.get("latitude") or rec.get("lat") or str(id(rec))
        reac_enak = rec.get("reaksi_enak", 0) or rec.get("enak", 0) or 0
        reac_murah = rec.get("reaksi_murah", 0) or rec.get("murah", 0) or 0

        reac_widget = QWidget()
        reac_widget.setStyleSheet("background:transparent;")
        reac_lay = QHBoxLayout(reac_widget)
        reac_lay.setContentsMargins(0, 0, 0, 0)
        reac_lay.setSpacing(10)

        self.enak_btn = QPushButton(f"👍 Enak ({reac_enak})" if reac_enak else "👍 Enak")
        self.enak_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
        self.enak_btn.setFixedHeight(40)
        self.enak_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enak_btn.setStyleSheet("QPushButton{background:white;color:#0D9488;border:2px solid #0D9488;border-radius:20px;padding:0 20px;}QPushButton:hover{background:#f0fdfa;}")
        self.enak_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.enak_btn.clicked.connect(lambda: self._on_reaction_clicked(rekomen_id, "enak"))

        self.murah_btn = QPushButton(f"💰 Murah ({reac_murah})" if reac_murah else "💰 Murah")
        self.murah_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
        self.murah_btn.setFixedHeight(40)
        self.murah_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.murah_btn.setStyleSheet("QPushButton{background:white;color:#0D9488;border:2px solid #0D9488;border-radius:20px;padding:0 20px;}QPushButton:hover{background:#f0fdfa;}")
        self.murah_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.murah_btn.clicked.connect(lambda: self._on_reaction_clicked(rekomen_id, "murah"))

        reac_lay.addWidget(self.enak_btn)
        reac_lay.addWidget(self.murah_btn)
        cl.addWidget(reac_widget)

        cl.addStretch()
        scroll.setWidget(cont)
        lay.addWidget(scroll, 1)

    def _load_photo(self, url):
        manager = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(url))
        timer = QTimer()
        timer.setSingleShot(True)
        current_reply = [None]

        def on_loaded(reply):
            timer.stop()
            current_reply[0] = reply
            if reply.error() == QNetworkReply.NetworkError.NoError:
                raw = reply.readAll()
                img = QImage.fromData(raw)
                if not img.isNull():
                    pix = QPixmap.fromImage(img).scaled(
                        480, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    if not pix.isNull():
                        self.hero_lbl.setPixmap(pix)
                        self.hero_lbl.setText("")

        def on_timeout():
            if current_reply[0] is not None:
                current_reply[0].abort()

        timer.timeout.connect(on_timeout)
        manager.finished.connect(on_loaded)
        timer.start(10000)
        reply = manager.get(request)
        current_reply[0] = reply

    def _on_reaction_clicked(self, rekomen_id, reaction_type):
        btn = self.enak_btn if reaction_type == "enak" else self.murah_btn
        btn.setEnabled(False)
        btn.setText("...")

        def do_reaction():
            result = data_manager.add_reaction(str(rekomen_id), reaction_type, delta=1)
            counts = {}
            if result and isinstance(result, dict):
                counts = result
            def update_ui():
                label = "Murah" if reaction_type == "murah" else "Enak"
                count = counts.get(reaction_type, 0)
                btn.setText(f"{'💰' if reaction_type == 'murah' else '👍'} {label} ({count})")
                QTimer.singleShot(2000, lambda: btn.setEnabled(True))
            QTimer.singleShot(0, update_ui)

        import threading
        t = threading.Thread(target=do_reaction, daemon=True)
        t.start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        super().keyPressEvent(event)

class RecommendationPage(QWidget):
    def __init__(self, t, toast=None, main=None):
        super().__init__()
        self.t = t
        self.toast = toast
        self.main = main
        self._card_w = 280
        self._build()

    def showEvent(self, event):
        super().showEvent(event)
        # Defer to next event loop iteration so viewport has its final size
        QTimer.singleShot(0, self._refresh_cards)

    def _build(self):
        self.setStyleSheet("background:#f0f0f0;")

        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background:#f0f0f0;")
        root.addWidget(header, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet("""
            QScrollArea { background: #f0f0f0; border: none; }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0,0,0,0.12);
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: rgba(0,0,0,0.25); }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)

        self.cards_widget = QWidget()
        self.cards_widget.setStyleSheet("background:#f0f0f0;")
        self.cards_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.cards_lay = QGridLayout(self.cards_widget)
        self.cards_lay.setContentsMargins(20, 20, 20, 20)
        self.cards_lay.setSpacing(12)
        self.cards_lay.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._scroll.setWidget(self.cards_widget)
        root.addWidget(self._scroll, 1, 0, 1, 1)

        self._btn_holder = QWidget(self._scroll.viewport())
        self._btn_holder.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        hb = QHBoxLayout(self._btn_holder)
        hb.setContentsMargins(0, 0, 0, 0)
        hb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.add_btn = QPushButton("+ Tambah Rekomendasi")
        self.add_btn.setFixedSize(220, 48)
        self.add_btn.setFont(QFont("Google Sans", 14, QFont.Weight.Bold))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #0FB291;
                color: white;
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.5);
                padding: 0 24px;
                font-family: "Google Sans", "Arial", sans-serif;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #0a8f75; }
        """)
        self.add_btn.clicked.connect(self._on_add)
        hb.addWidget(self.add_btn)
        self._btn_holder.setFixedSize(220, 48)

        self._scroll.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self._scroll.viewport() and event.type() == QEvent.Type.Resize:
            vp_w = self._scroll.viewport().width()
            vp_h = self._scroll.viewport().height()
            self._btn_holder.move(vp_w - 240, vp_h - 68)
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        avail_w = self._scroll.viewport().width()
        gap = 12
        margin = 20
        n_cols = max(1, (avail_w + gap - margin * 2) // (self._card_w + gap))
        new_card_w = (avail_w + gap - margin * 2 - n_cols * gap) // n_cols
        new_card_w = max(200, new_card_w)
        if abs(new_card_w - self._card_w) > 20:
            self._card_w = new_card_w
            self._refresh_cards()

    def _refresh_cards(self):
        while self.cards_lay.count():
            child = self.cards_lay.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        import json as _json
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rekomendasi.json")
        recs = []
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8-sig") as f:
                    recs = _json.load(f) or []
            except Exception:
                pass
        if not recs:
            from data_manager import get_demo_recommendations
            recs = get_demo_recommendations()

        if not recs:
            empty = QWidget()
            empty.setFixedSize(self.cards_widget.width(), 300)
            el = QVBoxLayout(empty)
            el.setContentsMargins(0, 0, 0, 0)
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl = QLabel("📍")
            icon_lbl.setFont(QFont("Google Sans", 48))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
            msg_lbl = QLabel("Belum ada rekomendasi")
            msg_lbl.setFont(QFont("Google Sans", 14))
            msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg_lbl.setStyleSheet("color:#9ca3af;background:transparent;")
            el.addWidget(icon_lbl)
            el.addWidget(msg_lbl)
            self.cards_lay.addWidget(empty, 0, 0)
            return

        avail_w = self._scroll.viewport().width()
        gap = 12
        margin = 20
        n_cols = max(1, (avail_w + gap - margin * 2) // (self._card_w + gap))

        col = 0
        row = 0
        for rec in recs:
            card = RecommendationCard(rec, self.t, card_w=self._card_w)
            card.detail_requested.connect(self._show_detail)
            self.cards_lay.addWidget(card, row, col)
            col += 1
            if col >= n_cols:
                col = 0
                row += 1

        # Set cards_widget height so scroll area knows total content height
        if recs:
            card_h = max(340, int(self._card_w * 1.15))
            rows = (len(recs) + n_cols - 1) // n_cols
            total_h = rows * (card_h + 12) + 40  # card_height + gap + margins
        else:
            total_h = 400
        self.cards_widget.setFixedHeight(total_h)

    def _show_detail(self, rec):
        from PyQt6.QtWidgets import QApplication
        dlg = RecommendationDetailDialog(rec, self.t, self)
        dlg.setModal(True)
        dlg.setFixedSize(460, 640)
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            dlg.move(
                sg.x() + (sg.width() - dlg.width()) // 2,
                sg.y() + (sg.height() - dlg.height()) // 2
            )
        dlg.show()

    def _on_add(self):
        from PyQt6.QtWidgets import QApplication
        dlg = RecommendationFormDialog(self.t, self)
        dlg.setModal(True)
        dlg.setFixedSize(440, 620)
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            dlg.move(
                sg.x() + (sg.width() - dlg.width()) // 2,
                sg.y() + (sg.height() - dlg.height()) // 2
            )
        dlg.accepted.connect(self._refresh_cards)
        dlg.show()

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet("background:#f0f0f0;")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #0FB291;
                color: white;
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.5);
                padding: 0 24px;
                font-family: "Google Sans", "Arial", sans-serif;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #0a8f75; }
        """)

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setStyleSheet("background: transparent;")
        spinner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "spinner.gif")
        if os.path.exists(spinner_path):
            self.movie = QMovie(spinner_path)
            self.movie.setScaledSize(QSize(64, 64))
            self.spinner_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.spinner_label.setText("⏳")
            self.spinner_label.setStyleSheet("background: transparent; font-size: 48px;")
        layout.addWidget(self.spinner_label)
        self.setFixedSize(80, 80)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

    def show_with_message(self, message="Mohon tunggu..."):
        print(f"[DEBUG] LoadingDialog.show_with_message() called: {message}")
        self.opacity_effect.setOpacity(0.0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()
        QApplication.processEvents()

    def hide_with_fade(self):
        print("[DEBUG] LoadingDialog.hide_with_fade() called")
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(200)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self._finish_close)
        self.fade_out.start()

    def _finish_close(self):
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
        self.accept()

    def closeEvent(self, event):
        if hasattr(self, 'movie') and self.movie:
            self.movie.stop()
        event.accept()

class Toast(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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

CARD_W, IMG_H = 220, 190  # 5 columns — wider cards

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
        self.img_lbl.setFont(QFont("Google Sans", 22))
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
            self.promo_overlay.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
            self.promo_overlay.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:6px 14px;min-width:80px;")
            self.promo_overlay.move(8, 8)
        
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(14, 12, 14, 14)
        il.setSpacing(6)
        
        self.cat_badge = QLabel(self.product["category"])
        self.cat_badge.setFont(QFont("Google Sans", 8, QFont.Weight.Bold))
        self.cat_badge.setStyleSheet(f"background:{self.t['badge_bg']};color:{self.t['badge_fg']};border-radius:4px;padding:2px 4px;")
        
        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        badge_row.addWidget(self.cat_badge)
        badge_row.addStretch()
        il.addLayout(badge_row)
        
        self.name_lbl = QLabel(self.product["name"])
        self.name_lbl.setObjectName("product_name")
        self.name_lbl.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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
                orig_font = QFont("Google Sans", 9)
                orig_font.setStrikeOut(True)
                orig_price.setFont(orig_font)
                orig_price.setStyleSheet(f"color:{self.t['text2']};")

                if diskon > 0:
                    diskon_lbl = QLabel(f"-{diskon:.0f}%")
                    diskon_lbl.setFont(QFont("Google Sans", 8, QFont.Weight.Bold))
                    diskon_lbl.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
                    orig_price_lay = QHBoxLayout()
                    orig_price_lay.addWidget(orig_price)
                    orig_price_lay.addWidget(diskon_lbl)
                    orig_price_lay.addStretch()
                    price_col.addLayout(orig_price_lay)
                else:
                    price_col.addWidget(orig_price)

                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
            else:
                self.product["is_promo"] = False
                self.price_lbl = QLabel(rp(harga_promo))
                self.price_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(self.price_lbl)
        else:
            self.product["is_promo"] = False
            self.product["effective_price"] = harga_promo
            self.price_lbl = QLabel(rp(harga_promo))
            self.price_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
            price_col.addWidget(self.price_lbl)
        
        il.addLayout(price_col)

        self.store_lbl = QLabel(f"🏪 {self.product.get('store_base', self.product['store'])}")
        self.store_lbl.setFont(QFont("Google Sans", 9))
        self.store_lbl.setStyleSheet(f"color:{self.t['store_fg']};")
        il.addWidget(self.store_lbl)

        self.add_btn = QPushButton(" Tambah")
        cart_icon_px = QPixmap(os.path.join(APP_BASE, "UI", "Home", "Assets", "Shopping cart.png"))
        if not cart_icon_px.isNull():
            from PyQt6.QtGui import QIcon
            self.add_btn.setIcon(QIcon(cart_icon_px.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)))
        self.add_btn.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
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
        ttl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
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
            badge.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
            badge.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:4px 10px;min-width:70px;")
            badge.move(8, 8)
            badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay.addWidget(img_lbl)

        pname = QLabel(self.product["name"])
        pname.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
        pname.setWordWrap(True)
        pname.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(pname)
        
        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        diskon = self.product.get("diskon_persen", 0)
        if diskon > 0:
            op = QLabel(rp(self.product.get("harga_normal", self.product["price"])))
            f = QFont("Google Sans", 10); f.setStrikeOut(True); op.setFont(f)
            op.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            pp = QLabel(rp(self.product["effective_price"]))
            pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(op)
            price_row.addWidget(pp)
            dk = QLabel(f"-{diskon:.0f}%")
            dk.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
            dk.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
            price_row.addWidget(dk)
        else:
            pp = QLabel(rp(self.product["price"]))
            pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(pp)
        price_row.addStretch()
        lay.addLayout(price_row)
        
        lbl_cabang = QLabel("Tersedia di:")
        lbl_cabang.setFont(QFont("Google Sans", 10))
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
            sn.setFont(QFont("Google Sans", 10, QFont.Weight.Bold))
            sn.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            sd = QLabel(f"📍 {b['distance']}")
            sd.setFont(QFont("Google Sans", 9))
            sd.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            bl.addWidget(sn); bl.addWidget(sd)
            c_lay.addWidget(bw)
            
        c_lay.addStretch()
        scroll.setWidget(c_wid)
        lay.addWidget(scroll)

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
        super().__init__(t["card_bg"], "#d0d0d0", 12, parent)
        self.product = product
        self.t = t
        self.setFixedSize(CARD_W, 400)
        print(f"[DEBUG] ProductListItem size: {CARD_W}x400")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._loaders = []

        # Promo badge — top-left corner
        self.promo_badge = QLabel(self)
        self.promo_badge.setStyleSheet("""
            QLabel {
                background: #e74c3c;
                color: white;
                font-size: 11px;
                font-weight: bold;
                border-radius: 4px;
                padding: 2px 8px;
                border: none;
            }
        """)
        self.promo_badge.hide()
        self.promo_badge.move(6, 6)
        self.promo_badge.raise_()

        # Show badge if product has discount
        diskon = self.product.get("diskon_persen", 0)
        if diskon and diskon > 0:
            self.promo_badge.setText(f"{int(diskon)}% OFF")
            self.promo_badge.show()

        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.img_cont = QWidget()
        self.img_cont.setFixedSize(CARD_W, IMG_H + 38)
        self.img_cont.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:10px 10px 0 0;")

        self.img_lbl = QLabel(self.img_cont)
        self.img_lbl.setGeometry(0, 0, CARD_W - 4, 200)
        self.img_lbl.setMinimumHeight(200)
        self.img_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setText("⏳")
        self.img_lbl.setFont(QFont("Google Sans", 22))
        self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
        self.img_lbl.setScaledContents(True)
        lay.addWidget(self.img_cont)

        jenis = self.product.get("jenis_harga", "")
        diskon = self.product.get("diskon_persen", 0)
        is_promo = (jenis == "PROMO")
        if is_promo:
            badge_text = "🔥 Promo"
            self.promo_overlay = QLabel(badge_text, self.img_cont)
            self.promo_overlay.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
            self.promo_overlay.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:6px 14px;min-width:80px;")
            self.promo_overlay.move(8, 8)
        
        info = QWidget()
        info.setStyleSheet("background:transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(14, 6, 14, 14)
        il.setSpacing(10)
        
        self.cat_badge = QLabel(self.product["category"])
        self.cat_badge.setFont(QFont("Google Sans", 8, QFont.Weight.Bold))
        self.cat_badge.setStyleSheet(f"background:{self.t['badge_bg']};color:{self.t['badge_fg']};border-radius:4px;padding:2px 4px;")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        badge_row.addWidget(self.cat_badge)
        badge_row.addStretch()
        il.addLayout(badge_row)
        
        product_name = self.product["name"]
        self.name_lbl = QLabel(product_name)
        self.name_lbl.setWordWrap(True)
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        fm = QFontMetrics(self.name_lbl.font())
        self.name_lbl.setMaximumHeight(fm.lineSpacing() * 2 + 4)
        self.name_lbl.setToolTip(product_name)
        self.name_lbl.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
        self.name_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;border:none;padding:0 4px;")
        il.addWidget(self.name_lbl)

        price_col = QVBoxLayout()
        price_col.setSpacing(6)
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
                orig_font = QFont("Google Sans", 9)
                orig_font.setStrikeOut(True)
                orig_price.setFont(orig_font)
                orig_price.setStyleSheet(f"color:{self.t['text2']};")

                if diskon > 0:
                    diskon_lbl = QLabel(f"-{diskon:.0f}%")
                    diskon_lbl.setFont(QFont("Google Sans", 8, QFont.Weight.Bold))
                    diskon_lbl.setStyleSheet(f"background:{self.t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
                    orig_price_lay = QHBoxLayout()
                    orig_price_lay.addWidget(orig_price)
                    orig_price_lay.addWidget(diskon_lbl)
                    orig_price_lay.addStretch()
                    price_col.addLayout(orig_price_lay)
                else:
                    price_col.addWidget(orig_price)

                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
            else:
                promo_price = QLabel(rp(effective_price))
                promo_price.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
                price_col.addWidget(promo_price)
        else:
            self.product["is_promo"] = False
            self.product["effective_price"] = harga_promo
            self.price_lbl = QLabel(rp(harga_promo))
            self.price_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
            price_col.addWidget(self.price_lbl)

        il.addLayout(price_col)

        self.add_btn = QPushButton("Lihat Detail")
        self.add_btn.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(30)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("QPushButton{background:transparent;color:#006550;border:1px solid #006550;border-radius:6px;}QPushButton:hover{background:rgba(15,178,145,0.15);color:#0FB291;}QPushButton:pressed{background:rgba(15,178,145,0.25);}")
        self.add_btn.clicked.connect(lambda: self._show_detail())
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
            scaled = px.scaled(
                self.img_lbl.width(),
                self.img_lbl.height(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.img_lbl.setPixmap(scaled)
            self.img_lbl.setText("")
        else:
            self.img_lbl.setText("🖼️")

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
        ttl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
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
            badge.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
            badge.setStyleSheet(f"background:{self.t['promo_badge_bg']};color:{self.t['promo_badge_fg']};border-radius:6px;padding:4px 10px;min-width:70px;")
            badge.move(8, 8)
            badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay.addWidget(img_lbl)

        pname = QLabel(self.product["name"])
        pname.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
        pname.setWordWrap(True)
        pname.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(pname)

        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        if diskon > 0:
            normal_price = self.product.get("harga_normal", self.product["price"])
            op = QLabel(rp(normal_price))
            op.setFont(QFont("Google Sans", 10))
            op.setStyleSheet(f"color:{self.t['text2']};text-decoration:line-through;")
            pp = QLabel(rp(self.product["effective_price"]))
            pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(op); price_row.addWidget(pp)
        else:
            pp = QLabel(rp(self.product["price"]))
            pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            pp.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
            price_row.addWidget(pp)
        price_row.addStretch()
        lay.addLayout(price_row)

        # B2 — Kategori badge
        kategori = self.product.get("kategori", "")
        if kategori:
            kat_lbl = QLabel(f"📂 {kategori}")
            kat_lbl.setFont(QFont("Google Sans", 10))
            kat_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            lay.addWidget(kat_lbl)

        promo_start = self.product.get("promo_start_date", "")
        promo_end = self.product.get("promo_end_date", "") or self.product.get("periode_promo", "")
        if promo_end:
            if promo_start:
                period_lbl = QLabel(f"📅 {promo_start} — tenggat promo sampai: {promo_end}")
            else:
                period_lbl = QLabel(f"📅 tenggat promo sampai: {promo_end}")
            period_lbl.setFont(QFont("Google Sans", 9))
            period_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            lay.addWidget(period_lbl)

        area_ex = self.product.get("area_exclusions", "")
        if area_ex:
            excl_lbl = QLabel(f"🚫 Tidak berlaku di: {area_ex}")
            excl_lbl.setFont(QFont("Google Sans", 9))
            excl_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            excl_lbl.setWordWrap(True)
            lay.addWidget(excl_lbl)

        # B4 — Syarat Promo
        syarat = self.product.get("promo_requirements", "")
        if syarat:
            syarat_lbl = QLabel(f"📋 {syarat}")
            syarat_lbl.setFont(QFont("Google Sans", 9))
            syarat_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            syarat_lbl.setWordWrap(True)
            lay.addWidget(syarat_lbl)

        # Regional price display
        regional_price = self.product.get("regional_price")
        multi_region_price = self.product.get("multi_region_price")
        if regional_price or multi_region_price:
            sep = QLabel("")
            sep.setFixedHeight(4)
            lay.addWidget(sep)
            lbl_regional = QLabel("🌏 Harga Regional")
            lbl_regional.setFont(QFont("Google Sans", 10, QFont.Weight.Bold))
            lbl_regional.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
            lay.addWidget(lbl_regional)
        if regional_price:
            rp_lbl = QLabel(f"Luar Jawa: Rp {regional_price:,}")
            rp_lbl.setFont(QFont("Google Sans", 9))
            rp_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            lay.addWidget(rp_lbl)
        if multi_region_price:
            mr_lbl = QLabel(f"Luar Jawa, Bali, Lombok: Rp {multi_region_price:,}")
            mr_lbl.setFont(QFont("Google Sans", 9))
            mr_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            lay.addWidget(mr_lbl)

        lbl_cabang = QLabel("🏪 Toko & Cabang:")
        lbl_cabang.setFont(QFont("Google Sans", 10, QFont.Weight.Bold))
        lbl_cabang.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(lbl_cabang)

        branches = self.product.get("branches", [{"store": self.product.get("store", ""), "area": self.product.get("area", ""), "distance": ""}])
        store_labels = QWidget()
        store_labels.setStyleSheet("background:transparent;")
        sl_lay = QVBoxLayout(store_labels)
        sl_lay.setContentsMargins(0, 0, 0, 0)
        sl_lay.setSpacing(5)
        for b in branches:
            store_name = b.get("store", "")
            area = b.get("area", "")
            # Split brand from full name
            brand = store_name.split()[0] if store_name else ""
            lbl = QLabel(f"• {store_name} — {area}")
            lbl.setFont(QFont("Google Sans", 9))
            lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            sl_lay.addWidget(lbl)
        sl_lay.addStretch()
        lay.addWidget(store_labels)

        def onDlgClose():
            overlay.hide()
        dlg.finished.connect(onDlgClose)
        dlg.exec()
        overlay.hide()

    def update_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['card_bg']};border:1px solid #d0d0d0;border-radius:12px;")
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
        back.setFont(QFont("Google Sans", 11))
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
        title.setFont(QFont("Google Sans", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        self.card_lay.addWidget(title)
        if not self.app.cart_items:
            e = QLabel("🛒\n\nKeranjang kamu masih kosong\nMulai tambahkan produk dari halaman utama")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            e.setFont(QFont("Google Sans", 13))
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
        bl2.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
        bl2.setStyleSheet(f"color:{t['text1']};background:transparent;")
        br.addWidget(bl2)
        br.addStretch()
        bv = QLabel(rp(self.budget))
        bv.setFont(QFont("Google Sans", 14, QFont.Weight.Bold))
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
        pl.setFont(QFont("Google Sans", 10))
        pl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pl.setStyleSheet(f"color:{t['text2']};background:transparent;")
        bl.addWidget(pl)
        self.card_lay.addWidget(bb)
        
        # total
        tb = Card(t["total_bg"], t["total_bg"], 16)
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(18, 12, 18, 12)
        tl1 = QLabel("Total")
        tl1.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
        tl1.setStyleSheet(f"color:{t['text1']};background:transparent;")
        tv = QLabel(rp(total))
        tv.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
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
        rl1.setFont(QFont("Google Sans", 12))
        rl1.setStyleSheet(f"color:{t['text1']};background:transparent;")
        rv = QLabel(rp(remaining))
        rv.setFont(QFont("Google Sans", 22, QFont.Weight.Bold))
        rv.setStyleSheet(f"color:{t['over_fg'] if over else t['remain_fg']};background:transparent;")
        rl.addWidget(rl1)
        rl.addWidget(rv)
        if over:
            w = QLabel("⚠️ Anggaran tidak cukup! Kurangi beberapa item.")
            w.setFont(QFont("Google Sans", 10))
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
        ic.setFont(QFont("Google Sans", 22))
        ic.setFixedSize(48, 48)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:12px;")
        rl.addWidget(ic)
        inf = QVBoxLayout()
        inf.setSpacing(3)
        n = QLabel(p["name"])
        n.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
        n.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        s = QLabel(p["store"])
        s.setFont(QFont("Google Sans", 10))
        s.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        inf.addWidget(n)
        inf.addWidget(s)
        rl.addLayout(inf)
        rl.addStretch()
        prc = QVBoxLayout()
        prc.setAlignment(Qt.AlignmentFlag.AlignRight)
        tv = QLabel(rp(p.get("effective_price", p.get("price", 0)) * q))
        tv.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
        tv.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        tv.setAlignment(Qt.AlignmentFlag.AlignRight)
        dv = QLabel(f"{q} x {rp(p.get('effective_price', p.get('price', 0)))}")
        dv.setFont(QFont("Google Sans", 9))
        dv.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        dv.setAlignment(Qt.AlignmentFlag.AlignRight)
        prc.addWidget(tv)
        prc.addWidget(dv)
        rl.addLayout(prc)
        db = QPushButton("🗑️")
        db.setFixedSize(34, 34)
        db.setFont(QFont("Google Sans", 14))
        db.setCursor(Qt.CursorShape.PointingHandCursor)
        db.setStyleSheet("QPushButton{background:transparent;border:none;}QPushButton:hover{background:rgba(220,50,50,0.12);border-radius:8px;}")
        db.clicked.connect(lambda _, pid=p["id"]: self._remove(pid))
        rl.addWidget(db)
        return row

    def _remove(self, pid):
        self.app.cart_items = [ci for ci in self.app.cart_items if ci["product"].get("id", "") != pid]
        self.app._save_cart()
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
        inp.setFont(QFont("Google Sans", 14))
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
        p.setFont(QFont("Google Sans", 9))
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
            p.drawText(0, y + 4, pad_l - 6, 12, Qt.AlignmentFlag.AlignRight, f"{int(yv):,}")
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
            fm = QFontMetrics(QFont("Google Sans", 8))
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
        # Filter small slices into "Lainnya" to avoid label overlap
        total_val = sum(v for _, v in self.data)
        threshold_pct = 5
        small_items = [(l, v) for l, v in self.data if total_val > 0 and v / total_val * 100 < threshold_pct]
        filtered_data = [(l, v) for l, v in self.data if total_val > 0 and v / total_val * 100 >= threshold_pct]
        if small_items:
            other_sum = sum(v for _, v in small_items)
            filtered_data.append(("Lainnya", other_sum))
        # Build slices from filtered_data
        start = 0; slices = []
        for i, (label, val) in enumerate(filtered_data):
            span = int(val / total * 5760) if total else 0
            slices.append((label, val, start, span, colors[i % len(colors)]))
            start += span
        # Draw slices
        for label, val, s, sp, col in slices:
            p.setBrush(QBrush(col))
            p.setPen(QPen(QColor(self.t["stat_card_bg"]), 2))
            p.drawPie(cx - r, cy - r, r * 2, r * 2, s, sp)
            # Draw count label on top of slice
            angle = math.radians(-(s + sp // 2) / 16)
            lx = cx + int(r * 0.65 * math.cos(angle))
            ly = cy + int(r * 0.65 * math.sin(angle))
            p.setPen(QColor(self.t["stat_card_bg"]))
            p.setFont(QFont("Google Sans", 8, QFont.Weight.Bold))
            fm_count = QFontMetrics(p.font())
            val_text = str(val)
            p.drawText(lx - fm_count.horizontalAdvance(val_text)//2, ly + fm_count.height()//3, val_text)
        # Draw legend on the right side (no overlapping labels)
        legend_x = W - 155
        legend_y = cy - len(slices) * 10
        p.setFont(QFont("Google Sans", 9))
        for i, (label, val, s, sp, col) in enumerate(slices):
            ly_pos = legend_y + i * 20
            p.setPen(col)
            pct = int(val / total * 100) if total else 0
            legend_text = f"{label} ({pct}%)"
            fm_leg = QFontMetrics(p.font())
            leg_elided = fm_leg.elidedText(legend_text, Qt.TextElideMode.ElideRight, 140)
            p.drawText(legend_x, ly_pos + 11, 140, 14, Qt.AlignmentFlag.AlignLeft, leg_elided)
    def apply_theme(self, t):
        self.t = t; self.update()

class StatistikPage(QWidget):
    def __init__(self, t, app=None):
        super().__init__()
        self.t = t
        self.app = app
        # Load real promo data
        raw_data = data_manager.read_local_data()
        # Filter to PROMO items only (jenis_harga == "PROMO")
        self.promo_products = [p for p in raw_data if p.get("jenis_harga") == "PROMO"]
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
        ttl.setFont(QFont("Google Sans", 24, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        
        # Last updated label synced with app
        if self.app:
            months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            m_idx = self.app.last_sync.month - 1
            formatted_date = f"{self.app.last_sync.day} {months[m_idx]} {self.app.last_sync.year}"
            self.sub = QLabel(f"Terakhir diperbarui: {formatted_date}")
        else:
            self.sub = QLabel("Terakhir diperbarui: -")
        self.sub.setFont(QFont("Google Sans", 12))
        self.sub.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
        lay.addWidget(ttl); lay.addWidget(self.sub)
        
        # bar chart card
        store_count = {}
        for p in self.promo_products:
            store = p.get("nama_cabang") or p.get("brand_toko") or "Unknown"
            store_count[store] = store_count.get(store, 0) + 1
        top3 = sorted(store_count.items(), key=lambda x: -x[1])[:3]
        self.bar_chart = BarChart(top3, self.t)
        bc = self._make_chart_card("Top 3 Toko dengan Promo Terbanyak", self.bar_chart)
        lay.addWidget(bc)
        
        # pie chart card
        cat_count = {}
        for p in self.promo_products:
            cat = p.get("kategori") or "Lainnya"
            cat_count[cat] = cat_count.get(cat, 0) + 1
        pie_data = list(cat_count.items())
        self.pie_chart = PieChart(pie_data, self.t)
        pc = self._make_chart_card("Distribusi Kategori Produk Promo", self.pie_chart)
        lay.addWidget(pc)
        
        # summary cards
        total_promo = len(self.promo_products)
        total_stores = len(set(p.get("nama_cabang") or p.get("brand_toko") for p in self.promo_products))
        total_cats = len(set(p.get("kategori") for p in self.promo_products if p.get("kategori")))
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
            nl.setFont(QFont("Google Sans", 38, QFont.Weight.Bold))
            nl.setStyleSheet(f"color:{color};background:transparent;")
            nl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ll = QLabel(label)
            ll.setFont(QFont("Google Sans", 12))
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
        tl.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
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
#         hdr.setFont(QFont("Google Sans", 16, QFont.Weight.Bold))
#         hdr.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
#         lay.addWidget(hdr)
#         
#         c1 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
#         cl1 = QVBoxLayout(c1)
#         l1 = QLabel("Sinkronisasi Data")
#         l1.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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
#         l2.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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
#         l3.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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
        ttl.setFont(QFont("Google Sans", 24, QFont.Weight.Bold))
        ttl.setStyleSheet(f"color:{t['text1']};background:transparent;")
        sub = QLabel("Kelola preferensi dan akses admin")
        sub.setFont(QFont("Google Sans", 12))
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
        ali.setFont(QFont("Google Sans", 18))
        ali.setStyleSheet("background:transparent;")
        aht = QLabel("Mode Admin")
        aht.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
        aht.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        ah.addWidget(ali); ah.addWidget(aht); ah.addStretch(); al.addLayout(ah)
        if not self.is_admin:
            login_btn = QPushButton("Login sebagai Admin")
            login_btn.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
            login_btn.setFixedSize(200, 44)
            login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            login_btn.setStyleSheet(f"QPushButton{{background:{t['price_fg']};color:white;border:none;border-radius:14px;}}QPushButton:hover{{background:{t['banner_from']};}}")
            login_btn.clicked.connect(self._show_login)
            al.addWidget(login_btn)
        else:
            status = QLabel("✅ Login sebagai Admin")
            status.setFont(QFont("Google Sans", 12))
            status.setStyleSheet(f"color:#22c55e;background:transparent;")
            logout = QPushButton("Logout")
            logout.setFont(QFont("Google Sans", 11))
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
        rhi.setFont(QFont("Google Sans", 18))
        rhi.setStyleSheet("background:transparent;")
        rht = QLabel("Sinkronisasi Data")
        rht.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
        rht.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
        rh.addWidget(rhi); rh.addWidget(rht); rh.addStretch(); rl.addLayout(rh)
        refresh_btn = QPushButton("↻ Perbarui Data Promo")
        refresh_btn.setFixedHeight(44)
        refresh_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Bold))
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
        fhi.setFont(QFont("Google Sans", 18))
        fhi.setStyleSheet("background:transparent;")
        fht = QLabel("Ukuran Font Aplikasi")
        fht.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
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
        sl_lay.addWidget(QLabel("A", font=QFont("Google Sans", 8)))
        sl_lay.addWidget(self.font_slider)
        sl_lay.addWidget(QLabel("A", font=QFont("Google Sans", 16)))
        fl.addLayout(sl_lay)
        
        self.font_lbl = QLabel(f"Terpilih: {self.font_size}")
        self.font_lbl.setFont(QFont("Google Sans", 10))
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
        abi.setFont(QFont("Google Sans", 18))
        abi.setStyleSheet("background:transparent;")
        abt = QLabel("Tentang Aplikasi")
        abt.setFont(QFont("Google Sans", 15, QFont.Weight.Bold))
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
            lbl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color:{t['text1']};background:transparent;")
            vl = QLabel(val)
            vl.setFont(QFont("Google Sans", 11))
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
            admin_user = os.environ.get("RADAR_ADMIN_USER", "")
            admin_pass = os.environ.get("RADAR_ADMIN_PASSWORD", "")
            if user.text() == admin_user and pwd.text() == admin_pass:
                self.is_admin = True
                self._populate()
                QMessageBox.information(self, "Berhasil", "Login berhasil! Membuka Dashboard Admin...")
                import admin_tool
                admin_tool.run_dashboard()
            else:
                QMessageBox.warning(self, "Login Gagal", "Username atau password salah!")

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


# ────────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────────
# HOMEPAGE — Clean layout with proper title/subtitle spacing
# ────────────────────────────────────────────────────────────────────
class HomePage(QWidget):
    """
    New HomePage with clean structure:
    - HTML QLabel title/subtitle (proven spacing)
    - Pill search bar
    - Category pills row
    - Supermarket cards (horizontal scroll)
    - Product grid (ProductListItem widgets)
    - Load More button
    """

    def __init__(self, main, t):
        super().__init__()
        self.setObjectName("HomePage")
        self.setStyleSheet("QWidget#HomePage { background: #ffffff; }")
        self.main = main
        self.t = t
        self._all_prods = []
        self._visible_count = 0
        self._page_size = 50
        self._cat_btns = {}
        self.user_lat = None
        self.user_lon = None
        self._location_acquired = False
        self._store_dist_labels = []
        self._prod_list = None   # QListWidget (lazy) — deprecated, use product_grid
        self.product_grid = None
        self._load_more_btn = None
        self._search_thread = None
        self._search_worker = None
        self._setup_ui()

    # ── Data ─────────────────────────────────────────────────────────

    def _get_products(self):
        raw_records = data_manager.read_local_data() if data_manager else []
        if raw_records:
            raw_records = data_manager.enrich_data(raw_records)
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
                "periode_promo": r.get("promo_end_date", "") or r.get("periode_promo", ""),
                "promo_requirements": r.get("promo_requirements", ""),
                "kategori": r.get("kategori", ""),
                "promo_type": r.get("promo_type", ""),
                "area_tags": r.get("area_tags", []),
            })
        records = engine.normalize_promo_data(records)
        selected_cat = getattr(self.main, "selected_cat", "Semua")
        search_q = getattr(self.main, "search_q", "") or ""
        filter_promo = getattr(self.main, "_filter_promo", False)
        reverse = None if getattr(self.main, "sort_opt", "default") == "default" else getattr(self.main, "sort_opt", "") == "termahal"
        jenis_harga = "PROMO" if selected_cat == "Promo" else None
        filtered, _ = engine.run_pipeline(
            records,
            area=None,
            category=selected_cat if selected_cat not in ("Semua", "Promo") else None,
            brand=None,
            jenis_harga=jenis_harga,
            keyword=search_q.strip() or None,
            reverse=reverse,
        )
        if filter_promo:
            filtered = engine.filter_promo_items(filtered)
        grouped = {}
        for p in filtered:
            norm_name = engine.normalize_product_name(p["name"])
            key = norm_name
            if key not in grouped:
                np = p.copy()
                np["normalized_name"] = norm_name
                np["stores"] = {}  # brand → [(nama_cabang, area), ...]
                np["branches"] = [{"store": p["store"], "area": p.get("area", ""), "distance": p.get("distance", "")}]
                np["min_price"] = p["price"]
                np["store_base"] = p["store"].split()[0]
                np["is_promo"] = p.get("jenis_harga") == "PROMO"
                first_brand = p["store"].split()[0]
                np["stores"][first_brand] = [(p["store"], p.get("area", ""))]
                grouped[key] = np
            else:
                grouped[key]["branches"].append({"store": p["store"], "area": p.get("area", ""), "distance": p.get("distance", "")})
                brand = p["store"].split()[0]
                grouped[key]["stores"].setdefault(brand, []).append((p["store"], p.get("area", "")))
                if p["price"] < grouped[key]["min_price"]:
                    grouped[key]["min_price"] = p["price"]
        return list(grouped.values())

    def refresh(self):
        self._all_prods = self._get_products()
        self._visible_count = min(self._page_size, len(self._all_prods))
        self._render_products()

    # ── Render ──────────────────────────────────────────────────────

    def _debug_print_geometry(self):
        print("\n=== PRODUCT GRID GEOMETRY DEBUG ===")
        print(f"Grid horizontalSpacing: {self.product_grid.horizontalSpacing()}")
        print(f"Grid verticalSpacing: {self.product_grid.verticalSpacing()}")
        print(f"Grid spacing: {self.product_grid.spacing()}")
        print(f"Grid contentsMargins: {self.product_grid.contentsMargins()}")
        print(f"Grid geometry: {self.product_grid.geometry()}")
        print(f"Grid parent size: {self.product_grid.parent().size()}")
        print(f"product_container size: {self.product_container.size()}, minimumSize: {self.product_container.minimumSize()}")
        for col in range(5):
            print(f"  Column {col} stretch: {self.product_grid.columnStretch(col)}")
        count = self.product_grid.count()
        print(f"Total items in grid: {count}")
        if count > 0:
            item = self.product_grid.itemAt(0)
            if item and item.widget():
                w = item.widget()
                print(f"First card size: {w.size()}, minimumSize: {w.minimumSize()}")
                print(f"First card sizePolicy H/V: {w.sizePolicy().horizontalPolicy()} / {w.sizePolicy().verticalPolicy()}")
        print("====================================\n")

    def _render_products(self):
        print(f"[DEBUG] _render_products ENTERED, current H={self.product_grid.horizontalSpacing()}, V={self.product_grid.verticalSpacing()}")
        if self.product_grid is None:
            return
        # Clear existing widgets from grid
        for i in reversed(range(self.product_grid.count())):
            widget = self.product_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        print(f"[DEBUG] Horizontal spacing: {self.product_grid.horizontalSpacing()}")
        print(f"[DEBUG] Vertical spacing: {self.product_grid.verticalSpacing()}")
        print(f"[DEBUG] Grid contentsMargins: {self.product_grid.contentsMargins()}")
        print(f"[DEBUG] Products to render: {len(self._all_prods[:self._visible_count])}")
        print(f"[DEBUG] product_grid count: {self.product_grid.count()}")

        cols = 5  # fixed 5 columns

        # Add product cards to grid
        prods = self._all_prods[:self._visible_count]
        for idx, prod in enumerate(prods):
            row = idx // cols
            col = idx % cols
            card = ProductListItem(prod, self.t)
            card.add_clicked.connect(lambda: None)
            self.product_grid.addWidget(card, row, col)

        total = len(self._all_prods)
        if self._load_more_btn:
            if self._visible_count < total:
                remaining = total - self._visible_count
                self._load_more_btn.setText(f"Muat Lebih Banyak ({remaining} tersisa)")
                self._load_more_btn.show()
            else:
                self._load_more_btn.hide()

        self._debug_print_geometry()

    def _request_location(self):
        """Trigger browser geolocation via hidden WebView."""
        if getattr(self, '_geo_requested', False):
            return
        self._geo_requested = True
        self._get_windows_location()

    def _get_windows_location(self):
        """Get user location via Windows native API (PowerShell/WinRT)."""
        import subprocess
        ps_script = r'''
Add-Type -AssemblyName System.Device
$w = New-Object System.Device.Location.GeoCoordinateWatcher
$started = $w.TryStart($false, [System.TimeSpan]::FromSeconds(30))
if (-not $started) {
    Write-Output "ERR|GeoCoordinateWatcher failed to start"
    exit
}
$maxWait = 30
$waited = 0
while ($w.Status -eq 'NoData' -and $waited -lt $maxWait) {
    Start-Sleep -Milliseconds 500
    $waited += 0.5
}
if ($w.Status -ne 'Ready') {
    Write-Output "ERR|Location status: $($w.Status) (waited $waited seconds)"
} else {
    $pos = $w.Position
    if ($null -ne $pos.Location -and $pos.Location.Latitude -ne [double]::NaN) {
        Write-Output "OK|$($pos.Location.Latitude)|$($pos.Location.Longitude)"
    } else {
        Write-Output "ERR|Position available but Lat/Lon is null/NaN"
    }
}
'''
        try:
            result = subprocess.run(
                ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
                capture_output=True, text=True, timeout=45
            )
            output = result.stdout.strip()
            if output.startswith('OK|'):
                parts = output.split('|')
                lat, lon = float(parts[1]), float(parts[2])
                print(f"[DEBUG] Windows location: {lat}, {lon}")
                self._on_location_ready(lat, lon)
            else:
                msg = output.split('|', 1)[1] if '|' in output else 'Unknown error'
                print(f"[DEBUG] Windows location error: {msg}")
                self._on_location_error(msg)
        except subprocess.TimeoutExpired:
            print("[DEBUG] Windows location timeout")
            self._on_location_error("Location request timed out")
        except Exception as e:
            print(f"[DEBUG] Windows location exception: {e}")
            self._on_location_error(str(e))

    def _geo_load_finished(self, ok):
        if not ok:
            print("[DEBUG] GeoPage load failed")
        else:
            print("[DEBUG] GeoPage load finished")

    def _on_location_ready(self, lat, lon):
        print(f"[DEBUG] Location acquired: {lat}, {lon}")
        self.user_lat = lat
        self.user_lon = lon
        self._location_acquired = True
        self.main.user_lat = lat
        self.main.user_lon = lon
        self.main._location_acquired = True
        self.loc_btn.setText("📍 Lokasi Aktif")
        self.loc_btn.setEnabled(False)
        self._refresh_store_distances()

    def _on_location_error(self, msg):
        print(f"[DEBUG] Location error: {msg}")
        short_msg = msg[:30] + "..." if len(msg) > 30 else msg
        self.loc_btn.setText(f"📍 Gagal: {short_msg}")
        self._geo_requested = False

    def _load_more(self):
        self._visible_count += self._page_size
        self._render_products()

    # ── Category & Search ─────────────────────────────────────────────

    def _on_cat_selected(self, cat):
        self.main.selected_cat = cat
        if cat == "Promo":
            self.main._filter_promo = True
            self.main.promo_toggle.set_active(True) if hasattr(self.main, "promo_toggle") else None
            self.main.selected_cat = "Semua"
        else:
            if hasattr(self.main, "_filter_promo"):
                self.main._filter_promo = False
            if hasattr(self.main, "promo_toggle"):
                self.main.promo_toggle.set_active(False)
        for c, btn in self._cat_btns.items():
            btn.set_active(c == cat)
        self.refresh()

    def _on_search_text_changed(self, text):
        self.main.search_q = text
        if self._search_thread and self._search_thread.isRunning():
            if self._search_worker:
                self._search_worker.requestInterruption()
            self._search_thread.quit()
            self._search_thread.wait(3000)
        self._search_worker = SearchWorker(text, getattr(self.main, "selected_cat", "Semua"), parent=self)
        self._search_worker.finishedSignal.connect(self._on_search_done)
        self._search_thread = self._search_worker
        self._search_thread.start()

    def _on_search_done(self, results):
        self._all_prods = results if results else []
        self._visible_count = min(self._page_size, len(self._all_prods))
        self._render_products()

    def _refresh_store_distances(self):
        """Update all store card distance labels with Haversine from user location."""
        if self.user_lat is None or self.user_lon is None:
            return

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        store_branches = []
        for brand_key, brand_data in data_manager.ADDRESS_BOOK.items():
            for branch in brand_data.get("branches", []):
                branch_lat = branch.get('latitude')
                branch_lon = branch.get('longitude')
                if branch_lat is not None and branch_lon is not None:
                    dist = haversine(self.user_lat, self.user_lon, branch_lat, branch_lon)
                else:
                    dist = float('inf')
                store_branches.append((dist, branch))

        store_branches.sort(key=lambda x: x[0])

        for i, (dist_km, branch) in enumerate(store_branches):
            if i < len(self._store_dist_labels):
                dist_text = f"{dist_km:.1f} km" if dist_km != float('inf') else "- km"
                self._store_dist_labels[i].setText(dist_text)

    # ── UI Setup ─────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
    QScrollArea {
        background: #ffffff;
        border: none;
    }
    QScrollArea > QWidget {
        background: #ffffff;
    }
    QScrollBar:vertical {
        width: 8px;
        background: transparent;
        border: none;
        margin: 0px 2px;
    }
    QScrollBar::handle:vertical {
        background: rgba(0, 0, 0, 0.12);
        border-radius: 4px;
        min-height: 40px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(0, 0, 0, 0.25);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
""")
        swidget = QWidget()
        sLay = QVBoxLayout(swidget)
        sLay.setContentsMargins(0, 0, 0, 0)
        sLay.setSpacing(0)

        # ── Top spacer ──────────────────────────────────────────────
        top_sp = QWidget()
        top_sp.setFixedHeight(16)
        top_sp.setStyleSheet(f"background:{self.t['bg']};")
        sLay.addWidget(top_sp)

        # ── Search Bar ──────────────────────────────────────────────
        search_wrap = QWidget()
        search_wrap.setStyleSheet(f"background:{self.t['bg']};")
        sLay_search = QHBoxLayout(search_wrap)
        sLay_search.setContentsMargins(20, 0, 20, 12)
        sLay_search.setSpacing(0)

        search_bar = QWidget()
        search_bar.setFixedHeight(52)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 40))
        search_bar.setGraphicsEffect(shadow)
        search_bar.setStyleSheet("QWidget{background:white;border-radius:26px;}")
        sl = QHBoxLayout(search_bar)
        sl.setContentsMargins(20, 0, 20, 0)
        sl.setSpacing(10)

        search_icon = QSvgWidget(os.path.join(APP_BASE, "assets", "search.svg"))
        search_icon.setFixedSize(20, 20)
        sl.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari produk, supermarket, atau lokasi...")
        self.search_input.setFont(QFont("Google Sans", 12))
        self.search_input.setStyleSheet(
            f"QLineEdit{{background:transparent;border:none;color:{self.t['search_fg']};}}"
            f"QLineEdit::placeholder{{color:#888888;}}"
        )
        self.search_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        sl.addWidget(self.search_input)
        sLay_search.addWidget(search_bar)
        sLay.addWidget(search_wrap)

        # ── Category Pills ───────────────────────────────────────────
        cat_row = QWidget()
        cat_row.setFixedHeight(52)
        cat_row.setStyleSheet(f"background:{self.t['bg']};")
        cl = QHBoxLayout(cat_row)
        cl.setContentsMargins(20, 0, 20, 0)
        cl.setSpacing(8)

        cats = [
            ("Semua", "Semua"),
            ("🍚 Sembako", "Sembako"),
            ("🍜 Makanan Instan", "Makanan Instan"),
            ("🍿 Snack", "Snack"),
            ("🥤 Minuman", "Minuman"),
            ("🧼 Kebersihan", "Mandi"),
            ("💊 Kesehatan", "Kesehatan"),
            ("📦 Lainnya", "Lainnya"),
        ]
        self._cat_btns = {}
        for disp, cat in cats:
            btn = PillBtn(disp, cat == "Semua", self.t)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda _, c=cat: self._on_cat_selected(c))
            self._cat_btns[cat] = btn
            cl.addWidget(btn)
        cl.addStretch()

        filter_btn = QPushButton()
        filter_btn.setFlat(True)
        filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_btn.setFixedSize(40, 40)
        filter_btn.setIcon(_svg_to_icon(os.path.join(APP_BASE, "assets", "filter.svg"), 20))
        filter_btn.setIconSize(QSize(20, 20))
        filter_btn.setStyleSheet(
            f"QPushButton{{background:#fff;color:#333;border:1px solid #e0e0e0;border-radius:20px;}}"
            f"QPushButton:hover{{background:#f0f0f0;}}"
        )
        filter_btn.clicked.connect(self.main._show_filter_dialog)
        cl.addWidget(filter_btn)
        sLay.addWidget(cat_row)

        # ── Spacer ──────────────────────────────────────────────────
        sp = QWidget()
        sp.setFixedHeight(6)
        sp.setStyleSheet(f"background:{self.t['bg']};")
        sLay.addWidget(sp)

        # ── Title + Subtitle (HTML — proven spacing) ─────────────────
        title_wrap = QWidget()
        title_wrap.setStyleSheet(f"background:{self.t['bg']};")
        tl = QVBoxLayout(title_wrap)
        tl.setContentsMargins(20, 0, 20, 0)
        tl.setSpacing(2)

        title_html = QLabel("""
            <div style="font-size: 18px; font-weight: bold; color: #000000; line-height: 1.3;">
                Daftar Supermarket Terdekat
            </div>
            <div style="font-size: 13px; color: #000000; line-height: 1.2; margin-top: 0px;">
                Diurutkan dari yang terdekat dari lokasimu
            </div>
        """)
        title_html.setStyleSheet("background:transparent;")
        tl.addWidget(title_html)
        sLay.addWidget(title_wrap)

        title_sp = QWidget()
        title_sp.setFixedHeight(16)
        title_sp.setStyleSheet(f"background:{self.t['bg']};")
        sLay.addWidget(title_sp)

        # ── Location Button ──────────────────────────────────────────────
        loc_btn_wrap = QWidget()
        loc_btn_wrap.setStyleSheet(f"background:{self.t['bg']};")
        loc_btn_lay = QHBoxLayout(loc_btn_wrap)
        loc_btn_lay.setContentsMargins(20, 6, 20, 6)
        loc_btn_lay.setSpacing(0)

        self.loc_btn = QPushButton("📍 Aktifkan Lokasi")
        self.loc_btn.setFixedHeight(38)
        self.loc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.loc_btn.setStyleSheet("""
            QPushButton {
                background: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 19px;
                font-family: "Google Sans", "Arial", sans-serif;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
            QPushButton:disabled {
                background: #f5f5f5;
                color: #aaaaaa;
            }
        """)
        self.loc_btn.clicked.connect(self._request_location)
        loc_btn_lay.addWidget(self.loc_btn)
        loc_btn_lay.addStretch()
        sLay.addWidget(loc_btn_wrap)

        # ── Geolocation WebView (hidden) ─────────────────────────────────
        from PyQt6.QtWebEngineCore import QWebEnginePage
        from PyQt6.QtCore import QUrl
        class GeoPage(QWebEnginePage):
            def acceptNavigationRequest(self, url, nav_type, is_main_frame):
                if is_main_frame and url.scheme() == "geo":
                    try:
                        path = url.path()
                        if path.startswith("/ok,"):
                            parts = path.split(",")
                            lat, lon = float(parts[1]), float(parts[2])
                            self.view().page()._geo_bridge.receiveUserLocation(lat, lon)
                        else:
                            msg = path.split(",", 1)[1] if "," in path else "Unknown error"
                            self.view().page()._geo_bridge.receiveLocationError(msg)
                    except Exception as e:
                        print(f"[DEBUG] GeoPage navigation parse error: {e}")
                    return False
                return super().acceptNavigationRequest(url, nav_type, is_main_frame)

        self._geo_view = QWebEngineView()
        self._geo_view.setPage(GeoPage(self._geo_view))
        self._geo_view.setFixedSize(0, 0)
        self._geo_view.setHidden(True)

        # QWebChannel setup — same pattern as LokasiPage map
        channel = QWebChannel(self._geo_view.page())
        self._geo_view.page().setWebChannel(channel)
        self._geo_bridge = JSBridge(self, None, self.t)
        channel.registerObject("pyBridge", self._geo_bridge)

        # Connect GeoPage bridge signals to HomePage handlers
        self._geo_bridge.location_ready.connect(self._on_location_ready)
        self._geo_bridge.location_error.connect(self._on_location_error)
        self._geo_view.loadFinished.connect(self._geo_load_finished)

        # Load qwebchannel.js library
        qwebchannel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "qwebchannel.js")
        with open(qwebchannel_path, "r", encoding="utf-8") as f:
            qwebchannel_js = f.read()
        self._geo_view.page().runJavaScript(qwebchannel_js)

        # ── Store Cards (horizontal strip — horizontal scroll only) ─────
        store_scroll = QScrollArea()
        store_scroll.setWidgetResizable(False)
        store_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        store_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        store_scroll.setFixedHeight(220)
        store_scroll.setStyleSheet("""
    QScrollArea {
        background: #ffffff;
        border: none;
    }
    QScrollArea > QWidget {
        background: #ffffff;
    }
    QScrollBar:horizontal {
        height: 6px;
        background: transparent;
        border: none;
        margin: 0px 2px;
    }
    QScrollBar::handle:horizontal {
        background: rgba(0, 0, 0, 0.12);
        border-radius: 3px;
        min-width: 30px;
    }
    QScrollBar::handle:horizontal:hover {
        background: rgba(0, 0, 0, 0.25);
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
        background: none;
    }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
    }
""")

        sc_widget = QWidget()
        sc_widget.setStyleSheet("background: #ffffff;")
        sc_lay = QHBoxLayout(sc_widget)
        sc_lay.setContentsMargins(20, 8, 20, 8)
        sc_lay.setSpacing(12)
        sc_lay.addStretch()

        # Haversine distance helper
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        # Sync from MainWindow shared state
        self.user_lat = getattr(self.main, 'user_lat', None)
        self.user_lon = getattr(self.main, 'user_lon', None)
        user_lat = self.user_lat
        user_lon = self.user_lon

        # Collect all stores with their distances
        sorted_stores = []
        for brand_key, brand_data in data_manager.ADDRESS_BOOK.items():
            for branch in brand_data.get("branches", []):
                if user_lat is not None and user_lon is not None:
                    branch_lat = branch.get('latitude')
                    branch_lon = branch.get('longitude')
                    if branch_lat is not None and branch_lon is not None:
                        dist = haversine(user_lat, user_lon, branch_lat, branch_lon)
                    else:
                        dist = float('inf')
                else:
                    dist = float('inf')
                sorted_stores.append((dist, brand_key, branch))

        # Sort by distance
        sorted_stores.sort(key=lambda x: x[0])

        store_index = 0
        for dist_km, brand_key, branch in sorted_stores:
            dist_text = f"{dist_km:.1f} km" if dist_km != float('inf') else "- km"

            card = QWidget()
            card.setFixedWidth(300)
            card.setMinimumHeight(130)
            card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)
            card.setStyleSheet(f"""
                QWidget{{background:{self.t['card_bg']};border-radius:10px;border:1px solid #d0d0d0;}}
                QWidget:hover{{border:2px solid #0FB291;}}
            """)

            main_lay = QHBoxLayout(card)
            main_lay.setContentsMargins(10, 8, 10, 8)
            main_lay.setSpacing(0)

            info_lay = QVBoxLayout()
            info_lay.setSpacing(2)

            nm = QLabel(branch.get("nama_cabang", brand_key))
            nm.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
            nm.setStyleSheet(f"color:{self.t['text1']};background:transparent;border:none;")
            nm.setWordWrap(True)
            nm.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            info_lay.addWidget(nm)

            dist_row = QHBoxLayout()
            dist_row.setSpacing(4)
            pin_icon = QLabel("📍")
            pin_icon.setStyleSheet("font-size: 13px; background: transparent;")
            dist_row.addWidget(pin_icon)
            dist_lbl = QLabel(dist_text)
            self._store_dist_labels.append(dist_lbl)
            dist_lbl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
            dist_lbl.setStyleSheet(f"color:{self.t['dist_fg']};background:transparent;border:none;")
            dist_row.addWidget(dist_lbl)
            dist_row.addStretch()
            info_lay.addLayout(dist_row)

            addr_lbl = QLabel(branch.get("address", "-"))
            addr_lbl.setFont(QFont("Google Sans", 11))
            addr_lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;border:none;")
            addr_lbl.setWordWrap(True)
            addr_lbl.setMinimumHeight(0)
            addr_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
            info_lay.addWidget(addr_lbl)

            main_lay.addLayout(info_lay, stretch=1)

            sc_lay.addWidget(card)
            store_index += 1

        store_scroll.setWidget(sc_widget)
        sLay.addWidget(store_scroll)

        # ── Promo Header ─────────────────────────────────────────────
        promo_header = QWidget()
        promo_header.setStyleSheet(f"background:{self.t['bg']};")
        ph_lay = QVBoxLayout(promo_header)
        ph_lay.setContentsMargins(20, 20, 20, 8)
        ph_lay.setSpacing(2)

        promo_title_html = QLabel("""
            <div style="font-size: 24px; font-weight: bold; color: #1F2937; line-height: 1.3;">
                Katalog Produk
            </div>
            <div style="font-size: 16px; color: #6B7280; line-height: 1.2; margin-top: 4px;">
                temukan produk kebutuhan harianmu
            </div>
        """)
        promo_title_html.setStyleSheet("background:transparent;")
        ph_lay.addWidget(promo_title_html)
        sLay.addWidget(promo_header)

        # ── Product Grid ─────────────────────────────────────────────
        self.product_container = QWidget()
        self.product_container.setStyleSheet("background: #ffffff;")
        self.product_grid = QGridLayout(self.product_container)
        print(f"[DEBUG] Initial grid H={self.product_grid.horizontalSpacing()}, V={self.product_grid.verticalSpacing()}")
        self.product_grid.setHorizontalSpacing(6)
        self.product_grid.setVerticalSpacing(8)
        self.product_grid.setContentsMargins(0, 0, 0, 0)
        self.product_container.setMinimumHeight(400)
        print(f"[DEBUG] product_container size: {self.product_container.size()}")
        print(f"[DEBUG] sLay margins: {sLay.contentsMargins()}, spacing: {sLay.spacing()}")
        sLay.addSpacing(16)
        sLay.addWidget(self.product_container)

        # ── Load More ────────────────────────────────────────────────
        load_more_btn = QPushButton("Muat Lebih Banyak")
        load_more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        load_more_btn.setStyleSheet(
            f"QPushButton{{background:{self.t['price_fg']};color:white;border:none;border-radius:12px;"
            f"padding:12px 24px;font-size:13px;font-weight:bold;}}"
            f"QPushButton:hover{{background:#1a9e6e;}}"
        )
        load_more_btn.hide()
        load_more_btn.clicked.connect(self._load_more)
        self._load_more_btn = load_more_btn
        sLay.addWidget(load_more_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        scroll.setWidget(swidget)
        root.addWidget(scroll)

        # Load initial data
        QTimer.singleShot(0, self.refresh)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Promo")
        self.resize(1280, 820)
        self.setMinimumSize(1000, 640)
        
        self.is_dark = False
        self.t = LIGHT
        self.selected_cat = "Semua"
        self.selected_area = "Semua Area"
        self._filter_promo = False
        self.sort_opt = "termurah"
        self.cart_items = []
        self.selected_brands = []
        self._search_thread = None
        self._search_worker = None
        self.search_q = ""
        self.last_sync = datetime.now()
        self._data_cache = {"data": None, "timestamp": 0, "ttl_ms": 30000}
        self.user_lat = None
        self.user_lon = None
        self._location_acquired = False
        
        self._all_prods = []
        self._visible_count = 0
        self._admin_login_callback = None
        self._profile = QWebEngineProfile.defaultProfile()
        self._load_cart()
        self._build()
        self._apply_theme()
        self.update_balance_display()
        self._reload_products()
        self._update_sync_lbl()
        self.change_global_font_size(self.setting_page.font_size)

    # ── BUILD ─────────────────────────────────────────────────────────────────

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        self._root_lay = QVBoxLayout(root)
        self._root_lay.setContentsMargins(0, 0, 0, 0)
        self._root_lay.setSpacing(0)
        
        self._build_navbar()
        
        # Content stack
        self.stack = QStackedWidget()
        self._root_lay.addWidget(self.stack, stretch=1)
        
        # Page 0: Home
        self.home_w = HomePage(self, self.t)
        # self.home_w = HomeTestPage2(self.t, self)
        self.stack.addWidget(self.home_w)       # idx 0

        # Toast (before LokasiPage needs it)
        self.toast = Toast(root)

        # Page 1: Rekomendasi
        from data_manager import fetch_cloud_data, get_demo_recommendations
        self.rekomendasi_page = RecommendationPage(self.t, toast=self.toast, main=self)
        self.stack.addWidget(self.rekomendasi_page)  # idx 1

        # Page 2: Statistik
        self.stat_page = StatistikPage(self.t, app=self)
        self.stack.addWidget(self.stat_page)    # idx 2

        # Page 3: Pengaturan
        self.setting_page = PengaturanPage(self, self.t)
        self.stack.addWidget(self.setting_page) # idx 3

        # Page 4: Cart (built dynamically)
        self.stack.addWidget(QWidget())          # idx 4

        # Bottom navbar
        self._build_bottom_nav()

    def _build_navbar(self):
        self.navbar = QFrame()
        self.navbar.setObjectName("navbar")
        self.navbar.setFixedHeight(64)
        nl = QHBoxLayout(self.navbar)
        nl.setContentsMargins(28, 0, 28, 0)
        nl.setSpacing(16)
        
        # Radar Promo logo
        self.radar_promo_lbl = QLabel()
        logo_px = QPixmap(os.path.join(APP_BASE, "gemini-svg.png"))
        if not logo_px.isNull():
            logo_px = logo_px.scaled(120, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.radar_promo_lbl.setPixmap(logo_px)
        self.radar_promo_lbl.setStyleSheet("background:transparent;")
        nl.addWidget(self.radar_promo_lbl)

        # Add spacer to balance layout
        nl.addStretch()

        # Bookmark button
        self.bookmark_btn = QPushButton()
        self.bookmark_btn.setFlat(True)
        self.bookmark_btn.setFixedSize(36, 36)
        self.bookmark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bookmark_btn.setStyleSheet("background:transparent;border:none;")
        self.bookmark_btn.setIcon(_svg_to_icon(os.path.join(APP_BASE, "assets", "boomark.svg")))
        nl.addWidget(self.bookmark_btn)

        # Dark/Light toggle button
        self.dark_btn = QPushButton()
        self.dark_btn.setFixedSize(42, 42)
        self.dark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dark_btn.clicked.connect(self._toggle_dark)
        self.dark_btn.setIcon(_svg_to_icon(os.path.join(APP_BASE, "assets", "dark.svg") if self.is_dark else os.path.join(APP_BASE, "assets", "light.svg")))
        self.dark_btn.setStyleSheet("background:transparent;border:none;")
        nl.addWidget(self.dark_btn)
        
        self._root_lay.addWidget(self.navbar)
        self.nav_line = QFrame()
        self.nav_line.setFixedHeight(1)
        self._root_lay.addWidget(self.nav_line)

    def _build_filter_bar(self, parent_lay):
        self.filter_frame = QFrame()
        self.filter_frame.setObjectName("filterBar")
        self.filter_frame.setFixedHeight(100)
        fl = QVBoxLayout(self.filter_frame)
        fl.setContentsMargins(28, 8, 28, 8)
        fl.setSpacing(8)

        cats_row = QHBoxLayout()
        cats_row.setSpacing(8)

        self.cat_btns = {}
        for cat in CATEGORIES:
            display = CAT_EMOJI.get(cat, cat)
            btn = PillBtn(display, cat == self.selected_cat, self.t)
            btn.clicked.connect(lambda _, c=cat: self._select_cat(c))
            self.cat_btns[cat] = btn
            cats_row.addWidget(btn)

        cats_row.addStretch()
        fl.addLayout(cats_row)

        promo_row = QHBoxLayout()
        promo_row.setSpacing(8)

        self.promo_toggle = PillBtn("🔥 Promo", False, self.t)
        self.promo_toggle.clicked.connect(self._toggle_promo_filter)
        promo_row.addWidget(self.promo_toggle)

        promo_row.addStretch()
        fl.addLayout(promo_row)

        self.filter_btn = QPushButton()
        filter_px = QPixmap(os.path.join(APP_BASE, "UI", "Home", "Assets", "Filter.png"))
        if not filter_px.isNull():
            from PyQt6.QtGui import QIcon
            filter_px = filter_px.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.filter_btn.setIcon(QIcon(filter_px))
        self.filter_btn.setText(" Filter")
        self.filter_btn.setFixedHeight(36)
        self.filter_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Medium))
        self.filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_btn.clicked.connect(self._show_filter_dialog)
        self.filter_btn.setStyleSheet(f"QPushButton{{background:{self.t['pill_on_bg']};color:white;border:1px solid {self.t['price_fg']};border-radius:18px;padding:0 20px;}}QPushButton:hover{{background:#1fa072;}}")
        promo_row.addWidget(self.filter_btn)

        self.refresh_btn = QPushButton("↻ Refresh")
        self.refresh_btn.setFixedHeight(36)
        self.refresh_btn.setFont(QFont("Google Sans", 11, QFont.Weight.Medium))
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.clicked.connect(self._force_reload_products)
        self.refresh_btn.setStyleSheet(f"QPushButton{{background:{self.t['btn_bg']};color:{self.t['text1']};border:1px solid {self.t['nav_border']};border-radius:18px;padding:0 16px;}}QPushButton:hover{{background:{self.t['price_fg']};color:white;}}")
        promo_row.addWidget(self.refresh_btn)

        parent_lay.addWidget(self.filter_frame)
        self.filter_line = QFrame()
        self.filter_line.setFixedHeight(1)
        parent_lay.addWidget(self.filter_line)

    def _build_bottom_nav(self):
        self.bottom_nav = QFrame()
        self.bottom_nav.setObjectName("bottomNav")
        self.bottom_nav.setFixedHeight(56)
        drop_shadow(self.bottom_nav, 20, "#00000015", -4)
        bl = QHBoxLayout(self.bottom_nav)
        bl.setContentsMargins(40, 0, 40, 0)
        bl.setSpacing(0)
        self.nav_tabs = [
            ("mdi.home", 0),
            ("mdi.map-marker", 1),
            ("mdi.chart-bar", 2),
            ("mdi.cog", 3),
        ]
        self.bottom_btns = []
        for icon_name, idx in self.nav_tabs:
            btn = QPushButton()
            btn.setFixedSize(56, 56)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            icon = qta.icon(icon_name, color="#9CA3AF")
            btn.setIcon(icon)
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            self.bottom_btns.append(btn)
            bl.addWidget(btn)
        self._root_lay.addWidget(self.bottom_nav)

    # ── NAVIGATION ────────────────────────────────────────────────────────────

    def _switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        self._style_bottom_btns(idx)
        self.navbar.show()
        self.nav_line.show()

    def _style_bottom_btns(self, active_idx):
        t = self.t
        for i, btn in enumerate(self.bottom_btns):
            is_active = (i == active_idx)
            icon_names = ["mdi.home", "mdi.map-marker", "mdi.chart-bar", "mdi.cog"]
            icon_name = icon_names[i]
            if is_active:
                btn.setStyleSheet("QPushButton{background:#4ECDC4;border:none;border-radius:12px;}")
                icon_color = "#000000"
            else:
                btn.setStyleSheet("QPushButton{background:transparent;border:none;border-radius:12px;}QPushButton:hover{background:rgba(128,128,128,0.10);}")
                icon_color = "#9CA3AF"
            icon = qta.icon(icon_name, color=icon_color)
            btn.setIcon(icon)

    def _show_cart(self):
        if not hasattr(self, '_cart_page'):
            self._cart_page = CartPage(self, self.t)
            self._cart_page.back.connect(lambda: self._switch_page(0))
        self.stack.removeWidget(self.stack.widget(4))
        self.stack.insertWidget(4, self._cart_page)
        self.stack.setCurrentIndex(4)
        self._cart_page._populate()
        self._style_bottom_btns(-1)
        self.update_balance_display()
        if hasattr(self, 'setting_page'):
            self.change_global_font_size(self.setting_page.font_size)

    # ── PRODUCTS ──────────────────────────────────────────────────────────────

    def _get_products(self):
        reverse = None if self.sort_opt == "default" else self.sort_opt == "termahal"
        jenis_harga = "PROMO" if self.selected_cat == "Promo" else None

        now = time.time()
        cache = self._data_cache
        if cache["data"] is not None and (now - cache["timestamp"]) * 1000 < cache["ttl_ms"]:
            raw_records = cache["data"]
        else:
            raw_records = data_manager.read_local_data() if data_manager else []
            cache["data"] = raw_records
            cache["timestamp"] = now

        # Map scraped data fields to UI expected fields
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

        records = engine.normalize_promo_data(records)

        filtered, _ = engine.run_pipeline(
            records,
            area=self.selected_area if self.selected_area != "Semua Area" else None,
            category=self.selected_cat if self.selected_cat not in ("Semua", "Promo") else None,
            brand=None,
            jenis_harga=jenis_harga,
            keyword=self.search_q if self.search_q.strip() else None,
            reverse=reverse
        )

        if self.selected_brands:
            filtered = engine.filter_by_brand_multi(filtered, self.selected_brands)

        if self._filter_promo:
            filtered = engine.filter_promo_items(filtered)

        grouped = {}
        for p in filtered:
            store_base = p["store"].split()[0]
            key = (p["name"], store_base, p["price"])
            if key not in grouped:
                np = p.copy()
                np["store_base"] = store_base
                np["is_promo"] = p.get("jenis_harga") == "PROMO"
                np["branches"] = [{"store": p["store"], "distance": p["distance"]}]
                grouped[key] = np
            else:
                grouped[key]["branches"].append({"store": p["store"], "distance": p["distance"]})

        return list(grouped.values())

    def _reload_products(self):
        if not hasattr(self, "prod_list"):
            return
        self._all_prods = self._get_products()
        self._visible_count = min(50, len(self._all_prods))
        self._render_visible_products()

    def _force_reload_products(self):
        if not hasattr(self, "prod_list"):
            return
        self._data_cache = {"data": None, "timestamp": 0, "ttl_ms": 30000}
        self._all_prods = self._get_products()
        self._visible_count = min(50, len(self._all_prods))
        self._render_visible_products()
        self.toast.show_msg("Data produk diperbarui", self.t)

    def _render_visible_products(self):
        if not hasattr(self, "prod_list"):
            return
        self.prod_list.clear()
        prods = self._all_prods[:self._visible_count]
        if not prods:
            self._load_more_btn.hide()
            if hasattr(self, 'setting_page'):
                self.change_global_font_size(self.setting_page.font_size)
            return

        for p in prods:
            item = QListWidgetItem()
            item.setSizeHint(QSize(CARD_W, 360))
            self.prod_list.addItem(item)
            item_widget = ProductListItem(p, self.t)
            item_widget.add_clicked.connect(self._add_to_cart)
            self.prod_list.setItemWidget(item, item_widget)

        total = len(self._all_prods)
        if self._visible_count < total:
            remaining = total - self._visible_count
            self._load_more_btn.setText(f"Muat Lebih Banyak ({remaining} tersisa)")
            self._load_more_btn.show()
        else:
            self._load_more_btn.hide()

        if hasattr(self, 'setting_page'):
            self.change_global_font_size(self.setting_page.font_size)
    
    def _load_more_products(self):
        if not hasattr(self, "prod_list"):
            return
        prev = self.prod_list.count()
        self._visible_count += 50
        prods = self._all_prods[prev:self._visible_count]
        for p in prods:
            item = QListWidgetItem()
            item.setSizeHint(QSize(CARD_W, 360))
            self.prod_list.addItem(item)
            item_widget = ProductListItem(p, self.t)
            item_widget.add_clicked.connect(self._add_to_cart)
            self.prod_list.setItemWidget(item, item_widget)
        total = len(self._all_prods)
        if self._visible_count >= total:
            self._load_more_btn.hide()
        else:
            remaining = total - self._visible_count
            self._load_more_btn.setText(f"Muat Lebih Banyak ({remaining} tersisa)")

    def _on_prod_item_clicked(self, item):
        w = self.prod_list.itemWidget(item)
        if w and hasattr(w, '_show_detail'):
            w._show_detail()

    def _show_product_detail(self, item_or_product):
        product = item_or_product
        if isinstance(item_or_product, QListWidgetItem):
            w = self.prod_list.itemWidget(item_or_product)
            if w:
                product = w.product
        if isinstance(product, dict) and "name" in product:
            dlg = QDialog(self)
            dlg.setWindowTitle(product["name"])
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(f"background:{self.t['card_bg']};")
            t = self.t
            lay = QVBoxLayout(dlg)
            lay.setContentsMargins(16, 16, 16, 16)
            lay.setSpacing(12)
            header = QHBoxLayout()
            ttl = QLabel("Detail Promo")
            ttl.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
            ttl.setStyleSheet(f"color:{t['text1']};background:transparent;")
            close_btn = QPushButton("✕")
            close_btn.setFixedSize(24, 24)
            close_btn.setStyleSheet(f"background:transparent;color:{t['text2']};border:none;font-weight:bold;")
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.clicked.connect(dlg.close)
            header.addWidget(ttl); header.addStretch(); header.addWidget(close_btn)
            lay.addLayout(header)
            img_lbl = QLabel()
            img_lbl.setFixedSize(368, 180)
            img_lbl.setStyleSheet(f"background:{t['card_img_bg']}; border-radius:8px;")
            img_lbl.setText("🖼️")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            diskon = product.get("diskon_persen", 0)
            if diskon > 0:
                badge = QLabel("🔥 Promo", img_lbl)
                badge.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
                badge.setStyleSheet(f"background:{t['promo_badge_bg']};color:{t['promo_badge_fg']};border-radius:6px;padding:4px 10px;min-width:70px;")
                badge.move(8, 8)
                badge.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            lay.addWidget(img_lbl)
            pname = QLabel(product["name"])
            pname.setFont(QFont("Google Sans", 12, QFont.Weight.Bold))
            pname.setWordWrap(True)
            pname.setStyleSheet(f"color:{t['text1']};background:transparent;")
            lay.addWidget(pname)
            price_row = QHBoxLayout()
            price_row.setSpacing(8)
            if diskon > 0:
                op = QLabel(rp(product.get("harga_normal", product["price"])))
                f = QFont("Google Sans", 10); f.setStrikeOut(True); op.setFont(f)
                op.setStyleSheet(f"color:{t['text2']};background:transparent;")
                pp = QLabel(rp(product["effective_price"]))
                pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                pp.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
                price_row.addWidget(op)
                price_row.addWidget(pp)
                dk = QLabel(f"-{diskon:.0f}%")
                dk.setFont(QFont("Google Sans", 9, QFont.Weight.Bold))
                dk.setStyleSheet(f"background:{t['price_fg']};color:white;border-radius:4px;padding:2px 4px;")
                price_row.addWidget(dk)
            else:
                pp = QLabel(rp(product["price"]))
                pp.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
                pp.setStyleSheet(f"color:{t['price_fg']};background:transparent;")
                price_row.addWidget(pp)
            price_row.addStretch()
            lay.addLayout(price_row)
            store_lbl = QLabel(f"🏪 {product.get('store_base', product.get('store', ''))}")
            store_lbl.setFont(QFont("Google Sans", 10))
            store_lbl.setStyleSheet(f"color:{t['store_fg']};background:transparent;")
            lay.addWidget(store_lbl)
            branches = product.get("branches", [{"store": product.get("store", ""), "distance": product.get("distance", "")}])
            for b in branches:
                bw = QFrame()
                bw.setStyleSheet(f"background:{t['cart_item_bg']};border-radius:8px;")
                bl = QVBoxLayout(bw)
                bl.setContentsMargins(12, 8, 12, 8)
                sn = QLabel(f"🏪 {b['store']}")
                sn.setFont(QFont("Google Sans", 10, QFont.Weight.Bold))
                sn.setStyleSheet(f"color:{t['text1']};background:transparent;")
                sd = QLabel(f"📍 {b['distance']}")
                sd.setFont(QFont("Google Sans", 9))
                sd.setStyleSheet(f"color:{t['text2']};background:transparent;")
                bl.addWidget(sn); bl.addWidget(sd)
                lay.addWidget(bw)
            lay.addStretch()
            dlg.exec()

    def _add_to_cart(self, product):
        pid = product.get("id", "")
        if not pid:
            pid = f"{product.get('nama_produk', product.get('name', ''))}_{product.get('store', product.get('brand_toko', 'unknown'))}"
            product["id"] = pid
        for ci in self.cart_items:
            if ci["product"].get("id", "") == pid:
                ci["quantity"] += 1
                self._save_cart()
                self.update_badge()
                self.update_balance_display()
                self.toast.show_msg("Produk berhasil ditambahkan ke keranjang", self.t)
                return
        self.cart_items.append({"product": product, "quantity": 1})
        self._save_cart()
        self.update_badge()
        self.update_balance_display()
        self.toast.show_msg("Produk berhasil ditambahkan ke keranjang", self.t)

    def _save_cart(self):
        try:
            with open(CART_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cart_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to save cart: {e}")

    def _load_cart(self):
        try:
            if os.path.exists(CART_FILE):
                with open(CART_FILE, "r", encoding="utf-8") as f:
                    self.cart_items = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load cart: {e}")
            self.cart_items = []

    def update_badge(self):
        if not hasattr(self, 'badge_lbl'):
            return
        total = sum(ci["quantity"] for ci in self.cart_items)
        if total > 0:
            self.badge_lbl.setText(str(total))
            self.badge_lbl.show()
        else:
            self.badge_lbl.hide()

    def update_balance_display(self):
        if not hasattr(self, 'budget_val'):
            return
        total = sum(ci["product"].get("effective_price", ci["product"].get("price", 0)) * ci["quantity"] for ci in self.cart_items)
        remaining = 100000 - total
        self.budget_val.setText(rp(max(0, remaining)))

    # ── FILTER / SORT ─────────────────────────────────────────────────────────

    def _select_cat(self, cat):
        print(f"[DEBUG] _select_cat called with cat={cat}, _filter_promo={self._filter_promo}")
        if self._filter_promo:
            self._filter_promo = False
            self.promo_toggle.set_active(False)
            self.selected_cat = "Semua"
            for c, btn in self.cat_btns.items():
                btn.set_active(c == "Semua")
        else:
            self.selected_cat = cat
            for c, btn in self.cat_btns.items():
                btn.set_active(c == cat)
        self._reload_products()

    def _toggle_promo_filter(self):
        print(f"[DEBUG] _toggle_promo_filter called, _filter_promo before toggle={self._filter_promo}")
        self._filter_promo = not self._filter_promo
        if self._filter_promo:
            self._saved_cat = self.selected_cat
            self.selected_cat = "Semua"
            for c, btn in self.cat_btns.items():
                btn.set_active(False)
        else:
            self.selected_cat = getattr(self, '_saved_cat', "Semua")
            for c, btn in self.cat_btns.items():
                btn.set_active(c == self.selected_cat)
        self.promo_toggle.set_active(self._filter_promo)
        print(f"[DEBUG] _toggle_promo_filter finished, _filter_promo={self._filter_promo}, selected_cat={self.selected_cat}")
        self._reload_products()

    def _on_area_change(self, area):
        self.selected_area = area
        self._reload_products()

    def _on_sort_change(self, idx):
        if idx == 1:
            self.sort_opt = "termurah"
        elif idx == 2:
            self.sort_opt = "termahal"
        self._reload_products()

    def _show_filter_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Filter & Urutkan")
        dlg.setFixedSize(360, 400)
        dlg.setStyleSheet(f"background:{self.t['setting_card_bg']};")
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(24, 24, 24, 24)
        dl.setSpacing(16)

        brand_lbl = QLabel("Pilih Supermarket")
        brand_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
        brand_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        dl.addWidget(brand_lbl)

        brand_keys = list(data_manager.ADDRESS_BOOK.keys())
        checkboxes = {}
        for bk in brand_keys:
            cb = QCheckBox(bk)
            cb.setFont(QFont("Google Sans", 11))
            cb.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            if bk in self.selected_brands:
                cb.setChecked(True)
            checkboxes[bk] = cb
            dl.addWidget(cb)

        sort_lbl = QLabel("Urutkan")
        sort_lbl.setFont(QFont("Google Sans", 13, QFont.Weight.Bold))
        sort_lbl.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        dl.addWidget(sort_lbl)

        sort_group = QButtonGroup(dlg)
        rb_default = QRadioButton("Default")
        rb_termurah = QRadioButton("Termurah")
        rb_termahal = QRadioButton("Termahal")
        for rb in (rb_default, rb_termurah, rb_termahal):
            rb.setFont(QFont("Google Sans", 11))
            rb.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
            dl.addWidget(rb)
        sort_group.addButton(rb_default, 0)
        sort_group.addButton(rb_termurah, 1)
        sort_group.addButton(rb_termahal, 2)

        if self.sort_opt == "termurah":
            rb_termurah.setChecked(True)
        elif self.sort_opt == "termahal":
            rb_termahal.setChecked(True)
        else:
            rb_default.setChecked(True)

        btn_row = QHBoxLayout()
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedSize(100, 40)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet(f"QPushButton{{background:{self.t['btn_bg']};color:{self.t['text1']};border:1px solid {self.t['nav_border']};border-radius:12px;font-weight:bold;}}QPushButton:hover{{background:{self.t['cart_item_bg']};}}")
        reset_btn.clicked.connect(lambda: self._reset_filter(checkboxes, rb_default))
        btn_row.addWidget(reset_btn)

        btn_row.addStretch()

        apply_btn = QPushButton("Terapkan")
        apply_btn.setFixedSize(120, 40)
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(f"QPushButton{{background:{self.t['price_fg']};color:white;border:none;border-radius:12px;font-weight:bold;}}QPushButton:hover{{background:{self.t['banner_from']};}}")
        apply_btn.clicked.connect(lambda: self._apply_filter(dlg, checkboxes, sort_group))
        btn_row.addWidget(apply_btn)
        dl.addLayout(btn_row)
        dlg.exec()

    def _reset_filter(self, checkboxes, rb_default):
        for cb in checkboxes.values():
            cb.setChecked(False)
        rb_default.setChecked(True)

    def _apply_filter(self, dlg, checkboxes, sort_group):
        self.selected_brands = [bk for bk, cb in checkboxes.items() if cb.isChecked()]
        sid = sort_group.checkedId()
        if sid == 1:
            self.sort_opt = "termurah"
        elif sid == 2:
            self.sort_opt = "termahal"
        else:
            self.sort_opt = "default"
        dlg.accept()
        self._reload_products()

    def _on_search(self, text):
        self.search_q = text
        if self._search_thread and self._search_thread.isRunning():
            old = self._search_worker
            if old:
                old.requestInterruption()
            self._search_thread.quit()
            # Wait up to 3 seconds, no terminate() as first choice
            if not self._search_thread.wait(3000):
                # Forceful termination as last resort only
                self._search_thread.terminate()
                self._search_thread.wait()
        self._search_worker = SearchWorker(text, self.selected_cat, parent=self)
        self._search_worker.finishedSignal.connect(self._on_search_done)
        self._search_thread = self._search_worker
        self._search_thread.start()

    @pyqtSlot(list)
    def _on_search_done(self, results):
        # Guard: ensure this callback is still valid (worker wasn't interrupted/replaced)
        if not self._search_worker or not hasattr(self._search_worker, 'results'):
            return
        try:
            self._all_prods = results if results else []
            self._visible_count = 0
            self._render_visible_products()
        except Exception as e:
            print(f"_on_search_done error: {e}")
        finally:
            self._search_worker = None
            self._search_thread = None

    # ── SYNC / DARK / SETTINGS ────────────────────────────────────────────────

    def _sync(self):
        if hasattr(self, 'refresh_btn') and self.refresh_btn:
            self.refresh_btn.setEnabled(False)
            self.refresh_btn.setText("⏳")

        def do_sync():
            try:
                data = data_manager.read_local_data()
                success = True
            except Exception:
                success = False

            def update_ui():
                if hasattr(self, 'refresh_btn') and self.refresh_btn:
                    self.refresh_btn.setEnabled(True)
                    self.refresh_btn.setText("↻")

                if success:
                    self.last_sync = datetime.now()
                    self._update_sync_lbl()
                    self.stat_page.update_sync_date()
                    self.toast.show_msg("Data dimuat ulang dari file lokal!", self.t)
                    self._data_cache = {"data": None, "timestamp": 0, "ttl_ms": 2000}
                    self._reload_products()
                else:
                    self.toast.show_msg("Gagal memuat data.", self.t)

            QTimer.singleShot(0, update_ui)

        QTimer.singleShot(0, do_sync)

    def _update_sync_lbl(self):
        pass

    def _toggle_dark(self):
        self.is_dark = not self.is_dark
        self.t = DARK if self.is_dark else LIGHT
        self.dark_btn.setIcon(_svg_to_icon(os.path.join(APP_BASE, "assets", "dark.svg") if self.is_dark else os.path.join(APP_BASE, "assets", "light.svg")))
        self._apply_theme()

    def _toggle_budget_visibility(self):
        if hasattr(self, '_budget_hidden') and self._budget_hidden:
            self.budget_val.setText(rp(max(0, 100000 - sum(ci["product"].get("effective_price", ci["product"].get("price", 0)) * ci["quantity"] for ci in self.cart_items))))
            self._budget_hidden = False
        else:
            self.budget_val.setText("Rp ••••••")
            self._budget_hidden = True

    def change_global_font_size(self, fs):
        sizes = {"Sangat Kecil": 10, "Kecil": 11, "Normal": 12, "Besar": 14, "Sangat Besar": 16}
        size = sizes.get(fs, 12)

        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSize(size)
            font.setFamily("Google Sans")
            app.setFont(font)

        for w in QApplication.allWidgets():
            if isinstance(w, QLabel) and len(w.text()) <= 2 and any(ord(c) > 1000 for c in w.text()):
                continue
            if isinstance(w, QPushButton) and len(w.text()) <= 2 and any(ord(c) > 1000 for c in w.text()):
                continue

            try:
                f = w.font()
                f.setPointSize(size)
                f.setFamily("Google Sans")
                w.setFont(f)

                if w.objectName() == "product_name":
                    fm = QFontMetrics(f)
                    w.setFixedHeight(fm.height() * 2 + 4)
            except:
                pass

        geom = self.geometry()
        self.resize(geom.width() + 1, geom.height())
        self.resize(geom.width(), geom.height())

    def set_admin_login_callback(self, callback):
        self._admin_login_callback = callback

    # ── SYNC ─────────────────────────────────────────────────────────────────

    # ── THEME ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        t = self.t
        self.centralWidget().setStyleSheet(f"background:{t['bg']};")
        self.navbar.setStyleSheet(f"QFrame#navbar{{background:{t['nav_bg']};}}")
        self.nav_line.setStyleSheet(f"background:{t['nav_border']};")

        nb = f"QPushButton{{background:{t['btn_bg']};color:{t['btn_fg']};border:none;border-radius:16px;}}QPushButton:hover{{background:{t['cart_item_bg']};}}"
        self.dark_btn.setStyleSheet(nb)
        if hasattr(self, 'bookmark_btn'):
            self.bookmark_btn.setStyleSheet("background:transparent;border:none;")
        if hasattr(self, 'search'):
            self.search.setStyleSheet(f"QLineEdit{{background:{t['search_bg']};color:{t['search_fg']};border:none;}}")

        if hasattr(self, 'filter_frame'):
            self.filter_frame.setStyleSheet(f"QFrame#filterBar{{background:{t['filter_bg']};}}")
        if hasattr(self, 'filter_line'):
            self.filter_line.setStyleSheet(f"background:{t['filter_border']};")

        if hasattr(self, 'prod_list'):
            self.prod_list.setStyleSheet(f"background:{t['bg']};border:none;")

        if hasattr(self, '_load_more_btn'):
            self._load_more_btn.setStyleSheet(f"QPushButton{{background:{t['price_fg']};color:white;border:none;border-radius:12px;padding:12px 24px;font-size:13px;font-weight:bold;}}QPushButton:hover{{background:{t['banner_from']};}}")

        self.bottom_nav.setStyleSheet(f"QFrame#bottomNav{{background:{t['bottom_bg']};border-top:1px solid {t['bottom_border']};}}")

        if hasattr(self, 'banner'):
            self.banner.apply_theme(t)
        if hasattr(self, 'cat_btns'):
            for btn in self.cat_btns.values():
                btn.apply_theme(t)

        self._style_bottom_btns(self.stack.currentIndex())
        self.rekomendasi_page.apply_theme(t)
        self.stat_page.apply_theme(t)
        self.setting_page.apply_theme(t)
        if hasattr(self, '_cart_page') and self._cart_page is not None:
            self._cart_page.apply_theme(t)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "toast") and self.toast.isVisible():
            pw = self.centralWidget().width()
            self.toast.move(pw - self.toast.width() - 24, 76)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Radar Promo")
    app.setFont(QFont("Google Sans", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())