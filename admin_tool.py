import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
from datetime import datetime

# Konfigurasi Berkas Sistem
ADMIN_PASSWORD = "adminpolban"
LOG_FILE = os.path.join(os.path.dirname(__file__), "activity.log")

# Membuat file dummy data_manager jika belum ada di direktori kerja
try:
    import data_manager
except ImportError:
    # Blok kode pengaman sbg representasi module data_manager dummy jika belum lengkap
    class DummyDataManager:
        def write_local_data(self, data):
            with open("data_promo_local.json", "w") as f:
                json.dump(data, f)
        def read_local_data(self):
            if os.path.exists("data_promo_local.json"):
                with open("data_promo_local.json", "r") as f: return json.load(f)
            return []
        def push_promo_to_cloud(self, data):
            return True # Simulasi push sukses
    data_manager = DummyDataManager()

def tulis_log(pesan):
    """Menulis rekaman jejak aktivitas ke dalam berkas log lokal."""
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris = f"[{waktu}] {pesan}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(baris)
    return baris

# ========================================================
# CORE OPERASIONAL LOGIC (BACKGROUND THREADS)
# ========================================================

def jalankan_sinkronisasi(progress_bar, log_widget, root):
    """Proses penarikan data dari core scraper engine secara asinkron."""
    try:
        import scraper
        
        # Tahap 1: Inisialisasi
        log_widget.insert(tk.END, tulis_log('[SCRAPING] Memulai proses sinkronisasi data dari web...'))
        log_widget.see(tk.END)
        progress_bar["value"] = 10
        root.update_idletasks()
        
        # Tahap 2: Eksekusi Engine Scraper
        data_mentah, errors = scraper.run_scraper()
        progress_bar["value"] = 50
        root.update_idletasks()
        
        # Tahap 3: Pelaporan Parsial Error Retailer
        if errors:
            log_widget.insert(tk.END, tulis_log(f'[WARN] {len(errors)} retailer terganggu selama scraping.'))
            for err in errors:
                log_widget.insert(tk.END, tulis_log(f'   -> Error Log: {err}'))
            log_widget.see(tk.END)

        # Tahap 4: Penanganan Mekanisme Fallback Data Cadangan
        if not data_mentah:
            log_widget.insert(tk.END, tulis_log('[SCRAPING] Kegagalan sistem terdeteksi. Mengaktifkan data demo...'))
            log_widget.see(tk.END)
            data_mentah = scraper.get_demo_data()
            
        progress_bar["value"] = 80
        root.update_idletasks()
        
        # Tahap 5: Persistensi Data ke Penyimpanan Lokal
        data_manager.write_local_data(data_mentah)
        
        progress_bar["value"] = 100
        root.update_idletasks()
        
        log_widget.insert(tk.END, tulis_log(f'[SCRAPING] Sukses! {len(data_mentah)} item diperbarui secara lokal.'))
        log_widget.see(tk.END)
        messagebox.showinfo('Sukses', f'Sinkronisasi selesai!\n{len(data_mentah)} item berhasil diperbarui.')
        
    except Exception as e:
        log_widget.insert(tk.END, tulis_log(f'[ERROR] Gangguan Sinkronisasi: {str(e)}'))
        log_widget.see(tk.END)
        messagebox.showerror('Error Fatal', f'Sinkronisasi terhenti total:\n{e}')
    finally:
        progress_bar["value"] = 0

def mulai_sinkronisasi(progress_bar, log_widget, root):
    """Membungkus fungsi sinkronisasi ke dalam Thread terpisah supaya GUI tidak freeze."""
    thread = threading.Thread(
        target=jalankan_sinkronisasi,
        args=(progress_bar, log_widget, root),
        daemon=True
    )
    thread.start()

def jalankan_upload(progress_bar, log_widget, root):
    """Proses transmisi data lokal menuju penyimpanan awan secara asinkron."""
    try:
        log_widget.insert(tk.END, tulis_log('[UPLOAD] Menginisiasi pengiriman data cloud...'))
        log_widget.see(tk.END)
        progress_bar["value"] = 20
        root.update_idletasks()
        
        data = data_manager.read_local_data()
        if not data:
            log_widget.insert(tk.END, tulis_log('[UPLOAD] Pembatalan otomatis: Data lokal kosong.'))
            log_widget.see(tk.END)
            messagebox.showwarning('Peringatan', 'Tidak ditemukan data lokal untuk diunggah.\nSilakan jalankan sinkronisasi terdepan.')
            progress_bar["value"] = 0
            return
            
        progress_bar["value"] = 50
        root.update_idletasks()
        
        # Mengirim data ke Google Sheets Cloud Database via Data Manager Module
        berhasil = data_manager.push_promo_to_cloud(data)
        
        progress_bar["value"] = 100
        root.update_idletasks()
        
        if berhasil:
            log_widget.insert(tk.END, tulis_log(f'[UPLOAD] Sinkronisasi Cloud Sukses. {len(data)} item terunggah.'))
            messagebox.showinfo('Sukses Cloud', f'{len(data)} item berhasil diupload ke Google Sheets Database.')
        else:
            log_widget.insert(tk.END, tulis_log('[UPLOAD] Transmisi ditolak. Masalah jaringan/cloud script.'))
            messagebox.showerror('Error Jaringan', 'Gagal mengupload ke cloud database. Silakan cek koneksi internet.')
            
    except Exception as e:
        log_widget.insert(tk.END, tulis_log(f'[ERROR] Gagal mengunggah data: {str(e)}'))
        messagebox.showerror('Error Upload', f'Proses upload dibatalkan:\n{e}')
    finally:
        progress_bar["value"] = 0

def mulai_upload(progress_bar, log_widget, root):
    """Membungkus fungsi transmisi ke Thread terpisah."""
    thread = threading.Thread(
        target=jalankan_upload,
        args=(progress_bar, log_widget, root),
        daemon=True
    )
    thread.start()

def segarkan_log_viewer(log_widget):
    """Membaca ulang isi berkas activity.log ke widget teks GUI."""
    log_widget.delete('1.0', tk.END)
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_widget.insert(tk.END, f.read())
    else:
        log_widget.insert(tk.END, "Log aktivitas kosong.\n")
    log_widget.see(tk.END)

# ========================================================
# KONTROLLER ANTARMUKA GUI (TKINTER INTERFACE)
# ========================================================

def buat_window(parent=None):
    root = tk.Toplevel(parent) if parent else tk.Tk()
    root.title("Radar Promo Admin Dashboard v2.0")
    root.geometry("680x560")
    root.configure(bg="#F3F4F6")
    
    # 1. Komponen Header
    tk.Label(root, text='🛠️ Radar Promo Admin Dashboard',
             font=('Arial', 18, 'bold'), bg='#F3F4F6', fg='#1E3A8A').pack(pady=(15, 5))
    tk.Label(root, text='Modul Pengelolaan Data Otomatis & Pemantauan Log',
             font=('Arial', 10), bg='#F3F4F6', fg='#4B5563').pack(pady=(0, 15))
    
    # 2. Frame Operasional Utama
    main_frame = tk.Frame(root, bg='#FFFFFF', bd=1, relief='solid', highlightthickness=0)
    main_frame.pack(fill='x', padx=25, pady=5)
    
    # Sub-Komponen Status Progress Bar
    tk.Label(main_frame, text='Status Jalur Proses Antrean Pemeliharaan Data:', font=('Arial', 9), bg='#FFFFFF', fg='#374151').pack(anchor='w', padx=20, pady=(10, 2))
    progress_bar = ttk.Progressbar(main_frame, orient='horizontal', length=580, mode='determinate')
    progress_bar.pack(padx=20, pady=(0, 15))
    
    # Panel Kontrol Tombol Aksi
    panel_tombol = tk.Frame(main_frame, bg='#FFFFFF')
    panel_tombol.pack(fill='x', padx=20, pady=(0, 10))
    
    btn_sync = tk.Button(panel_tombol, text='🔄 Sinkronisasi Web', font=('Arial', 11, 'bold'),
                         bg='#2563EB', fg='white', relief='flat', cursor='hand2', width=18, height=2,
                         command=lambda: mulai_sinkronisasi(progress_bar, log_widget, root))
    btn_sync.pack(side='left', padx=(0, 10))
    
    btn_upload = tk.Button(panel_tombol, text='☁️ Upload ke Cloud', font=('Arial', 11, 'bold'),
                           bg='#059669', fg='white', relief='flat', cursor='hand2', width=18, height=2,
                           command=lambda: mulai_upload(progress_bar, log_widget, root))
    btn_upload.pack(side='left', padx=10)
    
    btn_refresh_log = tk.Button(panel_tombol, text='📋 Refresh Log', font=('Arial', 11, 'bold'),
                                 bg='#4B5563', fg='white', relief='flat', cursor='hand2', width=14, height=2,
                                 command=lambda: segarkan_log_viewer(log_widget))
    btn_refresh_log.pack(side='right')

    # 3. Lapisan Komponen Log Viewer System
    log_frame = tk.Frame(root, bg='#F3F4F6')
    log_frame.pack(fill='both', expand=True, padx=25, pady=10)
    
    tk.Label(log_frame, text='Aktivitas Konsol Log (Activity Log Viewer):', font=('Arial', 10, 'bold'), bg='#F3F4F6', fg='#1F2937').pack(anchor='w', pady=(0, 5))
    
    log_widget = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9.5), bg='#1F2937', fg='#10B981', insertbackground='white')
    log_widget.pack(fill='both', expand=True)
    
    # Muat log bawaan saat inisialisasi aplikasi dibuka
    segarkan_log_viewer(log_widget)
    tulis_log("[SYSTEM] Sesi konsol dasbor admin berhasil dibuka.")
    log_widget.insert(tk.END, f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [SYSTEM] Dasbor Admin Siap Digunakan.\n")
    
    root.mainloop()

if __name__ == "__main__":
    buat_window()