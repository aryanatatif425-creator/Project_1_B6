"""
main.py — Radar Promo v2.0 Entry Point
=======================================
Langsung membuka Mode Pengguna.
Akses Admin dipindahkan ke halaman Pengaturan.
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox, QInputDialog, QLineEdit

# ─── Import modul tim ─────────────────────────────────────────────
try:
    import gui_pyqt          # GUI utama (milik Shahnaz / kamu)
    import data_manager      # Pengelola data (milik Alpedro)
    import engine             # Mesin logika (milik Zehan)
    import_error_msg = ""
except ImportError as e:
    import_error_msg = str(e)
    print(f"Modul belum tersedia: {e}")
    gui_pyqt = None
    data_manager = None
    engine = None

log = logging.getLogger(__name__)

# ─── Konstanta ────────────────────────────────────────────────────
ADMIN_PASSWORD = os.environ.get("RADAR_ADMIN_PASSWORD", "")

# ─── Data awal ────────────────────────────────────────────────────
def load_initial_data():
    """Memuat data awal dari data_manager atau mengembalikan list kosong."""
    if data_manager:
        try:
            db = data_manager.read_local_data()
            if db:
                log.info(f"Data dimuat dari data_promo.json ({len(db)} item)")
                return db
        except Exception as e:
            log.warning(f"Gagal memuat data via data_manager: {e}")
    # Fallback: list kosong agar GUI tidak crash
    log.warning("Data kosong. Harap jalankan Admin Tool untuk sinkronisasi.")
    return []

# ─── Login Admin ──────────────────────────────────────────────────
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
    """Membuka Dashboard Admin (jendela terpisah)."""
    import subprocess
    import sys
    import os
    try:
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
    except Exception as e:
        QMessageBox.information(parent, "Error", f"Gagal membuka Admin Tool: {e}")

# ─── Entry Point ──────────────────────────────────────────────────
def main():
    from PyQt6.QtGui import QPalette, QColor, QIcon

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gemini-svg.ico")))

    # Load Google Sans font into Qt font database
    from PyQt6.QtGui import QFontDatabase
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Fonts")
    for fname in [
        "GoogleSans-Regular.ttf",
        "GoogleSans-Medium.ttf",
        "GoogleSans-Bold.ttf",
        "GoogleSans-Italic.ttf",
        "GoogleSans-BoldItalic.ttf",
        "GoogleSans-MediumItalic.ttf",
    ]:
        fpath = os.path.join(font_dir, fname)
        if os.path.exists(fpath):
            QFontDatabase.addApplicationFont(fpath)

    # Terapkan gaya dan palet global agar konsisten (mencegah teks putih di tema gelap)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window,          QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.WindowText,      QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Base,            QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor("#F7F6F3"))
    pal.setColor(QPalette.ColorRole.Text,            QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Button,          QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor("#191919"))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor("#21C083"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(pal)

    # Muat data
    db = load_initial_data()

    # Langsung buat GUI Mode Pengguna
    if gui_pyqt:
        window = gui_pyqt.MainWindow()  # Tidak lagi kirim db, dihandle di dalam
        window.set_admin_login_callback(lambda parent=window: show_admin_login(parent))
        window.show()
    else:
        # Fallback: Dummy Window jika gui_pyqt belum ada
        window = QWidget()
        window.setWindowTitle("Error: Gagal Memuat Modul")
        window.resize(500, 250)
        layout = QVBoxLayout()
        
        err_msg = f"GUI tidak bisa dimuat karena error impor:\n\n{import_error_msg}\n\nPastikan semua file (.py) terbawa, dan pip install -r requirements.txt sukses."
        lbl = QLabel(err_msg)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        
        layout.addWidget(lbl)
        window.setLayout(layout)
        window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()