# Ringkasan Deteksi Tepi Sobel, Roberts, dan Kompas

Ambang tepi yang dipakai: **T=60** dalam satuan magnitudo ternormalisasi.

## Burj Khalifa

| Operator | Rerata \|G\| | Maks \|G\| | Ambang | Jumlah tepi | Kepadatan (%) | Waktu (ms) | Rasio \|Gx\|:\|Gy\| | Arah dominan | Arah dominan (%) |
|---|---|---|---|---|---|---|---|---|---|
| Sobel | 9.12 | 207.1 | 60.0 | 5323 | 4.861 | 5.49 | 1.51 | - | - |
| Roberts | 10.36 | 290.6 | 60.0 | 6618 | 6.044 | 3.83 | 0.988 | - | - |
| Kompas (Kirsch) | 7.84 | 186.3 | 60.0 | 3521 | 3.216 | 23.18 | - | T | 29.6 |

Sebaran arah tepi kompas:

Arah: U=utara, BL=barat laut, B=barat, BD=barat daya, S=selatan, TG=tenggara, T=timur, TL=timur laut.

| Arah | Jumlah | Persen (%) |
|---|---|---|
| U | 440 | 12.5 |
| BL | 145 | 4.1 |
| B | 932 | 26.5 |
| BD | 166 | 4.7 |
| S | 460 | 13.1 |
| TG | 163 | 4.6 |
| T | 1043 | 29.6 |
| TL | 172 | 4.9 |

## Jalan Route 66

| Operator | Rerata \|G\| | Maks \|G\| | Ambang | Jumlah tepi | Kepadatan (%) | Waktu (ms) | Rasio \|Gx\|:\|Gy\| | Arah dominan | Arah dominan (%) |
|---|---|---|---|---|---|---|---|---|---|
| Sobel | 10.98 | 143.8 | 60.0 | 8133 | 1.907 | 20.53 | 0.815 | - | - |
| Roberts | 11.97 | 196.0 | 60.0 | 6529 | 1.531 | 14.17 | 0.98 | - | - |
| Kompas (Kirsch) | 9.17 | 125.2 | 60.0 | 3902 | 0.915 | 89.87 | - | S | 20.7 |

Sebaran arah tepi kompas:

Arah: U=utara, BL=barat laut, B=barat, BD=barat daya, S=selatan, TG=tenggara, T=timur, TL=timur laut.

| Arah | Jumlah | Persen (%) |
|---|---|---|
| U | 649 | 16.6 |
| BL | 315 | 8.1 |
| B | 434 | 11.1 |
| BD | 274 | 7.0 |
| S | 807 | 20.7 |
| TG | 370 | 9.5 |
| T | 445 | 11.4 |
| TL | 608 | 15.6 |

## Sapuan ambang

| Citra | Operator | ambang | jumlah_tepi | kepadatan_persen |
|---|---|---|---|---|
| Burj Khalifa | Sobel | 30 | 12411 | 11.334 |
| Burj Khalifa | Sobel | 45 | 8306 | 7.585 |
| Burj Khalifa | Sobel | 60 | 5323 | 4.861 |
| Burj Khalifa | Sobel | 75 | 3248 | 2.966 |
| Burj Khalifa | Sobel | 90 | 1841 | 1.681 |
| Burj Khalifa | Roberts | 30 | 14083 | 12.861 |
| Burj Khalifa | Roberts | 45 | 9795 | 8.945 |
| Burj Khalifa | Roberts | 60 | 6618 | 6.044 |
| Burj Khalifa | Roberts | 75 | 4313 | 3.939 |
| Burj Khalifa | Roberts | 90 | 2802 | 2.559 |
| Burj Khalifa | Kompas (Kirsch) | 30 | 11131 | 10.165 |
| Burj Khalifa | Kompas (Kirsch) | 45 | 6396 | 5.841 |
| Burj Khalifa | Kompas (Kirsch) | 60 | 3521 | 3.216 |
| Burj Khalifa | Kompas (Kirsch) | 75 | 1839 | 1.679 |
| Burj Khalifa | Kompas (Kirsch) | 90 | 912 | 0.833 |
| Jalan Route 66 | Sobel | 30 | 31380 | 7.359 |
| Jalan Route 66 | Sobel | 45 | 14586 | 3.421 |
| Jalan Route 66 | Sobel | 60 | 8133 | 1.907 |
| Jalan Route 66 | Sobel | 75 | 4311 | 1.011 |
| Jalan Route 66 | Sobel | 90 | 1713 | 0.402 |
| Jalan Route 66 | Roberts | 30 | 35922 | 8.424 |
| Jalan Route 66 | Roberts | 45 | 13038 | 3.058 |
| Jalan Route 66 | Roberts | 60 | 6529 | 1.531 |
| Jalan Route 66 | Roberts | 75 | 3596 | 0.843 |
| Jalan Route 66 | Roberts | 90 | 1743 | 0.409 |
| Jalan Route 66 | Kompas (Kirsch) | 30 | 20082 | 4.71 |
| Jalan Route 66 | Kompas (Kirsch) | 45 | 8681 | 2.036 |
| Jalan Route 66 | Kompas (Kirsch) | 60 | 3902 | 0.915 |
| Jalan Route 66 | Kompas (Kirsch) | 75 | 1246 | 0.292 |
| Jalan Route 66 | Kompas (Kirsch) | 90 | 164 | 0.038 |
