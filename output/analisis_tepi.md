# Analisis Deteksi Tepi Sobel, Roberts, dan Kompas

## 1. Citra dan parameter

Citra yang dipakai sama dengan bagian deteksi titik dan Prewitt:

| | Burj Khalifa | Jalan Route 66 |
|---|---|---|
| Berkas | `img/Burj_Khalifa.avif` | `img/D11_Williams_Route_66_1.avif` |
| Ukuran asli | 250 x 438 piksel | 3840 x 2560 piksel |
| Ukuran proses | 250 x 438 piksel | 800 x 533 piksel |
| Orientasi | Potret | Lanskap |

Kedua citra diubah ke keabuan, lalu diproses dengan tiga operator. Magnitudo
mentah setiap operator dibagi jumlah bobot positif masknya: Sobel 4, Roberts 1,
dan Kompas 15. Normalisasi ini membuat nilai `|G|` berada pada satuan
intensitas piksel yang kurang lebih sama, sehingga satu ambang `T=60` dapat
dipakai untuk ketiganya. Pengaruh ambang diuji pada 30, 45, 60, 75, dan 90.

## 2. Mask yang dipakai

### Sobel

```
Gx = -1  0  1      Gy = -1 -2 -1
     -2  0  2            0  0  0
     -1  0  1            1  2  1
```

Sobel adalah pengembangan Prewitt. Bobot 2 pada baris atau kolom tengah memberi
penekanan lebih besar kepada piksel yang dekat dengan pusat mask. Pembobotan
ini sekaligus berfungsi sebagai perataan ringan, sehingga Sobel lebih tahan
terhadap derau daripada Roberts.

### Roberts

```
Gx =  1  0      Gy =  0  1
      0 -1            -1  0
```

Roberts memakai jendela 2x2 dan mengukur beda intensitas sepanjang dua diagonal.
Karena hanya melibatkan empat piksel, Roberts paling sederhana dan paling cepat,
tetapi tidak memiliki perataan sama sekali. Tepi yang dihasilkan tipis sekaligus
paling mudah terpicu oleh tekstur dan derau.

### Kompas (Kirsch)

Operator kompas memakai delapan mask 3x3 yang diputar tiap 45 derajat. Mask
pertama (arah utara) adalah:

```
 5  5  5
-3  0 -3
-3 -3 -3
```

Mask kedua sampai kedelapan diperoleh dengan memutar pola tersebut. Setiap
piksel dikonvolusi dengan kedelapan mask, lalu respons terbesar diambil sebagai
magnitudo. Mask pemenang menunjukkan arah gradien yang paling kuat. Berbeda
dari Sobel dan Roberts yang bersifat linear, Kompas bersifat non-linear karena
operasi maksimum dilakukan setelah konvolusi.

## 3. Hasil kuantitatif

Ambang yang dipakai `T=60` pada magnitudo ternormalisasi.

| Operator | Citra | Rerata \|G\| | Maks \|G\| | Jumlah tepi | Kepadatan | Rasio \|Gx\|:\|Gy\| |
|---|---|---|---:|---:|---:|---:|
| Sobel | Burj Khalifa | 9,12 | 207,1 | 5323 | 4,861% | 1,51 |
| Sobel | Route 66 | 10,98 | 143,8 | 8133 | 1,907% | 0,82 |
| Roberts | Burj Khalifa | 10,36 | 290,6 | 6618 | 6,044% | 0,99 |
| Roberts | Route 66 | 11,97 | 196,0 | 6529 | 1,531% | 0,98 |
| Kompas | Burj Khalifa | 7,84 | 186,3 | 3521 | 3,216% | arah dominan T |
| Kompas | Route 66 | 9,17 | 125,2 | 3902 | 0,915% | arah dominan S |

Rerata magnitudo Roberts paling tinggi pada kedua citra, tetapi angka itu tidak
berarti Roberts paling baik. Roberts tidak melakukan perataan, sehingga hampir
semua tekstur kecil menghasilkan respons menengah. Akibatnya ambang 60 masih
meloloskan banyak piksel, terutama pada fasad Burj Khalifa dan vegetasi Route 66.
Kompas justru memberi rerata dan kepadatan paling rendah karena hanya respons
arah terkuat yang dihitung.

## 4. Pembahasan per operator

### Sobel

Pada Burj Khalifa, Sobel menonjolkan sisi menara, tonjolan fasad, dan siluet
gedung di bagian kaki. Rasio `|Gx| : |Gy|` sebesar 1,51 menunjukkan tepi
vertikal lebih kuat, sesuai bentuk menara yang tinggi dan ramping. Nilai ini
hampir sama dengan Prewitt (1,53) karena kedua operator memakai orientasi yang
sama; perbedaannya hanya pada pembobotan piksel tengah.

Pada Route 66, Sobel berhasil menarik garis tepi jalan, marka tengah, tiang
listrik, dan papan Route 66. Rasio 0,82 berarti komponen horizontal sedikit
lebih kuat, terutama karena horizon dan permukaan jalan. Di langit Burj Khalifa
terlihat pita horizontal tipis pada ambang rendah. Pita itu berasal dari
kompresi AVIF dan tekstur gradasi langit, bukan objek nyata. Pembobotan Sobel
memang meredam gejalanya, tetapi tidak menghilangkannya sepenuhnya.

Sobel memberi kompromi paling seimbang: kontur cukup lengkap, tepi tidak
setipis Roberts, dan tekstur latar masih terkendali.

### Roberts

Pada Burj Khalifa, Roberts menghasilkan peta tepi paling ramai. Fasad yang
padat berubah menjadi kumpulan piksel pendek dan terputus. Kepadatan 6,044%
lebih tinggi daripada Sobel (4,861%) pada ambang yang sama.

Pada Route 66, Roberts juga peka terhadap vegetasi dan tekstur aspal, tetapi
kepadatan pada `T=60` justru 1,531%, lebih rendah daripada Sobel (1,907%).
Sebaran respons Roberts lebih sempit: persentil 99-nya 70,5 berbanding 75,3 pada
Sobel. Akibatnya, jumlah piksel di atas ambang tinggi lebih sedikit meskipun
rerata responsnya lebih besar. Pada ambang rendah `T=30`, Roberts tetap paling
tinggi di Route 66, yaitu 8,424%.

Rasio `|Gx| : |Gy|` Roberts hampir 1 pada kedua citra, yaitu 0,99 dan 0,98.
Angka ini bukan berarti kedua arah tepi benar-benar seimbang. Mask Roberts
mengukur diagonal, sehingga tepi vertikal dan horizontal sama-sama memberi
sumbangan pada kedua komponen. Rasio mendekati 1 karena sifat masknya, bukan
karena isi citra.

Kelebihan Roberts terlihat pada detail kecil: batas papan Route 66, tiang
listrik, dan tonjolan tipis pada menara masih terbaca. Namun untuk citra
bertekstur, hasilnya lebih sulit dibaca tanpa penapisan awal.

### Kompas (Kirsch)

Kompas memberi hasil paling bersih di antara ketiga operator. Pada Burj
Khalifa, hanya 3,216% piksel lolos ambang, dan sebagian besar berada di sisi
menara serta bangunan di kaki menara. Pada Route 66, hanya 0,915% piksel yang
bertahan, tetapi garis tepi jalan, marka, tiang, dan papan masih terbentuk.

Panel arah memperlihatkan orientasi gradien yang dominan:

| Citra | Arah dominan | Persentase piksel tepi |
|---|---|---:|
| Burj Khalifa | Timur (T) | 29,6% |
| Burj Khalifa | Barat (B) | 26,5% |
| Route 66 | Selatan (S) | 20,7% |
| Route 66 | Utara (U) | 16,6% |
| Route 66 | Timur laut (TL) | 15,6% |

Pada Burj Khalifa, arah T dan B bersama-sama mencakup 56,1% piksel tepi. Label
arah menunjukkan arah gradien (sisi terang yang ditangkap mask), bukan arah
garis tepinya. Tepi vertikal menara memang menghasilkan gradien mendatar,
sehingga mask dengan bobot +5 di sisi timur atau barat menang. Pada Route 66,
arah S dan U mencerminkan horizon dan permukaan jalan, sedangkan TL mengikuti
garis jalan yang miring.

Kompas paling selektif karena operasi maksimum membuang respons yang lemah.
Konsekuensinya, ambang yang terlalu tinggi cepat menghilangkan tepi. Waktu
prosesnya juga paling lama, sekitar empat sampai lima kali Sobel, karena setiap
piksel dikonvolusi dengan delapan mask.

## 5. Pengaruh ambang

Kepadatan tepi (%) pada beberapa ambang:

| Operator | Citra | T=30 | T=45 | T=60 | T=75 | T=90 |
|---|---|---:|---:|---:|---:|---:|
| Sobel | Burj Khalifa | 11,334 | 7,585 | 4,861 | 2,966 | 1,681 |
| Sobel | Route 66 | 7,359 | 3,421 | 1,907 | 1,011 | 0,402 |
| Roberts | Burj Khalifa | 12,861 | 8,945 | 6,044 | 3,939 | 2,559 |
| Roberts | Route 66 | 8,424 | 3,058 | 1,531 | 0,843 | 0,409 |
| Kompas | Burj Khalifa | 10,165 | 5,841 | 3,216 | 1,679 | 0,833 |
| Kompas | Route 66 | 4,710 | 2,036 | 0,915 | 0,292 | 0,038 |

Semakin tinggi ambang, semakin sedikit piksel yang bertahan. Penurunan paling
drastis terjadi pada Kompas Route 66: dari 4,710% pada `T=30` menjadi 0,038%
pada `T=90`. Hal ini terjadi karena distribusi respons Kompas relatif sempit;
setelah tepi kuat terlewati, hampir tidak ada respons menengah yang tersisa.
Roberts menurun paling landai pada Burj Khalifa karena tekstur fasad yang padat
tetap menghasilkan respons tinggi. Pada Route 66, penurunan Roberts mirip
Sobel, sedangkan Kompas tetap paling tajam.

Ambang 60 dipilih sebagai kompromi. Pada `T=30`, tekstur dan derau terlalu
dominan, terutama pada Roberts. Pada `T=90`, garis jalan Route 66 mulai
terputus dan fasad Burj Khalifa hampir hilang. Ambang 60 masih mempertahankan
kontur utama pada ketiga operator.

## 6. Perbandingan ketiga operator

| Aspek | Sobel | Roberts | Kompas (Kirsch) |
|---|---|---|---|
| Ukuran mask | 3x3 | 2x2 | delapan mask 3x3 |
| Dasar | Gradien horizontal dan vertikal | Beda diagonal | Respons maksimum delapan arah |
| Perataan | Ada, bobot 1-2-1 | Tidak ada | Ada, bobot 5 dan -3 |
| Ketebalan tepi | Sedang | Tipis | Sedang sampai tebal |
| Ketahanan derau | Baik | Rendah | Baik |
| Kelengkapan kontur | Tinggi | Tinggi tetapi terpecah | Sedang, hanya tepi kuat |
| Informasi arah | Tidak langsung | Tidak langsung | Langsung dari mask pemenang |
| Waktu relatif | Sedang | Cepat | Paling lambat |
| Kelebihan utama | Seimbang dan mudah dibaca | Peka detail kecil | Seleksi tepi kuat dan arah jelas |
| Kelemahan utama | Tepi tebal, pita kompresi ikut muncul | Derau dan tekstur ikut terangkat | Ambang tinggi cepat menghilangkan tepi |

Di antara kedua citra, Route 66 memberi hasil yang lebih mudah dibaca untuk
ketiga operator. Resolusinya lebih tinggi, garis jalan panjang dan lurus, serta
latar langit relatif rata. Burj Khalifa lebih sulit karena resolusinya rendah
dan fasadnya penuh tekstur.

## 7. Keterbatasan

1. Setiap operator memakai satu ambang global. Tidak ada penipisan tepi,
   penekanan non-maksimum, atau ambang ganda seperti pada Canny.
2. Normalisasi dengan jumlah bobot positif mask adalah pendekatan agar ambang
   dapat dibandingkan. Nilai `|G|` tetap bergantung pada susunan mask, sehingga
   perbandingan antarpiksel dalam satu operator lebih bermakna daripada
   perbandingan mutlak antarmask.
3. Roberts memakai jendela 2x2. Penempatan mask di batas citra memakai piksel
   tepi terdekat, sehingga baris dan kolom terakhir sedikit berbeda perlakuan
   dibanding bagian dalam citra.
4. Kompas memakai operasi maksimum sehingga tidak linear. Arah yang dilaporkan
   adalah arah gradien, bukan arah garis tepi. Garis tepi tegak lurus terhadap
   arah gradien.
5. Kompresi AVIF pada citra Burj Khalifa meninggalkan pita halus di langit.
   Pita itu dapat lolos ambang rendah dan bukan merupakan tepi objek.
6. Konversi ke keabuan menghilangkan informasi warna. Dua daerah berbeda warna
   dengan kecerahan sama tidak akan terpisah.
7. Konvolusi manual sudah diverifikasi terhadap `cv2.filter2D` dengan selisih
   maksimum 0,000000, sehingga hasil bukan disebabkan oleh perbedaan
   implementasi pustaka.

## 8. Kesimpulan

1. Sobel memberi hasil paling seimbang. Pada `T=60`, Sobel mendeteksi 4,861%
   piksel tepi pada Burj Khalifa dan 1,907% pada Route 66, dengan kontur jalan,
   marka, tiang, papan, siluet menara, dan tonjolan fasad masih terbaca.
2. Roberts paling peka terhadap detail kecil, tetapi juga paling mudah
   terpicu tekstur dan derau. Kepadatan tepinya 6,044% pada Burj Khalifa
   (tertinggi di antara ketiga operator) dan 1,531% pada Route 66 (di bawah
   Sobel pada `T=60`, tetapi tertinggi pada `T=30`, yaitu 8,424%).
3. Kompas paling selektif dan memberi informasi arah. Kepadatan tepinya
   3,216% pada Burj Khalifa dan 0,915% pada Route 66. Arah dominan T dan B pada
   Burj Khalifa sesuai dengan tepi vertikal menara, sedangkan arah S, U, dan TL
   pada Route 66 sesuai dengan horizon dan garis jalan yang miring.
4. Untuk laporan visual, Sobel paling mudah dibaca. Untuk analisis orientasi
   tepi, Kompas lebih informatif. Roberts berguna bila detail kecil lebih
   penting daripada ketahanan terhadap derau.
