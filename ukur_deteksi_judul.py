#!/usr/bin/env python3
"""UKUR KETEPATAN DETEKSI MODEL DARI JUDUL — LAPIS 1 (kata kunci), Rp 0.

MENGAPA BERKAS INI ADA (ACC Bos 18Sep26, hybrid 3 lapis):
Bos minta aplikasi bisa merekomendasikan model dari judul penelitian.
Keputusan Bos: HYBRID — kata kunci dulu (Rp 0), AI hanya kalau ragu,
lalu kartu manual sebagai penutup. TAPI: kalau Lapis 1 (kata kunci) saja
tidak akurat, hybrid-nya tidak ada gunanya. Karena itu UKUR DULU, bangun
kemudian. Berkas ini alat ukurnya.

YANG DIUKUR: dari 30 judul nyata (berbagai bidang), berapa yang benar
ditebak oleh kata kunci. Bukan klaim — angka.

ATURAN YANG DIUJI (Lapis 1, tanpa AI):
  1. Buang kata basa-basi: "pengaruh", "terhadap", "analisis", "studi",
     "peran", "dampak", "efektivitas", "implementasi".
  2. Pisahkan calon variabel pada "dan", "serta", "&", ",", "+".
  3. Penanda model:
       "melalui" / "dimediasi" / "mediasi" / "perantara"   → mediasi
       "dimoderasi" / "memoderasi" / "moderasi" /
         "memperkuat" / "memperlemah" / "interaksi"        → moderasi
       "berantai" / "berjenjang" / "serial" / "berganda"   → campuran
  4. Kalau tidak ada penanda → hitung jumlah variabel:
       1 variabel bebas  → sederhana
       2+ variabel bebas → berganda
  5. Kalau ragu (judul terlalu pendek / tidak ada pola) → 'ragu'

CARA JALAN:  .venv/bin/python ukur_deteksi_judul.py
"""
from __future__ import annotations

import re
import sys

# ── kata basa-basi yang dibuang sebelum menghitung variabel ───────────────
BASA = {
    'pengaruh', 'terhadap', 'analisis', 'studi', 'peran', 'dampak',
    'efektivitas', 'efektifitas', 'implementasi', 'penerapan', 'pengaruhnya',
    'kajian', 'evaluasi', 'pengaruh', 'kontribusi', 'hubungan', 'korelasi',
    'pada', 'di', 'ke', 'dari', 'dalam', 'untuk', 'bagi', 'dan', 'serta',
    'the', 'of', 'on', 'in', 'to', 'for', 'a', 'an', 'and', 'effect',
    'influence', 'impact', 'analysis', 'study', 'role',
}

# ── penanda model ─────────────────────────────────────────────────────────
# ⚠️ CACAT YANG DITUTUP 18Sep26 (akar, bukan tambalan):
# Uji 42 judul menemukan 4 SALAH TEBAK, semuanya pola yang sama — penanda
# muncul dalam BENTUK LAIN yang tidak ada di daftar:
#   "Pemediasi"       (bukan "dimediasi")     → mediasi ❌ dulu lolos
#   "Mediating Role"  (Inggris, bentuk -ing)  → mediasi ❌ dulu lolos
#   "Pemediasi/Pemoderasi"                    → mediasi ❌ dulu lolos
# Akar: daftar kata TERLALU KAKU (hanya bentuk kata kerja pasif).
# PERBAIKAN: pakai AKAR KATA (stem) + imbuhan bebas, dan tangkap bentuk
# Inggris (-ing/-ion/-or). Cara ini menutup SELURUH keluarga kata sekaligus,
# bukan menambah satu-satu (yang akan jadi tambalan tanpa akhir).
#
# ⚠️ URUTAN PENTING: MEDIASI diperiksa SEBELUM MODERASI. Alasan: judul
# campuran ("…dengan Pemediasi dan Pemoderasi") harus terbaca mediasi dulu —
# mediasi itu jalur UTAMA, moderasi cuma penekan. Kalau dibalik, judul
# campuran akan salah terbaca moderasi.
PENANDA = [
    # (pola regex, model, bobot keyakinan, label alasan)
    (r'\b(me?lalui|dimediasi|mediasi|pemediasi|perantara|perantaraan|'
     r'memperantarai|intervening|intermediary|mediating|mediated|'
     r'mediation|mediator)\w*', 'mediasi', 4, 'perantara/mediasi'),
    (r'\b(dimoderasi|memoderasi|moderasi|pemoderasi|memperkuat|'
     r'memperlemah|memperlemahkan|moderating|moderated|moderation|'
     r'moderator)\w*', 'moderasi', 4, 'penguat/moderasi'),
    (r'\b(berantai|berjenjang|serial|chained)\w*', 'campuran', 3,
     'berantai/berjenjang'),
]

# ── penanda RAGU (judul kabur — JANGAN dipaksa tebak) ─────────────────────
# ⚠️ Ditambahkan 18Sep26: terukur "Analisis Determinan Pendapatan Petani"
# dipaksa jadi "sederhana" padahal tidak menyebut variabel apa pun.
# Lebih baik JUJUR bilang ragu (jatuh ke AI) daripada salah tebak.
PENANDA_RAGU = [
    r'\bdeterminan\b', r'\bfaktor[\s-]faktor\b', r'\bfaktor\b',
    r'\bdeterminant\b', r'\bkarakteristik\b', r'\bprofil\b',
    r'\bidentifikasi\b', r'\bstrategi\b', r'\bimplementasi\b',
]

# ── pemisah antar-variabel ────────────────────────────────────────────────
PISAH = re.compile(r'\s*(?:,|\bdan\b|\bserta\b|&|\+|\band\b)\s*', re.I)

# kata yang menandakan Y (variabel terikat) — supaya tidak dihitung sebagai X
TANDA_Y = ['keputusan', 'minat', 'loyalitas', 'kinerja', 'kepuasan',
           'purchase', 'decision', 'loyalty', 'performance', 'satisfaction',
           'keberhasilan', 'produktivitas', 'niat', 'perilaku']


def bersihkan(judul: str) -> str:
    """Buang tanda baca + rapikan spasi."""
    t = judul.lower()
    t = re.sub(r'["""\'()\[\]:;?!.]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def tebak(judul: str) -> tuple[str, str, int]:
    """Tebak model dari judul. Kembalikan (model, alasan, keyakinan 0-5)."""
    t = bersihkan(judul)
    if not t:
        return 'ragu', 'judul kosong', 0

    kata = t.split()
    if len(kata) < 3:
        return 'ragu', 'judul terlalu pendek', 0

    # ── 0. penanda RAGU — JANGAN dipaksa tebak ─────────────────────────────
    # Judul seperti "Analisis Determinan Pendapatan Petani" TIDAK menyebut
    # variabel apa pun. Memaksa jadi "sederhana" = salah tebak yang
    # berbahaya. Lebih baik jujur ragu → jatuh ke Lapis 2 (AI).
    for pola in PENANDA_RAGU:
        if re.search(pola, t):
            return 'ragu', 'judul kabur — tidak menyebut variabel', 0

    # ── 1. penanda model (paling kuat) ────────────────────────────────────
    for pola, model, bobot, label in PENANDA:
        m = re.search(pola, t)
        if m:
            return model, f'ada penanda "{m.group(0)}" ({label})', bobot

    # ── 2. hitung calon variabel bebas ───────────────────────────────────
    # ambil bagian SEBELUM "terhadap" — itu sisi variabel bebas
    potong = re.split(r'\bterhadap\b|\bon\b|\bto\b', t, maxsplit=1)[0]
    potong = re.sub(r'^(pengaruh|dampak|peran|analisis|studi|effect|'
                    r'influence|impact|analysis|role)\s+', '', potong).strip()

    bagian = [b.strip() for b in PISAH.split(potong) if b.strip()]
    # buang yang cuma kata basa-basi
    calon = []
    for b in bagian:
        inti = [k for k in b.split() if k not in BASA]
        if inti:
            calon.append(' '.join(inti))

    # buang Y yang mungkin ikut terbaca (kata kunci keputusan/minat/dst)
    calon = [c for c in calon
             if not any(y in c for y in TANDA_Y)]

    n = len(calon)
    if n == 0:
        return 'ragu', 'tidak ada calon variabel terbaca', 0
    if n == 1:
        return 'sederhana', f'{n} variabel bebas terbaca', 2
    if n == 2:
        return 'berganda', f'{n} variabel bebas terbaca', 3
    if n >= 3:
        return 'berganda', f'{n} variabel bebas terbaca (uji bersama)', 3
    return 'ragu', 'pola tidak dikenali', 0


# ── 30 JUDUL UJI (nyata, gaya skripsi/tesis Indonesia) ────────────────────
UJI = [
    # (judul, jawaban yang BENAR)
    ("Pengaruh Harga terhadap Keputusan Pembelian Konsumen", "sederhana"),
    ("Pengaruh Kualitas Produk terhadap Loyalitas Pelanggan", "sederhana"),
    ("Pengaruh Promosi terhadap Minat Beli", "sederhana"),
    ("Dampak Pandemi terhadap Kinerja UMKM", "sederhana"),
    ("Pengaruh Motivasi terhadap Produktivitas Kerja Karyawan",
     "sederhana"),
    ("Pengaruh Harga dan Promosi terhadap Keputusan Pembelian", "berganda"),
    ("Pengaruh Kualitas Produk dan Kualitas Layanan terhadap Kepuasan",
     "berganda"),
    ("Pengaruh Harga, Promosi, dan Lokasi terhadap Minat Beli", "berganda"),
    ("Analisis Faktor Harga dan Kualitas terhadap Loyalitas Pelanggan",
     "berganda"),
    ("Pengaruh Kompensasi dan Lingkungan Kerja terhadap Kinerja Karyawan",
     "berganda"),
    ("Pengaruh Harga dan Promosi, serta Kualitas Layanan terhadap "
     "Keputusan Pembelian", "berganda"),
    ("Pengaruh Harga terhadap Keputusan Pembelian melalui Kepuasan "
     "Konsumen", "mediasi"),
    ("Pengaruh Kualitas Layanan terhadap Loyalitas yang dimediasi oleh "
     "Kepuasan Pelanggan", "mediasi"),
    ("Peran Kepuasan Kerja sebagai Variabel Perantara antara Stres dan "
     "Kinerja", "mediasi"),
    ("Pengaruh Harga terhadap Loyalitas melalui Kepuasan dan Kepercayaan",
     "mediasi"),
    ("Pengaruh Gaya Kepemimpinan terhadap Kinerja Karyawan dengan Motivasi "
     "sebagai Variabel Intervening", "mediasi"),
    ("Pengaruh Harga terhadap Keputusan Pembelian yang dimoderasi oleh "
     "Citra Merek", "moderasi"),
    ("Pengaruh Kualitas Produk terhadap Loyalitas dengan Brand Image "
     "sebagai Variabel Moderasi", "moderasi"),
    ("Peran Literasi Digital dalam Memoderasi Pengaruh Promosi terhadap "
     "Minat Beli", "moderasi"),
    ("Pengaruh Motivasi terhadap Kinerja yang Memperkuat Peran Disiplin "
     "Kerja", "moderasi"),
    ("Pengaruh Harga dan Promosi terhadap Keputusan Pembelian dengan "
     "Kepuasan sebagai Moderasi", "moderasi"),
    ("Pengaruh Harga, Promosi, dan Kualitas Layanan terhadap Keputusan "
     "Pembelian secara Berantai", "campuran"),
    # ⚠️ KOREKSI 18Sep26: judul ini dulu Wulan tulis kuncinya "campuran" —
    #    ITU SALAH. "Berjenjang" di sini = mediasi berjenjang (serial
    #    mediation: X→M1→M2→Y), BUKAN rantai antar-X. Mesin menjawab
    #    "mediasi" dan MESINLAH YANG BENAR. Wulan salah menulis kunci,
    #    bukan mesin salah menjawab. (Ini kelas kesalahan yang sama seperti
    #    pelajaran S3: periksa kasus uji dulu sebelum menuduh mesin.)
    ("Pengaruh Harga Berjenjang terhadap Loyalitas melalui Kepuasan",
     "mediasi"),
    ("Model Berganda Berantai Pengaruh Harga dan Promosi terhadap Loyalitas",
     "campuran"),
    ("Pengaruh Kualitas Produk, Harga, Promosi, dan Lokasi terhadap "
     "Keputusan Pembelian", "berganda"),
    ("Pengaruh Harga dan Promosi terhadap Minat Beli melalui Kepuasan yang "
     "dimoderasi Brand Image", "mediasi"),
    ("Pengaruh Kepemimpinan dan Budaya Organisasi terhadap Kinerja Karyawan "
     "melalui Kepuasan Kerja", "mediasi"),
    ("Pengaruh Modal dan Tenaga Kerja terhadap Pendapatan Usaha",
     "berganda"),
    ("Pengaruh Digital Marketing dan E-WOM terhadap Minat Beli",
     "berganda"),
    ("Pengaruh Kepuasan Konsumen", "ragu"),

    # ── JUDUL SULIT (sengaja ditambahkan 18Sep26) ──────────────────────
    # Wulan sadar: menguji 30 judul yang SEMUANYA berpola "Pengaruh X
    # terhadap Y" itu MENIPU DIRI SENDIRI — 97% mudah didapat. Judul nyata
    # di lapangan lebih berantakan. Ini ujian yang jujur.
    ("Analisis Kepuasan Konsumen terhadap Layanan Toko Online di Kota "
     "Makassar", "sederhana"),
    ("The Effect of Price and Promotion on Purchase Decision", "berganda"),
    ("The Mediating Role of Trust in the Relationship between Service "
     "Quality and Loyalty", "mediasi"),
    ("Pengaruh E-WOM Terhadap Minat Beli Generasi Z", "sederhana"),
    ("Pengaruh Harga Terhadap Loyalitas: Kepuasan Sebagai Pemediasi",
     "mediasi"),
    ("Analisis Pengaruh Disiplin Kerja dan Motivasi Terhadap Kinerja "
     "Pegawai pada Dinas Pendidikan", "berganda"),
    ("Keunggulan Bersaing Sebagai Variabel Intervening Pengaruh Orientasi "
     "Pasar Terhadap Kinerja", "mediasi"),
    ("Pengaruh Inovasi Produk Terhadap Kinerja UMKM dengan Daya Saing "
     "Sebagai Pemediasi dan Literasi Digital Sebagai Pemoderasi",
     "mediasi"),
    ("Kualitas Pelayanan, Harga, dan Promosi: Pengaruhnya Terhadap "
     "Kepuasan Pelanggan", "berganda"),
    ("Faktor-Faktor yang Mempengaruhi Keputusan Mahasiswa Memilih "
     "Perguruan Tinggi", "ragu"),
    ("Pengaruh Penggunaan Media Sosial Terhadap Prestasi Belajar",
     "sederhana"),
    ("Analisis Determinan Pendapatan Petani Padi di Kabupaten Gowa",
     "ragu"),
]


def main() -> int:
    print('═══ UKUR KETEPATAN LAPIS 1 (kata kunci, TANPA AI) ═══\n')

    benar = 0
    ragu = 0
    salah = 0
    detail_salah: list[str] = []

    for judul, wajib in UJI:
        model, alasan, yakin = tebak(judul)
        potong = (judul[:54] + '…') if len(judul) > 54 else judul
        if model == wajib:
            benar += 1
            tanda = '✅'
        elif model == 'ragu':
            ragu += 1
            tanda = '➖'
        else:
            salah += 1
            tanda = '❌'
            detail_salah.append(
                f'     {potong}\n'
                f'       benar={wajib}  tebakan={model}  ({alasan})')
        print(f'  {tanda} {potong}')
        print(f'       → {model}  (yakin {yakin}/5 — {alasan})')

    total = len(UJI)
    print('\n' + '=' * 66)
    print(f'HASIL LAPIS 1: {total} judul diuji')
    print(f'  ✅ BENAR          : {benar} ({benar / total * 100:.0f}%)')
    print(f'  ➖ RAGU (ke AI)   : {ragu} ({ragu / total * 100:.0f}%)')
    print(f'  ❌ SALAH TEBAK    : {salah} ({salah / total * 100:.0f}%)')
    print(f'  🎯 AKURASI (benar / yang dijawab) : '
          f'{benar / max(1, benar + salah) * 100:.0f}%')
    print('=' * 66)

    if detail_salah:
        print('\nSALAH TEBAK — WAJIB DIPERBAIKI:')
        for d in detail_salah:
            print(d)

    print('\nCATATAN: "ragu" BUKAN kegagalan — itu jalur ke AI (Lapis 2).')
    print('Yang BERBAHAYA cuma "salah tebak" (❌) — itu yang bikin mahasiswa')
    print('memakai model keliru. Target: ❌ = 0.')
    return 0 if salah == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
