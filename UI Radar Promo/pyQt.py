import sys
import urllib.request
import threading
import math
import folium
import io
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QGridLayout,
    QFrame, QStackedWidget, QSizePolicy, QComboBox, QDialog,
    QGraphicsDropShadowEffect, QMessageBox, QSlider, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal as Signal, QThread, QObject, QRect
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QColor, QLinearGradient, QBrush,
    QPen, QPainterPath, QImage, QFontMetrics
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

PRODUCTS = [
    {"id":"1",  "name":"Beras Premium 5kg",        "category":"Sembako",        "price":65000, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=400&fit=crop"},
    {"id":"2",  "name":"Minyak Goreng 2L",          "category":"Sembako",        "price":32000, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=400&fit=crop"},
    {"id":"3",  "name":"Gula Pasir 1kg",            "category":"Sembako",        "price":14000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1582381804013-81e8e2b82146?w=400&h=400&fit=crop"},
    {"id":"4",  "name":"Tepung Terigu 1kg",         "category":"Sembako",        "price":11000, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1628289623353-b29e18bdd44d?w=400&h=400&fit=crop"},
    {"id":"5",  "name":"Indomie Goreng (5 pcs)",    "category":"Makanan Instan", "price":12500, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&h=400&fit=crop"},
    {"id":"6",  "name":"Pop Mie Ayam Bawang",       "category":"Makanan Instan", "price":6500,  "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1617093727343-374698b1b08d?w=400&h=400&fit=crop"},
    {"id":"7",  "name":"Mie Sedaap Soto (5 pcs)",   "category":"Makanan Instan", "price":11500, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1585032226651-759b368d7246?w=400&h=400&fit=crop"},
    {"id":"8",  "name":"Susu Kental Manis 380g",    "category":"Makanan Instan", "price":13000, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop"},
    {"id":"9",  "name":"Sabun Mandi Lifebuoy 3pcs", "category":"Mandi",          "price":15000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1585828923118-587afa12bcc5?w=400&h=400&fit=crop"},
    {"id":"10", "name":"Shampoo Pantene 170ml",     "category":"Mandi",          "price":18500, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=400&h=400&fit=crop"},
    {"id":"11", "name":"Pasta Gigi Pepsodent",      "category":"Mandi",          "price":9500,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1622286346003-c44d93e0cc47?w=400&h=400&fit=crop"},
    {"id":"12", "name":"Sabun Cuci Piring 800ml",   "category":"Mandi",          "price":12000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1608042314453-ae338d5053d2?w=400&h=400&fit=crop"},
    {"id":"13", "name":"Masker Medis 50pcs",        "category":"Kesehatan",      "price":45000, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1584634731339-252c581abfc5?w=400&h=400&fit=crop"},
    {"id":"14", "name":"Vitamin C 100 tablet",      "category":"Kesehatan",      "price":35000, "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1550572017-4c0f2e5e8f6c?w=400&h=400&fit=crop"},
    {"id":"15", "name":"Hand Sanitizer 500ml",      "category":"Kesehatan",      "price":28000, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1584744982334-e8d2f7947871?w=400&h=400&fit=crop"},
    {"id":"16", "name":"Obat Batuk Herbal",         "category":"Kesehatan",      "price":22000, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=400&fit=crop"},
    {"id":"17", "name":"Chitato Sapi Panggang",     "category":"Snack",          "price":9500,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400&h=400&fit=crop"},
    {"id":"18", "name":"Oreo Chocolate 137g",       "category":"Snack",          "price":10500, "store":"Alfamart Waruga Jaya",    "area":"Gegerkalong", "distance":"1.5 km", "image":"https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop"},
    {"id":"19", "name":"Silverqueen Chunky Bar",    "category":"Snack",          "price":15000, "store":"Borma Toserba Dakota",    "area":"Ciwaruga",    "distance":"1.2 km", "image":"https://images.unsplash.com/photo-1511381939415-e44015466834?w=400&h=400&fit=crop"},
    {"id":"20", "name":"Tango Wafer Coklat",        "category":"Snack",          "price":7500,  "store":"Indomaret Sarijadi 01",   "area":"Sarijadi",    "distance":"0.8 km", "image":"https://images.unsplash.com/photo-1586526564426-a3242d4c7b4e?w=400&h=400&fit=crop"},
]

CATEGORIES  = ["Semua", "Promo", "Sembako", "Makanan Instan", "Mandi", "Kesehatan", "Snack"]
AREAS       = ["Semua Area", "Ciwaruga", "Sarijadi", "Gegerkalong"]
PROMO_IDS   = {"2","5","9","13","17","19"}   # produk yang sedang promo

LIGHT = {
    "bg":"#f5f5f7","nav_bg":"#f5f5f7","nav_border":"#fbfbfb",
    "banner_from":"#3D9797","banner_to":"#65E6B9",
    "filter_bg":"#ffffff","filter_border":"#e5e7eb",
    "pill_off_bg":"#f0f0f2","pill_off_fg":"#375145",
    "pill_on_bg":"#648281","pill_on_fg":"#ffffff",
    "card_bg":"#ffffff","card_border":"#ececec","card_img_bg":"#cfd6d3",
    "price_fg":"#4B7B6D","store_fg":"#6b8074","dist_fg":"#63B187",
    "add_bg":"#94E0BC","add_fg":"#ffffff",
    "text1":"#111827","text2":"#535855",
    "badge_bg":"#e7fcf6","badge_fg":"#39745D",
    "promo_badge_bg":"#fcb0b0","promo_badge_fg":"#a81a31",
    "search_bg":"#f5f4f2","search_border":"#98d7b1","search_fg":"#1E241E",
    "btn_bg":"#f5f4f2","btn_fg":"#1E241E",
    "bottom_bg":"#f0f0f2","bottom_border":"#e5e7eb",
    "bottom_active_bg":"#6FB8AD","bottom_active_fg":"#ffffff","bottom_fg":"#6b7280",
    "cart_bg":"#f5f5f7","cart_card_bg":"#ffffff","cart_item_bg":"#f5f4f2",
    "budget_bg":"#eef8ee","budget_border":"#6FB895",
    "total_bg":"#f5f4f2","remain_bg":"#eef1f8","remain_fg":"#6FB88A",
    "over_bg":"#fee2e2","over_fg":"#de6178",
    "prog_bg":"#e5ebe8","divider":"#e5e7eb",
    "combo_bg":"#f5f4f2","combo_border":"#e5e7eb",
    "stat_bg":"#f5f5f7","stat_card_bg":"#ffffff",
    "chart_colors":["#3D9797","#6FB89C","#65E6B9","#8fcca4","#a5d8aa"],
    "setting_bg":"#f5f5f7","setting_card_bg":"#ffffff",
    "input_bg":"#f5f4f2","input_border":"#d1dbd7",
    "loc_bg":"#f5f5f7","loc_card_bg":"#ffffff",
    "toast_bg":"#6FB8AB","toast_fg":"#ffffff",
}

DARK = {
    "bg":"#3c3d3f","nav_bg":"#3c3d3f","nav_border":"#333436",
    "banner_from":"#3D9797","banner_to":"#65E6B9",
    "filter_bg":"#161716","filter_border":"#1F2121",
    "pill_off_bg":"#2f3532","pill_off_fg":"#B1B5B3",
    "pill_on_bg":"#648281","pill_on_fg":"#f1f9f0",
    "card_bg":"#232323","card_border":"#2E2E2E","card_img_bg":"#363837",
    "price_fg":"#63D6B4","store_fg":"#86a895","dist_fg":"#63B187",
    "add_bg":"#94E0BC","add_fg":"#f1f9f0",
    "text1":"#f1f9f0","text2":"#d9ead6",
    "badge_bg":"#435B53","badge_fg":"#48B088",
    "promo_badge_bg":"#fcb0b0","promo_badge_fg":"#a81a31",
    "search_bg":"#2d4d3a","search_border":"#98d7b1","search_fg":"#f9fafb",
    "btn_bg":"#2d4d3a","btn_fg":"#e6ebe5",
    "bottom_bg":"#254a3e","bottom_border":"#375148",
    "bottom_active_bg":"#6FB8AD","bottom_active_fg":"#eaefec","bottom_fg":"#9cafa9",
    "cart_bg":"#3c3d3f","cart_card_bg":"#232323","cart_item_bg":"#363837",
    "budget_bg":"#2d4d43","budget_border":"#6FB896",
    "total_bg":"#2d4d3a","remain_bg":"#325641","remain_fg":"#e0f9f3",
    "over_bg":"#3b1515","over_fg":"#de6178",
    "prog_bg":"#375141","divider":"#375148",
    "combo_bg":"#2f3532","combo_border":"#375148",
    "stat_bg":"#3c3d3f","stat_card_bg":"#254a3c",
    "chart_colors":["#3D9797","#6FB89C","#65E6B9","#8fcca4","#a5d8aa"],
    "setting_bg":"#3c3d3f","setting_card_bg":"#254a33",
    "input_bg":"#2d4d3a","input_border":"#4b6358",
    "loc_bg":"#3c3d3f","loc_card_bg":"#254a3b",
    "toast_bg":"#A0ECA6","toast_fg":"#effcf2",
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

class _Sig(QObject):
    done = Signal(str, QPixmap)

class ImgLoader(QThread):
    def __init__(self, url, pid, w, h, sig):
        super().__init__()
        self.url = url; self.pid = pid; self.w = w; self.h = h; self.sig = sig
    def run(self):
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
        path.addRoundedRect(0, 0, self.width(), self.height(), self._r, self._r)
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
        self.setFixedHeight(140)
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(36, 12, 36, 12)
        
        self.bg = QFrame()
        self.bg.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #14b8a6); border-radius: 16px;")
        
        lay = QHBoxLayout(self.bg)
        lay.setContentsMargins(32, 16, 32, 16)
        lay.setSpacing(16)
        
        self.left_img = QLabel()
        self.left_img.setFixedSize(80, 80)
        self.left_img.setStyleSheet("background:rgba(255,255,255,0.2);border-radius:12px;")
        self.left_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_img.setText("📷")
        self.left_img.setFont(QFont("Arial", 20))
        lay.addWidget(self.left_img, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)
        text_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.title = QLabel("🔥 Promo Terbaru untuk Mahasiswa")
        self.title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.title.setStyleSheet("color:white;background:transparent;")
        
        self.sub = QLabel("Dapatkan harga termurah hari ini di sekitar Polban")
        self.sub.setFont(QFont("Arial", 13))
        self.sub.setStyleSheet("color:rgba(255,255,255,230);background:transparent;")
        
        text_lay.addWidget(self.title)
        text_lay.addWidget(self.sub)
        lay.addLayout(text_lay)
        lay.addStretch()
        
        self.img_lbl = QLabel()
        px = QPixmap("belanja-rp.png")
        if not px.isNull():
            px = px.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
            self.img_lbl.setPixmap(px)
        else:
            self.img_lbl.setText("🛒✨")
            self.img_lbl.setFont(QFont("Arial", 36))
        self.img_lbl.setStyleSheet("background:transparent;")
        lay.addWidget(self.img_lbl, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        main_lay.addWidget(self.bg)

    def apply_theme(self, t):
        self.t = t

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
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        
        self.img_cont = QWidget()
        self.img_cont.setFixedSize(CARD_W, IMG_H)
        self.img_cont.setStyleSheet(f"background:{self.t['card_img_bg']};border-radius:12px 12px 0 0;")
        
        self.img_lbl = QLabel(self.img_cont)
        self.img_lbl.setFixedSize(CARD_W, IMG_H)
        self.img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_lbl.setText("⏳")
        self.img_lbl.setFont(QFont("Arial", 22))
        self.img_lbl.setStyleSheet("background:transparent;color:#9ca3af;")
        lay.addWidget(self.img_cont)
        
        is_promo = self.product.get("is_promo", self.product["id"] in PROMO_IDS)
        if is_promo:
            self.promo_overlay = QLabel("🔥 Diskon 20%", self.img_cont)
            self.promo_overlay.setFont(QFont("Arial", 8, QFont.Weight.Bold))
            self.promo_overlay.setStyleSheet("background:#10b981;color:white;border-radius:6px;padding:4px 8px;")
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
        if is_promo:
            promo_price_val = int(self.product["price"] * 0.8)
            self.product['effective_price'] = promo_price_val
            
            orig_price = QLabel(rp(self.product["price"]))
            orig_font = QFont("Arial", 9)
            orig_font.setStrikeOut(True)
            orig_price.setFont(orig_font)
            orig_price.setStyleSheet(f"color:{self.t['text2']};")
            
            promo_price = QLabel(rp(promo_price_val))
            promo_price.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            promo_price.setStyleSheet(f"color:{self.t['price_fg']};")
            
            price_col.addWidget(orig_price)
            price_col.addWidget(promo_price)
        else:
            self.product['effective_price'] = self.product["price"]
            self.price_lbl = QLabel(rp(self.product["price"]))
            self.price_lbl.setFont(QFont("Arial", 13, QFont.Weight.Bold))
            self.price_lbl.setStyleSheet(f"color:{self.t['price_fg']};")
            price_col.addWidget(self.price_lbl)
        
        il.addLayout(price_col)

        self.store_lbl = QLabel(f"🏪 {self.product.get('store_base', self.product['store'])}")
        self.store_lbl.setFont(QFont("Arial", 9))
        self.store_lbl.setStyleSheet(f"color:{self.t['store_fg']};")
        il.addWidget(self.store_lbl)

        self.add_btn = QPushButton("+ Tambah")
        self.add_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(30)
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet(f"QPushButton{{background:#10b981;color:white;border:none;border-radius:6px;}}QPushButton:hover{{background:#059669;}}")
        self.add_btn.clicked.connect(lambda: self.add_clicked.emit(self.product))
        il.addWidget(self.add_btn)
        
        lay.addWidget(info)
        
        sig = _Sig()
        sig.done.connect(self._on_img)
        ldr = ImgLoader(self.product["image"], self.product["id"], CARD_W, IMG_H, sig)
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
        dlg = QDialog(self.window())
        dlg.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        dlg.setFixedSize(300, 440)
        dlg.setStyleSheet(f"background:{self.t['card_bg']}; border:1px solid {self.t['card_border']}; border-radius:12px;")
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
            img_lbl.setPixmap(self.img_lbl.pixmap().scaled(268, 130, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            img_lbl.setText("🖼️")
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(img_lbl)
        
        pname = QLabel(self.product["name"])
        pname.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pname.setWordWrap(True)
        pname.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(pname)
        
        price_row = QHBoxLayout()
        price_row.setSpacing(8)
        is_promo = self.product.get("is_promo", False)
        if is_promo:
            op = QLabel(rp(self.product["price"]))
            f = QFont("Arial", 10); f.setStrikeOut(True); op.setFont(f)
            op.setStyleSheet(f"color:{self.t['text2']};background:transparent;")
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
        dlg.exec()


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
            col = QColor("#6F84B8" if self.pct < 70 else "#F1C0CC" if self.pct < 90 else "#e8a5b5")
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
        total = sum(ci["product"]["effective_price"] * ci["quantity"] for ci in self.app.cart_items)
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
        tv = QLabel(rp(p["effective_price"] * q))
        tv.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        tv.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        tv.setAlignment(Qt.AlignmentFlag.AlignRight)
        dv = QLabel(f"{q} x {rp(p['effective_price'])}")
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
        self.app.cart_items = [ci for ci in self.app.cart_items if ci["product"]["id"] != pid]
        self.app.update_badge()
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
        self.data = data; self.t = t; self.setMinimumHeight(220)
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
            lbl = fm.elidedText(label, Qt.TextElideMode.ElideRight, bar_w + gap * 2)
            p.drawText(x - gap // 2, H - pad_b + 8, bar_w + gap, 40,
                       Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap, lbl)
    def apply_theme(self, t):
        self.t = t; self.update()

class PieChart(QWidget):
    def __init__(self, data, t):
        super().__init__()
        self.data = data; self.t = t; self.setMinimumHeight(260)
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
            tw = fm.horizontalAdvance(text)
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
            p.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        # legend
        lx = W // 2 - len(self.data) * 45 // 2; ly = H - 28
        p.setFont(QFont("Arial", 9))
        for i, (label, val, s, sp, col) in enumerate(slices):
            p.fillRect(lx + i * 90, ly, 12, 12, col)
            p.setPen(QColor(self.t["text2"]))
            p.drawText(lx + i * 90 + 16, ly, 80, 12, Qt.AlignmentFlag.AlignLeft, label)
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
        bc = self._make_chart_card("Top 3 Toko dengan Promo Terbanyak", BarChart(top3, self.t))
        lay.addWidget(bc)
        
        # pie chart card
        cat_count = {}
        for p in PRODUCTS:
            if p["id"] in PROMO_IDS:
                cat_count[p["category"]] = cat_count.get(p["category"], 0) + 1
        pie_data = list(cat_count.items())
        pc = self._make_chart_card("Distribusi Kategori Produk Promo", PieChart(pie_data, self.t))
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
        cl.addWidget(tl)
        cl.addWidget(chart_widget)
        return card

    def apply_theme(self, t):
        self.t = t
        self.setStyleSheet(f"background:{t['stat_bg']};")


# ═══════════════════════════════════════════════════════════════════════════════
# LOKASI PAGE (WITH FOLIUM MAP)
# ═══════════════════════════════════════════════════════════════════════════════

class LokasiPage(QWidget):
    def __init__(self, t):
        super().__init__()
        self.t = t
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
            {"name":"Borma Toserba Dakota", "area":"Ciwaruga", "address":"Jl. Ciwaruga No. 12, Bandung Utara", "lat": -6.8624, "lon": 107.5755, "items":len([p for p in PRODUCTS if p["store"]=="Borma Toserba Dakota"]), "open":"08.00 - 21.00"},
            {"name":"Indomaret Sarijadi 01", "area":"Sarijadi", "address":"Jl. Sarijadi No. 45, Bandung Utara", "lat": -6.8731, "lon": 107.5768, "items":len([p for p in PRODUCTS if p["store"]=="Indomaret Sarijadi 01"]), "open":"07.00 - 23.00"},
            {"name":"Alfamart Waruga Jaya", "area":"Gegerkalong", "address":"Jl. Gegerkalong No. 88, Bandung Utara", "lat": -6.8680, "lon": 107.5890, "items":len([p for p in PRODUCTS if p["store"]=="Alfamart Waruga Jaya"]), "open":"24 Jam"},
        ]
        
        # Folium Interactive Map
        map_card = Card(self.t["loc_card_bg"], self.t["card_border"], 18)
        drop_shadow(map_card, 14, "#00000010", 3)
        ml = QVBoxLayout(map_card)
        ml.setContentsMargins(24, 20, 24, 20)
        ml.setSpacing(8)
        mtl = QLabel("Peta Area Interaktif")
        mtl.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        mtl.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        
        # Generate folium map
        fmap = folium.Map(location=[-6.868, 107.580], zoom_start=14)
        for st in stores:
            folium.Marker(
                location=[st["lat"], st["lon"]],
                popup=st["name"],
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(fmap)
        
        data = io.BytesIO()
        fmap.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())
        
        ml.addWidget(mtl)
        ml.addWidget(self.web_view)
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


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class AdminDashboard(QDialog):
    def __init__(self, parent=None, t=None):
        super().__init__(parent)
        self.t = t or LIGHT
        self.setWindowTitle("Radar Promo Admin Dashboard")
        self.setFixedSize(600, 500)
        self.setStyleSheet(f"background:{self.t['setting_bg']};")
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(16)
        
        hdr = QLabel("Radar Promo Admin Dashboard")
        hdr.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        lay.addWidget(hdr)
        
        c1 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
        cl1 = QVBoxLayout(c1)
        l1 = QLabel("Sinkronisasi Data")
        l1.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        l1.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        b1 = QPushButton("Sinkronisasi Sekarang")
        b1.setFixedHeight(36)
        b1.setCursor(Qt.CursorShape.PointingHandCursor)
        b1.setStyleSheet(f"background:#6FB8AD;color:white;border-radius:8px;font-weight:bold;")
        cl1.addWidget(l1); cl1.addWidget(b1)
        lay.addWidget(c1)
        
        c2 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
        cl2 = QVBoxLayout(c2)
        l2 = QLabel("Upload ke Cloud")
        l2.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        l2.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        b2 = QPushButton("Upload Promo ke Cloud")
        b2.setFixedHeight(36)
        b2.setCursor(Qt.CursorShape.PointingHandCursor)
        b2.setStyleSheet(f"background:#F1C0CC;color:white;border-radius:8px;font-weight:bold;")
        cl2.addWidget(l2); cl2.addWidget(b2)
        lay.addWidget(c2)
        
        c3 = Card(self.t['setting_card_bg'], self.t['card_border'], 12)
        cl3 = QVBoxLayout(c3)
        l3 = QLabel("Log Aktivitas")
        l3.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        l3.setStyleSheet(f"color:{self.t['text1']};background:transparent;")
        
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.setStyleSheet(f"background:{self.t['input_bg']};color:{self.t['text2']};border:1px solid {self.t['input_border']};border-radius:8px;")
        log_text.setPlainText("[UPLOAD] upload berhasil\n[SYNC] sinkronisasi selesai\n[INFO] Data dimuat dari data_promo.json (6742 item)")
        cl3.addWidget(l3); cl3.addWidget(log_text)
        lay.addWidget(c3)

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
        
        # Font size card
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
                dash = AdminDashboard(self, self.t)
                dash.exec()
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
        self.sort_opt = "termurah"
        self.cart_items = []
        self.search_q = ""
        self.last_sync = datetime.now()
        
        self._card_refs = []
        self._build()
        self._apply_theme()
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
        self.home_w = QWidget()
        hl = QVBoxLayout(self.home_w)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        self.banner = BannerWidget(self.t)
        hl.addWidget(self.banner)
        self._build_filter_bar(hl)
        
        self.prod_scroll = QScrollArea()
        self.prod_scroll.setWidgetResizable(True)
        self.prod_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.prod_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.prod_cont = QWidget()
        self.prod_grid_lay = QGridLayout()
        self.prod_grid_lay.setSpacing(18)
        wl = QVBoxLayout(self.prod_cont)
        wl.setContentsMargins(36, 24, 36, 24)
        wl.addLayout(self.prod_grid_lay)
        wl.addStretch()
        self.prod_scroll.setWidget(self.prod_cont)
        hl.addWidget(self.prod_scroll)
        self.stack.addWidget(self.home_w)       # idx 0
        
        # Page 1: Lokasi
        self.lokasi_page = LokasiPage(self.t)
        self.stack.addWidget(self.lokasi_page)  # idx 1
        
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
        
        # Toast
        self.toast = Toast(root)

    def _build_navbar(self):
        self.navbar = QFrame()
        self.navbar.setObjectName("navbar")
        self.navbar.setFixedHeight(64)
        nl = QHBoxLayout(self.navbar)
        nl.setContentsMargins(28, 0, 28, 0)
        nl.setSpacing(16)
        
        # Logo with Placeholder
        self.logo_btn = QPushButton()
        self.logo_btn.setFlat(True)
        self.logo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logo_btn.setStyleSheet("background:transparent;border:none;")
        self.logo_btn.clicked.connect(lambda: self._switch_page(0))
        
        logo_lay = QHBoxLayout(self.logo_btn)
        logo_lay.setContentsMargins(0, 0, 0, 0)
        logo_lay.setSpacing(8)
        
        self.logo_img = QLabel()
        self.logo_img.setFixedSize(140, 40)
        self.logo_img.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        px = QPixmap("assets/logo.png")
        if not px.isNull():
            self.logo_img.setPixmap(px.scaled(140, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo_img.setText("🖼️ LOGO")
            self.logo_img.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            self.logo_img.setStyleSheet("color:#10b981;background:transparent;")
            
        logo_lay.addWidget(self.logo_img)
        nl.addWidget(self.logo_btn)
        
        # Search with margin/padding
        search_container = QWidget()
        s_lay = QHBoxLayout(search_container)
        s_lay.setContentsMargins(20, 0, 20, 0)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari promo yang kamu inginkan...")
        self.search.setFont(QFont("Arial", 12))
        self.search.setFixedHeight(42)
        self.search.textChanged.connect(self._on_search)
        s_lay.addWidget(self.search)
        nl.addWidget(search_container, stretch=1)
        
        # Date updated (no time, just date)
        self.sync_btn = QPushButton()
        self.sync_btn.setFixedSize(220, 42)
        self.sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_btn.setFont(QFont("Arial", 10))
        self.sync_btn.clicked.connect(self._sync)
        nl.addWidget(self.sync_btn)
        
        # Dark btn
        self.dark_btn = QPushButton("⏾")
        self.dark_btn.setFixedSize(42, 42)
        self.dark_btn.setFont(QFont("Arial", 17))
        self.dark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dark_btn.clicked.connect(self._toggle_dark)
        nl.addWidget(self.dark_btn)
        
        # Cart btn
        cw = QWidget()
        cw.setStyleSheet("background:transparent;")
        cwl = QHBoxLayout(cw)
        cwl.setContentsMargins(0, 0, 0, 0)
        cwl.setSpacing(0)
        self.cart_btn = QPushButton("🛒")
        self.cart_btn.setFixedSize(42, 42)
        self.cart_btn.setFont(QFont("Arial", 17))
        self.cart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cart_btn.clicked.connect(self._show_cart)
        self.badge_lbl = QLabel()
        self.badge_lbl.setFixedSize(20, 20)
        self.badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.badge_lbl.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.badge_lbl.setStyleSheet("background:#F1C0CC;color:white;border-radius:10px;")
        self.badge_lbl.hide()
        
        cwl.addWidget(self.cart_btn)
        cwl.addWidget(self.badge_lbl)
        nl.addWidget(cw)
        
        self._root_lay.addWidget(self.navbar)
        self.nav_line = QFrame()
        self.nav_line.setFixedHeight(1)
        self._root_lay.addWidget(self.nav_line)

    def _build_filter_bar(self, parent_lay):
        self.filter_frame = QFrame()
        self.filter_frame.setObjectName("filterBar")
        self.filter_frame.setFixedHeight(58)
        fl = QHBoxLayout(self.filter_frame)
        fl.setContentsMargins(28, 8, 28, 8)
        fl.setSpacing(8)
        
        self.cat_btns = {}
        for cat in CATEGORIES:
            btn = PillBtn(cat, cat == self.selected_cat, self.t)
            btn.clicked.connect(lambda _, c=cat: self._select_cat(c))
            self.cat_btns[cat] = btn
            fl.addWidget(btn)
            
        fl.addStretch()
        
        # Sort combo
        sort_icon = QLabel("⇅")
        sort_icon.setFont(QFont("Arial", 14))
        sort_icon.setStyleSheet(f"color:{self.t['price_fg']};background:transparent;")
        
        self.sort_combo = QComboBox()
        # Default text via placeholder
        self.sort_combo.addItem("Urutkan Harga")
        self.sort_combo.addItem("Harga Termurah")
        self.sort_combo.addItem("Harga Termahal")
        self.sort_combo.setFont(QFont("Arial", 11))
        self.sort_combo.setFixedSize(160, 36)
        self.sort_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_change)
        
        # Area combo moved here
        self.area_combo = QComboBox()
        self.area_combo.addItems(AREAS)
        self.area_combo.setFont(QFont("Arial", 11))
        self.area_combo.setFixedSize(160, 36)
        self.area_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.area_combo.currentTextChanged.connect(self._on_area_change)
        
        fl.addWidget(self.area_combo)
        fl.addWidget(sort_icon)
        fl.addWidget(self.sort_combo)
        
        parent_lay.addWidget(self.filter_frame)
        self.filter_line = QFrame()
        self.filter_line.setFixedHeight(1)
        parent_lay.addWidget(self.filter_line)

    def _build_bottom_nav(self):
        self.bottom_nav = QFrame()
        self.bottom_nav.setObjectName("bottomNav")
        self.bottom_nav.setFixedHeight(70)
        drop_shadow(self.bottom_nav, 20, "#00000015", -4)
        bl = QHBoxLayout(self.bottom_nav)
        bl.setContentsMargins(16, 0, 16, 0)
        bl.setSpacing(8)
        self.nav_tabs = [
            ("⌂", "Beranda", 0), ("🧭", "Jelajah", 1), ("📊", "Statistik", 2), ("⚙️", "Pengaturan", 3),
        ]
        self.bottom_btns = []
        for icon, label, idx in self.nav_tabs:
            btn = QPushButton()
            btn_lay = QVBoxLayout(btn)
            btn_lay.setContentsMargins(4, 8, 4, 8)
            btn_lay.setSpacing(4)
            ic = QLabel(icon)
            ic.setFont(QFont("Arial", 22))
            ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ic.setStyleSheet("background:transparent;")
            lb = QLabel(label)
            lb.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lb.setStyleSheet("background:transparent;")
            btn_lay.addWidget(ic)
            btn_lay.addWidget(lb)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            self.bottom_btns.append((btn, ic, lb))
            bl.addWidget(btn)
        self._root_lay.addWidget(self.bottom_nav)

    # ── NAVIGATION ────────────────────────────────────────────────────────────

    def _switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        self._style_bottom_btns(idx)

    def _style_bottom_btns(self, active_idx):
        t = self.t
        for i, (btn, ic, lb) in enumerate(self.bottom_btns):
            is_active = (i == active_idx)
            if is_active:
                btn.setStyleSheet("QPushButton{background:transparent;border:none;}")
                ic.setStyleSheet(f"background:transparent;color:{t['price_fg']};")
                lb.setStyleSheet(f"background:transparent;color:{t['price_fg']};font-weight:bold;")
            else:
                btn.setStyleSheet(f"QPushButton{{background:transparent;border:none;}}QPushButton:hover{{background:{t['pill_off_bg']}55;border-radius:16px;}}")
                ic.setStyleSheet(f"background:transparent;color:{t['bottom_fg']};")
                lb.setStyleSheet(f"background:transparent;color:{t['bottom_fg']};font-weight:normal;")

    def _show_cart(self):
        cart = CartPage(self, self.t)
        cart.back.connect(lambda: self._switch_page(0))
        self.stack.removeWidget(self.stack.widget(4))
        self.stack.insertWidget(4, cart)
        self.stack.setCurrentIndex(4)
        self._style_bottom_btns(-1)
        if hasattr(self, 'setting_page'):
            self.change_global_font_size(self.setting_page.font_size)

    # ── PRODUCTS ──────────────────────────────────────────────────────────────

    def _get_products(self):
        prods = PRODUCTS
        if self.selected_cat == "Promo":
            prods = [p for p in prods if p["id"] in PROMO_IDS]
        elif self.selected_cat != "Semua":
            prods = [p for p in prods if p["category"] == self.selected_cat]
        if self.selected_area != "Semua Area":
            prods = [p for p in prods if p["area"] == self.selected_area]
        
        q = self.search_q.lower().strip()
        if q:
            prods = [p for p in prods if q in p["name"].lower()
                     or q in p["category"].lower() or q in p["store"].lower()]
                     
        grouped = {}
        for p in prods:
            store_base = p["store"].split()[0]
            key = (p["name"], store_base, p["price"])
            if key not in grouped:
                np = p.copy()
                np["store_base"] = store_base
                np["is_promo"] = np["id"] in PROMO_IDS
                np["branches"] = [{"store": p["store"], "distance": p["distance"]}]
                grouped[key] = np
            else:
                grouped[key]["branches"].append({"store": p["store"], "distance": p["distance"]})
                
        grouped_prods = list(grouped.values())
        if self.sort_opt == "termurah":
            grouped_prods = sorted(grouped_prods, key=lambda p: p.get("effective_price", p["price"]))
        else:
            grouped_prods = sorted(grouped_prods, key=lambda p: p.get("effective_price", p["price"]), reverse=True)
            
        return grouped_prods

    def _reload_products(self):
        while self.prod_grid_lay.count():
            it = self.prod_grid_lay.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self._card_refs.clear()
        prods = self._get_products()
        COLS = 5
        if not prods:
            lbl = QLabel("😢  Produk tidak ditemukan\nCoba kata kunci atau filter lain")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Arial", 15))
            lbl.setStyleSheet(f"color:{self.t['text2']};background:transparent;padding:60px;")
            self.prod_grid_lay.addWidget(lbl, 0, 0, 1, COLS)
            return
        
        for i, p in enumerate(prods):
            card = ProductCard(p, self.t)
            card.add_clicked.connect(self._add_to_cart)
            self.prod_grid_lay.addWidget(card, i // COLS, i % COLS,
                                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            self._card_refs.append(card)
        for c in range(COLS):
            self.prod_grid_lay.setColumnStretch(c, 1)
            
        if hasattr(self, 'setting_page'):
            self.change_global_font_size(self.setting_page.font_size)

    def _add_to_cart(self, product):
        for ci in self.cart_items:
            if ci["product"]["id"] == product["id"]:
                ci["quantity"] += 1
                self.update_badge()
                self.toast.show_msg("Produk berhasil ditambahkan ke keranjang", self.t)
                return
        self.cart_items.append({"product": product, "quantity": 1})
        self.update_badge()
        self.toast.show_msg("Produk berhasil ditambahkan ke keranjang", self.t)

    def update_badge(self):
        total = sum(ci["quantity"] for ci in self.cart_items)
        if total > 0:
            self.badge_lbl.setText(str(total))
            self.badge_lbl.show()
        else:
            self.badge_lbl.hide()

    # ── FILTER / SORT ─────────────────────────────────────────────────────────

    def _select_cat(self, cat):
        self.selected_cat = cat
        for c, btn in self.cat_btns.items():
            btn.set_active(c == cat)
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

    def _on_search(self, text):
        self.search_q = text
        self._reload_products()

    # ── SYNC / DARK / SETTINGS ────────────────────────────────────────────────

    def _sync(self):
        if not hasattr(self, 'setting_page') or not getattr(self.setting_page, 'is_admin', False):
            return
        self.last_sync = datetime.now()
        self._update_sync_lbl()
        self.stat_page.update_sync_date()
        self.toast.show_msg("Data promo berhasil diperbarui!", self.t)

    def _update_sync_lbl(self):
        # Format "12 Mei 2026"
        months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        m_idx = self.last_sync.month - 1
        formatted_date = f"{self.last_sync.day} {months[m_idx]} {self.last_sync.year}"
        self.sync_btn.setText(f"Terakhir diperbarui: {formatted_date}")

    def _toggle_dark(self):
        self.is_dark = not self.is_dark
        self.t = DARK if self.is_dark else LIGHT
        self.dark_btn.setText("☀︎" if self.is_dark else "⏾")
        
        idx = self.stack.currentIndex()
        
        self.stack.removeWidget(self.lokasi_page)
        self.lokasi_page.deleteLater()
        self.lokasi_page = LokasiPage(self.t)
        self.stack.insertWidget(1, self.lokasi_page)
        
        self.stack.removeWidget(self.stat_page)
        self.stat_page.deleteLater()
        self.stat_page = StatistikPage(self.t, app=self)
        self.stack.insertWidget(2, self.stat_page)
        
        self.stack.removeWidget(self.setting_page)
        self.setting_page.deleteLater()
        self.setting_page = PengaturanPage(self, self.t)
        self.stack.insertWidget(3, self.setting_page)
        
        if self.stack.widget(4) and isinstance(self.stack.widget(4), CartPage):
            self.stack.removeWidget(self.stack.widget(4))
            cart = CartPage(self, self.t)
            cart.back.connect(lambda: self._switch_page(0))
            self.stack.insertWidget(4, cart)
            
        self.stack.setCurrentIndex(idx)
        
        self._apply_theme()
        self._reload_products()
        if hasattr(self.setting_page, 'font_size'):
            self.change_global_font_size(self.setting_page.font_size)

    def change_global_font_size(self, fs):
        sizes = {"Sangat Kecil": 10, "Kecil": 11, "Normal": 12, "Besar": 14, "Sangat Besar": 16}
        size = sizes.get(fs, 12)
        
        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSize(size)
            app.setFont(font)
            
        for w in QApplication.allWidgets():
            if isinstance(w, QLabel) and len(w.text()) <= 2 and any(ord(c) > 1000 for c in w.text()):
                continue
            if isinstance(w, QPushButton) and len(w.text()) <= 2 and any(ord(c) > 1000 for c in w.text()):
                continue
                
            try:
                f = w.font()
                f.setPointSize(size)
                w.setFont(f)
                
                if w.objectName() == "product_name":
                    fm = QFontMetrics(f)
                    w.setFixedHeight(fm.height() * 2 + 4)
            except:
                pass

    # ── THEME ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        t = self.t
        self.centralWidget().setStyleSheet(f"background:{t['bg']};")
        self.navbar.setStyleSheet(f"QFrame#navbar{{background:{t['nav_bg']};}}")
        self.nav_line.setStyleSheet(f"background:{t['nav_border']};")
        
        nb = f"QPushButton{{background:{t['btn_bg']};color:{t['btn_fg']};border:none;border-radius:16px;}}QPushButton:hover{{background:{t['cart_item_bg']};}}"
        self.sync_btn.setStyleSheet(nb)
        self.dark_btn.setStyleSheet(nb)
        self.cart_btn.setStyleSheet(nb)
        
        self.search.setStyleSheet(f"QLineEdit{{background:{t['search_bg']};color:{t['search_fg']};border:1px solid {t['search_border']};border-radius:21px;padding:0 18px;}}QLineEdit:focus{{border:2px solid #6F84B8;}}")
        
        combo_style = f"QComboBox{{background:{t['combo_bg']};color:{t['text1']};border:1px solid {t['combo_border']};border-radius:18px;padding:0 12px;}}QComboBox::drop-down{{border:none;width:20px;}}QComboBox QAbstractItemView{{background:{t['combo_bg']};color:{t['text1']};border:1px solid {t['combo_border']};}}"
        self.sort_combo.setStyleSheet(combo_style)
        self.area_combo.setStyleSheet(combo_style)
        
        self.filter_frame.setStyleSheet(f"QFrame#filterBar{{background:{t['filter_bg']};}}")
        self.filter_line.setStyleSheet(f"background:{t['filter_border']};")
        
        self.prod_scroll.setStyleSheet(f"background:{t['bg']};border:none;")
        self.prod_cont.setStyleSheet(f"background:{t['bg']};")
        
        self.bottom_nav.setStyleSheet(f"QFrame#bottomNav{{background:{t['bottom_bg']};border-top:1px solid {t['bottom_border']};}}")
        
        self.banner.apply_theme(t)
        for btn in self.cat_btns.values():
            btn.apply_theme(t)
            
        self._style_bottom_btns(self.stack.currentIndex())
        self.lokasi_page.apply_theme(t)
        self.stat_page.apply_theme(t)
        self.setting_page.apply_theme(t)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "toast") and self.toast.isVisible():
            pw = self.centralWidget().width()
            self.toast.move(pw - self.toast.width() - 24, 76)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Radar Promo")
    app.setFont(QFont("Arial", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
