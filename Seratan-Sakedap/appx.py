import gradio as gr
import os
import time
import threading
import uuid
import secrets
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
from pdf2docx import Converter
from PIL import Image

# ==========================================
# 1. SISTEM KEAMANAN & MANAJEMEN FILE
# ==========================================
FOLDER_TEMP = "./secure_temp_pdf"
if not os.path.exists(FOLDER_TEMP):
    os.makedirs(FOLDER_TEMP)

def penghancur_file_permanen(filepath):
    try:
        if os.path.exists(filepath):
            ukuran_file = os.path.getsize(filepath)
            with open(filepath, "br+") as f:
                f.write(secrets.token_bytes(ukuran_file))
            os.remove(filepath)
    except Exception as e:
        print(f"Gagal menghapus {filepath}: {e}")

def sapu_bersih_otomatis():
    while True:
        waktu_sekarang = time.time()
        for nama_file in os.listdir(FOLDER_TEMP):
            path_file = os.path.join(FOLDER_TEMP, nama_file)
            if waktu_sekarang - os.path.getmtime(path_file) > 300:
                penghancur_file_permanen(path_file)
        time.sleep(60)

threading.Thread(target=sapu_bersih_otomatis, daemon=True).start()

def buat_nama_file(path_asli, ekstensi_baru, suffix=""):
    nama_dasar = os.path.splitext(os.path.basename(path_asli))[0] if path_asli else f"file_{uuid.uuid4().hex[:4]}"
    return os.path.join(FOLDER_TEMP, f"{nama_dasar}{suffix}_{uuid.uuid4().hex[:4]}.{ekstensi_baru}")

# FUNGSI BANTUAN: Memastikan hanya 1 file yang diproses jika input berupa list
def ambil_satu_file(file_input):
    if isinstance(file_input, list):
        return file_input[0] if len(file_input) > 0 else None
    return file_input

# ==========================================
# 2. LOGIKA FITUR (BACKEND)
# ==========================================

def pdf_ke_word(file_pdf):
    file_pdf = ambil_satu_file(file_pdf)
    if not file_pdf: return None
    path_output = buat_nama_file(file_pdf.name, "docx", "_Word")
    cv = Converter(file_pdf.name)
    cv.convert(path_output)
    cv.close()
    return path_output

def pdf_ke_gambar(file_pdf):
    file_pdf = ambil_satu_file(file_pdf)
    if not file_pdf: return None
    doc = fitz.open(file_pdf.name)
    paths = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        img_path = buat_nama_file(file_pdf.name, "png", f"_hal_{i+1}")
        pix.save(img_path)
        paths.append(img_path)
    doc.close()
    return paths[0] 

def gambar_ke_pdf(file_gambars):
    if not file_gambars: return None
    path_output = buat_nama_file(file_gambars[0].name, "pdf", "_Converted")
    imgs = [Image.open(f.name).convert('RGB') for f in file_gambars]
    imgs[0].save(path_output, save_all=True, append_images=imgs[1:])
    return path_output

def gabung_pdf(file_pdfs):
    if not file_pdfs: return None
    path_output = buat_nama_file(file_pdfs[0].name, "pdf", "_Gabungan")
    writer = PdfWriter()
    for f in file_pdfs: writer.append(f.name)
    writer.write(path_output)
    return path_output

def pisah_pdf(file_pdf, m, a):
    file_pdf = ambil_satu_file(file_pdf)
    if not file_pdf or m is None or a is None: return None
    
    path_output = buat_nama_file(file_pdf.name, "pdf", f"_Hal_{int(m)}-{int(a)}")
    reader = PdfReader(file_pdf.name)
    writer = PdfWriter()
    
    idx_mulai = max(0, int(m) - 1)
    idx_akhir = min(int(a), len(reader.pages))
    
    for i in range(idx_mulai, idx_akhir):
        writer.add_page(reader.pages[i])
    writer.write(path_output)
    return path_output

def kompres_gambar(file_img):
    file_img = ambil_satu_file(file_img)
    if not file_img: return None
    path_output = buat_nama_file(file_img.name, "jpg", "_Compressed")
    img = Image.open(file_img.name)
    if img.mode != "RGB": img = img.convert("RGB")
    img.save(path_output, "JPEG", quality=40, optimize=True)
    return path_output

def kompres_pdf_fixed(file_pdf):
    file_pdf = ambil_satu_file(file_pdf)
    if not file_pdf: return None
    path_output = buat_nama_file(file_pdf.name, "pdf", "_Ringan")
    doc = fitz.open(file_pdf.name)
    doc.save(path_output, deflate=True, garbage=4)
    doc.close()
    return path_output

# ==========================================
# 3. TAMPILAN (GRADIO UI)
# ==========================================
theme = gr.themes.Soft(primary_hue="blue", secondary_hue="slate").set(
    button_primary_background_fill="*primary_600",
    block_radius="md"
)

css = """
.container { max-width: 1000px; margin: auto; }
.header { text-align: center; padding: 20px; }
.footer-info { font-size: 0.8em; text-align: center; color: gray; }
"""

with gr.Blocks(title="Seratan Sakedap") as app:
    
    with gr.Column(elem_classes="header"):
        gr.Markdown("# 📄 Seratan Sakedap — Secure Zero-Retention PDF Utility")
        gr.Markdown("### Solusi Dokumen Cepat & Aman")

    with gr.Tabs():
        with gr.TabItem("🛠️ PDF Utama"):
            with gr.Row():
                with gr.Column():
                    f_pdf = gr.File(label="Pilih File PDF", file_count="multiple")
                    with gr.Row():
                        start_h = gr.Number(label="Mulai Hal", value=1, precision=0)
                        end_h = gr.Number(label="Sampai Hal", value=2, precision=0)
                with gr.Column():
                    btn_mrg = gr.Button("🔗 Gabung PDF")
                    btn_spl = gr.Button("✂️ Pisah PDF")
                    btn_com_p = gr.Button("🗜️ Kompres PDF")
                    out_pdf = gr.File(label="Hasil PDF")

        with gr.TabItem("🔄 Konversi"):
            with gr.Row():
                with gr.Column():
                    f_conv = gr.File(label="Upload File (PDF/Gambar)", file_count="multiple")
                with gr.Column():

                    btn_p2w = gr.Button("PDF ke Word")
                    btn_p2i = gr.Button("PDF ke Gambar")
                    btn_i2p = gr.Button("Gambar ke PDF")
                    out_conv = gr.File(label="Hasil Konversi")

        with gr.TabItem("🖼️ Image Tool"):
            with gr.Row():
                with gr.Column():
                    f_img = gr.File(label="Upload Gambar", file_types=["image"])
                with gr.Column():
                    btn_com_i = gr.Button("🗜️ Kompres Gambar", variant="primary")
                    out_img = gr.File(label="Hasil Kompresi")

    with gr.Row():
        btn_reset = gr.Button("🗑️ Reset Tampilan & Hapus Semua", variant="stop")

    gr.Markdown("---")
    gr.Markdown("🔒 *Keamanan: File dihancurkan permanen secara berkala setiap 5 menit.*", elem_classes="footer-info")

    btn_mrg.click(gabung_pdf, f_pdf, out_pdf)
    btn_spl.click(pisah_pdf, [f_pdf, start_h, end_h], out_pdf)
    btn_com_p.click(kompres_pdf_fixed, f_pdf, out_pdf)
    
    btn_p2w.click(pdf_ke_word, f_conv, out_conv)
    btn_p2i.click(pdf_ke_gambar, f_conv, out_conv)
    btn_i2p.click(gambar_ke_pdf, f_conv, out_conv)
    
    btn_com_i.click(kompres_gambar, f_img, out_img)

    def reset_ui():
        return [None]*7 

    btn_reset.click(
        fn=reset_ui, 
        inputs=None, 
        outputs=[f_pdf, f_conv, f_img, out_pdf, out_conv, out_img, f_pdf]
    )

if __name__ == "__main__":
    app.launch(theme=theme, css=css)
