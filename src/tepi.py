"""Deteksi tepi dengan operator Sobel, Roberts, dan Kompas (Kirsch).

Program ini melengkapi bagian deteksi tepi pada ``src/deteksi.py`` yang
memakai operator Prewitt. Tiga operator yang diimplementasikan:

    1. Sobel   : gradien dua arah dengan pembobotan 1-2-1.
    2. Roberts : gradien diagonal dengan mask 2x2.
    3. Kompas  : delapan mask Kirsch yang diputar tiap 45 derajat.

Setiap magnitudo gradien dinormalisasi dengan jumlah bobot positif mask,
sehingga satu ambang yang sama dapat dipakai untuk ketiga operator.
Hasilnya ditulis ke ``output/`` tanpa mengubah keluaran Prewitt.

Jalankan dari direktori repositori:
    python src/tepi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Utilitas pemuatan citra, konvolusi, penyusunan panel, dan tabel dipakai
# bersama dengan src/deteksi.py agar gaya keluaran kedua program konsisten.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from deteksi import (  # noqa: E402
    AKAR,
    DAFTAR_CITRA,
    DIR_CITRA,
    DIR_GAMBAR,
    DIR_KELUARAN,
    DIR_KOMPOSIT,
    DIR_PANEL,
    DIR_TABEL,
    komposit,
    muat_citra,
    normalkan,
    simpan_panel,
    tabel_markdown,
    waktu_ms,
)

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------

# Ambang tepi dalam satuan magnitudo ternormalisasi (0 sampai sekitar 255).
AMBANG_TEPI = 60.0
AMBANG_SAPUAN = [30, 45, 60, 75, 90]

# Mask Sobel. Jumlah bobot positif tiap arah = 4.
SOBEL_GX = np.array(
    [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1],
    ],
    dtype=np.float32,
)

SOBEL_GY = np.array(
    [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1],
    ],
    dtype=np.float32,
)

# Mask Roberts 2x2. Jumlah bobot positif tiap arah = 1.
ROBERTS_GX = np.array(
    [
        [1, 0],
        [0, -1],
    ],
    dtype=np.float32,
)

ROBERTS_GY = np.array(
    [
        [0, 1],
        [-1, 0],
    ],
    dtype=np.float32,
)

# Delapan mask Kirsch untuk operator kompas. Urutan mengikuti arah mata
# angin: utara, barat laut, barat, barat daya, selatan, tenggara, timur,
# timur laut. Setiap mask memiliki tiga bobot +5 dan jumlah bobot positif 15.
KOMPAS_MASK = [
    np.array([  # Utara
        [5, 5, 5],
        [-3, 0, -3],
        [-3, -3, -3],
    ], dtype=np.float32),
    np.array([  # Barat laut
        [5, 5, -3],
        [5, 0, -3],
        [-3, -3, -3],
    ], dtype=np.float32),
    np.array([  # Barat
        [5, -3, -3],
        [5, 0, -3],
        [5, -3, -3],
    ], dtype=np.float32),
    np.array([  # Barat daya
        [-3, -3, -3],
        [5, 0, -3],
        [5, 5, -3],
    ], dtype=np.float32),
    np.array([  # Selatan
        [-3, -3, -3],
        [-3, 0, -3],
        [5, 5, 5],
    ], dtype=np.float32),
    np.array([  # Tenggara
        [-3, -3, -3],
        [-3, 0, 5],
        [-3, 5, 5],
    ], dtype=np.float32),
    np.array([  # Timur
        [-3, -3, 5],
        [-3, 0, 5],
        [-3, -3, 5],
    ], dtype=np.float32),
    np.array([  # Timur laut
        [-3, 5, 5],
        [-3, 0, 5],
        [-3, -3, -3],
    ], dtype=np.float32),
]

KOMPAS_ARAH = ["U", "BL", "B", "BD", "S", "TG", "T", "TL"]

# Warna untuk panel arah kompas.
WARNA_ARAH = np.array(
    [
        [230, 25, 75],    # U  merah
        [245, 130, 48],   # BL oranye
        [255, 225, 25],   # B  kuning
        [60, 180, 75],    # BD hijau
        [70, 240, 240],   # S  sian
        [0, 130, 200],    # TG biru
        [145, 30, 180],   # T  ungu
        [240, 50, 230],   # TL magenta
    ],
    dtype=np.uint8,
)

# Keterangan tiap operator. ``skala`` adalah jumlah bobot positif mask,
# dipakai untuk mengubah magnitudo mentah menjadi satuan intensitas piksel.
OPERATOR = {
    "sobel": {
        "judul": "Sobel",
        "jenis": "gradien",
        "skala": 4.0,
        "mask_x": SOBEL_GX,
        "mask_y": SOBEL_GY,
        "keterangan": "Mask 3x3 dengan pembobotan 1-2-1",
    },
    "roberts": {
        "judul": "Roberts",
        "jenis": "gradien",
        "skala": 1.0,
        "mask_x": ROBERTS_GX,
        "mask_y": ROBERTS_GY,
        "keterangan": "Mask 2x2 diagonal",
    },
    "kompas": {
        "judul": "Kompas (Kirsch)",
        "jenis": "kompas",
        "skala": 15.0,
        "mask": KOMPAS_MASK,
        "keterangan": "Delapan mask 3x3, diputar tiap 45 derajat",
    },
}

URUTAN_OPERATOR = ["sobel", "roberts", "kompas"]


# ---------------------------------------------------------------------------
# Konvolusi dan deteksi
# ---------------------------------------------------------------------------


def konvolusi_umum(citra: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Terapkan mask berukuran sembarang dengan penambahan batas tepi.

    Mask ganjil (3x3) diletakkan di tengah jendela. Mask genap (2x2 pada
    Roberts) diletakkan dengan sudut kiri atas sebagai acuan. Batas citra
    diisi dengan piksel tepi terdekat agar tidak muncul tepi palsu.
    """
    citra = np.asarray(citra, dtype=np.float32)
    mask = np.asarray(mask, dtype=np.float32)
    tinggi_mask, lebar_mask = mask.shape

    atas = (tinggi_mask - 1) // 2
    bawah = tinggi_mask - 1 - atas
    kiri = (lebar_mask - 1) // 2
    kanan = lebar_mask - 1 - kiri

    berbingkai = np.pad(citra, ((atas, bawah), (kiri, kanan)), mode="edge")
    jendela = np.lib.stride_tricks.sliding_window_view(
        berbingkai, (tinggi_mask, lebar_mask)
    )
    return np.einsum("ijkl,kl->ij", jendela, mask)


def verifikasi_konvolusi(keabuan: np.ndarray) -> float:
    """Bandingkan konvolusi manual dengan cv2.filter2D untuk semua mask."""
    selisih = 0.0
    for mask in (SOBEL_GX, SOBEL_GY, ROBERTS_GX, ROBERTS_GY, *KOMPAS_MASK):
        manual = konvolusi_umum(keabuan, mask)
        anchor = (0, 0) if mask.shape == (2, 2) else (-1, -1)
        acuan = cv2.filter2D(
            keabuan.astype(np.float32),
            cv2.CV_32F,
            mask,
            anchor=anchor,
            borderType=cv2.BORDER_REPLICATE,
        )
        selisih = max(selisih, float(np.max(np.abs(manual - acuan))))
    return selisih


def deteksi_tepi(keabuan: np.ndarray, kunci: str) -> dict[str, np.ndarray]:
    """Hitung respons salah satu operator dan magnitudo ternormalisasinya."""
    operator = OPERATOR[kunci]
    skala = operator["skala"]

    if operator["jenis"] == "gradien":
        gx = konvolusi_umum(keabuan, operator["mask_x"])
        gy = konvolusi_umum(keabuan, operator["mask_y"])
        magnitudo = np.hypot(gx, gy) / skala
        return {
            "gx": gx / skala,
            "gy": gy / skala,
            "magnitudo": magnitudo,
        }

    # Operator kompas: konvolusikan kedelapan mask, lalu ambil respons
    # terbesar. Mask yang menghasilkan respons terbesar menunjukkan arah
    # tepi yang paling kuat di piksel tersebut.
    respons = np.stack(
        [konvolusi_umum(keabuan, mask) for mask in operator["mask"]]
    )
    indeks_arah = np.argmax(respons, axis=0)
    magnitudo = np.max(respons, axis=0) / skala
    magnitudo = np.clip(magnitudo, 0, None)
    return {
        "respons": respons,
        "arah": indeks_arah,
        "magnitudo": magnitudo,
    }


def binerkan(peta: np.ndarray, ambang: float) -> np.ndarray:
    """Ubah peta respons menjadi citra biner 0/255."""
    return np.where(peta >= ambang, 255, 0).astype(np.uint8)


def overlay_tepi(keabuan: np.ndarray, tepi: np.ndarray) -> np.ndarray:
    """Tandai piksel tepi dengan warna merah pada citra keabuan."""
    rgb = cv2.cvtColor(keabuan, cv2.COLOR_GRAY2RGB)
    ukuran = 2 if keabuan.shape[1] <= 300 else 3
    penanda = cv2.dilate(tepi, np.ones((ukuran, ukuran), np.uint8))
    rgb[penanda > 0] = (220, 45, 45)
    return rgb


def peta_arah(arah: np.ndarray, tepi: np.ndarray) -> np.ndarray:
    """Warnai piksel tepi menurut arah kompas yang paling kuat."""
    rgb = np.full((*arah.shape, 3), 30, dtype=np.uint8)
    rgb[tepi > 0] = WARNA_ARAH[arah[tepi > 0]]
    return rgb


# ---------------------------------------------------------------------------
# Metrik
# ---------------------------------------------------------------------------


def hitung_metrik(
    hasil: dict[str, np.ndarray],
    tepi: np.ndarray,
    waktu: float,
    kunci: str,
) -> dict[str, float | int | str]:
    """Kumpulkan angka pembanding untuk satu operator pada satu citra."""
    magnitudo = hasil["magnitudo"]
    metrik: dict[str, float | int | str] = {
        "rerata_magnitudo": round(float(magnitudo.mean()), 2),
        "maks_magnitudo": round(float(magnitudo.max()), 1),
        "ambang": AMBANG_TEPI,
        "jumlah_tepi": int((tepi > 0).sum()),
        "kepadatan_tepi_persen": round(100 * float((tepi > 0).mean()), 3),
        "waktu_ms": round(waktu, 2),
    }

    if OPERATOR[kunci]["jenis"] == "gradien":
        gx = np.abs(hasil["gx"])
        gy = np.abs(hasil["gy"])
        metrik["rasio_gx_gy"] = round(
            float(gx.mean() / max(gy.mean(), 1e-6)), 3
        )
        return metrik

    # Sebaran arah pada piksel tepi untuk operator kompas.
    arah_tepi = hasil["arah"][tepi > 0]
    jumlah_tepi = max(int(arah_tepi.size), 1)
    sebaran = []
    for indeks, nama in enumerate(KOMPAS_ARAH):
        jumlah = int((arah_tepi == indeks).sum())
        sebaran.append(
            {
                "arah": nama,
                "jumlah": jumlah,
                "persen": round(100 * jumlah / jumlah_tepi, 1),
            }
        )
    dominan = max(sebaran, key=lambda isi: isi["jumlah"])
    metrik["arah_dominan"] = dominan["arah"]
    metrik["arah_dominan_persen"] = dominan["persen"]
    metrik["sebaran_arah"] = sebaran
    return metrik


def sapuan_ambang(magnitudo: np.ndarray) -> list[dict]:
    """Hitung jumlah tepi pada beberapa ambang ternormalisasi."""
    baris = []
    for ambang in AMBANG_SAPUAN:
        jumlah = int((magnitudo >= ambang).sum())
        baris.append(
            {
                "ambang": ambang,
                "jumlah_tepi": jumlah,
                "kepadatan_persen": round(
                    100 * jumlah / magnitudo.size, 3
                ),
            }
        )
    return baris


# ---------------------------------------------------------------------------
# Gambar
# ---------------------------------------------------------------------------


def buat_gambar(hasil: dict, konteks: dict) -> None:
    """Simpan panel tunggal dan komposit untuk satu citra."""
    kunci_citra = hasil["kunci"]
    keabuan = konteks["keabuan"]

    for kunci_op in URUTAN_OPERATOR:
        isi = konteks[kunci_op]
        magnitudo = isi["magnitudo"]
        tepi = isi["tepi"]
        batas = float(np.percentile(magnitudo, 99.9))

        if OPERATOR[kunci_op]["jenis"] == "gradien":
            gx = isi["gx"]
            gy = isi["gy"]
            batas_gradien = float(
                max(
                    np.percentile(np.abs(gx), 99.9),
                    np.percentile(np.abs(gy), 99.9),
                )
            )
            awalan = f"{kunci_citra}_{kunci_op}"
            simpan_panel(
                normalkan(np.abs(gx), batas_gradien),
                DIR_PANEL / f"{awalan}_gx.png",
            )
            simpan_panel(
                normalkan(np.abs(gy), batas_gradien),
                DIR_PANEL / f"{awalan}_gy.png",
            )
            simpan_panel(
                normalkan(magnitudo, batas),
                DIR_PANEL / f"{awalan}_magnitudo.png",
            )
            simpan_panel(tepi, DIR_PANEL / f"{awalan}_tepi.png")

            panel = [
                {"array": keabuan, "judul": "Citra keabuan"},
                {
                    "array": np.abs(gx),
                    "judul": "|Gx| (tepi vertikal)",
                    "vmin": 0,
                    "vmax": batas_gradien,
                },
                {
                    "array": np.abs(gy),
                    "judul": "|Gy| (tepi horizontal)",
                    "vmin": 0,
                    "vmax": batas_gradien,
                },
                {
                    "array": magnitudo,
                    "judul": "Magnitudo |G|",
                    "vmin": 0,
                    "vmax": batas,
                },
                {
                    "array": tepi,
                    "judul": f"Tepi biner (T={AMBANG_TEPI:g})",
                    "vmin": 0,
                    "vmax": 255,
                },
            ]
        else:
            awalan = f"{kunci_citra}_{kunci_op}"
            tampil_arah = peta_arah(isi["arah"], tepi)
            simpan_panel(
                normalkan(magnitudo, batas),
                DIR_PANEL / f"{awalan}_magnitudo.png",
            )
            simpan_panel(tampil_arah, DIR_PANEL / f"{awalan}_arah.png")
            simpan_panel(tepi, DIR_PANEL / f"{awalan}_tepi.png")
            simpan_panel(
                overlay_tepi(keabuan, tepi),
                DIR_PANEL / f"{awalan}_overlay.png",
            )

            panel = [
                {"array": keabuan, "judul": "Citra keabuan"},
                {
                    "array": magnitudo,
                    "judul": "Magnitudo kompas",
                    "vmin": 0,
                    "vmax": batas,
                },
                {
                    "array": tampil_arah,
                    "judul": "Arah tepi terkuat",
                },
                {
                    "array": tepi,
                    "judul": f"Tepi biner (T={AMBANG_TEPI:g})",
                    "vmin": 0,
                    "vmax": 255,
                },
                {
                    "array": overlay_tepi(keabuan, tepi),
                    "judul": "Tepi pada citra",
                },
            ]

        potret = keabuan.shape[0] > keabuan.shape[1]
        komposit(
            panel,
            DIR_KOMPOSIT / f"{kunci_citra}_{kunci_op}.png",
            nkolom=5 if potret else 3,
        )


def buat_gambar_perbandingan(
    hasil_semua: list[dict], konteks_semua: list[dict]
) -> None:
    """Bandingkan citra keabuan dengan tiga peta tepi biner."""
    lebar = 7.2
    nkolom = 1 + len(URUTAN_OPERATOR)
    lebar_panel = lebar / nkolom
    tinggi_baris = [
        lebar_panel * konteks["keabuan"].shape[0] / konteks["keabuan"].shape[1]
        for konteks in konteks_semua
    ]

    gambar, sumbu = plt.subplots(
        len(hasil_semua),
        nkolom,
        figsize=(lebar, sum(tinggi_baris) + 0.75),
        gridspec_kw={"height_ratios": tinggi_baris},
        constrained_layout=True,
        squeeze=False,
    )

    judul_kolom = ["Citra keabuan"] + [
        OPERATOR[kunci]["judul"] for kunci in URUTAN_OPERATOR
    ]
    for baris, (hasil, konteks) in enumerate(zip(hasil_semua, konteks_semua)):
        tampilan = [konteks["keabuan"]] + [
            konteks[kunci]["tepi"] for kunci in URUTAN_OPERATOR
        ]
        for kolom, isi in enumerate(tampilan):
            aks = sumbu[baris, kolom]
            aks.imshow(
                isi,
                cmap="gray",
                vmin=0,
                vmax=255,
                interpolation="nearest",
            )
            aks.set_axis_off()
            if baris == 0:
                aks.set_title(judul_kolom[kolom], pad=3)
        sumbu[baris, 0].text(
            -0.05,
            0.5,
            hasil["judul"],
            transform=sumbu[baris, 0].transAxes,
            rotation=90,
            va="center",
            ha="right",
        )

    gambar.savefig(DIR_KOMPOSIT / "perbandingan_operator.png")
    plt.close(gambar)


def buat_gambar_sapuan(
    hasil_semua: list[dict], konteks_semua: list[dict]
) -> None:
    """Buat gambar pengaruh ambang untuk tiap citra dan operator."""
    for hasil, konteks in zip(hasil_semua, konteks_semua):
        gambar, sumbu = plt.subplots(
            len(URUTAN_OPERATOR),
            len(AMBANG_SAPUAN),
            figsize=(7.2, 5.2),
            constrained_layout=True,
        )
        gambar.suptitle(
            f"Pengaruh ambang pada {hasil['judul']}", fontsize=9
        )
        for baris, kunci_op in enumerate(URUTAN_OPERATOR):
            magnitudo = konteks[kunci_op]["magnitudo"]
            for kolom, ambang in enumerate(AMBANG_SAPUAN):
                biner = np.where(magnitudo >= ambang, 255, 0).astype(np.uint8)
                aks = sumbu[baris, kolom]
                aks.imshow(
                    biner,
                    cmap="gray",
                    vmin=0,
                    vmax=255,
                    interpolation="nearest",
                )
                aks.set_axis_off()
                kepadatan = 100 * float((magnitudo >= ambang).mean())
                if baris == 0:
                    aks.set_title(
                        f"T={ambang}\n{kepadatan:.2f}% piksel",
                        fontsize=8,
                        pad=2,
                    )
                else:
                    aks.set_title(f"{kepadatan:.2f}%", fontsize=7, pad=1)
            sumbu[baris, 0].text(
                -0.08,
                0.5,
                OPERATOR[kunci_op]["judul"],
                transform=sumbu[baris, 0].transAxes,
                rotation=90,
                va="center",
                ha="right",
                fontsize=8,
            )
        gambar.savefig(
            DIR_KOMPOSIT / f"sapuan_ambang_{hasil['kunci']}.png"
        )
        plt.close(gambar)


# ---------------------------------------------------------------------------
# Tabel dan ringkasan
# ---------------------------------------------------------------------------


def tulis_tabel(hasil_semua: list[dict]) -> None:
    """Tulis tabel metrik, sapuan ambang, dan ringkasan Markdown."""
    DIR_TABEL.mkdir(parents=True, exist_ok=True)

    baris_metrik = []
    baris_ambang = []
    for hasil in hasil_semua:
        for kunci_op in URUTAN_OPERATOR:
            metrik = hasil["operator"][kunci_op]
            baris_metrik.append(
                {
                    "Citra": hasil["judul"],
                    "Operator": OPERATOR[kunci_op]["judul"],
                    "Rerata |G|": metrik["rerata_magnitudo"],
                    "Maks |G|": metrik["maks_magnitudo"],
                    "Ambang": metrik["ambang"],
                    "Jumlah tepi": metrik["jumlah_tepi"],
                    "Kepadatan (%)": metrik["kepadatan_tepi_persen"],
                    "Waktu (ms)": metrik["waktu_ms"],
                    "Rasio |Gx|:|Gy|": metrik.get("rasio_gx_gy", "-"),
                    "Arah dominan": metrik.get("arah_dominan", "-"),
                    "Arah dominan (%)": metrik.get("arah_dominan_persen", "-"),
                }
            )
            for isi in hasil["sapuan"][kunci_op]:
                baris_ambang.append(
                    {
                        "Citra": hasil["judul"],
                        "Operator": OPERATOR[kunci_op]["judul"],
                        **isi,
                    }
                )

    tabel_metrik = pd.DataFrame(baris_metrik)
    tabel_ambang = pd.DataFrame(baris_ambang)
    tabel_metrik.to_csv(DIR_TABEL / "tepi_metrik.csv", index=False)
    tabel_ambang.to_csv(DIR_TABEL / "tepi_ambang.csv", index=False)

    with (DIR_KELUARAN / "tepi_ringkasan.md").open(
        "w", encoding="utf-8"
    ) as berkas:
        berkas.write("# Ringkasan Deteksi Tepi Sobel, Roberts, dan Kompas\n\n")
        berkas.write(
            f"Ambang tepi yang dipakai: **T={AMBANG_TEPI:g}** dalam satuan "
            "magnitudo ternormalisasi.\n\n"
        )
        for hasil in hasil_semua:
            berkas.write(f"## {hasil['judul']}\n\n")
            tabel_citra = tabel_metrik[
                tabel_metrik["Citra"] == hasil["judul"]
            ].drop(columns=["Citra"])
            berkas.write(tabel_markdown(tabel_citra))
            berkas.write("\n\n")

            kompas = hasil["operator"]["kompas"]
            berkas.write("Sebaran arah tepi kompas:\n\n")
            berkas.write(
                "Arah: U=utara, BL=barat laut, B=barat, BD=barat daya, "
                "S=selatan, TG=tenggara, T=timur, TL=timur laut.\n\n"
            )
            tabel_arah = pd.DataFrame(kompas["sebaran_arah"]).rename(
                columns={
                    "arah": "Arah",
                    "jumlah": "Jumlah",
                    "persen": "Persen (%)",
                }
            )
            berkas.write(tabel_markdown(tabel_arah))
            berkas.write("\n\n")

        berkas.write("## Sapuan ambang\n\n")
        berkas.write(tabel_markdown(tabel_ambang))
        berkas.write("\n")


# ---------------------------------------------------------------------------
# Program utama
# ---------------------------------------------------------------------------


def main() -> None:
    for direktori in (DIR_GAMBAR, DIR_PANEL, DIR_KOMPOSIT, DIR_TABEL):
        direktori.mkdir(parents=True, exist_ok=True)

    hasil_semua: list[dict] = []
    konteks_semua: list[dict] = []

    for item in DAFTAR_CITRA:
        berkas = DIR_CITRA / item["berkas"]
        warna, keabuan, ukuran_asli = muat_citra(berkas, item["lebar_proses"])
        tinggi, lebar = keabuan.shape

        selisih = verifikasi_konvolusi(keabuan)
        if selisih > 1e-3:
            raise RuntimeError(
                f"Konvolusi manual berbeda dari cv2.filter2D sebesar "
                f"{selisih:.4f}."
            )

        konteks: dict = {"warna": warna, "keabuan": keabuan}
        hasil = {
            "kunci": item["kunci"],
            "judul": item["judul"],
            "berkas": str(berkas.relative_to(AKAR)),
            "ukuran_asli": list(ukuran_asli),
            "ukuran_proses": [lebar, tinggi],
            "selisih_konvolusi": selisih,
            "operator": {},
            "sapuan": {},
        }

        print(f"\n=== {item['judul']} ===")
        print(f"Ukuran asli   : {ukuran_asli[0]} x {ukuran_asli[1]}")
        print(f"Ukuran proses : {lebar} x {tinggi}")
        print(f"Selisih konvolusi manual vs OpenCV: {selisih:.6f}")

        for kunci_op in URUTAN_OPERATOR:
            keluaran, waktu = waktu_ms(
                lambda k=kunci_op: deteksi_tepi(keabuan, k)
            )
            tepi = binerkan(keluaran["magnitudo"], AMBANG_TEPI)
            metrik = hitung_metrik(keluaran, tepi, waktu, kunci_op)

            konteks[kunci_op] = {**keluaran, "tepi": tepi}
            hasil["operator"][kunci_op] = metrik
            hasil["sapuan"][kunci_op] = sapuan_ambang(
                keluaran["magnitudo"]
            )

            print(
                f"{OPERATOR[kunci_op]['judul']:<16}: "
                f"rerata |G|={metrik['rerata_magnitudo']:.2f}, "
                f"maks |G|={metrik['maks_magnitudo']:.1f}, "
                f"tepi T={AMBANG_TEPI:g} sebanyak {metrik['jumlah_tepi']} "
                f"piksel ({metrik['kepadatan_tepi_persen']:.2f}%), "
                f"{waktu:.1f} ms"
            )
            if "rasio_gx_gy" in metrik:
                print(
                    f"{'':16}  rasio |Gx|:|Gy| = {metrik['rasio_gx_gy']:.2f}"
                )
            else:
                print(
                    f"{'':16}  arah dominan = {metrik['arah_dominan']} "
                    f"({metrik['arah_dominan_persen']:.1f}% piksel tepi)"
                )

        buat_gambar(hasil, konteks)
        hasil_semua.append(hasil)
        konteks_semua.append(konteks)

    buat_gambar_perbandingan(hasil_semua, konteks_semua)
    buat_gambar_sapuan(hasil_semua, konteks_semua)

    keluaran = {
        "parameter": {
            "ambang_tepi": AMBANG_TEPI,
            "ambang_sapuan": AMBANG_SAPUAN,
            "normalisasi": (
                "Magnitudo mentah dibagi jumlah bobot positif mask "
                "(Sobel 4, Roberts 1, Kompas 15)."
            ),
        },
        "operator": {
            kunci: {
                "judul": OPERATOR[kunci]["judul"],
                "jenis": OPERATOR[kunci]["jenis"],
                "skala": OPERATOR[kunci]["skala"],
                "keterangan": OPERATOR[kunci]["keterangan"],
                "mask_x": (
                    OPERATOR[kunci]["mask_x"].astype(int).tolist()
                    if "mask_x" in OPERATOR[kunci]
                    else None
                ),
                "mask_y": (
                    OPERATOR[kunci]["mask_y"].astype(int).tolist()
                    if "mask_y" in OPERATOR[kunci]
                    else None
                ),
                "mask": (
                    [mask.astype(int).tolist() for mask in OPERATOR[kunci]["mask"]]
                    if "mask" in OPERATOR[kunci]
                    else None
                ),
                "arah": KOMPAS_ARAH if kunci == "kompas" else None,
            }
            for kunci in URUTAN_OPERATOR
        },
        "citra": hasil_semua,
    }
    with (DIR_KELUARAN / "tepi.json").open("w", encoding="utf-8") as berkas:
        json.dump(keluaran, berkas, indent=2, ensure_ascii=False)

    tulis_tabel(hasil_semua)

    print("\nSelesai.")
    print(f"Gambar   : {DIR_GAMBAR}")
    print(f"Tabel    : {DIR_TABEL}")
    print(f"Ringkasan: {DIR_KELUARAN / 'tepi_ringkasan.md'}")


if __name__ == "__main__":
    main()
