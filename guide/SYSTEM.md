# Signage — Dokumentasi Teknis Sistem

Sistem digital signage berbasis web untuk menampilkan konten iklan (gambar, video, dan HTML kustom) di satu atau banyak layar melalui jaringan lokal (LAN).

---

## Daftar Isi

1. [Arsitektur Sistem](#arsitektur-sistem)
2. [Struktur Direktori](#struktur-direktori)
3. [Skema Database](#skema-database)
4. [Modul Core](#modul-core)
5. [API Reference](#api-reference)
6. [Halaman Dashboard](#halaman-dashboard)
7. [Display Player](#display-player)
8. [Konfigurasi](#konfigurasi)
9. [Instalasi & Menjalankan](#instalasi--menjalankan)
10. [Deployment Lokal (LAN)](#deployment-lokal-lan)

---

## Arsitektur Sistem

```
[ PC / Server ]                    [ LAN ]
┌──────────────────────┐
│  Flask App :5500     │ ◄────────── Browser (Dashboard)
│                      │            http://192.168.x.x:5500/dashboard
│  ┌────────────────┐  │
│  │  SQLite DB     │  │ ◄────────── TV / Monitor 1
│  └────────────────┘  │            http://192.168.x.x:5500/display-lobby
│  ┌────────────────┐  │
│  │  static/       │  │ ◄────────── TV / Monitor 2
│  │  uploads/      │  │            http://192.168.x.x:5500/display-lantai2
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ generated_     │  │
│  │ items/         │  │
│  └────────────────┘  │
└──────────────────────┘
```

**Alur kerja umum:**

1. Admin upload media atau template HTML via `/dashboard`
2. Admin membuat **Item** — bisa berupa media (gambar/video) atau HTML dari template
3. Admin membuat **Channel** dan menyusun **Playlist** berisi item-item tersebut
4. Layar display membuka `/display-{slug}` di browser fullscreen
5. Display player otomatis loop playlist, polling update setiap 10 detik

---

## Struktur Direktori

```
signage/
├── app.py                      # Entry point, factory function create_app()
├── config.py                   # Konfigurasi path, ekstensi, secret key
├── requirements.txt
├── database.db                 # SQLite database (auto-created)
│
├── core/
│   ├── models.py               # SQLAlchemy models (5 tabel)
│   ├── template_parser.py      # Parser field {{...}} dari template HTML
│   ├── item_generator.py       # Generate & hapus file HTML statis
│   └── file_manager.py         # Upload, validasi, hapus file media
│
├── routes/
│   ├── dashboard.py            # Route halaman dashboard (render HTML)
│   ├── display.py              # Route /display-{slug}
│   └── api.py                  # Semua REST API endpoint
│
├── templates/
│   ├── dashboard/
│   │   ├── base.html           # Layout dasar (sidebar, topbar, breadcrumb)
│   │   ├── index.html          # Halaman utama dashboard
│   │   ├── media.html          # Media library
│   │   ├── templates.html      # Kelola template HTML
│   │   ├── items.html          # Kelola items
│   │   ├── channels.html       # Kelola channels
│   │   └── playlist.html       # Kelola playlist per channel
│   ├── display/
│   │   ├── index.html          # Display player fullscreen
│   │   └── 404.html            # Halaman 404 khusus display
│   └── errors/
│       └── 404.html            # Halaman 404 umum
│
├── static/
│   └── uploads/                # File media yang diupload (gambar/video)
│
├── signage_templates/          # File HTML template mentah (belum digenerate)
│   ├── promo_basic.html
│   └── produk_feature.html
│
└── generated_items/            # File HTML statis hasil generate dari template
    └── item_1_a3b4c5d6.html
```

---

## Skema Database

### Tabel `media_files`

Menyimpan metadata file gambar dan video yang diupload.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `name` | TEXT | Nama asli file (display) |
| `filename` | TEXT | Nama file di disk (UUID-based) |
| `type` | TEXT | `image` atau `video` |
| `path` | TEXT | Path relatif dari `static/` |
| `size` | INTEGER | Ukuran file dalam bytes |
| `created_at` | DATETIME | |

### Tabel `template_files`

Menyimpan referensi ke file template HTML di `signage_templates/`.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `name` | TEXT | Nama display template |
| `filename` | TEXT | Nama file di `signage_templates/` |
| `description` | TEXT | Deskripsi opsional |
| `created_at` | DATETIME | |

### Tabel `items`

Unit konten yang bisa dimasukkan ke playlist. Bisa berupa media atau HTML.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `name` | TEXT | Nama item |
| `type` | TEXT | `media` atau `html` |
| `media_id` | INTEGER FK | Referensi ke `media_files` (jika type=media) |
| `template_id` | INTEGER FK | Referensi ke `template_files` (jika type=html) |
| `field_data` | JSON | Hasil isian form field template |
| `generated_file` | TEXT | Nama file hasil generate di `generated_items/` |
| `created_at` | DATETIME | |
| `updated_at` | DATETIME | Auto-update saat item diedit |

### Tabel `channels`

Representasi satu layar display dengan playlist-nya sendiri.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `name` | TEXT | Nama channel |
| `slug` | TEXT UNIQUE | Identifier URL, misal `lobby` → `/display-lobby` |
| `created_at` | DATETIME | |

### Tabel `playlist_items`

Relasi many-to-many antara channel dan item, beserta urutan dan durasi.

| Kolom | Tipe | Keterangan |
|---|---|---|
| `id` | INTEGER PK | |
| `channel_id` | INTEGER FK | Referensi ke `channels` |
| `item_id` | INTEGER FK | Referensi ke `items` |
| `order` | INTEGER | Urutan tampil (0-based) |
| `duration` | INTEGER | Durasi tampil dalam detik. `NULL` = auto (khusus video) |

### Relasi antar tabel

```
media_files ──┐
              ├──► items ──► playlist_items ◄── channels
template_files─┘
```

---

## Modul Core

### `core/template_parser.py`

Membaca file HTML template dan mengekstrak definisi field dari sintaks `{{...}}`.

**Fungsi utama:**

```python
parse_fields(html_content: str) -> list[dict]
```
Mengekstrak semua field dari string HTML. Return list dict berurutan sesuai kemunculan di template. Field dengan nama duplikat diabaikan (diambil yang pertama).

```python
render_template(html_content: str, field_data: dict) -> str
```
Mengganti semua `{{field...}}` dengan nilai dari `field_data`. Jika field tidak ada di `field_data`, digunakan nilai `default` dari definisi field.

```python
parse_template_file(filepath: str) -> tuple[str | None, list]
```
Shortcut: baca file lalu langsung parse. Return `(html_content, fields)` atau `(None, [])` jika file tidak ada.

---

### `core/item_generator.py`

Menghasilkan file HTML statis dari template + data field, dan menyimpannya ke `generated_items/`.

**Fungsi utama:**

```python
generate_item_file(item: Item, html_content=None) -> str | None
```
Generate file HTML untuk item bertipe `html`. Jika `html_content` tidak diberikan, dibaca dari template file di disk. File lama otomatis dihapus sebelum file baru dibuat. Return nama file yang disimpan, atau `None` jika gagal.

```python
delete_generated_file(filename: str)
```
Hapus file dari `generated_items/`.

```python
get_generated_url(filename: str) -> str | None
```
Return URL untuk mengakses file generated, misal `/generated/item_1_abc123.html`.

---

### `core/file_manager.py`

Menangani upload, validasi, dan penghapusan file media.

**Fungsi utama:**

```python
save_upload(file: FileStorage) -> dict | None
```
Validasi ekstensi, simpan dengan nama UUID, return metadata `{filename, original_name, path, type, size}`.

```python
delete_upload(path: str) -> bool
```
Hapus file dari disk berdasarkan path relatif dari `static/`.

**Ekstensi yang diizinkan:**

| Tipe | Ekstensi |
|---|---|
| Image | `png`, `jpg`, `jpeg`, `gif`, `webp` |
| Video | `mp4`, `webm`, `mov` |

Batas ukuran upload: **200 MB** per file.

---

## API Reference

Base URL: `http://localhost:5500/api`

### Status

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/status` | Jumlah media, template, item, channel |

### Media

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/media` | List semua media. Query param: `?type=image\|video` |
| POST | `/media/upload` | Upload file. Form-data: `files` (multi) |
| DELETE | `/media/{id}` | Hapus media. Gagal jika masih dipakai item |

### Templates

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/templates` | List semua template terdaftar |
| POST | `/templates` | Daftarkan file yang sudah ada di disk |
| POST | `/templates/upload` | Upload file HTML baru dan daftarkan |
| GET | `/templates/{id}/fields` | Parse dan return daftar field |
| GET | `/templates/scan` | List file `.html` di `signage_templates/` yang belum terdaftar |
| DELETE | `/templates/{id}` | Hapus template dan file-nya |

### Items

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/items` | List semua item |
| POST | `/items` | Buat item baru. Body: `{name, type, media_id?, template_id?, field_data?}` |
| GET | `/items/{id}` | Detail item |
| PUT | `/items/{id}` | Edit item, regenerate file jika tipe HTML |
| DELETE | `/items/{id}` | Hapus item + file generated |
| POST | `/items/{id}/regenerate` | Paksa regenerate file (khusus tipe HTML) |

### Channels

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/channels` | List semua channel |
| POST | `/channels` | Buat channel. Body: `{name, slug?}`. Slug auto-generate jika kosong |
| PUT | `/channels/{id}` | Update nama channel |
| DELETE | `/channels/{id}` | Hapus channel + seluruh playlist-nya |

### Playlist

| Method | Endpoint | Keterangan |
|---|---|---|
| GET | `/channels/{id}/playlist` | Ambil playlist beserta detail item |
| POST | `/channels/{id}/playlist` | Tambah item. Body: `{item_id, duration?}` |
| PUT | `/channels/{id}/playlist` | Simpan urutan & durasi. Body: `[{playlist_item_id, order, duration}]` |
| DELETE | `/channels/{id}/playlist/{pi_id}` | Hapus item dari playlist |
| GET | `/channels/by-slug/{slug}/playlist` | Ambil playlist via slug (dipakai display player) |

---

## Halaman Dashboard

| URL | Keterangan |
|---|---|
| `/dashboard` | Halaman utama, stat counts + channel aktif |
| `/dashboard/media` | Upload dan kelola file media |
| `/dashboard/templates` | Upload dan kelola template HTML |
| `/dashboard/items` | Buat dan kelola items |
| `/dashboard/channels` | Buat dan kelola channels |
| `/dashboard/channels/{id}/playlist` | Susun playlist per channel (drag & drop) |

**Stack frontend dashboard:**
- Tailwind CSS 3.4.17 (CDN, tidak perlu build step)
- Alpine.js 3.14.1 (reaktivitas form dan UI)
- SortableJS 1.15.2 (drag & drop playlist)

---

## Display Player

URL: `/display-{slug}`

File template: `templates/display/index.html`

**Cara kerja:**

1. Halaman load, fetch playlist via `/api/channels/by-slug/{slug}/playlist`
2. Bangun slot DOM untuk setiap item (`<img>`, `<video>`, atau `<iframe>`)
3. Tampilkan item satu per satu secara berurutan dengan transisi fade 0.5s
4. Durasi per item:
   - **Gambar / HTML**: sesuai nilai `duration` di playlist (detik)
   - **Video**: tunggu event `ended` dari elemen `<video>`, `duration` diabaikan
5. Setelah item terakhir, kembali ke item pertama (infinite loop)
6. Polling ke API setiap **10 detik** — jika playlist berubah, langsung rebuild dan lanjutkan dari posisi terdekat

**Ketentuan tampilan:**
- Background: hitam (`#000`)
- Media (`<img>`, `<video>`): `object-fit: contain`, tidak stretch, centered
- HTML item: ditampilkan via `<iframe>` 100vw × 100vh
- Tidak ada overlay, progress bar, atau UI apapun yang terlihat

**Halaman 404 display** (`templates/display/404.html`): ditampilkan jika slug tidak ditemukan, menggunakan latar gelap tanpa elemen UI apapun — agar tidak mencolok di layar display.

---

## Konfigurasi

File: `config.py`

| Variabel | Default | Keterangan |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-...` | Ganti di production via env var |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///database.db` | Path database SQLite |
| `UPLOAD_FOLDER` | `static/uploads/` | Direktori file media |
| `TEMPLATES_STORE` | `signage_templates/` | Direktori template HTML mentah |
| `GENERATED_ITEMS` | `generated_items/` | Direktori file HTML generated |
| `MAX_CONTENT_LENGTH` | 200 MB | Batas ukuran upload |

Untuk mengubah `SECRET_KEY` via environment variable:

```bash
export SECRET_KEY="kunci-rahasia-anda"
python app.py
```

---

## Instalasi & Menjalankan

**Prasyarat:** Python 3.10+

```bash
# 1. Clone / ekstrak project
cd signage

# 2. (Opsional) Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan
python app.py
```

Buka browser: `http://localhost:5500/dashboard`

---

## Deployment Lokal (LAN)

### 1. Set IP statis di router

Agar alamat server tidak berubah saat restart, set DHCP reservation berdasarkan MAC address server di pengaturan router. Contoh: `192.168.1.100`.

### 2. Akses dari device lain

Dashboard dari PC manapun di jaringan:
```
http://192.168.1.100:5500/dashboard
```

Display dari TV / monitor:
```
http://192.168.1.100:5500/display-lobby
```

### 3. Jalankan otomatis saat boot (Linux/systemd)

Buat file service `/etc/systemd/system/signage.service`:

```ini
[Unit]
Description=Signage App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/signage
ExecStart=/home/pi/signage/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Aktifkan:

```bash
sudo systemctl enable signage
sudo systemctl start signage
```

### 4. Mode kiosk di display device

**Linux / Raspberry Pi:**
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars \
  http://192.168.1.100:5500/display-lobby
```

**Windows:**
```
chrome.exe --kiosk http://192.168.1.100:5500/display-lobby
```

Untuk autostart, tambahkan command di atas ke startup script / task scheduler.

---

## Dependencies

| Package | Versi | Keterangan |
|---|---|---|
| Flask | ≥3.0.0 | Web framework |
| Flask-SQLAlchemy | ≥3.1.0 | ORM dan koneksi database |
| SQLAlchemy | ≥2.0.0 | Query builder |
| Pillow | ≥10.0.0 | Validasi file gambar (opsional, siap dipakai) |
| python-dotenv | ≥1.0.0 | Load env vars dari `.env` |
| Werkzeug | (bawaan Flask) | File upload handling |
