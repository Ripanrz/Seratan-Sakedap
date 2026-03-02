# 📄 Seratan Sakedap - Secure Zero-Retention PDF Utility

[![Live Demo on Hugging Face](https://img.shields.io/badge/Live%20Demo-%F0%9F%A4%97%20Hugging%20Face-blue?style=for-the-badge)](https://huggingface.co/spaces/Ripanrz/Seratan-Sakedap)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Security](https://img.shields.io/badge/Security-Secure_Wipe_Protocol-red)
![PyPDF](https://img.shields.io/badge/Library-PyPDF_&_PyMuPDF-green)
![Gradio](https://img.shields.io/badge/UI-Gradio-lightgrey)

**Pernahkah Anda merasa khawatir saat mengunggah dokumen pribadi atau rahasia (seperti KTP, CV, kontrak kerja, atau data finansial) ke situs konverter PDF publik?** Sebagian besar platform gratis tidak memberikan transparansi mengenai kapan dan bagaimana data Anda benar-benar dihapus dari *server* mereka.

Berangkat dari kekhawatiran (*privacy concerns*) tersebut, **Seratan Sakedap** (berasal dari Bahasa Sunda yang berarti *"Dokumen Sementara"*) dibangun. Ini adalah aplikasi utilitas dokumen berbasis web yang mengedepankan prinsip **Privacy by Design** dan **Zero-Retention Data**. Sistem ini dilengkapi dengan protokol penghancur data otomatis (*background thread daemon*) yang menjamin setiap file pengguna dihancurkan secara permanen dalam waktu maksimal 5 menit setelah diproses.

---

## 🚀 Fitur Utama

Aplikasi ini tidak hanya aman, tetapi juga menyediakan *suite* lengkap untuk produktivitas dokumen Anda:

* 🛡️ **Military-Grade Auto-Delete (Secure Wipe)**: Sistem secara asinkron menimpa isi file Anda dengan deretan kode acak (*random bytes*) sebelum menghapusnya secara fisik (`os.remove`). File tidak akan bisa dikembalikan (*recovery*) oleh *software* pemulihan data apa pun.
* 🗜️ **Kompresi Pintar**: Mengurangi ukuran file **PDF** tanpa merusak kualitas visual, serta kompresi **Gambar (JPG/PNG)** dengan penyesuaian kualitas yang optimal.
* 🔄 **Konversi Universal**: 
  * **PDF ke Word**: Ekstrak dokumen PDF menjadi format Word (`.docx`) yang sepenuhnya dapat diedit.
  * **PDF ke Gambar**: Ubah halaman PDF menjadi kumpulan gambar berkualitas tinggi.
  * **Gambar ke PDF**: Susun tumpukan gambar menjadi satu file PDF yang rapi.
* ✂️ **Manajemen Halaman**: **Gabung (Merge)** beberapa file PDF menjadi satu, atau **Pisah (Split)** halaman spesifik dari dokumen yang besar.
* 🧹 **One-Click Reset Workspace**: Tombol instan untuk menghapus semua *input* dan *output* dari layar UI untuk transisi tugas yang cepat.

---

## 🔁 Arsitektur Keamanan (Asynchronous Pipeline)

Sistem pemrosesan file dan sistem keamanan berjalan secara paralel (*multithreading*) agar performa antarmuka pengguna tidak mengalami perlambatan (*lag*).

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
