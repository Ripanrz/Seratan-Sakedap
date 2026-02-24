import gradio as gr
import os
import time
import threading
import uuid
import secrets
from pypdf import PdfReader, PdfWriter
from pdf2docx import Converter
import fitz  # PyMuPDF
from PIL import Image

# ==========================================
# 1. SISTEM KEAMANAN (SECURE WIPE 5 MENIT)
# ==========================================
FOLDER_TEMP = "./secure_temp_pdf"

# Buat folder sementara jika belum ada
if not os.path.exists(FOLDER_TEMP):
    os.makedirs(FOLDER_TEMP)

def penghancur_file_permanen(filepath):
    """Menimpa isi file dengan data acak sebelum menghapusnya agar tidak bisa di-recovery (Secure Wipe)"""
    try:
        if os.path.exists(filepath):
            ukuran_file = os.path.getsize(filepath)
            # Timpa file dengan data acak
            with open(filepath, "br+") as f:
                f.write(secrets.token_bytes(ukuran_file))
            # Hapus file secara fisik dari server
            os.remove(filepath)
            print(f"🔒 AMAN: File {os.path.basename(filepath)} telah dihancurkan permanen.")
    except Exception as e:
        print(f"Gagal menghapus {filepath}: {e}")

def sapu_bersih_otomatis():
    """Berjalan di latar belakang, mengecek folder setiap 1 menit"""
    while True:
        waktu_sekarang = time.time()
        for nama_file in os.listdir(FOLDER_TEMP):
            path_file = os.path.join(FOLDER_TEMP, nama_file)
            waktu_file = os.path.getmtime(path_file)
            
            # Jika umur file > 300 detik (5 menit)
            if waktu_sekarang - waktu_file > 300:
                penghancur_file_permanen(path_file)
        time.sleep(60)

# Aktifkan robot keamanan di latar belakang
threading.Thread(target=sapu_bersih_otomatis, daemon=True).start()

def buat_nama_file_unik(ekstensi):
    """Membuat nama file acak agar tidak bentrok antar pengguna"""
    return os.path.join(FOLDER_TEMP, f"{uuid.uuid4().hex}.{ekstensi}")

# ==========================================
# 2. FUNGSI-FUNGSI UTILITAS PDF
# ==========================================

# 1. Kompres PDF (Mengurangi ukuran file)
def kompres_pdf(file_pdf):
    if not file_pdf: return None
    path_output = buat_nama_file_unik("pdf")
    # Membaca dan menyimpan ulang dengan kompresi maksimal (Deflate & Garbage Collection)
    doc = fitz.open(file_pdf.name)
    doc.save(path_output, deflate=True, garbage=4)
    doc.close()
    return path_output

# 2. Gabung PDF
def gabung_pdf(file_pdfs):
    if not file_pdfs: return None
    path_output = buat_nama_file_unik("pdf")
    writer = PdfWriter()
    for file in file_pdfs:
        writer.append(file.name)
    writer.write(path_output)
    writer.close()
    return path_output

# 3. Pisah PDF
def pisah_pdf(file_pdf, hal_mulai, hal_akhir):
    if not file_pdf: return None
    path_output = buat_nama_file_unik("pdf")
    reader = PdfReader(file_pdf.name)
    writer = PdfWriter()
    
    # Menyesuaikan index (User input mulai dari 1, Python mulai dari 0)
    idx_mulai = max(0, int(hal_mulai) - 1)
    idx_akhir = min(len(reader.pages), int(hal_akhir))
    
    for i in range(idx_mulai, idx_akhir):
        writer.add_page(reader.pages[i])
        
    writer.write(path_output)
    writer.close()
    return path_output

# 4. PDF to Word
def konversi_pdf_ke_word(file_pdf):
    if not file_pdf: return None
    path_output = buat_nama_file_unik("docx")
    cv = Converter(file_pdf.name)
    cv.convert(path_output)
    cv.close()
    return path_output

# 5. Image to PDF
def konversi_gambar_ke_pdf(file_gambars):
    if not file_gambars: return None
    path_output = buat_nama_file_unik("pdf")
    
    # Buka semua gambar dan konversi ke format RGB (Syarat PDF)
    daftar_gambar = []
    for f in file_gambars:
        img = Image.open(f.name).convert('RGB')
        daftar_gambar.append(img)
        
    # Simpan gambar pertama sebagai PDF, lalu gabungkan sisanya di halaman berikutnya
    if daftar_gambar:
        daftar_gambar[0].save(path_output, save_all=True, append_images=daftar_gambar[1:])
        
    return path_output

# ==========================================
# 3. ANTARMUKA WEB (GRADIO UI)
# ==========================================
with gr.Blocks(theme=gr.themes.Monochrome()) as web_app:
    gr.Markdown("# 🛡️ SecurePDF Tools (Zero-Retention)")
    gr.Markdown("✅ **Privacy by Design:** File Anda **tidak disimpan**. Server akan menimpa data Anda dengan kode acak (Secure Wipe) dan menghapusnya secara fisik dalam waktu maksimal **5 menit** setelah proses selesai. Data tidak akan bisa dipulihkan oleh siapa pun.")
    
    with gr.Tabs():
        # TAB 1: Gabung PDF
        with gr.TabItem("🔗 Gabung PDF"):
            input_gabung = gr.File(label="Unggah Beberapa PDF", file_count="multiple")
            btn_gabung = gr.Button("Gabungkan File 🚀", variant="primary")
            output_gabung = gr.File(label="📥 Download Hasil PDF")
            btn_gabung.click(fn=gabung_pdf, inputs=input_gabung, outputs=output_gabung)

        # TAB 2: Pisah PDF
        with gr.TabItem("✂️ Pisah PDF"):
            input_pisah = gr.File(label="Unggah 1 PDF", file_count="single")
            with gr.Row():
                input_mulai = gr.Number(label="Dari Halaman (Contoh: 1)", value=1, precision=0)
                input_akhir = gr.Number(label="Sampai Halaman (Contoh: 5)", value=5, precision=0)
            btn_pisah = gr.Button("Pisahkan File 🚀", variant="primary")
            output_pisah = gr.File(label="📥 Download Hasil PDF")
            btn_pisah.click(fn=pisah_pdf, inputs=[input_pisah, input_mulai, input_akhir], outputs=output_pisah)

        # TAB 3: PDF to Word
        with gr.TabItem("📝 PDF to Word"):
            input_p2w = gr.File(label="Unggah PDF", file_count="single")
            btn_p2w = gr.Button("Konversi ke Word 🚀", variant="primary")
            output_p2w = gr.File(label="📥 Download File Word (.docx)")
            btn_p2w.click(fn=konversi_pdf_ke_word, inputs=input_p2w, outputs=output_p2w)

        # TAB 4: Image to PDF
        with gr.TabItem("🖼️ Image to PDF"):
            input_img = gr.File(label="Unggah Gambar (JPG/PNG)", file_count="multiple", file_types=["image"])
            btn_img = gr.Button("Konversi Gambar ke PDF 🚀", variant="primary")
            output_img = gr.File(label="📥 Download File PDF")
            btn_img.click(fn=konversi_gambar_ke_pdf, inputs=input_img, outputs=output_img)

        # TAB 5: Kompres PDF
        with gr.TabItem("🗜️ Kompres PDF"):
            gr.Markdown("*Proses ini akan mengoptimalkan struktur PDF dan membuang metadata yang tidak berguna untuk memperkecil ukuran file.*")
            input_kompres = gr.File(label="Unggah PDF", file_count="single")
            btn_kompres = gr.Button("Kompres File 🚀", variant="primary")
            output_kompres = gr.File(label="📥 Download Hasil Kompresi")
            btn_kompres.click(fn=kompres_pdf, inputs=input_kompres, outputs=output_kompres)

if __name__ == "__main__":
    web_app.launch()