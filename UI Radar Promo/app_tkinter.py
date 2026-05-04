"""
Radar Promo - Aplikasi Desktop Tkinter
Versi lengkap dengan semua fitur
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import threading
import urllib.request
from PIL import Image, ImageTk, ImageDraw, ImageFilter
from io import BytesIO
from datetime import datetime
from data import PRODUCTS

# ─── THEME ────────────────────────────────────────────────────────────────────

LIGHT = {
    "bg":               "#faf9f7",
    "nav_bg":           "#ffffff",
    "nav_border":       "#e5e7eb",
    "banner_from":      "#6F84B8",
    "banner_to":        "#F1C0CC",
    "filter_bg":        "#ffffff",
    "filter_border":    "#e5e7eb",
    "pill_inactive_bg": "#f5f4f2",
    "pill_inactive_fg": "#374151",
    "pill_active_bg":   "#6F84B8",
    "pill_active_fg":   "#ffffff",
    "card_bg":          "#ffffff",
    "card_border":      "#e5e7eb",
    "card_img_bg":      "#f3f4f6",
    "price_fg":         "#6F84B8",
    "store_fg":         "#6b7280",
    "dist_fg":          "#6F84B8",
    "add_btn_bg":       "#F1C0CC",
    "add_btn_fg":       "#ffffff",
    "add_btn_hover":    "#e8aabb",
    "text_primary":     "#111827",
    "text_secondary":   "#6b7280",
    "badge_bg":         "#fce7eb",
    "badge_fg":         "#d89aaa",
    "search_bg":        "#f5f4f2",
    "search_border":    "#d1d5db",
    "search_fg":        "#111827",
    "search_placeholder": "#9ca3af",
    "scrollbar_bg":     "#e5e7eb",
    "scrollbar_thumb":  "#9ca3af",
    "cart_bg":          "#ffffff",
    "cart_card_bg":     "#f9fafb",
    "cart_item_bg":     "#f5f4f2",
    "budget_bg":        "#e8edf7",
    "budget_border":    "#c5cfe8",
    "total_bg":         "#f5f4f2",
    "remain_bg":        "#e8edf7",
    "remain_fg":        "#6F84B8",
    "remain_over_bg":   "#fee2e2",
    "remain_over_fg":   "#ef4444",
    "progress_bg":      "#e5e7eb",
    "progress_fill":    "#6F84B8",
    "divider":          "#e5e7eb",
    "btn_bg":           "#f5f4f2",
    "btn_fg":           "#374151",
    "btn_border":       "#e5e7eb",
    "sort_active_bg":   "#6F84B8",
    "sort_active_fg":   "#ffffff",
    "empty_fg":         "#9ca3af",
    "toast_bg":         "#6F84B8",
    "toast_fg":         "#ffffff",
}

DARK = {
    "bg":               "#1a1b2e",
    "nav_bg":           "#25264a",
    "nav_border":       "#374151",
    "banner_from":      "#5a6a94",
    "banner_to":        "#d4a5b3",
    "filter_bg":        "#25264a",
    "filter_border":    "#374151",
    "pill_inactive_bg": "#2d2f4d",
    "pill_inactive_fg": "#e5e7eb",
    "pill_active_bg":   "#6F84B8",
    "pill_active_fg":   "#ffffff",
    "card_bg":          "#25264a",
    "card_border":      "#374151",
    "card_img_bg":      "#2d2f4d",
    "price_fg":         "#8fa1cc",
    "store_fg":         "#9ca3af",
    "dist_fg":          "#8fa1cc",
    "add_btn_bg":       "#F1C0CC",
    "add_btn_fg":       "#ffffff",
    "add_btn_hover":    "#e8aabb",
    "text_primary":     "#f9fafb",
    "text_secondary":   "#9ca3af",
    "badge_bg":         "#3d2535",
    "badge_fg":         "#f5d4de",
    "search_bg":        "#2d2f4d",
    "search_border":    "#4b5563",
    "search_fg":        "#f9fafb",
    "search_placeholder": "#6b7280",
    "scrollbar_bg":     "#2d2f4d",
    "scrollbar_thumb":  "#4b5563",
    "cart_bg":          "#1a1b2e",
    "cart_card_bg":     "#25264a",
    "cart_item_bg":     "#2d2f4d",
    "budget_bg":        "#2d2f4d",
    "budget_border":    "#4a5a7a",
    "total_bg":         "#2d2f4d",
    "remain_bg":        "#2d2f4d",
    "remain_fg":        "#8fa1cc",
    "remain_over_bg":   "#3b1515",
    "remain_over_fg":   "#f87171",
    "progress_bg":      "#374151",
    "progress_fill":    "#6F84B8",
    "divider":          "#374151",
    "btn_bg":           "#2d2f4d",
    "btn_fg":           "#e5e7eb",
    "btn_border":       "#374151",
    "sort_active_bg":   "#6F84B8",
    "sort_active_fg":   "#ffffff",
    "empty_fg":         "#6b7280",
    "toast_bg":         "#6F84B8",
    "toast_fg":         "#ffffff",
}

CATEGORIES = ["Semua", "Sembako", "Makanan Instan", "Mandi", "Kesehatan", "Snack"]

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp_color(c1, c2, t):
    r = int(c1[0] + (c2[0]-c1[0])*t)
    g = int(c1[1] + (c2[1]-c1[1])*t)
    b = int(c1[2] + (c2[2]-c1[2])*t)
    return f"#{r:02x}{g:02x}{b:02x}"

def format_rp(amount):
    return "Rp " + f"{int(amount):,}".replace(",", ".")

def make_rounded_image(img, radius=16):
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0,0), img.size], radius=radius, fill=255)
    img.putalpha(mask)
    return img

def make_gradient_image(w, h, color1, color2):
    img = Image.new("RGB", (w, h))
    c1 = hex_to_rgb(color1)
    c2 = hex_to_rgb(color2)
    for x in range(w):
        t = x / max(w-1, 1)
        col = lerp_color(c1, c2, t)
        r, g, b = hex_to_rgb(col)
        for y in range(h):
            img.putpixel((x, y), (r, g, b))
    return img

# ─── IMAGE LOADER ─────────────────────────────────────────────────────────────

_image_cache = {}
_image_cache_lock = threading.Lock()

def load_image_async(url, product_id, size, callback):
    def _load():
        with _image_cache_lock:
            if product_id in _image_cache:
                callback(product_id, _image_cache[product_id])
                return
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                data = r.read()
            img = Image.open(BytesIO(data)).convert("RGB")
            # Crop to square
            w, h = img.size
            s = min(w, h)
            left = (w - s)//2
            top = (h - s)//2
            img = img.crop((left, top, left+s, top+s))
            img = img.resize(size, Image.LANCZOS)
            img = make_rounded_image(img, radius=14)
            photo = ImageTk.PhotoImage(img)
            with _image_cache_lock:
                _image_cache[product_id] = photo
            callback(product_id, photo)
        except Exception:
            callback(product_id, None)
    threading.Thread(target=_load, daemon=True).start()

# ─── SCROLLABLE FRAME ─────────────────────────────────────────────────────────

class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_inner_configure(self, e):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self.canvas.itemconfig(self.inner_id, width=e.width)

    def _on_mousewheel(self, e):
        if e.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif e.num == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")

    def update_bg(self, bg):
        self.configure(bg=bg)
        self.canvas.configure(bg=bg)
        self.inner.configure(bg=bg)

# ─── TOAST NOTIFICATION ───────────────────────────────────────────────────────

class Toast:
    def __init__(self, root):
        self.root = root
        self._win = None

    def show(self, message, t):
        if self._win:
            try: self._win.destroy()
            except: pass
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=t["toast_bg"])
        lbl = tk.Label(win, text=message, bg=t["toast_bg"], fg=t["toast_fg"],
                       font=("Arial", 11, "bold"), padx=18, pady=10)
        lbl.pack()
        # Position bottom-right
        self.root.update_idletasks()
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        win.update_idletasks()
        ww = win.winfo_reqwidth()
        wh = win.winfo_reqheight()
        x = rx + rw - ww - 24
        y = ry + rh - wh - 48
        win.geometry(f"+{x}+{y}")
        self._win = win
        self.root.after(2500, self._dismiss)

    def _dismiss(self):
        try:
            if self._win:
                self._win.destroy()
                self._win = None
        except: pass

# ─── PRODUCT CARD ─────────────────────────────────────────────────────────────

CARD_W = 240
CARD_IMG_H = 180
CARD_H = 340

class ProductCard(tk.Frame):
    def __init__(self, parent, product, t, on_add, **kwargs):
        super().__init__(parent, bg=t["card_bg"],
                         highlightbackground=t["card_border"],
                         highlightthickness=1,
                         **kwargs)
        self.product = product
        self.t = t
        self.on_add = on_add
        self._photo = None
        self._build()
        self._load_image()

    def _build(self):
        t = self.t
        self.configure(width=CARD_W, height=CARD_H, cursor="hand2")
        self.pack_propagate(False)

        # Image area
        self.img_frame = tk.Frame(self, bg=t["card_img_bg"],
                                  width=CARD_W, height=CARD_IMG_H)
        self.img_frame.pack(fill="x")
        self.img_frame.pack_propagate(False)
        self.img_label = tk.Label(self.img_frame, bg=t["card_img_bg"],
                                  text="⏳", font=("Arial", 22))
        self.img_label.place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info = tk.Frame(self, bg=t["card_bg"])
        info.pack(fill="both", expand=True, padx=12, pady=(8,10))

        # Badge
        badge_row = tk.Frame(info, bg=t["card_bg"])
        badge_row.pack(anchor="w")
        badge = tk.Label(badge_row, text=self.product["category"],
                         bg=t["badge_bg"], fg=t["badge_fg"],
                         font=("Arial", 9), padx=8, pady=2)
        badge.pack(anchor="w")

        # Name
        tk.Label(info, text=self.product["name"], bg=t["card_bg"],
                 fg=t["text_primary"], font=("Arial", 11, "bold"),
                 wraplength=CARD_W-24, justify="left", anchor="w"
                 ).pack(anchor="w", pady=(4,2))

        # Price
        tk.Label(info, text=format_rp(self.product["price"]),
                 bg=t["card_bg"], fg=t["price_fg"],
                 font=("Arial", 13, "bold")
                 ).pack(anchor="w")

        # Store + button row
        bottom = tk.Frame(info, bg=t["card_bg"])
        bottom.pack(fill="x", pady=(6,0))

        store_col = tk.Frame(bottom, bg=t["card_bg"])
        store_col.pack(side="left")
        tk.Label(store_col, text=self.product["store"], bg=t["card_bg"],
                 fg=t["store_fg"], font=("Arial", 10)).pack(anchor="w")
        tk.Label(store_col, text=f"📍 {self.product['distance']}", bg=t["card_bg"],
                 fg=t["dist_fg"], font=("Arial", 9)).pack(anchor="w")

        self.add_btn = tk.Label(bottom, text="+ Tambah",
                                bg=t["add_btn_bg"], fg=t["add_btn_fg"],
                                font=("Arial", 10, "bold"),
                                padx=12, pady=5, cursor="hand2")
        self.add_btn.pack(side="right")
        self.add_btn.bind("<Button-1>", lambda e: self.on_add(self.product))
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.config(bg=t["add_btn_hover"]))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.config(bg=t["add_btn_bg"]))

    def _load_image(self):
        pid = self.product["id"]
        def _cb(pid, photo):
            if not self.winfo_exists():
                return
            self._photo = photo
            if photo:
                self.img_label.config(image=photo, text="", bg=self.t["card_img_bg"])
            else:
                self.img_label.config(text="🖼️", font=("Arial", 22))
        load_image_async(self.product["image"], pid, (CARD_W, CARD_IMG_H), _cb)

    def update_theme(self, t):
        self.t = t
        self.configure(bg=t["card_bg"], highlightbackground=t["card_border"])
        self.img_frame.configure(bg=t["card_img_bg"])
        self.img_label.configure(bg=t["card_img_bg"])
        # Rebuild faster - just destroy and recreate is simpler
        for w in self.winfo_children():
            if w != self.img_frame:
                w.destroy()
        # Partial re-theme (shortcuts)
        self._build_info_only(t)

    def _build_info_only(self, t):
        info = tk.Frame(self, bg=t["card_bg"])
        info.pack(fill="both", expand=True, padx=12, pady=(8,10))
        badge_row = tk.Frame(info, bg=t["card_bg"])
        badge_row.pack(anchor="w")
        tk.Label(badge_row, text=self.product["category"],
                 bg=t["badge_bg"], fg=t["badge_fg"],
                 font=("Arial", 9), padx=8, pady=2).pack(anchor="w")
        tk.Label(info, text=self.product["name"], bg=t["card_bg"],
                 fg=t["text_primary"], font=("Arial", 11, "bold"),
                 wraplength=CARD_W-24, justify="left", anchor="w").pack(anchor="w", pady=(4,2))
        tk.Label(info, text=format_rp(self.product["price"]),
                 bg=t["card_bg"], fg=t["price_fg"],
                 font=("Arial", 13, "bold")).pack(anchor="w")
        bottom = tk.Frame(info, bg=t["card_bg"])
        bottom.pack(fill="x", pady=(6,0))
        store_col = tk.Frame(bottom, bg=t["card_bg"])
        store_col.pack(side="left")
        tk.Label(store_col, text=self.product["store"], bg=t["card_bg"],
                 fg=t["store_fg"], font=("Arial", 10)).pack(anchor="w")
        tk.Label(store_col, text=f"📍 {self.product['distance']}", bg=t["card_bg"],
                 fg=t["dist_fg"], font=("Arial", 9)).pack(anchor="w")
        add_btn = tk.Label(bottom, text="+ Tambah",
                           bg=t["add_btn_bg"], fg=t["add_btn_fg"],
                           font=("Arial", 10, "bold"),
                           padx=12, pady=5, cursor="hand2")
        add_btn.pack(side="right")
        add_btn.bind("<Button-1>", lambda e: self.on_add(self.product))
        add_btn.bind("<Enter>", lambda e: add_btn.config(bg=t["add_btn_hover"]))
        add_btn.bind("<Leave>", lambda e: add_btn.config(bg=t["add_btn_bg"]))

# ─── BANNER ───────────────────────────────────────────────────────────────────

class BannerWidget(tk.Canvas):
    def __init__(self, parent, t, **kwargs):
        super().__init__(parent, height=160, highlightthickness=0, bd=0, **kwargs)
        self.t = t
        self._gradient_img = None
        self.bind("<Configure>", self._draw)
        self._draw()

    def _draw(self, e=None):
        w = self.winfo_width() or 1280
        h = 160
        img = make_gradient_image(w, h, self.t["banner_from"], self.t["banner_to"])
        self._gradient_img = ImageTk.PhotoImage(img)
        self.delete("all")
        self.create_image(0, 0, image=self._gradient_img, anchor="nw")
        self.create_text(48, 56, text="Promo Terbaru untuk Mahasiswa",
                         anchor="w", fill="white",
                         font=("Arial", 28, "bold"))
        self.create_text(48, 100, text="Hemat lebih banyak dengan promo terbaik dari supermarket terdekat",
                         anchor="w", fill="#e8edf5",
                         font=("Arial", 13))

    def update_theme(self, t):
        self.t = t
        self._draw()

# ─── CART PAGE ────────────────────────────────────────────────────────────────

class CartPage(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.budget = 100000
        self._build()

    def _build(self):
        self.configure(bg=self.app.t["cart_bg"])

        # Scroll container
        self.scroll = ScrollableFrame(self, bg=self.app.t["cart_bg"])
        self.scroll.pack(fill="both", expand=True)
        inner = self.scroll.inner

        # Back button
        back_row = tk.Frame(inner, bg=self.app.t["cart_bg"])
        back_row.pack(fill="x", padx=32, pady=(20, 10))
        self.back_btn = tk.Label(back_row, text="← Kembali ke Beranda",
                                  bg=self.app.t["btn_bg"], fg=self.app.t["btn_fg"],
                                  font=("Arial", 11), padx=14, pady=7, cursor="hand2",
                                  relief="flat")
        self.back_btn.pack(anchor="w")
        self.back_btn.bind("<Button-1>", lambda e: self.app.show_home())
        self.back_btn.bind("<Enter>", lambda e: self.back_btn.config(bg=self.app.t["cart_item_bg"]))
        self.back_btn.bind("<Leave>", lambda e: self.back_btn.config(bg=self.app.t["btn_bg"]))

        # Card
        self.card = tk.Frame(inner, bg=self.app.t["cart_card_bg"],
                             highlightbackground=self.app.t["card_border"],
                             highlightthickness=1)
        self.card.pack(fill="x", padx=32, pady=(0, 24))
        self._build_card_contents()

    def _build_card_contents(self):
        for w in self.card.winfo_children():
            w.destroy()
        t = self.app.t

        # Title
        tk.Label(self.card, text="Keranjang Belanja",
                 bg=t["cart_card_bg"], fg=t["price_fg"],
                 font=("Arial", 20, "bold")).pack(anchor="w", padx=28, pady=(22, 12))

        # Items
        self.items_frame = tk.Frame(self.card, bg=t["cart_card_bg"])
        self.items_frame.pack(fill="x", padx=20, pady=(0, 12))

        cart_items = self.app.cart_items
        if not cart_items:
            tk.Label(self.items_frame,
                     text="🛒\nKeranjang kamu masih kosong\nMulai tambahkan produk dari halaman utama",
                     bg=t["cart_card_bg"], fg=t["text_secondary"],
                     font=("Arial", 12), justify="center").pack(pady=30)
        else:
            for ci in cart_items:
                self._build_cart_item(ci)

        # Divider
        divider = tk.Frame(self.card, bg=t["divider"], height=1)
        divider.pack(fill="x", padx=20, pady=8)

        # Budget box
        budget_box = tk.Frame(self.card, bg=t["budget_bg"],
                              highlightbackground=t["budget_border"], highlightthickness=1)
        budget_box.pack(fill="x", padx=20, pady=(4, 8))

        budget_top = tk.Frame(budget_box, bg=t["budget_bg"])
        budget_top.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(budget_top, text="Anggaran", bg=t["budget_bg"],
                 fg=t["text_primary"], font=("Arial", 12, "bold")).pack(side="left")
        self.budget_val_lbl = tk.Label(budget_top, text=format_rp(self.budget),
                                       bg=t["budget_bg"], fg=t["text_primary"],
                                       font=("Arial", 13, "bold"))
        self.budget_val_lbl.pack(side="right", padx=(0, 4))
        edit_btn = tk.Label(budget_top, text="✏️", bg=t["budget_bg"],
                            cursor="hand2", font=("Arial", 12))
        edit_btn.pack(side="right")
        edit_btn.bind("<Button-1>", lambda e: self._edit_budget())

        # Progress bar
        prog_bg = tk.Canvas(budget_box, height=10, bg=t["progress_bg"],
                            highlightthickness=0, bd=0)
        prog_bg.pack(fill="x", padx=14, pady=(0, 4))
        prog_bg.bind("<Configure>", lambda e: self._draw_progress(prog_bg))
        self._prog_canvas = prog_bg
        self._draw_progress(prog_bg)

        self.pct_lbl = tk.Label(budget_box, text="", bg=t["budget_bg"],
                                fg=t["text_secondary"], font=("Arial", 9))
        self.pct_lbl.pack(pady=(0, 10))
        self._update_pct_label()

        # Total
        total_box = tk.Frame(self.card, bg=t["total_bg"],
                             highlightbackground=t["card_border"], highlightthickness=1)
        total_box.pack(fill="x", padx=20, pady=4)
        total_inner = tk.Frame(total_box, bg=t["total_bg"])
        total_inner.pack(fill="x", padx=14, pady=10)
        tk.Label(total_inner, text="Total", bg=t["total_bg"],
                 fg=t["text_primary"], font=("Arial", 12, "bold")).pack(side="left")
        total = sum(ci["product"]["price"] * ci["quantity"] for ci in self.app.cart_items)
        self.total_lbl = tk.Label(total_inner, text=format_rp(total),
                                  bg=t["total_bg"], fg=t["text_primary"],
                                  font=("Arial", 14, "bold"))
        self.total_lbl.pack(side="right")

        # Remaining
        total = sum(ci["product"]["price"] * ci["quantity"] for ci in self.app.cart_items)
        remaining = self.budget - total
        over = remaining < 0
        rem_bg = t["remain_over_bg"] if over else t["remain_bg"]
        rem_fg = t["remain_over_fg"] if over else t["remain_fg"]

        remain_box = tk.Frame(self.card, bg=rem_bg,
                              highlightbackground=t["budget_border"], highlightthickness=1)
        remain_box.pack(fill="x", padx=20, pady=(4, 20))
        remain_inner = tk.Frame(remain_box, bg=rem_bg)
        remain_inner.pack(fill="x", padx=14, pady=12)
        tk.Label(remain_inner, text="Sisa Anggaran", bg=rem_bg,
                 fg=t["text_primary"], font=("Arial", 11)).pack(anchor="w")
        tk.Label(remain_inner, text=format_rp(remaining), bg=rem_bg,
                 fg=rem_fg, font=("Arial", 20, "bold")).pack(anchor="w", pady=(4, 0))

        if over:
            tk.Label(remain_inner,
                     text="⚠️ Anggaran tidak cukup! Kurangi beberapa item.",
                     bg=rem_bg, fg=rem_fg, font=("Arial", 10)).pack(anchor="w", pady=(4, 0))

    def _build_cart_item(self, ci):
        t = self.app.t
        p = ci["product"]
        q = ci["quantity"]

        row = tk.Frame(self.items_frame, bg=t["cart_item_bg"],
                       highlightbackground=t["card_border"], highlightthickness=1)
        row.pack(fill="x", pady=4)
        inner = tk.Frame(row, bg=t["cart_item_bg"])
        inner.pack(fill="x", padx=12, pady=10)

        # Icon placeholder
        tk.Label(inner, text="🛒", bg=t["cart_item_bg"],
                 font=("Arial", 22), width=3).pack(side="left")

        info_frame = tk.Frame(inner, bg=t["cart_item_bg"])
        info_frame.pack(side="left", padx=10, fill="x", expand=True)
        tk.Label(info_frame, text=p["name"], bg=t["cart_item_bg"],
                 fg=t["text_primary"], font=("Arial", 11, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(info_frame, text=p["store"], bg=t["cart_item_bg"],
                 fg=t["text_secondary"], font=("Arial", 9),
                 anchor="w").pack(anchor="w")

        right = tk.Frame(inner, bg=t["cart_item_bg"])
        right.pack(side="right")
        total_price = p["price"] * q
        tk.Label(right, text=format_rp(total_price), bg=t["cart_item_bg"],
                 fg=t["price_fg"], font=("Arial", 12, "bold")).pack(anchor="e")
        tk.Label(right, text=f"{q} x {format_rp(p['price'])}", bg=t["cart_item_bg"],
                 fg=t["text_secondary"], font=("Arial", 9)).pack(anchor="e")

        del_btn = tk.Label(inner, text="🗑️", bg=t["cart_item_bg"],
                           font=("Arial", 15), cursor="hand2")
        del_btn.pack(side="right", padx=(8, 0))
        del_btn.bind("<Button-1>", lambda e, pid=p["id"]: self._remove_item(pid))
        del_btn.bind("<Enter>", lambda e: del_btn.config(bg="#fee2e2"))
        del_btn.bind("<Leave>", lambda e: del_btn.config(bg=t["cart_item_bg"]))

    def _remove_item(self, product_id):
        self.app.cart_items = [ci for ci in self.app.cart_items
                               if ci["product"]["id"] != product_id]
        self.app.update_cart_badge()
        self._build_card_contents()

    def _edit_budget(self):
        val = simpledialog.askinteger("Set Anggaran",
                                     "Masukkan anggaran kamu (Rp):",
                                     initialvalue=self.budget,
                                     minvalue=0, parent=self.app.root)
        if val is not None:
            self.budget = val
            self._build_card_contents()

    def _draw_progress(self, canvas):
        canvas.update_idletasks()
        w = canvas.winfo_width()
        h = 10
        if w < 2:
            return
        canvas.delete("all")
        t = self.app.t
        total = sum(ci["product"]["price"] * ci["quantity"] for ci in self.app.cart_items)
        pct = min(total / self.budget, 1.0) if self.budget > 0 else 0
        canvas.create_rectangle(0, 0, w, h, fill=t["progress_bg"], outline="")
        fill_w = int(w * pct)
        if fill_w > 0:
            color = "#6F84B8" if pct < 0.7 else "#F1C0CC" if pct < 0.9 else "#e8a5b5"
            canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="")

    def _update_pct_label(self):
        total = sum(ci["product"]["price"] * ci["quantity"] for ci in self.app.cart_items)
        pct = min(int((total / self.budget) * 100), 100) if self.budget > 0 else 0
        self.pct_lbl.config(text=f"{pct}% dari anggaran terpakai")

    def update_theme(self, t):
        self.scroll.update_bg(t["cart_bg"])
        self.configure(bg=t["cart_bg"])
        self._build_card_contents()

# ─── MAIN APP ─────────────────────────────────────────────────────────────────

class RadarPromoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Radar Promo")
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)

        self.is_dark = False
        self.t = LIGHT
        self.selected_category = "Semua"
        self.sort_option = "termurah"
        self.cart_items = []
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.last_sync = datetime.now()
        self.toast = Toast(self.root)
        self._card_refs = []

        self._build()
        self._apply_theme()
        self._load_products()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        self.root.configure(bg=self.t["bg"])

        # Main vertical layout
        self.main_frame = tk.Frame(self.root, bg=self.t["bg"])
        self.main_frame.pack(fill="both", expand=True)

        self._build_navbar()
        self._build_pages()

    def _build_navbar(self):
        self.navbar = tk.Frame(self.main_frame, bg=self.t["nav_bg"], height=64)
        self.navbar.pack(fill="x")
        self.navbar.pack_propagate(False)

        # Bottom border
        self.nav_border_line = tk.Frame(self.main_frame, bg=self.t["nav_border"], height=1)
        self.nav_border_line.pack(fill="x")

        inner = tk.Frame(self.navbar, bg=self.t["nav_bg"])
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Logo
        logo_frame = tk.Frame(inner, bg=self.t["nav_bg"], cursor="hand2")
        logo_frame.pack(side="left", padx=(28, 16))
        tk.Label(logo_frame, text="📡", bg=self.t["nav_bg"],
                 font=("Arial", 20)).pack(side="left")
        self.logo_lbl = tk.Label(logo_frame, text="Radar Promo",
                                 bg=self.t["nav_bg"], fg="#F1C0CC",
                                 font=("Arial", 18, "bold"), cursor="hand2")
        self.logo_lbl.pack(side="left", padx=(6, 0))
        logo_frame.bind("<Button-1>", lambda e: self.show_home())
        self.logo_lbl.bind("<Button-1>", lambda e: self.show_home())

        # Right controls frame
        right_frame = tk.Frame(inner, bg=self.t["nav_bg"])
        right_frame.pack(side="right", padx=28)

        # Cart button
        cart_frame = tk.Frame(right_frame, bg=self.t["nav_bg"])
        cart_frame.pack(side="right", padx=(6, 0))
        self.cart_btn = tk.Label(cart_frame, text="🛒",
                                  bg=self.t["btn_bg"], fg=self.t["btn_fg"],
                                  font=("Arial", 16), width=3, pady=6,
                                  cursor="hand2", relief="flat")
        self.cart_btn.pack(side="left")
        self.cart_btn.bind("<Button-1>", lambda e: self.show_cart())
        self.cart_badge_lbl = tk.Label(cart_frame, text="",
                                        bg="#F1C0CC", fg="white",
                                        font=("Arial", 8, "bold"),
                                        width=2, height=1)
        self.cart_badge_lbl.pack_forget()

        # Dark mode toggle
        self.dark_btn = tk.Label(right_frame, text="🌙",
                                  bg=self.t["btn_bg"], fg=self.t["btn_fg"],
                                  font=("Arial", 16), width=3, pady=6,
                                  cursor="hand2", relief="flat")
        self.dark_btn.pack(side="right", padx=(6, 0))
        self.dark_btn.bind("<Button-1>", lambda e: self._toggle_dark())

        # Sync button
        self.sync_btn = tk.Label(right_frame,
                                  bg=self.t["btn_bg"], fg=self.t["btn_fg"],
                                  font=("Arial", 10), pady=6, padx=12,
                                  cursor="hand2", relief="flat")
        self.sync_btn.pack(side="right", padx=(6, 0))
        self.sync_btn.bind("<Button-1>", lambda e: self._sync())
        self._update_sync_label()

        # Search bar (center)
        search_frame = tk.Frame(inner, bg=self.t["nav_bg"])
        search_frame.pack(side="left", fill="x", expand=True, padx=16)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     bg=self.t["search_bg"], fg=self.t["search_fg"],
                                     insertbackground=self.t["search_fg"],
                                     font=("Arial", 12), relief="flat",
                                     highlightbackground=self.t["search_border"],
                                     highlightthickness=1, bd=0)
        self.search_entry.pack(fill="x", ipady=8, padx=4)
        self._set_placeholder()

    def _set_placeholder(self):
        if not self.search_var.get():
            self.search_entry.config(fg=self.t["search_placeholder"])
            self.search_entry.insert(0, "Cari promo yang kamu inginkan...")
            self.search_entry.bind("<FocusIn>", self._clear_placeholder)
            self.search_entry.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, e):
        if self.search_entry.get() == "Cari promo yang kamu inginkan...":
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=self.t["search_fg"])

    def _restore_placeholder(self, e):
        if not self.search_entry.get():
            self.search_entry.config(fg=self.t["search_placeholder"])
            self.search_entry.insert(0, "Cari promo yang kamu inginkan...")

    def _build_pages(self):
        # Page container
        self.page_frame = tk.Frame(self.main_frame, bg=self.t["bg"])
        self.page_frame.pack(fill="both", expand=True)

        self._build_home_page()
        self._build_cart_page()
        self.show_home()

    def _build_home_page(self):
        self.home_page = tk.Frame(self.page_frame, bg=self.t["bg"])

        # Banner
        self.banner = BannerWidget(self.home_page, self.t, bg=self.t["banner_from"])
        self.banner.pack(fill="x")

        # Filter bar
        self._build_filter_bar()

        # Product scroll area
        self.product_scroll = ScrollableFrame(self.home_page, bg=self.t["bg"])
        self.product_scroll.pack(fill="both", expand=True)

        # Grid inside scroll
        self.product_grid = tk.Frame(self.product_scroll.inner, bg=self.t["bg"])
        self.product_grid.pack(fill="x", padx=32, pady=20)

    def _build_filter_bar(self):
        self.filter_bar = tk.Frame(self.home_page, bg=self.t["filter_bg"], height=56)
        self.filter_bar.pack(fill="x")
        self.filter_bar.pack_propagate(False)

        self.filter_border_line = tk.Frame(self.home_page, bg=self.t["filter_border"], height=1)
        self.filter_border_line.pack(fill="x")

        inner = tk.Frame(self.filter_bar, bg=self.t["filter_bg"])
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Category pills
        self.cat_btns = {}
        cats_frame = tk.Frame(inner, bg=self.t["filter_bg"])
        cats_frame.pack(side="left", padx=28, pady=10)

        for cat in CATEGORIES:
            btn = tk.Label(cats_frame, text=cat,
                           font=("Arial", 10), padx=14, pady=5,
                           cursor="hand2")
            btn.pack(side="left", padx=3)
            btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
            self.cat_btns[cat] = btn

        # Sort buttons
        sort_frame = tk.Frame(inner, bg=self.t["filter_bg"])
        sort_frame.pack(side="right", padx=28, pady=10)

        self.sort_cheap_btn = tk.Label(sort_frame, text="↑ Termurah",
                                        font=("Arial", 10), padx=14, pady=5,
                                        cursor="hand2")
        self.sort_cheap_btn.pack(side="left", padx=3)
        self.sort_cheap_btn.bind("<Button-1>", lambda e: self._set_sort("termurah"))

        self.sort_exp_btn = tk.Label(sort_frame, text="↓ Termahal",
                                      font=("Arial", 10), padx=14, pady=5,
                                      cursor="hand2")
        self.sort_exp_btn.pack(side="left", padx=3)
        self.sort_exp_btn.bind("<Button-1>", lambda e: self._set_sort("termahal"))

        self._update_filter_styles()
        self._update_sort_styles()

    def _build_cart_page(self):
        self.cart_page = CartPage(self.page_frame, self, bg=self.t["cart_bg"])

    # ── Navigation ────────────────────────────────────────────────────────────

    def show_home(self):
        self.cart_page.pack_forget()
        self.home_page.pack(fill="both", expand=True)

    def show_cart(self):
        self.home_page.pack_forget()
        self.cart_page.pack_forget()
        self.cart_page = CartPage(self.page_frame, self, bg=self.t["cart_bg"])
        self.cart_page.pack(fill="both", expand=True)

    # ── Products ──────────────────────────────────────────────────────────────

    def _get_filtered_products(self):
        search = self.search_var.get().strip().lower()
        if search == "cari promo yang kamu inginkan...":
            search = ""
        prods = PRODUCTS
        if self.selected_category != "Semua":
            prods = [p for p in prods if p["category"] == self.selected_category]
        if search:
            prods = [p for p in prods if
                     search in p["name"].lower() or
                     search in p["category"].lower() or
                     search in p["store"].lower()]
        if self.sort_option == "termurah":
            prods = sorted(prods, key=lambda p: p["price"])
        else:
            prods = sorted(prods, key=lambda p: p["price"], reverse=True)
        return prods

    def _load_products(self):
        for w in self.product_grid.winfo_children():
            w.destroy()
        self._card_refs.clear()

        prods = self._get_filtered_products()
        COLS = 4

        if not prods:
            tk.Label(self.product_grid,
                     text="😢  Produk tidak ditemukan\nCoba kata kunci lain",
                     bg=self.t["bg"], fg=self.t["empty_fg"],
                     font=("Arial", 16), justify="center").pack(pady=60)
            return

        for i, p in enumerate(prods):
            row, col = divmod(i, COLS)
            card = ProductCard(self.product_grid, p, self.t, self._add_to_cart)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nw")
            self._card_refs.append(card)

        for c in range(COLS):
            self.product_grid.columnconfigure(c, weight=1)

    def _add_to_cart(self, product):
        for ci in self.cart_items:
            if ci["product"]["id"] == product["id"]:
                ci["quantity"] += 1
                self.update_cart_badge()
                self.toast.show(f"✓ {product['name']} ditambahkan!", self.t)
                return
        self.cart_items.append({"product": product, "quantity": 1})
        self.update_cart_badge()
        self.toast.show(f"✓ {product['name']} ditambahkan!", self.t)

    def update_cart_badge(self):
        total = sum(ci["quantity"] for ci in self.cart_items)
        if total > 0:
            self.cart_badge_lbl.config(text=str(total))
            self.cart_badge_lbl.pack(side="left")
        else:
            self.cart_badge_lbl.pack_forget()

    # ── Category / Sort ───────────────────────────────────────────────────────

    def _select_category(self, cat):
        self.selected_category = cat
        self._update_filter_styles()
        self._load_products()

    def _set_sort(self, option):
        self.sort_option = option
        self._update_sort_styles()
        self._load_products()

    def _on_search_change(self, *args):
        query = self.search_var.get()
        if query != "Cari promo yang kamu inginkan...":
            self._load_products()

    # ── Sync & Dark Mode ──────────────────────────────────────────────────────

    def _sync(self):
        self.last_sync = datetime.now()
        self._update_sync_label()
        self.toast.show("✓ Data promo berhasil diperbarui!", self.t)

    def _update_sync_label(self):
        time_str = self.last_sync.strftime("%H:%M")
        self.sync_btn.config(text=f"🔄  Diperbarui: {time_str}")

    def _toggle_dark(self):
        self.is_dark = not self.is_dark
        self.t = DARK if self.is_dark else LIGHT
        self.dark_btn.config(text="☀️" if self.is_dark else "🌙")
        self._apply_theme()
        self._load_products()

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        t = self.t
        self.root.configure(bg=t["bg"])
        self.main_frame.configure(bg=t["bg"])
        self.page_frame.configure(bg=t["bg"])
        self.home_page.configure(bg=t["bg"])

        # Navbar
        self.navbar.configure(bg=t["nav_bg"])
        self.nav_border_line.configure(bg=t["nav_border"])
        for w in self._all_navbar_widgets(self.navbar):
            if isinstance(w, tk.Frame):
                w.configure(bg=t["nav_bg"])
            elif isinstance(w, tk.Label) and w != self.logo_lbl:
                w.configure(bg=t["nav_bg"])
        self.logo_lbl.configure(bg=t["nav_bg"])
        self.sync_btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
        self.dark_btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
        self.cart_btn.configure(bg=t["btn_bg"], fg=t["btn_fg"])
        self.search_entry.configure(
            bg=t["search_bg"], fg=t["search_fg"],
            insertbackground=t["search_fg"],
            highlightbackground=t["search_border"])

        # Filter
        self.filter_bar.configure(bg=t["filter_bg"])
        self.filter_border_line.configure(bg=t["filter_border"])
        for w in self._all_navbar_widgets(self.filter_bar):
            if isinstance(w, tk.Frame):
                w.configure(bg=t["filter_bg"])

        # Banner
        self.banner.update_theme(t)

        # Product grid bg
        self.product_scroll.update_bg(t["bg"])
        self.product_grid.configure(bg=t["bg"])

        self._update_filter_styles()
        self._update_sort_styles()

    def _all_navbar_widgets(self, parent):
        result = []
        for w in parent.winfo_children():
            result.append(w)
            result.extend(self._all_navbar_widgets(w))
        return result

    def _update_filter_styles(self):
        t = self.t
        for cat, btn in self.cat_btns.items():
            if cat == self.selected_category:
                btn.config(bg=t["pill_active_bg"], fg=t["pill_active_fg"])
            else:
                btn.config(bg=t["pill_inactive_bg"], fg=t["pill_inactive_fg"])
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg=t["cart_item_bg"]))
                btn.bind("<Leave>", lambda e, b=btn, c=cat:
                         b.config(bg=t["pill_active_bg"] if c == self.selected_category
                                  else t["pill_inactive_bg"]))

    def _update_sort_styles(self):
        t = self.t
        if self.sort_option == "termurah":
            self.sort_cheap_btn.config(bg=t["sort_active_bg"], fg=t["sort_active_fg"])
            self.sort_exp_btn.config(bg=t["pill_inactive_bg"], fg=t["pill_inactive_fg"])
        else:
            self.sort_exp_btn.config(bg=t["sort_active_bg"], fg=t["sort_active_fg"])
            self.sort_cheap_btn.config(bg=t["pill_inactive_bg"], fg=t["pill_inactive_fg"])

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ─── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = RadarPromoApp()
    app.run()
