# Signage

Sistem digital signage berbasis web untuk menampilkan konten iklan — gambar, video, dan HTML kustom — di satu atau banyak layar melalui jaringan lokal (LAN).

## Fitur

- **Media library** — upload dan kelola file gambar dan video
- **Template HTML** — buat layout iklan kustom dengan field yang bisa diisi via form, tanpa menyentuh kode
- **Item** — unit konten yang bisa berupa media maupun HTML hasil dari template
- **Channel & Playlist** — atur channel per layar, susun urutan item, set durasi tampil
- **Display fullscreen** — buka `/display-{slug}` di browser layar mana pun, konten loop otomatis
- **Live update** — perubahan playlist dari dashboard langsung terefleksi di layar dalam 10 detik

## Tech Stack

- **Backend** — Python, Flask, SQLAlchemy, SQLite
- **Frontend** — Alpine.js, Tailwind CSS, SortableJS
- **Deployment** — self-hosted, cocok untuk LAN / intranet

## Cara Menjalankan

```bash
pip install -r requirements.txt
python app.py
```

Buka `http://localhost:5500/dashboard`

Dokumentasi lengkap tersedia di [`docs/SYSTEM.md`](docs/SYSTEM.md) dan panduan pembuatan template di [`docs/TEMPLATE_GUIDE.md`](docs/TEMPLATE_GUIDE.md).

## Status

> ⚠️ **Project ini masih dalam tahap pengembangan aktif.** Belum direkomendasikan untuk lingkungan produksi. Struktur database, API, dan antarmuka dapat berubah sewaktu-waktu tanpa pemberitahuan sebelumnya.

## Keterlibatan AI

Project ini dikembangkan dengan keterlibatan signifikan dari [Claude](https://claude.ai) (Anthropic) — mulai dari perancangan arsitektur, skema database, implementasi backend dan frontend, hingga penulisan dokumentasi. Kode di-*review* dan diarahkan oleh developer manusia.
