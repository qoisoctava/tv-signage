# Panduan Pembuatan Template HTML

Template HTML adalah cara membuat tampilan iklan kustom yang bisa diisi kontennya melalui form di dashboard — tanpa perlu menyentuh kode setiap kali ingin mengganti teks, gambar, atau warna.

---

## Daftar Isi

1. [Konsep Dasar](#konsep-dasar)
2. [Format Sintaks Field](#format-sintaks-field)
3. [Tipe Field](#tipe-field)
4. [Aturan Nama Field](#aturan-nama-field)
5. [Penggunaan Field di CSS](#penggunaan-field-di-css)
6. [Penggunaan Field di HTML](#penggunaan-field-di-html)
7. [Field Berulang](#field-berulang)
8. [Struktur HTML yang Disarankan](#struktur-html-yang-disarankan)
9. [Contoh Template Lengkap](#contoh-template-lengkap)
10. [Tips & Best Practices](#tips--best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Konsep Dasar

Template HTML adalah file `.html` biasa yang di dalamnya terdapat **placeholder field** dengan format khusus. Saat admin membuat item dari template, sistem akan:

1. Membaca file template dan menemukan semua field
2. Menampilkan form otomatis di dashboard berdasarkan field yang ditemukan
3. Admin mengisi form → sistem mengganti semua placeholder dengan nilai yang diisi
4. Hasil akhirnya disimpan sebagai file HTML statis yang ditampilkan di layar

```
Template HTML (dengan placeholder)
          │
          ▼
    Admin isi form
          │
          ▼
  File HTML generated (siap tampil)
```

---

## Format Sintaks Field

```
{{nama_field:tipe:Label:nilai_default}}
```

| Bagian | Wajib | Keterangan |
|---|---|---|
| `nama_field` | ✓ | Identifier unik, huruf/angka/underscore |
| `tipe` | — | Menentukan input di form. Default: `text` |
| `Label` | — | Teks yang muncul di atas input form. Default: nama field di-*title case* |
| `nilai_default` | — | Nilai awal saat form pertama dibuka |

**Contoh:**

```html
{{judul:text:Judul Utama:Selamat Datang}}
{{deskripsi:textarea:Deskripsi}}
{{gambar_produk:image:Foto Produk}}
{{warna_bg:color:Warna Background:#1a1a2e}}
{{harga:number:Harga:0}}
```

---

## Tipe Field

### `text` — Input teks satu baris

Cocok untuk judul, nama, label pendek, URL, atau nilai CSS non-warna.

```html
<h1>{{judul:text:Judul Iklan:Produk Terbaru}}</h1>
<span class="label">{{kategori:text:Kategori:Unggulan}}</span>
```

Form yang muncul: `<input type="text">`

---

### `textarea` — Input teks multi-baris

Cocok untuk deskripsi, body teks, atau konten yang panjang.

```html
<p>{{deskripsi:textarea:Deskripsi Produk:Masukkan deskripsi di sini.}}</p>
```

Form yang muncul: `<textarea rows="3">`

> **Catatan:** Jika teks mengandung baris baru (`\n`), gunakan `white-space: pre-line` di CSS agar baris baru ditampilkan dengan benar di browser.

---

### `image` — Pilih atau upload gambar

Cocok untuk foto produk, banner, logo, atau ilustrasi. Nilai yang disimpan adalah URL lengkap gambar (misal `/static/uploads/abc123.jpg`).

```html
<img src="{{foto_produk:image:Foto Produk}}" alt="produk">
```

Form yang muncul: grid gambar dari media library + tab upload baru.

> **Penting:** Selalu beri atribut `alt` yang bermakna. Jika gambar belum dipilih, `src` akan kosong dan gambar tidak tampil — desain template dengan mempertimbangkan kondisi ini.

---

### `color` — Color picker

Cocok untuk warna background, teks, border, atau aksen. Nilai yang disimpan dalam format hex (`#rrggbb`).

```html
<style>
  body { background: {{warna_bg:color:Warna Background:#0f172a}}; }
  .aksen { color: {{warna_aksen:color:Warna Aksen:#6366f1}}; }
</style>
```

Form yang muncul: `<input type="color">` dengan preview hex.

> **Catatan:** Field `color` paling berguna ditempatkan di CSS, bukan di atribut HTML.

---

### `number` — Input angka

Cocok untuk harga, jumlah, persentase diskon, atau nilai numerik lain.

```html
<div class="harga">Rp {{harga:number:Harga:0}}</div>
<div class="diskon">Diskon {{diskon:number:Persen Diskon:0}}%</div>
```

Form yang muncul: `<input type="number">`

> **Catatan:** Nilai disimpan sebagai string — format tampilan (titik ribuan, desimal) ditangani di CSS/JS template jika diperlukan.

---

## Aturan Nama Field

- Hanya boleh mengandung huruf, angka, dan underscore (`_`)
- Tidak boleh diawali angka
- **Case-sensitive**: `judul` dan `Judul` dianggap field berbeda
- Jika nama field sama muncul lebih dari satu kali, **hanya definisi pertama** yang dijadikan field — kemunculan berikutnya tetap diganti dengan nilai yang sama

**Nama yang valid:**
```
judul, nama_produk, bg_color, harga2, cta_text
```

**Nama yang tidak valid:**
```
2judul, nama-produk, nama produk, judul!
```

---

## Penggunaan Field di CSS

Field bisa dipakai langsung sebagai nilai properti CSS — ini cara yang paling efektif untuk field tipe `color`.

```html
<style>
  body {
    background-color: {{bg_color:color:Warna Background:#0f172a}};
    color: {{text_color:color:Warna Teks:#ffffff}};
  }

  .tombol {
    background: {{aksen:color:Warna Aksen:#3b82f6}};
    border-radius: {{radius:text:Border Radius:8px}};
  }
</style>
```

> **Perhatian:** Pastikan nilai default yang diberikan adalah nilai CSS yang valid. Untuk field `color`, selalu beri default berupa hex code lengkap (`#rrggbb`).

---

## Penggunaan Field di HTML

Field bisa dipakai di mana saja dalam HTML: sebagai konten elemen, nilai atribut, atau bagian dari teks.

```html
<!-- Sebagai konten elemen -->
<h1>{{judul:text:Judul}}</h1>
<p>{{deskripsi:textarea:Deskripsi}}</p>

<!-- Sebagai nilai atribut -->
<img src="{{gambar:image:Gambar}}" alt="{{judul:text:Judul}}">
<a href="{{link_url:text:URL Tombol:#}}">{{cta:text:Teks Tombol:Klik di sini}}</a>

<!-- Sebagai bagian teks -->
<div class="harga">Rp {{harga:number:Harga:0}},-</div>
<div class="label">{{persen:number:Diskon:0}}% OFF</div>
```

---

## Field Berulang

Jika nama field yang sama muncul **lebih dari satu kali** dalam template, semua kemunculannya akan diganti dengan **nilai yang sama**. Ini berguna untuk nilai seperti warna aksen yang dipakai di beberapa tempat.

```html
<style>
  /* warna_aksen didefinisikan di sini (kemunculan PERTAMA) */
  .tombol { background: {{warna_aksen:color:Warna Aksen:#e63946}}; }
</style>

<body>
  <!-- kemunculan berikutnya: tidak perlu definisi ulang,
       cukup nama field saja — tipe/label/default boleh diisi atau dikosongkan -->
  <h2 style="color: {{warna_aksen}}">{{judul:text:Judul:Judul Iklan}}</h2>
  <span class="badge" style="border-color: {{warna_aksen}}">NEW</span>
</body>
```

Form hanya akan menampilkan **satu input** untuk `warna_aksen`, dan nilainya berlaku untuk semua kemunculan di template.

---

## Struktur HTML yang Disarankan

Template harus dirancang untuk ditampilkan **fullscreen** di layar display. Gunakan struktur berikut sebagai dasar:

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* WAJIB: reset dan fullscreen */
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    html, body {
      width: 100vw;
      height: 100vh;
      overflow: hidden;           /* jangan ada scrollbar */
      font-family: ui-sans-serif, system-ui, sans-serif;
    }

    /* Letakkan style konten di sini */
    body {
      background: {{bg_color:color:Warna Background:#000000}};
      display: flex;
      align-items: center;
      justify-content: center;
    }
  </style>
</head>
<body>
  <!-- Konten iklan di sini -->
</body>
</html>
```

**Yang wajib ada:**
- `width: 100vw; height: 100vh` pada `body`
- `overflow: hidden` — mencegah scrollbar muncul di layar display
- Tidak ada elemen yang keluar dari batas layar

**Yang sebaiknya dihindari:**
- Scroll horizontal atau vertikal
- Font dari Google Fonts atau CDN eksternal (membutuhkan internet)
- JavaScript yang berat atau animasi CPU-intensive
- `position: fixed` tanpa memperhitungkan batas layar

---

## Contoh Template Lengkap

### 1. Template Promo Sederhana

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100vw; height: 100vh; overflow: hidden;
      font-family: ui-sans-serif, system-ui, sans-serif;
      background: {{bg_color:color:Warna Background:#1a1a2e}};
      display: flex; align-items: center; justify-content: center;
    }
    .wrap { text-align: center; padding: 60px; }
    .label {
      font-size: 1rem; font-weight: 600; letter-spacing: 0.15em;
      text-transform: uppercase;
      color: {{aksen:color:Warna Aksen:#e63946}};
      margin-bottom: 20px;
    }
    h1 {
      font-size: 4rem; font-weight: 800; color: #fff;
      line-height: 1.1; letter-spacing: -0.02em;
      margin-bottom: 16px;
    }
    p { font-size: 1.5rem; color: rgba(255,255,255,0.6); margin-bottom: 40px; }
    .cta {
      display: inline-block; padding: 16px 48px;
      background: {{aksen:color:Warna Aksen:#e63946}};
      color: #fff; font-size: 1.125rem; font-weight: 700;
      border-radius: 100px;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <p class="label">{{label:text:Label Atas:Penawaran Terbatas}}</p>
    <h1>{{judul:text:Judul Utama:Diskon 50%}}</h1>
    <p>{{deskripsi:textarea:Deskripsi:Dapatkan penawaran terbaik hari ini.}}</p>
    <div class="cta">{{cta_text:text:Teks Tombol:Beli Sekarang}}</div>
  </div>
</body>
</html>
```

**Field yang dihasilkan:**

| Field | Tipe | Label | Default |
|---|---|---|---|
| `bg_color` | color | Warna Background | `#1a1a2e` |
| `aksen` | color | Warna Aksen | `#e63946` |
| `label` | text | Label Atas | `Penawaran Terbatas` |
| `judul` | text | Judul Utama | `Diskon 50%` |
| `deskripsi` | textarea | Deskripsi | `Dapatkan penawaran...` |
| `cta_text` | text | Teks Tombol | `Beli Sekarang` |

---

### 2. Template Produk dengan Foto

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100vw; height: 100vh; overflow: hidden;
      font-family: ui-sans-serif, system-ui, sans-serif;
      background: {{bg_color:color:Warna Background:#0f172a}};
      display: flex; align-items: center; justify-content: center;
    }
    .layout {
      display: flex; align-items: center;
      gap: 80px; padding: 60px; max-width: 1200px; width: 100%;
    }
    .foto {
      flex-shrink: 0; width: 420px; height: 320px;
      border-radius: 16px; overflow: hidden; background: #1e293b;
    }
    .foto img { width: 100%; height: 100%; object-fit: cover; }
    .konten { flex: 1; }
    .tag {
      display: inline-block; padding: 4px 14px; border-radius: 100px;
      background: {{aksen:color:Warna Aksen:#6366f1}};
      color: #fff; font-size: 0.85rem; font-weight: 600; margin-bottom: 20px;
    }
    h1 {
      font-size: 3rem; font-weight: 800; color: #fff;
      letter-spacing: -0.02em; margin-bottom: 12px;
    }
    p { font-size: 1.125rem; color: rgba(255,255,255,0.55); margin-bottom: 28px; }
    .harga { font-size: 2.5rem; font-weight: 800; color: {{aksen}}; }
  </style>
</head>
<body>
  <div class="layout">
    <div class="foto">
      <img src="{{foto:image:Foto Produk}}" alt="{{nama:text:Nama Produk}}">
    </div>
    <div class="konten">
      <span class="tag">{{tag:text:Tag:Produk Unggulan}}</span>
      <h1>{{nama:text:Nama Produk:Nama Produk Anda}}</h1>
      <p>{{deskripsi:textarea:Deskripsi:Deskripsi singkat produk.}}</p>
      <div class="harga">{{harga:text:Harga:Rp 0}}</div>
    </div>
  </div>
</body>
</html>
```

---

### 3. Template Pengumuman / Running Text

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100vw; height: 100vh; overflow: hidden;
      background: {{bg_color:color:Warna Background:#0a0a0a}};
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      font-family: ui-sans-serif, system-ui, sans-serif;
    }
    .judul-wrap {
      border-left: 6px solid {{aksen:color:Warna Aksen:#f59e0b}};
      padding: 0 0 0 28px; margin-bottom: 32px;
    }
    .kategori {
      font-size: 0.875rem; font-weight: 600; letter-spacing: 0.1em;
      text-transform: uppercase; color: {{aksen}};
      margin-bottom: 10px;
    }
    h1 {
      font-size: 3.5rem; font-weight: 800; color: #fff;
      line-height: 1.1; max-width: 900px;
    }
    .isi {
      font-size: 1.25rem; color: rgba(255,255,255,0.65);
      max-width: 700px; text-align: center; line-height: 1.7;
      white-space: pre-line;
    }
    .tanggal {
      margin-top: 40px; font-size: 0.875rem; color: rgba(255,255,255,0.3);
    }
  </style>
</head>
<body>
  <div class="judul-wrap">
    <p class="kategori">{{kategori:text:Kategori:Pengumuman}}</p>
    <h1>{{judul:text:Judul Pengumuman:Judul Pengumuman}}</h1>
  </div>
  <p class="isi">{{isi:textarea:Isi Pengumuman:Isi pengumuman di sini.}}</p>
  <p class="tanggal">{{tanggal:text:Tanggal:}}</p>
</body>
</html>
```

---

## Tips & Best Practices

### Urutan field = urutan form

Field muncul di form dashboard sesuai urutan kemunculannya di file template. Letakkan field yang paling sering diubah di bagian atas template (misalnya di `<style>` atau awal `<body>`).

### Beri default yang bermakna

Default value membantu admin memahami format yang diharapkan dan mempercepat pengisian form.

```html
<!-- Baik: default jelas -->
{{harga:text:Harga:Rp 150.000}}
{{tanggal:text:Tanggal:31 Desember 2025}}

<!-- Kurang baik: default kosong, admin bingung format yang diharapkan -->
{{harga:text:Harga}}
```

### Gunakan field `color` untuk tema

Alih-alih hardcode warna di seluruh CSS, definisikan warna sebagai field di awal `<style>` dan pakai ulang melalui mekanisme field berulang.

```html
<style>
  /* Definisi warna sebagai field */
  :root {
    --aksen: {{aksen:color:Warna Aksen:#3b82f6}};
    --bg: {{bg:color:Background:#0f172a}};
  }
  /* Pakai variabel CSS — lebih bersih dari field berulang */
  .tombol { background: var(--aksen); }
  .border  { border-color: var(--aksen); }
  body     { background: var(--bg); }
</style>
```

> Ini adalah cara terbaik untuk field warna yang dipakai banyak elemen: definisikan sekali sebagai CSS variable, pakai via `var(--nama)` di seluruh CSS.

### Hindari dependensi eksternal

Template dirender secara lokal tanpa koneksi internet. Hindari:

```html
<!-- Jangan: butuh internet -->
<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/..."></script>

<!-- Aman: font sistem -->
font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
font-family: ui-serif, Georgia, serif;
font-family: ui-monospace, monospace;
```

### Pastikan teks terbaca dari jarak jauh

Layar display biasanya dilihat dari jarak 1–3 meter. Gunakan ukuran font yang besar:

| Elemen | Ukuran minimum yang disarankan |
|---|---|
| Judul utama | `2.5rem` (40px) |
| Subjudul | `1.5rem` (24px) |
| Body text | `1.125rem` (18px) |
| Label kecil | `0.875rem` (14px) |

---

## Troubleshooting

### Field tidak muncul di form dashboard

Kemungkinan penyebab:
- Nama field mengandung karakter yang tidak valid (spasi, tanda hubung, dll.)
- Sintaks field tidak lengkap atau salah (misal tanda `{{` tidak ditutup dengan `}}`)
- Tipe yang ditulis tidak dikenali — sistem akan fallback ke `text`, periksa ejaan

### Nilai tidak terganti di hasil generate

- Pastikan nama field di template sama persis dengan yang tersimpan (case-sensitive)
- Jika field gambar kosong, atribut `src` pada `<img>` akan kosong — gambar tidak tampil, ini normal

### Tampilan berantakan di layar

- Pastikan ada `overflow: hidden` di `body`
- Cek apakah ada elemen yang lebar/tingginya melebihi 100vw/100vh
- Uji di resolusi yang sama dengan layar display target (misal 1920×1080)

### File generated tidak diperbarui setelah edit

Klik tombol **Edit** pada item di dashboard, ubah nilai field, lalu **Simpan** — sistem akan otomatis regenerate file. Atau gunakan endpoint `POST /api/items/{id}/regenerate` secara manual.
