import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

# ─── Import modul tim ─────────────────────────────────────────────
try:
    import gui_v2          # GUI utama 
    import data_manager    # Pengelola data 
    import engine           # Mesin logika 
except ImportError as e:
    print(f"Modul belum tersedia: {e}")
    print("Aplikasi akan berjalan dengan data dummy.")
    gui_v2 = None
    data_manager = None
    engine = None

log = logging.getLogger(__name__)

# ─── Password Admin ──────────────────────────────────────────────
ADMIN_PASSWORD = "adminpolban"

# ─── Data Dummy (sementara sebelum modul siap) ───────────────────
DUMMY_DATA = [
    {
        "id": "superindo|superindo_pasteur|beras_365_5kg",
        "nama_produk": "Beras 365 Pulen Wangi 5kg",
        "brand_toko": "Superindo",
        "nama_cabang": "Superindo Pasteur",
        "kategori": "Sembako",
        "harga_promo": 72900,
        "harga_normal": 85000,
        "jenis_harga": "PROMO",
        "display_harga": "Rp 72.900",
        "image_url": "",
        "logo_url": "",
        "area_tags": ["Sarijadi", "Gegerkalong"],
        "search_vector": "beras 365 pulen wangi 5kg superindo superindo pasteur"
    }
]

def load_initial_data():
    """Memuat data awal (database lokal atau dummy)."""
    if data_manager:
        try:
            db = data_manager.load_database()
            if db:
                return db
        except Exception as e:
            log.warning(f"Gagal muat data_manager: {e}")
    return DUMMY_DATA

def show_admin_login(parent):
    """Menampilkan dialog login admin. Dipanggil dari tombol di Settings."""
    password = simpledialog.askstring(
        "Login Admin",
        "Masukkan kata sandi Admin:",
        parent=parent,
        show="*"
    )
    if password == ADMIN_PASSWORD:
        messagebox.showinfo("Berhasil", "Login sebagai Admin berhasil.")
        open_admin_dashboard(parent)
    elif password is not None:
        messagebox.showerror("Gagal", "Kata sandi salah.")

def open_admin_dashboard(parent):
    """Membuka Dashboard Admin (jendela terpisah atau mengganti UI)."""
    try:
        import admin_tool
        admin_tool.run_dashboard(parent)
    except ImportError:
        messagebox.showinfo(
            "Admin Tool",
            "Modul admin_tool belum tersedia.\n"
            "Ini akan menjadi Dashboard Admin."
        )

def main():
    """Entry point aplikasi."""
    root = tk.Tk()
    root.withdraw()  # Sembunyikan sampai siap

    # Muat data
    db = load_initial_data()

    # Langsung buat GUI Mode Pengguna
    if gui_v2:
        app = gui_v2.RadarPromoAppV2(
            root=root,
            db=db,
            on_search=None,  # Nanti diisi oleh engine
            on_sync=None     # Tidak dipakai di Mode Pengguna
        )
        # Beri referensi fungsi login admin ke GUI
        app.set_admin_login_callback(lambda parent=root: show_admin_login(parent))
    else:
        # Fallback: GUI minimal jika modul belum ada
        tk.Label(root, text="GUI belum tersedia.\nMode teks.").pack()

    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
