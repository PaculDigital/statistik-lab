"""LAPIS 1 — Deteksi model penelitian dari JUDUL, tanpa AI (Rp 0, instan).

MENGAPA BERKAS INI ADA (ACC Bos 18Sep26, hybrid 3 lapis):
Bos minta aplikasi bisa merekomendasikan model penelitian dari judul user.
Keputusan Bos: HYBRID —
   Lapis 1: kata kunci (berkas ini)  → terukur 40/42 benar, 0 salah tebak
   Lapis 2: AI 9router               → hanya kalau Lapis 1 ragu
   Lapis 3: kartu manual             → penutup, aplikasi TIDAK PERNAH buntu

PRINSIP YANG DIPEGANG:
· PERSIS vs MIRIP: di sini kita hanya membaca TEKS judul, tidak menghitung
  statistik. Jadi tidak ada toleransi — harus tegas salah/benar.
· LEBIH BAIK RAGU DARIPADA SALAH TEBAK. Salah tebak = mahasiswa memakai
  model keliru → analisisnya salah dari akar. Ragu = jatuh ke Lapis 2.
· ALASAN HARUS JUJUR: alasan diambil dari KATA YANG BENAR-BENAR DITEMUKAN
  di judul, bukan karangan. Kalau tidak ada bukti, jangan mengaku yakin.

AKAR YANG DITUTUP (pelajaran 18Sep26, dari uji 42 judul):
Daftar kata versi pertama TERLALU KAKU — hanya bentuk pasif ("dimediasi",
"melalui"). Judul nyata memakai bentuk lain: "Pemediasi", "Mediating Role",
"Pemoderasi". Akibatnya 4 SALAH TEBAK. Perbaikannya bukan menambah kata
satu-satu (itu tambalan tanpa akhir), tapi memakai AKAR KATA + imbuhan
bebas + bentuk Inggris (-ing/-ion/-or). Satu perbaikan menutup satu
keluarga kata sekaligus.

⚠️ URUTAN PENTING: MEDIASI diperiksa SEBELUM MODERASI. Judul campuran
("…dengan Pemediasi dan Pemoderasi") harus terbaca mediasi dulu, karena
mediasi itu jalur UTAMA sedangkan moderasi hanya penekan pengaruh.
"""
from __future__ import annotations

import re

# ── kata basa-basi (dibuang sebelum menghitung variabel) ──────────────────
BASA = {
    'pengaruh', 'terhadap', 'analisis', 'studi', 'peran', 'dampak',
    'efektivitas', 'efektifitas', 'implementasi', 'penerapan', 'pengaruhnya',
    'kajian', 'evaluasi', 'kontribusi', 'hubungan', 'korelasi',
    'pada', 'di', 'ke', 'dari', 'dalam', 'untuk', 'bagi',
    'the', 'of', 'on', 'in', 'to', 'for', 'a', 'an',
    'effect', 'influence', 'impact', 'analysis', 'study', 'role',
}

# ── penanda model (URUTAN PENTING: mediasi sebelum moderasi) ──────────────
PENANDA = [
    (r'\b(me?lalui|dimediasi|mediasi|pemediasi|perantara|perantaraan|'
     r'memperantarai|intervening|intermediary|mediating|mediated|'
     r'mediation|mediator)\w*', 'mediasi', 4, 'perantara / mediasi'),
    (r'\b(dimoderasi|memoderasi|moderasi|pemoderasi|memperkuat|'
     r'memperlemah|memperlemahkan|moderating|moderated|moderation|'
     r'moderator)\w*', 'moderasi', 4, 'penguat / moderasi'),
    (r'\b(berantai|berjenjang|serial|chained)\w*', 'campuran', 3,
     'berantai / berjenjang'),
]

# ── penanda RAGU — JANGAN dipaksa tebak (jatuh ke Lapis 2) ────────────────
PENANDA_RAGU = [
    r'\bdeterminan\b', r'\bfaktor[\s-]faktor\b', r'\bfaktor\b',
    r'\bdeterminant\b', r'\bkarakteristik\b', r'\bprofil\b',
    r'\bidentifikasi\b', r'\bstrategi\b', r'\bimplementasi\b',
]

# pemisah antar-variabel
PISAH = re.compile(r'\s*(?:,|\bdan\b|\bserta\b|&|\+|\band\b)\s*', re.I)

# kata yang menandakan VARIABEL TERIKAT (jangan dihitung sebagai X)
TANDA_Y = [
    'keputusan', 'minat', 'loyalitas', 'kinerja', 'kepuasan',
    'purchase', 'decision', 'loyalty', 'performance', 'satisfaction',
    'keberhasilan', 'produktivitas', 'niat', 'perilaku', 'pendapatan',
    'prestasi', 'kunjungan', 'penjualan', 'profitabilitas',
]

# pemisah sisi kiri (variabel bebas) vs sisi kanan (variabel terikat)
POTONG = re.compile(r'\bterhadap\b|\bon\b|\bto\b|\bupon\b', re.I)

# ── nama model dalam bahasa AWAM (untuk tampilan ke user) ─────────────────
NAMA_AWAM = {
    'sederhana': 'Regresi Linear Sederhana',
    'berganda': 'Regresi Linear Berganda',
    'mediasi': 'Mediasi (ada perantara)',
    'moderasi': 'Moderasi (ada penguat/pelemah)',
    'campuran': 'Model Gabungan / Berantai',
    'ragu': 'Belum bisa dipastikan',
}

# kode model → halaman pengisian
KODE = {
    'sederhana': 'sederhana',
    'berganda': 'berganda',
    'mediasi': 'mediasi',
    'moderasi': 'moderasi',
    'campuran': 'gabungan',
    'ragu': '',
}


def bersihkan(judul: str) -> str:
    """Buang tanda baca, rapikan spasi, huruf kecil semua."""
    t = (judul or '').lower()
    t = re.sub(r'["“”\'‘’()\[\]:;?!.]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def baca(judul: str) -> dict:
    """Baca judul → usulan model + ALASAN yang bisa diaudit.

    Mengembalikan dict:
      model      : 'sederhana'|'berganda'|'mediasi'|'moderasi'|'campuran'|'ragu'
      yakin      : 0-5 (0 = tidak tahu)
      alasan     : kalimat bahasa Indonesia, HANYA menyebut bukti yang ada
      penanda    : teks penanda yang ditemukan ('' kalau tidak ada)
      variabel   : daftar calon variabel bebas yang terbaca
      butuh_ai   : True kalau sebaiknya dilanjutkan ke Lapis 2
    """
    t = bersihkan(judul)
    if not t:
        return {'model': 'ragu', 'yakin': 0,
                'alasan': 'Judulnya masih kosong.', 'penanda': '',
                'variabel': [], 'butuh_ai': False}

    kata = t.split()
    if len(kata) < 3:
        return {'model': 'ragu', 'yakin': 0,
                'alasan': 'Judulnya masih terlalu pendek untuk dibaca.',
                'penanda': '', 'variabel': [], 'butuh_ai': True}

    # ── 0. penanda RAGU — jangan dipaksa tebak ────────────────────────────
    # Judul seperti "Analisis Determinan Pendapatan Petani" TIDAK menyebut
    # variabel apa pun. Memaksa jadi "sederhana" = salah tebak berbahaya.
    for pola in PENANDA_RAGU:
        if re.search(pola, t):
            return {'model': 'ragu', 'yakin': 0,
                    'alasan': 'Judul ini belum menyebut variabel yang '
                              'dibandingkan, jadi belum bisa dipastikan.',
                    'penanda': '', 'variabel': [], 'butuh_ai': True}

    # ── 1. penanda model (bukti paling kuat) ──────────────────────────────
    for pola, model, bobot, label in PENANDA:
        m = re.search(pola, t)
        if m:
            # ambil kalimat penjelas sesuai model
            if model == 'mediasi':
                alasan = (f'Judulmu menyebut kata "{m.group(0)}" — artinya '
                          f'ada variabel perantara yang meneruskan pengaruh '
                          f'sebelum sampai ke tujuan.')
            elif model == 'moderasi':
                alasan = (f'Judulmu menyebut kata "{m.group(0)}" — artinya '
                          f'ada variabel lain yang memperkuat atau '
                          f'melemahkan pengaruhnya.')
            else:
                alasan = (f'Judulmu menyebut kata "{m.group(0)}" — artinya '
                          f'variabel bebasnya juga saling berhubungan, '
                          f'bukan berdiri sendiri.')
            return {'model': model, 'yakin': bobot, 'alasan': alasan,
                    'penanda': m.group(0), 'variabel': [], 'butuh_ai': False}

    # ── 2. hitung calon variabel BEBAS ────────────────────────────────────
    potong = POTONG.split(t, maxsplit=1)[0]
    potong = re.sub(
        r'^(pengaruh|dampak|peran|analisis|studi|effect|influence|impact|'
        r'analysis|role)\s+', '', potong).strip()

    bagian = [b.strip() for b in PISAH.split(potong) if b.strip()]
    calon = []
    for b in bagian:
        inti = [k for k in b.split() if k not in BASA]
        if inti:
            calon.append(' '.join(inti))

    # buang yang sebenarnya variabel TERIKAT (kata kunci keputusan/minat/dst)
    calon = [c for c in calon if not any(y in c for y in TANDA_Y)]

    n = len(calon)
    if n == 0:
        return {'model': 'ragu', 'yakin': 0,
                'alasan': 'Belum terbaca variabel yang dibandingkan '
                          'di judul ini.',
                'penanda': '', 'variabel': [], 'butuh_ai': True}
    if n == 1:
        return {'model': 'sederhana', 'yakin': 2,
                'alasan': f'Judulmu menyebut satu hal yang diuji '
                          f'({calon[0]}), jadi pengaruhnya diukur sendirian.',
                'penanda': '', 'variabel': calon, 'butuh_ai': False}
    if n == 2:
        return {'model': 'berganda', 'yakin': 3,
                'alasan': f'Judulmu menyebut dua hal yang diuji bersama-sama '
                          f'({calon[0]} dan {calon[1]}) ke satu tujuan.',
                'penanda': '', 'variabel': calon, 'butuh_ai': False}
    return {'model': 'berganda', 'yakin': 3,
            'alasan': f'Judulmu menyebut {n} hal yang diuji bersama-sama '
                      f'({", ".join(calon[:3])}{"…" if n > 3 else ""}) '
                      f'ke satu tujuan.',
            'penanda': '', 'variabel': calon, 'butuh_ai': False}


def nama_awam(model: str) -> str:
    """Nama model dalam bahasa yang bisa dipahami orang awam."""
    return NAMA_AWAM.get(model, 'Belum bisa dipastikan')


def kode_model(model: str) -> str:
    """Kode model untuk tautan ke /buat-data?model=..."""
    return KODE.get(model, '')
