# ⏱️ Seratan Sakedap - Secure Zero-Retention PDF Utility

[![Live Demo on Hugging Face](https://img.shields.io/badge/Live%20Demo-%F0%9F%A4%97%20Hugging%20Face-blue?style=for-the-badge)](https://huggingface.co/spaces/Ripanrz/Seratan-Sakedap)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Security](https://img.shields.io/badge/Security-Secure_Wipe_Protocol-red)
![PyPDF](https://img.shields.io/badge/Library-PyPDF_&_PyMuPDF-green)
![Gradio](https://img.shields.io/badge/UI-Gradio-lightgrey)
![Hugging Face](https://img.shields.io/badge/Deployment-Hugging_Face_Spaces-purple)

**Pernahkah Anda merasa khawatir saat mengunggah dokumen pribadi atau rahasia (seperti KTP, CV, kontrak kerja, atau data finansial) ke situs konverter PDF publik?** Sebagian besar platform gratis tidak memberikan transparansi mengenai kapan dan bagaimana data Anda benar-benar dihapus dari *server* mereka.

Berangkat dari kekhawatiran (*privacy concerns*) tersebut, **Seratan Sakedap** (berasal dari Bahasa Sunda yang berarti *"Dokumen Sementara"*) dibangun. Ini adalah aplikasi utilitas PDF berbasis web yang mengedepankan prinsip **Privacy by Design** dan **Zero-Retention Data**. Sistem ini dilengkapi dengan protokol penghancur data otomatis (*background thread daemon*) yang menjamin setiap file pengguna dihancurkan secara permanen dalam waktu maksimal 5 menit setelah diproses.

---

## 📸 Tampilan Dashboard

> *Antarmuka yang bersih dan interaktif dengan tab navigasi, dirancang untuk memproses dokumen dengan cepat tanpa meninggalkan jejak.*

![Tampilan Dashboard](SeratanSakedap/Dashboard_Utilitas.png)
*(Catatan: Ganti dengan path screenshot aplikasi Anda)*

---

## 🚀 Fitur Utama & Protokol Keamanan

* 🛡️ **Military-Grade Auto-Delete (Secure Wipe)**: Ini bukan sekadar fungsi hapus (`os.remove`) biasa. Sistem secara asinkron akan menimpa isi file Anda dengan deretan kode acak (*random bytes*) sebelum menghapusnya secara fisik. File tidak akan bisa dikembalikan (*recovery*) oleh *software* apa pun.
* 🗜️ **Kompresi PDF Cerdas**: Mengurangi ukuran file PDF dengan mengoptimalkan struktur *deflate* dan *garbage collection* tanpa merusak kualitas dokumen.
* 🔗 **Gabung PDF (Merge)**: Menggabungkan beberapa file PDF terpisah menjadi satu dokumen utuh yang rapi.
* ✂️ **Pisah PDF (Split)**: Mengekstrak halaman spesifik dari sebuah dokumen PDF besar dengan cepat.
* 📝 **PDF to Word**: Mengonversi dokumen PDF menjadi format Word (`.docx`) yang sepenuhnya dapat diedit.
* 🖼️ **Image to PDF**: Mengonversi tumpukan gambar (JPG/PNG) dan menyusunnya menjadi satu file PDF.

---

## 🔁 Arsitektur Keamanan (Asynchronous Pipeline)

Sistem pemrosesan file dan sistem keamanan berjalan secara paralel (*multithreading*) agar antrean pengguna tidak mengalami *lag*.

```mermaid
graph TD
    subgraph user_flow [User Flow]
        A[Upload Dokumen] --> B{Pilih Utilitas PDF}
        B -->|Kompres/Gabung/Pisah/Convert| C[Proses via PyPDF/PyMuPDF]
        C --> D[File Output Dihasilkan]
        D --> E[User Download Hasil]
    end

    subgraph security_daemon [Security Daemon - Background Thread]
        F((Timer 60 Detik)) --> G{Cek Umur File di Server}
        G -->|Umur < 5 Menit| F
        G -->|Umur > 5 Menit| H[Generate Random Bytes]
        H --> I[Timpa Isi File Asli & Output]
        I --> J[Hapus Fisik dari Server os.remove]
        J --> K((File Lenyap Permanen))
    end
    
    C -.->|Simpan Sementara| G
