# admin_tool.py

import tkinter as tk
from tkinter import messagebox, ttk
import scraper  # import scraper.py

#variabel global
progress = None

def sinkronisasi():
    progress["value"] = 20
    root.update_idletasks()
    messagebox.showinfo("Info", "Sinkronisasi dimulai")

    progress["value"] = 100
    root.update_idletasks()

    global progress

def buat_window():
    global progress
    
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
    
    #Progress Bar
    progress = ttk.Progressbar(
        root,
        orient = "horizontal",
        length = 300,
        mode = "determinate",
    )
    progress.pack(pady = 10)
    
    # Area Log Viewer
    log_text = tk.Text(root, height=10)
    log_text.pack(padx=20, pady=10, fill="both", expand=True)

    log_text.insert(tk.END, "Log aktivitas akan muncul di sini.\n")

    root.mainloop()


if __name__ == "__main__":
    buat_window()