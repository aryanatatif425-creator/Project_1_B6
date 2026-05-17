from data_manager import upload_photo

# Jangan lupa ganti path sesuai gambar yang mau diupload.
url = upload_photo(r"C:\testing\download.jpg")

if url:
    print(f"✅ Berhasil! URL: {url}")
    print("Silakan buka URL di browser.")
else:
    print("❌ Gagal upload.")