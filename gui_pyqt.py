"""
gui_pyqt.py — Radar Promo GUI v2.0
====================================
Redesign: Notion-style minimalis — Putih · Hitam · Hijau
PyQt6 desktop app, 4 tab: Home, Jelajah, Statistik, Pengaturan.
"""

import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QGridLayout,
    QFrame, QStackedWidget, QSizePolicy, QDialog, QComboBox,
    QMessageBox, QSpacerItem,
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading
import urllib.request
from io import BytesIO
from PyQt6.QtCore import pyqtSignal, QThread, QObject
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image, ImageDraw

_cache, _lock = {}, threading.Lock()
_active_threads = []

class _Sig(QObject):
    done = pyqtSignal(str, QPixmap)

class ImgLoader(QThread):
    def __init__(self, url, pid, w, h, sig):
        super().__init__()
        self.url = url
        self.pid = pid
        self.w = w
        self.h = h
        self.sig = sig
    def run(self):
        with _lock:
            if self.pid in _cache:
                self.sig.done.emit(self.pid, _cache[self.pid])
                return
        if not self.url:
            self.sig.done.emit(self.pid, QPixmap())
            return
        try:
            req = urllib.request.Request(self.url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as r: data = r.read()
            img = Image.open(BytesIO(data)).convert("RGBA")
            s = min(img.width, img.height)
            img = img.crop(((img.width-s)//2, (img.height-s)//2, (img.width+s)//2, (img.height+s)//2))
            img = img.resize((self.w, self.h), Image.LANCZOS)
            mask = Image.new("L", img.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([(0,0), img.size], radius=10, fill=255)
            img.putalpha(mask)
            qimg = QImage(img.tobytes("raw", "RGBA"), img.width, img.height, QImage.Format.Format_RGBA8888)
            px = QPixmap.fromImage(qimg)
            with _lock: _cache[self.pid] = px
            self.sig.done.emit(self.pid, px)
        except Exception:
            self.sig.done.emit(self.pid, QPixmap())

import matplotlib

# ─────────────────────────────────────────────────────────────────
# DESIGN TOKENS  (Notion palette)
# ─────────────────────────────────────────────────────────────────

BG           = "#FFFFFF"
BG_SOFT      = "#F7F6F3"
BG_HOVER     = "#EFEFED"
TEXT_1       = "#191919"
TEXT_2       = "#787774"
TEXT_3       = "#ACABA8"
BORDER       = "#E9E9E7"
ACCENT       = "#21C083"
ACCENT_LIGHT = "#E6F7F0"
ACCENT_DARK  = "#17875C"
PROMO_BG     = "#FEF9C3"
PROMO_FG     = "#854D0E"

CATEGORIES = [
    "Semua", "Sembako", "Makanan Instan", "Minuman",
    "Kamar & Kebersihan", "Kesehatan", "Snack",
]
CAT_ICONS = {"Semua": "", "Sembako": "🌾 ", "Makanan Instan": "🍜 ", "Minuman": "🧃 ", "Kamar & Kebersihan": "🛁 ", "Kesehatan": "💊 ", "Snack": "🥨 "}
AREAS     = ["Semua Area", "Ciwaruga", "Sarijadi", "Gegerkalong"]
SORT_OPTS = [("Termurah", "termurah"), ("Termahal", "termahal"), ("Diskon Terbesar", "diskon")]

# ─────────────────────────────────────────────────────────────────
# imports opsional
# ─────────────────────────────────────────────────────────────────
try:
    from engine import get_statistics
except ImportError:
    get_statistics = None

try:
    import data_manager
except ImportError:
    data_manager = None


# ═══════════════════════════════════════════════════════════════════
# KOMPONEN DASAR
# ═══════════════════════════════════════════════════════════════════

class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {BORDER}; border: none;")


class ChipButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh()

    def _refresh(self):
        if self.active:
            self.setStyleSheet("""
                QPushButton {
                    background: #EAF7F2;
                    color: #21C083;
                    border: 1.5px solid #21C083;
                    border-radius: 17px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 600;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #F3F4F6;
                    color: #4B5563;
                    border: 1.5px solid #E5E7EB;
                    border-radius: 17px;
                    padding: 6px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #E5E7EB;
                }
            """)

    def set_active(self, val: bool):
        self.active = val
        self._refresh()


# ═══════════════════════════════════════════════════════════════════
# PRODUCT CARD
# ═══════════════════════════════════════════════════════════════════

class ProductCard(QFrame):
    def __init__(self, product: dict, on_add_cart, parent=None):
        super().__init__(parent)
        self.product  = product
        self.on_add_cart = on_add_cart
        self._build()

    def _build(self):
        self.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #21C083;
                border-width: 1.5px;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(4)

        p = self.product

        # Image Container
        self.img_cont = QLabel(self)
        self.img_cont.setFixedSize(180, 140)
        self.img_cont.setStyleSheet("background:#F9FAFB; border-radius:8px; border:none;")
        self.img_cont.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_cont.setText("⏳")
        lay.addWidget(self.img_cont, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(6)
        
        if p.get("image_url"):
            self._sig = _Sig()
            self._sig.done.connect(self._on_img)
            loader = ImgLoader(p["image_url"], p["id"], 180, 140, self._sig)
            _active_threads.append(loader)
            loader.finished.connect(lambda l=loader: _active_threads.remove(l) if l in _active_threads else None)
            loader.start()
        else:
            self.img_cont.setText("🖼️")

        # Title
        title_str = p.get("nama_produk", "—")
        if len(title_str) > 42:
            title_str = title_str[:39] + "..."
        nama = QLabel(title_str)
        nama.setWordWrap(True)
        nama.setFixedHeight(38) # Maksimal 2 baris
        nama.setStyleSheet("color:#111827; font-size:13px; font-weight:bold; background:transparent; border:none;")
        nama.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(nama)

        # Category
        cat_lbl = QLabel(p.get("kategori", "Lainnya"))
        cat_lbl.setStyleSheet("color:#6B7280; font-size:11px; background:transparent; border:none;")
        lay.addWidget(cat_lbl)
        
        # Branch
        toko = QLabel(p.get("nama_cabang") or p.get("brand_toko", "—"))
        toko.setStyleSheet("color:#9CA3AF; font-size:10px; background:transparent; border:none;")
        lay.addWidget(toko)

        # Price
        harga = p.get("harga_promo", 0)
        price_lbl = QLabel("Rp" + "{:,}".format(harga).replace(",", "."))
        price_lbl.setStyleSheet("color:#111827; font-size:15px; font-weight:900; background:transparent; border:none; padding-top:4px;")
        lay.addWidget(price_lbl)

    def mousePressEvent(self, event):
        # Click card to add to cart
        self.on_add_cart(self.product)
        super().mousePressEvent(event)

    def _on_img(self, pid, px):
        try:
            if pid != self.product.get("id"): return
            if not px.isNull():
                self.img_cont.setPixmap(px)
                self.img_cont.setText("")
            else:
                self.img_cont.setText("🖼️")
        except RuntimeError:
            pass # Widget sudah dihapus (user sudah pindah halaman)


# ═══════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════

class HomePage(QWidget):
    def __init__(self, db: list, on_add_cart, parent=None):
        super().__init__(parent)
        self.db            = db
        self.on_add_cart   = on_add_cart
        self.selected_cat  = "Semua"
        self.selected_area = "Semua Area"
        self.search_q      = ""
        self.sort_opt      = "termurah"
        self.cat_btns: dict[str, ChipButton] = {}
        self.sort_btns: dict[str, ChipButton] = {}
        
        # Pagination state
        self.current_page = 1
        self.items_per_page = 50
        self.total_pages = 1
        self.filtered_prods = []
        
        self.setStyleSheet(f"background:{BG};")
        self._build()
        self._refresh()

    # ── LAYOUT ─────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_banner())
        root.addWidget(self._make_filter_bar())

        # Scrollable product grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border:none; background:{BG_SOFT}; }}
            QScrollBar:vertical {{
                background:{BG_SOFT}; width:6px; border:none;
            }}
            QScrollBar::handle:vertical {{
                background:{BORDER}; border-radius:3px; min-height:30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height:0; background:none;
            }}
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet(f"background:{BG_SOFT};")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(40, 10, 40, 40)
        self.grid_layout.setSpacing(16)
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.scroll.setWidget(self.grid_container)
        root.addWidget(self.scroll, stretch=1)
        
        # Pagination Bar
        self.page_bar = QFrame()
        self.page_bar.setStyleSheet("background:transparent;")
        page_lay = QHBoxLayout(self.page_bar)
        page_lay.setContentsMargins(40, 10, 40, 20)
        
        page_lay.addStretch(1)
        
        self.btn_prev = QPushButton("◄ Sebelumnya")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #E5E7EB; border-radius: 6px; padding: 6px 12px; color: #374151; font-weight: bold; }
            QPushButton:hover { background: #F3F4F6; }
            QPushButton:disabled { color: #D1D5DB; background: #F9FAFB; }
        """)
        self.btn_prev.clicked.connect(self._prev_page)
        
        self.lbl_page = QLabel("Halaman 1 / 1")
        self.lbl_page.setStyleSheet("color: #374151; font-weight: bold; font-size: 13px; margin: 0 10px;")
        
        self.btn_next = QPushButton("Selanjutnya ►")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setStyleSheet("""
            QPushButton { background: white; border: 1px solid #E5E7EB; border-radius: 6px; padding: 6px 12px; color: #374151; font-weight: bold; }
            QPushButton:hover { background: #F3F4F6; }
            QPushButton:disabled { color: #D1D5DB; background: #F9FAFB; }
        """)
        self.btn_next.clicked.connect(self._next_page)
        
        page_lay.addWidget(self.btn_prev)
        page_lay.addWidget(self.lbl_page)
        page_lay.addWidget(self.btn_next)
        page_lay.addStretch(1)
        
        root.addWidget(self.page_bar)

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_current_page()

    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._render_current_page()

    def _make_banner(self) -> QFrame:
        banner = QFrame()
        banner.setFixedHeight(140)
        banner.setStyleSheet("""
            QFrame {
                background: #21C083;
                border-radius: 12px;
                margin: 20px 40px 0px 40px;
            }
        """)
        h = QHBoxLayout(banner)
        h.setContentsMargins(40, 20, 0, 0)
        
        # Left Text
        text_col = QVBoxLayout()
        text_col.setSpacing(5)
        text_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        t1 = QLabel("🔥 Promo Terbaru untuk Mahasiswa")
        t1.setStyleSheet("color: white; font-size: 24px; font-weight: 800; background: transparent; padding-top:20px;")
        t2 = QLabel("Dapatkan harga termurah hari ini di sekitar Polban!")
        t2.setStyleSheet("color: white; font-size: 16px; font-weight: 500; background: transparent;")
        text_col.addWidget(t1)
        text_col.addWidget(t2)
        text_col.addStretch(1)
        h.addLayout(text_col)
        
        # Right Images (People + Bag)
        h.addStretch(1)
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        lbl_people = QLabel()
        img_people_path = os.path.join(base_path, "img_people.png")
        if os.path.exists(img_people_path):
            px_people = QPixmap(img_people_path).scaledToHeight(140, Qt.TransformationMode.SmoothTransformation)
            lbl_people.setPixmap(px_people)
        lbl_people.setStyleSheet("background:transparent;")
        lbl_people.setAlignment(Qt.AlignmentFlag.AlignBottom)
        h.addWidget(lbl_people)
        
        lbl_bag = QLabel()
        img_bag_path = os.path.join(base_path, "img_bag.png")
        if os.path.exists(img_bag_path):
            px_bag = QPixmap(img_bag_path).scaledToHeight(120, Qt.TransformationMode.SmoothTransformation)
            lbl_bag.setPixmap(px_bag)
        lbl_bag.setStyleSheet("background:transparent;")
        lbl_bag.setAlignment(Qt.AlignmentFlag.AlignBottom)
        h.addWidget(lbl_bag)
        
        return banner

    def _make_filter_bar(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet("background:#FFFFFF;")
        v = QVBoxLayout(bar)
        v.setContentsMargins(40, 20, 40, 10)
        
        r = QHBoxLayout()
        r.setSpacing(10)
        
        for cat in CATEGORIES:
            label = CAT_ICONS.get(cat, "") + cat if cat != "Kamar & Kebersihan" else "🛁 Mandi"
            label = label if cat != "Semua" else "Semua"
            btn = ChipButton(label)
            btn.set_active(cat == "Semua")
            btn.clicked.connect(lambda _, c=cat: self._select_cat(c))
            self.cat_btns[cat] = btn
            r.addWidget(btn)
            
        r.addStretch(1)
        
        # Sort Button
        sort_btn = QPushButton("↑ ↓ Harga")
        sort_btn.setFixedHeight(34)
        sort_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sort_btn.setStyleSheet("""
            QPushButton {
                background: #21C083; color: white; font-weight: bold; font-size: 14px;
                border-radius: 8px; padding: 0 16px; border:none;
            }
            QPushButton:hover { background: #1B9C69; }
        """)
        sort_btn.clicked.connect(lambda: self._select_sort("termahal" if self.sort_opt == "termurah" else "termurah"))
        r.addWidget(sort_btn)
        
        v.addLayout(r)
        return bar

    # ── EVENT HANDLERS ─────────────────────────────────────────────

    def _select_cat(self, cat: str):
        self.current_page = 1
        self.selected_cat = cat
        for c, b in self.cat_btns.items():
            b.set_active(c == cat)
        self._refresh()

    def _set_filter(self, key: str, val: str):
        self.current_page = 1
        if key == "area":
            self.selected_area = val
        self._refresh()

    def _select_sort(self, opt: str):
        self.current_page = 1
        self.sort_opt = opt
        for o, b in self.sort_btns.items():
            b.set_active(o == opt)
        self._refresh()

    def set_search(self, query: str):
        self.current_page = 1
        self.search_q = query
        self._refresh()

    # ── RENDER PRODUK ──────────────────────────────────────────────

    def _refresh(self):
        prods = list(self.db)

        # Filter kategori
        if self.selected_cat == "Promo":
            prods = [p for p in prods if p.get("jenis_harga") == "PROMO"]
        elif self.selected_cat != "Semua":
            prods = [p for p in prods if p.get("kategori") == self.selected_cat]

        # Filter area
        if self.selected_area != "Semua Area":
            prods = [p for p in prods
                     if self.selected_area in p.get("area_tags", [])]

        # Filter pencarian
        kw = self.search_q.lower().strip()
        if kw:
            prods = [p for p in prods
                     if kw in p.get("search_vector", p.get("nama_produk", "") + " " + p.get("brand_toko", "")).lower()]

        # Sort
        if self.sort_opt == "termurah":
            prods.sort(key=lambda p: p.get("harga_promo", 0))
        elif self.sort_opt == "termahal":
            prods.sort(key=lambda p: p.get("harga_promo", 0), reverse=True)
            
        self.filtered_prods = prods
        
        import math
        self.total_pages = max(1, math.ceil(len(prods) / self.items_per_page))
        
        # Jika halaman saat ini lebih besar dari total halaman setelah filter, kembalikan ke 1
        if self.current_page > self.total_pages:
            self.current_page = 1
            
        self._render_current_page()

    def _render_current_page(self):
        # Bersihkan grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Update UI text
        self.lbl_page.setText(f"Halaman {self.current_page} / {self.total_pages}")
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)

        if not self.filtered_prods:
            empty = self._make_empty_state()
            self.grid_layout.addWidget(empty, 0, 0, 1, 4)
            self.page_bar.setVisible(False)
            return
            
        self.page_bar.setVisible(True)

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = self.filtered_prods[start_idx:end_idx]

        cols = 5
        for i, product in enumerate(page_items):
            card = ProductCard(product, self.on_add_cart)
            self.grid_layout.addWidget(card, i // cols, i % cols)
            
        # Scroll ke atas secara otomatis saat ganti halaman
        self.scroll.verticalScrollBar().setValue(0)

    @staticmethod
    def _make_empty_state() -> QWidget:
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        v = QVBoxLayout(w)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setSpacing(8)

        ico = QLabel("🔍")
        ico.setStyleSheet("font-size:40px; background:transparent;")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)

        t1 = QLabel("Tidak ada produk ditemukan")
        t1.setStyleSheet(f"color:{TEXT_1}; font-size:14px; font-weight:600; background:transparent;")
        t1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        t2 = QLabel("Coba ubah filter atau kata kunci pencarian")
        t2.setStyleSheet(f"color:{TEXT_3}; font-size:12px; background:transparent;")
        t2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        v.addStretch()
        v.addWidget(ico)
        v.addWidget(t1)
        v.addWidget(t2)
        v.addStretch()
        return w


# ═══════════════════════════════════════════════════════════════════
# CART DIALOG
# ═══════════════════════════════════════════════════════════════════

class CartDialog(QDialog):
    def __init__(self, cart_items: list, parent=None):
        super().__init__(parent)
        self.cart_items = cart_items
        self.setWindowTitle("Keranjang Belanja")
        self.setMinimumSize(440, 540)
        self.setStyleSheet(f"background:{BG};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 28, 28, 24)
        lay.setSpacing(16)

        # Header
        h = QHBoxLayout()
        title = QLabel("🛒  Keranjang Belanja")
        title.setStyleSheet(f"""
            color:{TEXT_1}; font-size:18px; font-weight:700; background:transparent;
        """)
        h.addWidget(title)
        h.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFlat(True)
        close_btn.setStyleSheet(f"""
            QPushButton {{ color:{TEXT_2}; font-size:16px; border:none; background:transparent; }}
            QPushButton:hover {{ color:{TEXT_1}; }}
        """)
        close_btn.clicked.connect(self.close)
        h.addWidget(close_btn)
        lay.addLayout(h)
        lay.addWidget(Divider())

        if not self.cart_items:
            ico = QLabel("🛒")
            ico.setStyleSheet("font-size:36px; background:transparent;")
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg = QLabel("Keranjang masih kosong")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet(f"color:{TEXT_2}; font-size:13px; background:transparent;")
            lay.addWidget(ico)
            lay.addWidget(msg)
            lay.addStretch()
            return

        # Item list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        items_w = QWidget()
        items_w.setStyleSheet("background:transparent;")
        items_v = QVBoxLayout(items_w)
        items_v.setContentsMargins(0, 0, 0, 0)
        items_v.setSpacing(8)

        total = 0
        for item in self.cart_items:
            row = QFrame()
            row.setStyleSheet(f"background:{BG_SOFT}; border-radius:8px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 10, 14, 10)

            name = QLabel(item.get("nama_produk", "?"))
            name.setWordWrap(True)
            name.setStyleSheet(f"color:{TEXT_1}; font-size:12px; background:transparent;")
            rl.addWidget(name, stretch=1)

            harga = item.get("harga_promo", 0)
            total += harga
            price = QLabel("Rp {:,}".format(harga).replace(",", "."))
            price.setStyleSheet(f"""
                color:{ACCENT}; font-size:13px; font-weight:700; background:transparent;
            """)
            rl.addWidget(price)
            items_v.addWidget(row)

        items_v.addStretch()
        scroll.setWidget(items_w)
        lay.addWidget(scroll, stretch=1)
        lay.addWidget(Divider())

        # Total
        tot_row = QHBoxLayout()
        tot_row.addWidget(
            _lbl("Total", size=14, weight=600, color=TEXT_1)
        )
        tot_row.addStretch()
        tot_row.addWidget(
            _lbl("Rp {:,}".format(total).replace(",", "."), size=16, weight=700, color=ACCENT)
        )
        lay.addLayout(tot_row)

        save_btn = QPushButton("Simpan ke Anggaran")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background:{ACCENT}; color:white; border:none;
                border-radius:8px; padding:12px;
                font-size:14px; font-weight:600;
            }}
            QPushButton:hover {{ background:{ACCENT_DARK}; }}
        """)
        save_btn.clicked.connect(
            lambda: QMessageBox.information(self, "Info", "Fitur anggaran segera hadir!")
        )
        lay.addWidget(save_btn)


# ═══════════════════════════════════════════════════════════════════
# STATISTIK PAGE
# ═══════════════════════════════════════════════════════════════════

class StatistikPage(QWidget):
    def __init__(self, records=None, parent=None):
        super().__init__(parent)
        self.records = records or []
        self.setStyleSheet(f"background:{BG_SOFT};")
        self._build()

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        container = QWidget()
        container.setStyleSheet(f"background:{BG_SOFT};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(24)

        # Title
        lay.addWidget(_lbl("📊  Statistik Promo", size=22, weight=700, color=TEXT_1))
        lay.addWidget(Divider())

        # Get stats
        if get_statistics and self.records:
            stats = get_statistics(self.records)
        else:
            stats = {
                "top_3_toko": [("Superindo", 12), ("Indomaret", 8), ("Alfamart", 6)],
                "komposisi_kategori": {
                    "Sembako": 35, "Makanan Instan": 28, "Minuman": 20, "Snack": 17
                },
            }

        # Matplotlib global style
        matplotlib.rcParams.update({
            "font.family": "DejaVu Sans",
            "axes.facecolor": BG,
            "figure.facecolor": BG,
            "axes.edgecolor": BORDER,
            "text.color": TEXT_1,
            "axes.labelcolor": TEXT_2,
            "xtick.color": TEXT_2,
            "ytick.color": TEXT_2,
            "axes.spines.top": False,
            "axes.spines.right": False,
        })

        # Dua card chart bersebelahan
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        # ── Bar chart ──────────────────────────────────
        if stats.get("top_3_toko"):
            bc = self._card_wrap("🏪  Top Toko Promo Terbanyak")
            fig = Figure(figsize=(5.2, 3), dpi=80)
            fig.patch.set_facecolor(BG)
            ax  = fig.add_subplot(111)
            ax.set_facecolor(BG)
            toko, jumlah = zip(*stats["top_3_toko"])
            bars = ax.barh(toko, jumlah, color=ACCENT, edgecolor="none", height=0.45)
            ax.set_xlabel("Jumlah Promo", fontsize=9, color=TEXT_2)
            ax.set_xlim(0, max(jumlah) * 1.35)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.tick_params(labelsize=9, colors=TEXT_2)
            for bar, val in zip(bars, jumlah):
                ax.text(
                    bar.get_width() + 0.2,
                    bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=9,
                    fontweight="bold", color=TEXT_1,
                )
            fig.tight_layout(pad=1.2)
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background:transparent;")
            bc.layout().addWidget(canvas)
            charts_row.addWidget(bc)

        # ── Pie chart ──────────────────────────────────
        if stats.get("komposisi_kategori"):
            pc = self._card_wrap("🗂  Komposisi Kategori")
            fig2 = Figure(figsize=(5.2, 3.4), dpi=80)
            fig2.patch.set_facecolor(BG)
            ax2  = fig2.add_subplot(111)
            ax2.set_facecolor(BG)
            labels, sizes = zip(*stats["komposisi_kategori"].items())
            palette = ["#2EA43C", "#5EC472", "#8DD89A", "#B8EABD", "#1D7330"]
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=labels,
                autopct="%1.0f%%",
                colors=palette[:len(labels)],
                startangle=90,
                pctdistance=0.78,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
            )
            for t in texts:
                t.set_fontsize(8); t.set_color(TEXT_1)
            for at in autotexts:
                at.set_fontsize(8); at.set_color("white"); at.set_fontweight("bold")
            fig2.tight_layout(pad=1.2)
            canvas2 = FigureCanvas(fig2)
            canvas2.setStyleSheet("background:transparent;")
            pc.layout().addWidget(canvas2)
            charts_row.addWidget(pc)

        lay.addLayout(charts_row)

        # ── Summary cards ─────────────────────────────
        lay.addWidget(_lbl("Ringkasan", size=15, weight=600, color=TEXT_1))

        sum_row = QHBoxLayout()
        sum_row.setSpacing(16)
        total_promo  = sum(1 for r in self.records if r.get("jenis_harga") == "PROMO")
        total_toko   = len(set(r.get("brand_toko", "") for r in self.records))
        for icon, label, value in [
            ("📦", "Total Produk", str(len(self.records))),
            ("🏷", "Produk Promo", str(total_promo)),
            ("🏪", "Jumlah Toko",  str(total_toko)),
        ]:
            card = QFrame()
            card.setStyleSheet(f"""
                background:{BG}; border:1.5px solid {BORDER};
                border-radius:10px;
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(20, 16, 20, 16)
            cl.setSpacing(3)
            cl.addWidget(_lbl(icon, size=24))
            cl.addWidget(_lbl(value, size=22, weight=700, color=ACCENT))
            cl.addWidget(_lbl(label, size=11, color=TEXT_2))
            sum_row.addWidget(card)

        lay.addLayout(sum_row)
        lay.addStretch()

        scroll.setWidget(container)
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(scroll)

    @staticmethod
    def _card_wrap(title_text: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG}; border:1.5px solid {BORDER}; border-radius:12px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(20, 18, 20, 18)
        cl.setSpacing(12)
        cl.addWidget(_lbl(title_text, size=13, weight=600, color=TEXT_1))
        cl.addWidget(Divider())
        return card


# ═══════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════════

class SettingsPage(QWidget):
    def __init__(self, parent_window=None, parent=None):
        super().__init__(parent)
        self.parent_window       = parent_window
        self._admin_login_cb     = None
        self._refresh_cb         = None
        self.setStyleSheet(f"background:{BG_SOFT};")
        self._build()

    def set_refresh_callback(self, callback):
        self._refresh_cb = callback

    def set_admin_login_callback(self, callback):
        self._admin_login_cb = callback

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")

        container = QWidget()
        container.setStyleSheet(f"background:{BG_SOFT};")
        lay = QVBoxLayout(container)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(16)

        lay.addWidget(_lbl("⚙️  Pengaturan", size=22, weight=700, color=TEXT_1))
        lay.addWidget(Divider())

        # ── Admin ──────────────────────────────────────
        lay.addWidget(self._section_card(
            "🔒  Mode Admin",
            self._admin_body,
        ))

        # ── Tampilan ───────────────────────────────────
        lay.addWidget(self._section_card(
            "🎨  Tampilan",
            self._appearance_body,
        ))

        # ── Data & Sync ────────────────────────────────
        lay.addWidget(self._section_card(
            "☁️  Data & Sinkronisasi",
            self._sync_body,
        ))

        # ── About ──────────────────────────────────────
        lay.addWidget(self._section_card(
            "ℹ️  Tentang Radar Promo",
            self._about_body,
        ))

        lay.addStretch()

        scroll.setWidget(container)
        ml = QVBoxLayout(self)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.addWidget(scroll)

    # ── Content builders ───────────────────────────────────────────

    def _admin_body(self, cl: QVBoxLayout):
        row = QHBoxLayout()
        row.addWidget(
            _lbl("Akses dashboard admin untuk sinkronisasi data promo.",
                 size=12, color=TEXT_2),
            stretch=1,
        )
        self.admin_btn = QPushButton("🔑  Masuk sebagai Admin")
        self.admin_btn.setStyleSheet(f"""
            QPushButton {{
                background:{TEXT_1}; color:white; border:none;
                border-radius:6px; padding:8px 16px;
                font-size:12px; font-weight:600;
            }}
            QPushButton:hover {{ background:#333333; }}
        """)
        self.admin_btn.clicked.connect(self._on_admin)
        row.addWidget(self.admin_btn)
        cl.addLayout(row)

    def _appearance_body(self, cl: QVBoxLayout):
        # Dark mode row
        dm = QHBoxLayout()
        dm_col = QVBoxLayout()
        dm_col.setSpacing(2)
        dm_col.addWidget(_lbl("🌙  Mode Gelap", size=13, color=TEXT_1))
        dm_col.addWidget(_lbl("Aktifkan tampilan gelap", size=11, color=TEXT_3))
        dm.addLayout(dm_col)
        dm.addStretch()
        dark_btn = QPushButton("Aktifkan")
        dark_btn.setStyleSheet(f"""
            QPushButton {{
                background:{BG_SOFT}; color:{TEXT_1};
                border:1.5px solid {BORDER}; border-radius:6px;
                padding:6px 14px; font-size:12px;
            }}
            QPushButton:hover {{ background:{BG_HOVER}; }}
        """)
        dark_btn.clicked.connect(
            lambda: QMessageBox.information(self, "Info", "Dark mode akan segera hadir.")
        )
        dm.addWidget(dark_btn)
        cl.addLayout(dm)

        cl.addWidget(Divider())

        # Font size
        fr = QHBoxLayout()
        fr.addWidget(_lbl("🔤  Ukuran Font", size=13, color=TEXT_1))
        fr.addStretch()
        for size in ["Kecil", "Normal", "Besar"]:
            btn = QPushButton(size)
            active = size == "Normal"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{"" + TEXT_1 if active else BG_SOFT};
                    color:{"white" if active else TEXT_1};
                    border:1.5px solid {BORDER}; border-radius:5px;
                    padding:5px 12px; font-size:11px;
                }}
                QPushButton:hover {{ background:{BG_HOVER}; color:{TEXT_1}; }}
            """)
            btn.clicked.connect(
                lambda _, s=size: QMessageBox.information(self, "Font", f"Ukuran font: {s}")
            )
            fr.addWidget(btn)
        cl.addLayout(fr)

    def _sync_body(self, cl: QVBoxLayout):
        row = QHBoxLayout()
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(_lbl("🔄  Perbarui data rekomendasi", size=13, color=TEXT_1))
        col.addWidget(_lbl("Menarik 100 rekomendasi terbaru dari cloud", size=11, color=TEXT_3))
        row.addLayout(col)
        row.addStretch()
        btn = QPushButton("Refresh Sekarang")
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{ACCENT_LIGHT}; color:{ACCENT_DARK};
                border:1.5px solid {ACCENT}; border-radius:6px;
                padding:7px 14px; font-size:12px; font-weight:600;
            }}
            QPushButton:hover {{ background:{ACCENT}; color:white; }}
        """)
        def _on_refresh():
            if self._refresh_cb:
                self._refresh_cb()
            else:
                QMessageBox.information(self, "Sync", "Fungsi refresh belum dihubungkan.")
        btn.clicked.connect(_on_refresh)
        row.addWidget(btn)
        cl.addLayout(row)

    def _about_body(self, cl: QVBoxLayout):
        for key, val in [
            ("Aplikasi",    "Radar Promo"),
            ("Versi",       "2.0"),
            ("Platform",    "Python 3.10+  ·  PyQt6"),
            ("Target",      "Mahasiswa Polban — Ciwaruga, Sarijadi, Gegerkalong"),
            ("Dibuat oleh", "Tim Radar Promo · D4 TI · Polban"),
        ]:
            row = QHBoxLayout()
            k = _lbl(key, size=12, color=TEXT_2)
            k.setFixedWidth(110)
            row.addWidget(k)
            row.addWidget(_lbl(val, size=12, color=TEXT_1))
            row.addStretch()
            cl.addLayout(row)

    # ── Helper ─────────────────────────────────────────────────────

    def _section_card(self, title_text: str, content_fn) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background:{BG}; border:1.5px solid {BORDER};
                border-radius:10px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(22, 18, 22, 18)
        cl.setSpacing(12)
        cl.addWidget(_lbl(title_text, size=13, weight=600, color=TEXT_1))
        cl.addWidget(Divider())
        content_fn(cl)
        return card

    def _on_admin(self):
        if self._admin_login_cb:
            self._admin_login_cb(self.parent_window)
        else:
            QMessageBox.information(self, "Admin", "Fungsi admin belum terhubung.")


# ═══════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Promo v2.0")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(f"background:{BG};")

        self.db                  = data_manager.read_local_data() if data_manager else []
        self.cart_items: list    = []
        self._admin_login_cb     = None

        self._build()
        if hasattr(self, "settings_page"):
            self.settings_page.set_refresh_callback(self.reload_data)

    def set_admin_login_callback(self, callback):
        self._admin_login_cb = callback
        if hasattr(self, "settings_page"):
            self.settings_page.set_admin_login_callback(callback)

    # ── BUILD ──────────────────────────────────────────────────────

    def reload_data(self):
        try:
            self.db = data_manager.read_local_data() if data_manager else []
            # Update HomePage
            self.home_page.db = self.db
            self.home_page._refresh()
            
            # Recreate StatistikPage
            self.stack.removeWidget(self.stat_page)
            self.stat_page.deleteLater()
            self.stat_page = StatistikPage(records=self.db)
            self.stack.insertWidget(2, self.stat_page)
            
            QMessageBox.information(self, "Berhasil", f"Data berhasil diperbarui! ({len(self.db)} produk dimuat)")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal memperbarui data: {e}")

    def _build(self):
        root = QWidget()
        root.setStyleSheet(f"background:{BG};")
        self.setCentralWidget(root)
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._build_header())

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{BG};")
        lay.addWidget(self.stack, stretch=1)

        # Page 0 — Home
        self.home_page = HomePage(self.db, self._add_to_cart)
        self.stack.addWidget(self.home_page)

        # Page 1 — Jelajah
        self.map_view = QWebEngineView()
        profile = QWebEngineProfile.defaultProfile()
        profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map.html")
        if os.path.exists(map_path):
            self.map_view.load(QUrl.fromLocalFile(map_path))
        else:
            self.map_view.setHtml(self._map_placeholder_html())
        self.stack.addWidget(self.map_view)

        # Page 2 — Statistik
        self.stat_page = StatistikPage(records=self.db)
        self.stack.addWidget(self.stat_page)

        # Page 3 — Pengaturan
        self.settings_page = SettingsPage(parent_window=self)
        if self._admin_login_cb:
            self.settings_page.set_admin_login_callback(self._admin_login_cb)
        self.stack.addWidget(self.settings_page)

        # Bottom nav
        lay.addWidget(self._build_nav())

        self._switch_tab(0)

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(75)
        header.setStyleSheet("background:#FFFFFF; border:none;")
        h = QHBoxLayout(header)
        h.setContentsMargins(40, 10, 40, 10)
        h.setSpacing(20)

        # Logo RP
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0,0,0,0)
        logo_layout.setSpacing(0)
        
        lbl_r = QLabel("R")
        lbl_r.setStyleSheet("color:#3498db; font-size:28px; font-weight:900; font-style:italic;")
        lbl_p = QLabel("P")
        lbl_p.setStyleSheet("color:#3498db; font-size:28px; font-weight:900; font-style:italic;")
        
        logo_layout.addWidget(lbl_r)
        logo_layout.addWidget(lbl_p)
        h.addWidget(logo_container)
        
        h.addStretch(1)

        # Search Bar
        search_container = QWidget()
        search_container.setFixedSize(600, 42)
        search_container.setStyleSheet("""
            QWidget {
                background: #F0F2F5;
                border-radius: 21px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(15, 0, 15, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color:#787774; font-size:16px; background:transparent;")
        search_layout.addWidget(search_icon)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none;
                font-size: 15px; color: #191919;
            }
            QLineEdit::placeholder { color: #8C8C8C; font-weight:500; }
        """)
        self.search_bar.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_bar)
        
        h.addWidget(search_container)
        h.addStretch(1)

        # Cart button
        self.cart_btn = QPushButton("🛒")
        self.cart_btn.setFixedSize(45, 45)
        self.cart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cart_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #191919; border: none; font-size: 26px;
            }
            QPushButton:hover { color: #21C083; }
        """)
        self.cart_btn.clicked.connect(self._show_cart)
        h.addWidget(self.cart_btn)

        return header

    def _build_nav(self) -> QFrame:
        nav = QFrame()
        nav.setFixedHeight(58)
        nav.setStyleSheet(f"""
            QFrame {{ background:{BG}; border-top:1.5px solid {BORDER}; }}
        """)
        h = QHBoxLayout(nav)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self.nav_btns: list[QPushButton] = []
        for icon, label, idx in [
            ("🏠", "Home",        0),
            ("🗺️",  "Jelajah",    1),
            ("📊", "Statistik",   2),
            ("⚙️",  "Pengaturan", 3),
        ]:
            btn = QPushButton(f"{icon}   {label}")
            btn.setFixedHeight(58)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self._switch_tab(i))
            h.addWidget(btn, stretch=1)
            self.nav_btns.append(btn)

        return nav

    def _nav_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background:{ACCENT_LIGHT};
                    color:{ACCENT};
                    border:none;
                    border-top:2.5px solid {ACCENT};
                    font-size:13px; font-weight:700;
                }}
            """
        return f"""
            QPushButton {{
                background:transparent; color:{TEXT_2};
                border:none; font-size:13px;
            }}
            QPushButton:hover {{
                background:{BG_HOVER}; color:{TEXT_1};
            }}
        """

    # ── EVENTS ────────────────────────────────────────────────────

    def _switch_tab(self, idx: int):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_btns):
            btn.setStyleSheet(self._nav_style(i == idx))

    def _on_search(self, text: str):
        self.home_page.set_search(text)
        if self.stack.currentIndex() != 0:
            self._switch_tab(0)

    def _add_to_cart(self, product: dict):
        self.cart_items.append(product)
        n = len(self.cart_items)
        self.cart_btn.setText(f"🛒   Keranjang ({n})")

    def _show_cart(self):
        CartDialog(self.cart_items, parent=self).exec()

    # ── HELPERS ───────────────────────────────────────────────────

    @staticmethod
    def _map_placeholder_html() -> str:
        return f"""
        <html><body style="
            margin:0; background:{BG_SOFT};
            display:flex; align-items:center; justify-content:center;
            height:100vh; font-family:system-ui,-apple-system,sans-serif;">
          <div style="text-align:center; color:{TEXT_2};">
            <div style="font-size:52px; margin-bottom:14px;">🗺️</div>
            <div style="font-size:18px; font-weight:600; color:{TEXT_1};">
              Peta Belum Tersedia
            </div>
            <div style="font-size:13px; margin-top:8px;">
              File <code>map.html</code> tidak ditemukan
            </div>
          </div>
        </body></html>
        """


# ═══════════════════════════════════════════════════════════════════
# UTILITAS
# ═══════════════════════════════════════════════════════════════════

def _lbl(
    text: str,
    size: int = 12,
    weight: int = 400,
    color: str = TEXT_1,
    wrap: bool = False,
) -> QLabel:
    """Factory untuk QLabel dengan style cepat."""
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        color:{color}; font-size:{size}px;
        font-weight:{weight}; background:transparent;
    """)
    if wrap:
        lbl.setWordWrap(True)
    return lbl


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Notion-white global palette
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor(BG))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(TEXT_1))
    pal.setColor(QPalette.ColorRole.Base,            QColor(BG))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(BG_SOFT))
    pal.setColor(QPalette.ColorRole.Text,            QColor(TEXT_1))
    pal.setColor(QPalette.ColorRole.Button,          QColor(BG))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(TEXT_1))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(ACCENT))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())