# admin_tool.py

import tkinter as tk
from tkinter import messagebox
import scraper  # import scraper.py

def sinkronisasi():
    messagebox.showinfo("Info", "Fitur dalam pengembangan")

def buat_window():
    root = tk.Tk()
    root.title("Radar Promo Admin Dashboard")
    root.geometry("600x400")

    # Tombol Sinkronisasi
    btn_sync = tk.Button(
        root,
        text="🔄 Sinkronisasi Sekarang",
        font=("Arial", 14),
        height=2,
        command=sinkronisasi
    )
    btn_sync.pack(pady=20)

    # Area Log Viewer
    log_text = tk.Text(root, height=10)
    log_text.pack(padx=20, pady=10, fill="both", expand=True)

    log_text.insert(tk.END, "Log aktivitas akan muncul di sini.\n")

    root.mainloop()


if __name__ == "__main__":
    buat_window()