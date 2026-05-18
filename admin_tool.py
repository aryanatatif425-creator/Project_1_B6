"""
admin_tool.py — Radar Promo Admin Dashboard
============================================
Dashboard Admin berbasis Tkinter (aplikasi terpisah).
Hanya berisi alat sinkronisasi, upload cloud, dan Log Viewer.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from datetime import datetime

# ═══════════════ KONFIGURASI ═══════════════
LOG_FILE = os.path.join(os.path.dirname(__file__), "activity.log")


# ═══════════════ FUNGSI PEMBANTU ═══════════════
def tulis_log(pesan):
    """Menulis pesan ke activity.log dan mengembalikan string untuk Log Viewer."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris = f"[{waktu}] {pesan}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(baris)
    except:
        pass
    return baris


# ═══════════════ FUNGSI UTAMA ═══════════════
def jalankan_sinkronisasi(progress_bar, log_widget, root):
    """Menjalankan scraping di background thread, memperbarui progress bar."""
    try:
        import scraper

        # Tahap 1: Mulai
        log_widget.insert(tk.END, tulis_log("[SCRAPING] Memulai sinkronisasi data..."))
        log_widget.see(tk.END)
        progress_bar["value"] = 10
        root.update_idletasks()

        # Tahap 2: Jalankan scraper
        data_mentah, errors = scraper.run_scraper()
        
        if errors:
            for err in errors:
                log_widget.insert(tk.END, tulis_log(f"[SCRAPING] ⚠️ {err}"))
        progress_bar["value"] = 50
        root.update_idletasks()

        # Tahap 3: Fallback jika scraping gagal
        if not data_mentah:
            log_widget.insert(tk.END, tulis_log("[SCRAPING] ⚠️ Scraping gagal. Menggunakan data demo..."))
            log_widget.see(tk.END)
            data_mentah = scraper.get_demo_data()

            if not data_mentah:
                log_widget.insert(tk.END, tulis_log("[ERROR] Data demo juga kosong! Sinkronisasi dibatalkan."))
                log_widget.see(tk.END)
                messagebox.showerror("Error", "Scraping dan data demo sama-sama gagal.\nPeriksa koneksi internet.")
                progress_bar["value"] = 0
                return

        progress_bar["value"] = 80
        root.update_idletasks()

        # Tahap 4: Perkaya data dengan Address Book, lalu simpan
        import data_manager
        if data_mentah:
            data_mentah = data_manager.enrich_data(data_mentah)
        data_manager.write_local_data(data_mentah)
        progress_bar["value"] = 100
        root.update_idletasks()

        log_widget.insert(tk.END, tulis_log(f"[SCRAPING] ✅ Sinkronisasi selesai. {len(data_mentah)} item diperbarui."))
        log_widget.see(tk.END)
        messagebox.showinfo("Sukses", f"Sinkronisasi selesai!\n{len(data_mentah)} item berhasil diperbarui.")

    except ImportError as e:
        log_widget.insert(tk.END, tulis_log(f"[ERROR] Modul tidak ditemukan: {e}"))
        log_widget.see(tk.END)
        messagebox.showerror("Error", f"Modul tidak ditemukan:\n{e}\nPastikan scraper.py dan data_manager.py ada.")
        progress_bar["value"] = 0
    except Exception as e:
        log_widget.insert(tk.END, tulis_log(f"[ERROR] Sinkronisasi gagal: {e}"))
        log_widget.see(tk.END)
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")
        progress_bar["value"] = 0


def mulai_sinkronisasi(progress_bar, log_widget, root):
    """Membungkus sinkronisasi dalam thread agar GUI tidak freeze."""
    thread = threading.Thread(
        target=jalankan_sinkronisasi,
        args=(progress_bar, log_widget, root),
        daemon=True
    )
    thread.start()


def jalankan_upload(progress_bar, log_widget, root):
    """Mengunggah data promo ke Google Sheets."""
    try:
        import data_manager

        log_widget.insert(tk.END, tulis_log("[UPLOAD] Memulai upload ke cloud... (Ini memakan waktu, harap tunggu)"))
        log_widget.see(tk.END)
        progress_bar["value"] = 20
        root.update_idletasks()

        data = data_manager.read_local_data()
        if not data:
            log_widget.insert(tk.END, tulis_log("[UPLOAD] Tidak ada data untuk diupload."))
            log_widget.see(tk.END)
            messagebox.showwarning("Peringatan", "Tidak ada data lokal.\nLakukan sinkronisasi terlebih dahulu.")
            progress_bar["value"] = 0
            return

        progress_bar["value"] = 50
        root.update_idletasks()

        berhasil = data_manager.push_promo_to_cloud(data)
        progress_bar["value"] = 100
        root.update_idletasks()

        if berhasil:
            log_widget.insert(tk.END, tulis_log(f"[UPLOAD] ✅ Upload berhasil. {len(data)} item terkirim ke cloud."))
            log_widget.see(tk.END)
            messagebox.showinfo("Sukses", f"Upload berhasil!\n{len(data)} item terkirim ke Google Sheets.")
        else:
            log_widget.insert(tk.END, tulis_log("[UPLOAD] ❌ Upload gagal. Periksa koneksi internet atau Timeout."))
            log_widget.see(tk.END)
            messagebox.showerror("Error", "Upload gagal. Periksa koneksi internet atau URL Apps Script (kemungkinan Timeout).")

    except ImportError as e:
        log_widget.insert(tk.END, tulis_log(f"[ERROR] Modul tidak ditemukan: {e}"))
        log_widget.see(tk.END)
        messagebox.showerror("Error", f"Modul tidak ditemukan:\n{e}")
        progress_bar["value"] = 0
    except Exception as e:
        log_widget.insert(tk.END, tulis_log(f"[ERROR] Upload gagal: {e}"))
        log_widget.see(tk.END)
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")
        progress_bar["value"] = 0

def upload_ke_cloud(progress_bar, log_widget, root):
    """Membungkus upload dalam thread agar GUI tidak freeze."""
    thread = threading.Thread(
        target=jalankan_upload,
        args=(progress_bar, log_widget, root),
        daemon=True
    )
    thread.start()


# ═══════════════ MEMBANGUN GUI ═══════════════
def buat_window(parent=None):
    """Membuat jendela Dashboard Admin."""

    root = tk.Toplevel(parent) if parent else tk.Tk()
    root.title("Radar Promo Admin Dashboard")
    root.geometry("680x520")
    root.resizable(True, True)
    root.configure(bg="#f5f5f7")

    # Judul
    header = tk.Label(
        root,
        text="🛠️ Radar Promo Admin Dashboard",
        font=("Arial", 18, "bold"),
        bg="#f5f5f7",
        fg="#6F84B8"
    )
    header.pack(pady=(20, 10))

    sub_header = tk.Label(
        root,
        text="Alat pemeliharaan data promo dan pemantauan aktivitas",
        font=("Arial", 11),
        bg="#f5f5f7",
        fg="#6b7280"
    )
    sub_header.pack(pady=(0, 20))

    # Frame Sinkronisasi
    sync_frame = tk.Frame(root, bg="#ffffff", highlightbackground="#e5e7eb", highlightthickness=1)
    sync_frame.pack(fill="x", padx=30, pady=(0, 10))

    tk.Label(
        sync_frame,
        text="📥 Sinkronisasi Data",
        font=("Arial", 13, "bold"),
        bg="#ffffff",
        fg="#111827"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    tk.Label(
        sync_frame,
        text="Ambil data promo terbaru dari hemat.id dan simpan ke database lokal.",
        font=("Arial", 10),
        bg="#ffffff",
        fg="#6b7280"
    ).pack(anchor="w", padx=20, pady=(0, 10))

    progress_bar = ttk.Progressbar(
        sync_frame,
        orient="horizontal",
        length=400,
        mode="determinate",
        maximum=100
    )
    progress_bar.pack(padx=20, pady=(5, 10))

    sync_btn = tk.Button(
        sync_frame,
        text="🔄 Sinkronisasi Sekarang",
        font=("Arial", 12, "bold"),
        bg="#6F84B8",
        fg="white",
        activebackground="#5a72a8",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2",
        command=lambda: mulai_sinkronisasi(progress_bar, log_widget, root)
    )
    sync_btn.pack(pady=(0, 15))

    # Frame Upload
    upload_frame = tk.Frame(root, bg="#ffffff", highlightbackground="#e5e7eb", highlightthickness=1)
    upload_frame.pack(fill="x", padx=30, pady=(0, 10))

    tk.Label(
        upload_frame,
        text="☁️ Upload ke Cloud",
        font=("Arial", 13, "bold"),
        bg="#ffffff",
        fg="#111827"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    tk.Label(
        upload_frame,
        text="Kirim data yang sudah di-sinkronisasi ke Google Sheets (database ).",
        font=("Arial", 10),
        bg="#ffffff",
        fg="#6b7280"
    ).pack(anchor="w", padx=20, pady=(0, 15))

    upload_btn = tk.Button(
        upload_frame,
        text="☁️ Upload Promo ke Cloud",
        font=("Arial", 12, "bold"),
        bg="#F1C0CC",
        fg="white",
        activebackground="#e8aabb",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=20,
        pady=8,
        cursor="hand2",
        command=lambda: upload_ke_cloud(progress_bar, log_widget, root)
    )
    upload_btn.pack(pady=(0, 15))

    # Frame Log Viewer
    log_frame = tk.Frame(root, bg="#ffffff", highlightbackground="#e5e7eb", highlightthickness=1)
    log_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    tk.Label(
        log_frame,
        text="📋 Log Aktivitas",
        font=("Arial", 13, "bold"),
        bg="#ffffff",
        fg="#111827"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    log_widget = scrolledtext.ScrolledText(
        log_frame,
        wrap=tk.WORD,
        width=70,
        height=12,
        font=("Consolas", 9),
        bg="#f5f4f2",
        fg="#111827",
        relief="flat",
        bd=0,
        padx=10,
        pady=10
    )
    log_widget.pack(fill="both", expand=True, padx=20, pady=(0, 5))

    refresh_btn = tk.Button(
        log_frame,
        text="🔄 Refresh Log",
        font=("Arial", 10),
        bg="#eef1f8",
        fg="#374151",
        activebackground="#d1d5db",
        activeforeground="#374151",
        relief="flat",
        bd=0,
        padx=14,
        pady=4,
        cursor="hand2",
        command=lambda: muat_ulang_log(log_widget)
    )
    refresh_btn.pack(pady=(0, 10))

    # Muat log yang sudah ada
    muat_ulang_log(log_widget)

    if not parent:
        root.mainloop()

    return root


def muat_ulang_log(log_widget):
    """Membaca isi activity.log dan menampilkannya di Log Viewer."""
    log_widget.delete(1.0, tk.END)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            isi = f.read()
        if isi.strip():
            log_widget.insert(tk.END, isi)
            log_widget.see(tk.END)
        else:
            log_widget.insert(tk.END, "[INFO] File log kosong. Aktivitas akan muncul di sini.\n")
    else:
        log_widget.insert(tk.END, "[INFO] File log belum ada. Aktivitas akan muncul di sini.\n")


# ═══════════════ FUNGSI UNTUK DIPANGGIL OLEH MAIN.PY ═══════════════
def run_dashboard(parent=None):
    """Fungsi yang akan dipanggil oleh main.py saat Admin login."""
    return buat_window(parent)


# ═══════════════ ENTRY POINT (UNTUK PENGUJIAN MANDIRI) ═══════════════
if __name__ == "__main__":
    buat_window()