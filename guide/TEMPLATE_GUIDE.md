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
8. [Animasi](#animasi)
9. [Struktur HTML yang Disarankan](#struktur-html-yang-disarankan)
10. [Contoh Template Lengkap](#contoh-template-lengkap)
11. [Tips & Best Practices](#tips--best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Konsep Dasar

Template HTML adalah **satu file `.html` tunggal** yang di dalamnya terdapat **placeholder field** dengan format khusus. CSS dan JavaScript ditulis langsung di dalam file yang sama — tidak ada file eksternal.

Saat admin membuat item dari template, sistem akan:

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
  File HTML generated (siap tampil di layar)
```

### Penting: Template adalah konten pasif

Template dirancang untuk **ditonton, bukan diinteraksikan**. Tidak ada pengguna yang mengklik, mengetik, atau berinteraksi dengan layar display. Oleh karena itu:

- **Tidak perlu tombol (button)** — tidak ada aksi yang bisa diklik
- **Tidak perlu form input** — isian sudah ditentukan saat membuat item di dashboard
- **Tidak perlu hover effect** — layar hanya dilihat dari jarak jauh
- **Fokus pada visual** — animasi, tipografi besar, dan warna yang menarik perhatian

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

Cocok untuk judul, nama, label pendek, atau nilai CSS non-warna.

```html
<h1>{{judul:text:Judul Iklan:Produk Terbaru}}</h1>
<span class="label">{{kategori:text:Kategori:Unggulan}}</span>
```

---

### `textarea` — Input teks multi-baris

Cocok untuk deskripsi, body teks, atau konten panjang.

```html
<p>{{deskripsi:textarea:Deskripsi Produk:Masukkan deskripsi di sini.}}</p>
```

> **Catatan:** Tambahkan `white-space: pre-line` di CSS agar baris baru dari textarea ditampilkan dengan benar di browser.

---

### `image` — Pilih atau upload gambar

Nilai yang disimpan adalah URL gambar (misal `/static/uploads/abc123.jpg`).

```html
<img src="{{foto_produk:image:Foto Produk}}" alt="produk">
```

Form yang muncul: grid gambar dari media library + tab upload baru.

> **Catatan:** Jika field gambar belum dipilih, atribut `src` kosong dan gambar tidak tampil. Rancang template dengan mempertimbangkan kondisi ini.

---

### `color` — Color picker

Nilai disimpan dalam format hex (`#rrggbb`). Paling berguna dipakai di CSS.

```html
<style>
  body { background: {{warna_bg:color:Warna Background:#0f172a}}; }
  .aksen { color: {{warna_aksen:color:Warna Aksen:#6366f1}}; }
</style>
```

---

### `number` — Input angka

Cocok untuk harga, persentase diskon, atau nilai numerik lain.

```html
<div class="harga">Rp {{harga:number:Harga:0}}</div>
<div class="diskon">Diskon {{diskon:number:Persen Diskon:0}}%</div>
```

---

## Aturan Nama Field

- Hanya boleh mengandung huruf, angka, dan underscore (`_`)
- Tidak boleh diawali angka
- **Case-sensitive**: `judul` dan `Judul` dianggap field berbeda
- Jika nama field sama muncul lebih dari satu kali, **hanya definisi pertama** yang dijadikan field — kemunculan berikutnya tetap diganti dengan nilai yang sama

**Valid:** `judul`, `nama_produk`, `bg_color`, `harga2`  
**Tidak valid:** `2judul`, `nama-produk`, `nama produk`, `judul!`

---

## Penggunaan Field di CSS

```html
<style>
  :root {
    --aksen: {{aksen:color:Warna Aksen:#3b82f6}};
    --bg:    {{bg:color:Background:#0f172a}};
  }
  body      { background: var(--bg); }
  .sorot    { color: var(--aksen); }
  .badge    { background: var(--aksen); }
</style>
```

Mendefinisikan field warna sebagai CSS variable di `:root` adalah cara terbersih — field cukup dideklarasikan satu kali, lalu dipakai berulang via `var(--nama)` tanpa perlu menduplikasi sintaks `{{...}}`.

---

## Penggunaan Field di HTML

Field bisa dipakai di mana saja: konten elemen, nilai atribut, atau bagian dari teks.

```html
<!-- Konten elemen -->
<h1>{{judul:text:Judul}}</h1>
<p>{{deskripsi:textarea:Deskripsi}}</p>

<!-- Nilai atribut -->
<img src="{{gambar:image:Gambar}}" alt="{{judul}}">

<!-- Bagian dari teks -->
<div class="harga">Rp {{harga:number:Harga:0}},-</div>
<div class="badge">{{persen:number:Diskon:0}}% OFF</div>
```

---

## Field Berulang

Nama field yang muncul lebih dari satu kali akan diganti dengan **nilai yang sama**. Definisi (tipe/label/default) cukup ditulis pada kemunculan pertama.

```html
<style>
  /* definisi PERTAMA — tipe, label, dan default ditulis di sini */
  .badge { background: {{aksen:color:Warna Aksen:#e63946}}; }
</style>
<body>
  <!-- kemunculan berikutnya — cukup nama field -->
  <h2 style="color: {{aksen}}">{{judul:text:Judul:Judul Iklan}}</h2>
  <div style="border-color: {{aksen}}">NEW</div>
</body>
```

Form hanya menampilkan **satu input** untuk `aksen`, berlaku untuk semua kemunculan.

---

## Animasi

Karena tidak ada interaksi pengguna, **animasi CSS looping** adalah cara utama membuat tampilan terasa hidup dan menarik perhatian. Gunakan `@keyframes` dengan `animation-iteration-count: infinite`.

### Animasi yang disarankan

**Fade in konten saat tampil:**

```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}

.judul    { animation: fadeUp 0.8s ease both; }
.subjudul { animation: fadeUp 0.8s 0.15s ease both; }
.harga    { animation: fadeUp 0.8s 0.3s ease both; }
```

**Pulse — efek denyut pada elemen penting:**

```css
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(1.04); }
}
.badge { animation: pulse 2s ease-in-out infinite; }
```

**Float — melayang naik turun:**

```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-12px); }
}
.gambar-produk { animation: float 3s ease-in-out infinite; }
```

**Shimmer — kilap pada teks atau border:**

```css
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
.judul {
  background: linear-gradient(90deg, #fff 25%, #f59e0b 50%, #fff 75%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shimmer 3s linear infinite;
}
```

**Marquee — teks berjalan (cocok untuk pengumuman):**

```css
@keyframes marquee {
  from { transform: translateX(100vw); }
  to   { transform: translateX(-100%); }
}
.teks-berjalan {
  white-space: nowrap;
  animation: marquee 12s linear infinite;
}
```

**Rotate — elemen berputar pelan:**

```css
@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
.dekorasi { animation: rotate-slow 20s linear infinite; }
```

### Stagger — animasi berurutan

Untuk membuat elemen muncul bergantian, gunakan `animation-delay` yang meningkat:

```css
.item:nth-child(1) { animation-delay: 0s;    }
.item:nth-child(2) { animation-delay: 0.15s; }
.item:nth-child(3) { animation-delay: 0.3s;  }
.item:nth-child(4) { animation-delay: 0.45s; }
```

### Animasi dengan JavaScript

JavaScript boleh digunakan untuk animasi yang lebih kompleks — misalnya counter angka, efek partikel, atau perpindahan konten:

```html
<script>
  // Contoh: counter angka animasi
  function animateCount(el, target, duration) {
    const start = performance.now();
    function step(now) {
      const progress = Math.min((now - start) / duration, 1);
      el.textContent = Math.floor(progress * target).toLocaleString('id-ID');
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  const el = document.getElementById('angka');
  animateCount(el, 1500000, 2000); // hitung dari 0 ke 1.500.000 dalam 2 detik
</script>
```

> **Catatan:** Hindari animasi yang sangat berat (Three.js, canvas dengan banyak partikel) pada hardware display yang terbatas seperti Raspberry Pi.

---

## Struktur HTML yang Disarankan

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    /* ── RESET & FULLSCREEN (wajib) ── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body {
      width: 100vw;
      height: 100vh;
      overflow: hidden;    /* tidak ada scrollbar */
      font-family: ui-sans-serif, system-ui, sans-serif;
      background: {{bg:color:Warna Background:#0f172a}};
    }

    /* ── LAYOUT ── */
    body {
      display: flex;
      align-items: center;
      justify-content: center;
    }

    /* ── ANIMASI ── */
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(20px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    /* ── KONTEN ── */
    .wrap { text-align: center; }
    h1 {
      font-size: 4rem; color: #fff;
      animation: fadeUp 0.8s ease both;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>{{judul:text:Judul:Judul Iklan}}</h1>
  </div>

  <!-- JavaScript (opsional, inline) -->
  <script>
    // animasi atau logika tambahan di sini
  </script>
</body>
</html>
```

**Yang wajib:**
- `width: 100vw; height: 100vh` pada `body`
- `overflow: hidden` — mencegah scrollbar
- Semua CSS dan JS di dalam satu file yang sama

**Yang harus dihindari:**
- Elemen interaktif: `<button>`, `<input>`, `<select>`, `<a href>` yang terlihat sebagai tombol
- Scroll vertikal atau horizontal
- File CSS/JS eksternal (butuh internet atau path absolut yang mungkin tidak valid)
- `alert()`, `prompt()`, `confirm()` di JavaScript

---

## Contoh Template Lengkap

### 1. Promo dengan Animasi Fade & Pulse

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
      background: {{bg:color:Warna Background:#0d0d1a}};
      display: flex; align-items: center; justify-content: center;
    }

    :root { --aksen: {{aksen:color:Warna Aksen:#e63946}}; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(32px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 color-mix(in srgb, var(--aksen) 40%, transparent); }
      50%       { transform: scale(1.03); box-shadow: 0 0 0 16px transparent; }
    }

    .wrap { text-align: center; padding: 60px; max-width: 900px; }
    .label {
      font-size: 0.9rem; font-weight: 700; letter-spacing: 0.2em;
      text-transform: uppercase; color: var(--aksen);
      margin-bottom: 20px;
      animation: fadeUp 0.6s ease both;
    }
    h1 {
      font-size: 5rem; font-weight: 900; color: #fff;
      line-height: 1.05; letter-spacing: -0.03em; margin-bottom: 20px;
      animation: fadeUp 0.6s 0.1s ease both;
    }
    p {
      font-size: 1.4rem; color: rgba(255,255,255,0.55);
      margin-bottom: 48px; line-height: 1.6;
      animation: fadeUp 0.6s 0.2s ease both;
    }
    .badge {
      display: inline-block; padding: 16px 52px;
      background: var(--aksen); color: #fff;
      font-size: 1.25rem; font-weight: 800; border-radius: 100px;
      animation: fadeUp 0.6s 0.3s ease both, pulse 2.5s 1s ease-in-out infinite;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <p class="label">{{label:text:Label Atas:Penawaran Terbatas}}</p>
    <h1>{{judul:text:Judul Utama:Diskon 50%}}</h1>
    <p>{{deskripsi:textarea:Deskripsi:Dapatkan penawaran terbaik untuk semua produk pilihan.}}</p>
    <div class="badge">{{cta:text:Teks Badge:Berlaku Hari Ini}}</div>
  </div>
</body>
</html>
```

---

### 2. Produk dengan Foto & Float Animation

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
      background: {{bg:color:Warna Background:#0f172a}};
      display: flex; align-items: center; justify-content: center;
    }

    :root { --aksen: {{aksen:color:Warna Aksen:#6366f1}}; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
      0%, 100% { transform: translateY(0); }
      50%       { transform: translateY(-14px); }
    }

    .layout {
      display: flex; align-items: center;
      gap: 80px; padding: 60px; max-width: 1200px; width: 100%;
    }
    .foto-wrap {
      flex-shrink: 0; width: 400px; height: 400px; border-radius: 50%;
      overflow: hidden; background: #1e293b;
      animation: float 4s ease-in-out infinite;
      box-shadow: 0 40px 80px rgba(0,0,0,0.5);
    }
    .foto-wrap img { width: 100%; height: 100%; object-fit: cover; }
    .konten { flex: 1; }
    .tag {
      display: inline-block; padding: 5px 16px; border-radius: 100px;
      background: var(--aksen); color: #fff;
      font-size: 0.8rem; font-weight: 700; margin-bottom: 20px;
      animation: fadeUp 0.6s ease both;
    }
    h1 {
      font-size: 3.5rem; font-weight: 800; color: #fff;
      letter-spacing: -0.02em; margin-bottom: 14px;
      animation: fadeUp 0.6s 0.1s ease both;
    }
    p {
      font-size: 1.125rem; color: rgba(255,255,255,0.5);
      margin-bottom: 30px; line-height: 1.7; white-space: pre-line;
      animation: fadeUp 0.6s 0.2s ease both;
    }
    .harga {
      font-size: 2.75rem; font-weight: 900; color: var(--aksen);
      animation: fadeUp 0.6s 0.3s ease both;
    }
  </style>
</head>
<body>
  <div class="layout">
    <div class="foto-wrap">
      <img src="{{foto:image:Foto Produk}}" alt="produk">
    </div>
    <div class="konten">
      <span class="tag">{{tag:text:Tag:Produk Unggulan}}</span>
      <h1>{{nama:text:Nama Produk:Nama Produk Anda}}</h1>
      <p>{{deskripsi:textarea:Deskripsi:Deskripsi singkat produk Anda.}}</p>
      <div class="harga">{{harga:text:Harga:Rp 0}}</div>
    </div>
  </div>
</body>
</html>
```

---

### 3. Pengumuman dengan Marquee

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
      background: {{bg:color:Warna Background:#0a0a0a}};
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
    }

    :root { --aksen: {{aksen:color:Warna Aksen:#f59e0b}}; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(20px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes marquee {
      from { transform: translateX(100vw); }
      to   { transform: translateX(-100%); }
    }

    .konten { text-align: center; padding: 0 80px; max-width: 1100px; }
    .kategori {
      font-size: 0.875rem; font-weight: 700; letter-spacing: 0.15em;
      text-transform: uppercase; color: var(--aksen); margin-bottom: 16px;
      animation: fadeUp 0.6s ease both;
    }
    h1 {
      font-size: 4rem; font-weight: 900; color: #fff;
      line-height: 1.1; margin-bottom: 24px;
      animation: fadeUp 0.6s 0.1s ease both;
    }
    .isi {
      font-size: 1.3rem; color: rgba(255,255,255,0.6); line-height: 1.7;
      white-space: pre-line;
      animation: fadeUp 0.6s 0.2s ease both;
    }
    .tanggal {
      margin-top: 36px; font-size: 0.875rem; color: rgba(255,255,255,0.25);
      animation: fadeUp 0.6s 0.3s ease both;
    }

    /* Ticker berjalan di bagian bawah */
    .ticker {
      position: fixed; bottom: 0; left: 0; right: 0;
      background: var(--aksen); padding: 10px 0; overflow: hidden;
    }
    .ticker-inner {
      white-space: nowrap;
      font-size: 1rem; font-weight: 700; color: #000;
      animation: marquee {{ticker_speed:text:Kecepatan Ticker:14s}} linear infinite;
    }
  </style>
</head>
<body>
  <div class="konten">
    <p class="kategori">{{kategori:text:Kategori:Pengumuman}}</p>
    <h1>{{judul:text:Judul:Judul Pengumuman}}</h1>
    <p class="isi">{{isi:textarea:Isi:Isi pengumuman di sini.}}</p>
    <p class="tanggal">{{tanggal:text:Tanggal:}}</p>
  </div>
  <div class="ticker">
    <div class="ticker-inner">
      {{ticker:text:Teks Ticker:Selamat datang &nbsp;•&nbsp; Informasi penting &nbsp;•&nbsp; Terima kasih telah berkunjung}}
    </div>
  </div>
</body>
</html>
```

---

## Tips & Best Practices

### Urutan field = urutan form

Field muncul di form dashboard sesuai urutan kemunculannya di template. Letakkan field yang paling sering diubah (judul, gambar) di bagian atas — misalnya di awal `<style>` atau `<body>`.

### Beri default yang bermakna

Default membantu admin memahami format yang diharapkan:

```html
<!-- Baik -->
{{harga:text:Harga:Rp 150.000}}
{{tanggal:text:Tanggal:31 Desember 2025}}

<!-- Kurang baik — admin tidak tahu format yang diharapkan -->
{{harga:text:Harga}}
```

### Gunakan CSS variable untuk warna

```html
<style>
  :root {
    --aksen: {{aksen:color:Warna Aksen:#3b82f6}};
    --bg:    {{bg:color:Background:#0f172a}};
  }
  body { background: var(--bg); }
  .sorot { color: var(--aksen); }
  .badge { background: var(--aksen); }
</style>
```

Lebih bersih daripada menduplikasi `{{aksen}}` di setiap elemen.

### Hindari dependensi eksternal

Template dirender secara lokal — tidak ada koneksi internet yang dijamin. Hindari CDN dan Google Fonts:

```css
/* Jangan */
@import url('https://fonts.googleapis.com/css2?family=Inter');

/* Gunakan font sistem */
font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
font-family: ui-serif, Georgia, serif;
```

### Ukuran teks untuk layar display

Layar dilihat dari jarak 1–3 meter, teks harus besar:

| Elemen | Minimum |
|---|---|
| Judul utama | `2.5rem` |
| Subjudul | `1.5rem` |
| Body text | `1.125rem` |
| Label kecil | `0.875rem` |

### Animasi yang bersahabat dengan hardware ringan

Gunakan properti yang di-*composite* oleh browser (tidak memicu reflow):

```css
/* Baik — GPU-accelerated */
transform: translateY(), scale(), rotate()
opacity

/* Hindari jika bisa — memicu reflow/repaint */
width, height, top, left, margin, padding
```

---

## Troubleshooting

### Field tidak muncul di form dashboard

- Nama field mengandung karakter tidak valid (spasi, tanda hubung, dll.)
- Sintaks `{{` tidak ditutup dengan `}}`
- Tipe tidak dikenali — fallback ke `text`, periksa ejaan

### Nilai tidak terganti di hasil generate

- Nama field case-sensitive — `Judul` ≠ `judul`
- Field gambar kosong → `src=""` → gambar tidak tampil, ini normal

### Tampilan berantakan di layar

- Pastikan `overflow: hidden` ada di `body`
- Uji di resolusi yang sama dengan layar target (misal 1920×1080)
- Cek elemen yang mungkin meluber keluar `100vw` atau `100vh`

### Animasi terasa patah-patah

- Kurangi jumlah elemen yang dianimasikan sekaligus
- Gunakan hanya `transform` dan `opacity` (GPU-accelerated)
- Tambahkan `will-change: transform` pada elemen yang dianimasikan:

```css
.gambar { will-change: transform; animation: float 3s ease-in-out infinite; }
```

### File generated tidak diperbarui setelah edit

Klik **Edit** pada item di dashboard, ubah nilai field, lalu **Simpan** — sistem otomatis regenerate file. Atau gunakan endpoint `POST /api/items/{id}/regenerate` secara manual.
