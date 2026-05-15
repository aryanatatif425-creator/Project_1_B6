import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog, QWidget, QVBoxLayout, QLabel, QLineEdit
import logging

# ─── Import modul tim ─────────────────────────────────────────────
try:
    import gui_pyqt          # GUI utama 
    import data_manager    # Pengelola data 
    import engine           # Mesin logika 
except ImportError as e:
    print(f"Modul belum tersedia: {e}")
    print("Aplikasi akan berjalan dengan data dummy.")
    gui_pyqt = None
    data_manager = None
    engine = None

log = logging.getLogger(__name__)

# ─── Password Admin ──────────────────────────────────────────────
ADMIN_PASSWORD = "adminpolban"

# ─── Path database utama ──────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data_promo.json")

def load_initial_data():
    """Memuat data awal dari data_manager atau langsung dari data_promo.json."""
    if data_manager:
        try:
            db = data_manager.load_database()
            if db:
                return db
        except Exception as e:
            log.warning(f"Gagal muat data_manager: {e}")

    # Fallback: baca langsung dari data_promo.json
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
        log.info(f"Data dimuat dari data_promo.json ({len(db)} item)")
        return db
    except Exception as e:
        log.error(f"Gagal membaca data_promo.json: {e}")
        return []

def show_admin_login(parent):
    """Menampilkan dialog login admin. Dipanggil dari tombol di Settings."""
    password, ok = QInputDialog.getText(
        parent,
        "Login Admin",
        "Masukkan kata sandi Admin:",
        QLineEdit.EchoMode.Password
    )
    if ok and password == ADMIN_PASSWORD:
        QMessageBox.information(parent, "Berhasil", "Login sebagai Admin berhasil.")
        open_admin_dashboard(parent)
    elif ok:
        QMessageBox.warning(parent, "Gagal", "Kata sandi salah.")

def open_admin_dashboard(parent):
    """Membuka Dashboard Admin (jendela terpisah atau mengganti UI)."""
    try:
        import admin_tool
        admin_tool.run_dashboard(parent)
    except ImportError:
        QMessageBox.information(
            parent,
            "Admin Tool",
            "Modul admin_tool belum tersedia.\n"
            "Ini akan menjadi Dashboard Admin."
        )

def main():
    """Entry point aplikasi."""
    app = QApplication(sys.argv)

    # Muat data
    db = load_initial_data()

    # Langsung buat GUI Mode Pengguna
    if gui_pyqt:
        window = gui_pyqt.RadarPromoAppV2(
            db=db,
            on_search=None,  # Nanti diisi oleh engine
            on_sync=None     # Tidak dipakai di Mode Pengguna
        )
        # Beri referensi fungsi login admin ke GUI
        window.set_admin_login_callback(lambda parent=window: show_admin_login(parent))
        window.show()
    else:
        # Fallback: Dummy Window jika gui_pyqt belum ada
        window = QWidget()
        window.setWindowTitle("Menunggu gui_pyqt.py...")
        window.resize(400, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("GUI belum tersedia.\nSedang menunggu file gui_pyqt.py..."))
        window.setLayout(layout)
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
