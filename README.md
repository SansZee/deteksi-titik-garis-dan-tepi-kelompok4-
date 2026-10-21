# Deteksi Titik dan Deteksi Tepi

Tugas Kelompok 4 mata kuliah Analisis Data Citra Biomedik (ADCB) tentang
deteksi titik, garis, dan tepi pada citra digital.

Bagian yang dikerjakan dalam repositori ini:

- Nomor 1: dua citra masukan yang diubah ke citra keabuan.
- Nomor 2a: deteksi titik dengan mask 8 tetangga.
- Nomor 2c: deteksi tepi dengan operator Prewitt, Sobel, Roberts, dan Kompas.

Deteksi garis (2b) tidak termasuk dalam bagian ini.

## Citra

| | Burj Khalifa | Jalan Route 66 |
|---|---|---|
| Berkas | `img/Burj_Khalifa.avif` | `img/D11_Williams_Route_66_1.avif` |
| Ukuran asli | 250 x 438 piksel | 3840 x 2560 piksel |
| Ukuran proses | 250 x 438 piksel | 800 x 533 piksel |

Citra Route 66 diperkecil ke lebar 800 piksel dengan interpolasi area. Citra
Burj Khalifa tidak diperbesar karena ukurannya sudah lebih kecil dari 800 piksel.

## Metode

1. Citra dibaca dari AVIF, diubah ke keabuan dengan rumus luminansi standar,
   lalu diproses pada ukuran yang telah ditentukan.
2. Konvolusi 3x3 diimplementasikan manual dengan NumPy dan diverifikasi
   terhadap `cv2.filter2D`. Selisih maksimum yang diperoleh 0,000000.
3. Deteksi titik memakai mask Laplacian 8 tetangga. Respons dihitung sebagai
   nilai mutlak hasil konvolusi, lalu titik ditandai dengan ambang persentil
   99,5 respons tiap citra.
4. Deteksi tepi Prewitt memakai mask `Gx` dan `Gy`, magnitudo
   `|G| = akar(Gx^2 + Gy^2)`, dan ambang tepi 200.
5. Analisis pengaruh ambang dilakukan dengan sapuan persentil 99, 99,5, 99,9,
   dan 99,99 untuk titik, serta ambang 100, 150, 200, dan 250 untuk Prewitt.

### Sobel, Roberts, dan Kompas

Program `src/tepi.py` menambahkan tiga operator deteksi tepi:

| Operator | Mask | Skala normalisasi |
|---|---|---|
| Sobel | 3x3, bobot 1-2-1 | 4 |
| Roberts | 2x2 diagonal | 1 |
| Kompas (Kirsch) | delapan mask 3x3, diputar tiap 45 derajat | 15 |

Sobel dan Roberts memakai `|G| = akar(Gx^2 + Gy^2)`. Kompas menghitung
respons kedelapan arah lalu mengambil nilai terbesar; arah dengan respons
terbesar ditampilkan sebagai peta warna. Agar ambang ketiga operator dapat
dibandingkan, magnitudo mentah dibagi jumlah bobot positif mask (Sobel 4,
Roberts 1, Kompas 15). Dengan begitu `|G|` berada pada satuan intensitas
piksel yang kurang lebih sama. Ambang yang dipakai adalah `T=60`, dan
pengaruh ambang diuji pada 30, 45, 60, 75, dan 90.

## Menjalankan

### Memakai lingkungan Python baru

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/deteksi.py   # deteksi titik dan Prewitt
python src/tepi.py      # Sobel, Roberts, dan Kompas
```

### Memakai lingkungan ADCB yang sudah ada

Dari direktori repositori ini:

```bash
uv run --project .. python src/deteksi.py
uv run --project .. python src/tepi.py
```

Atau langsung memakai venv ADCB:

```bash
../.venv/bin/python src/deteksi.py
../.venv/bin/python src/tepi.py
```

## Keluaran

```
output/
├── data.json                 angka deteksi titik dan Prewitt
├── tepi.json                 angka Sobel, Roberts, dan Kompas
├── ringkasan.md              tabel metrik titik dan Prewitt
├── tepi_ringkasan.md         tabel metrik dan sapuan ambang tiga operator
├── analisis.md               analisis deteksi titik dan Prewitt
├── analisis_tepi.md          analisis Sobel, Roberts, dan Kompas
├── gambar/
│   ├── panel/                panel tunggal tanpa judul, resolusi asli
│   └── komposit/             gambar gabungan berjudul
└── tabel/                    metrik.csv, ambang_*.csv, tepi_metrik.csv,
                              tepi_ambang.csv
```

## Hasil utama

| Besaran | Burj Khalifa | Jalan Route 66 |
|---|---|---|
| Titik pada p99,5 | 552 titik, T=512 | 2148 titik, T=247 |
| Kepadatan titik | 0,504% | 0,504% |
| Kepadatan tepi Prewitt (T=200) | 3,837% | 1,386% |
| Rasio energi Gx : Gy | 1,53 | 0,81 |

Prewitt menghasilkan tepi yang lebih jelas daripada deteksi titik karena
keluarannya berupa kontur yang menyambung. Di antara kedua citra, Route 66
memberi hasil tepi paling bersih. Burj Khalifa terkendala tekstur fasad yang
padat dan resolusi yang rendah.

### Sobel, Roberts, dan Kompas (T=60)

| Operator | Kepadatan tepi Burj Khalifa | Kepadatan tepi Route 66 | Rasio Gx : Gy (Burj / Route) |
|---|---:|---:|---|
| Sobel | 4,861% | 1,907% | 1,51 / 0,82 |
| Roberts | 6,044% | 1,531% | 0,99 / 0,98 |
| Kompas (Kirsch) | 3,216% | 0,915% | arah dominan T / S |

Sobel memberi kompromi paling baik antara kelengkapan tepi dan ketebalan
kontur. Roberts paling peka terhadap tekstur karena mask 2x2 tidak melakukan
perataan. Pada Burj Khalifa kepadatannya paling tinggi (6,044%), sedangkan pada
Route 66 turun menjadi 1,531% karena sebaran responsnya lebih sempit. Kompas
paling selektif: hanya tepi yang benar-benar kuat yang bertahan, dan arah
gradien dapat dibaca langsung dari warna panel arah. Rasio Gx : Gy Roberts
mendekati 1 karena mask diagonal memberi sumbangan pada kedua komponen, bukan
karena isi citra benar-benar seimbang.

## Catatan

- `src/deteksi.py` menghasilkan ulang keluaran titik dan Prewitt, sedangkan
  `src/tepi.py` menghasilkan ulang keluaran Sobel, Roberts, dan Kompas.
- Bila `img/Burj_Khalifa.avif` diganti dengan versi beresolusi lebih tinggi
  dengan nama yang sama, jalankan ulang kedua program agar angka dan gambar
  diperbarui.
- Analisis lengkap tersedia di `output/analisis.md` (titik dan Prewitt) dan
  `output/analisis_tepi.md` (Sobel, Roberts, Kompas).
