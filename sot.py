#!/usr/bin/env python3
"""SOT STATISTIK LAB — SATU PINTU INFORMASI (Single Source of Truth).

═══════════════════════════════════════════════════════════════════════════
PRINSIP (arahan Bos 18Sep26): "tetap prinsip SOT single source of truth".

Sumber kebenaran TERTINGGI = **KODE DI DISK** (bukan dokumen, bukan memory).
Dokumen (MASTER_PLAN / FLAG / skill / memory) hanya SALINAN — kalau berbeda,
KODE yang menang.

Skrip ini menyatukan segala informasi penting yang SEBELUMNYA tercerai-berai:
  • peta kemampuan mesin (bentuk model + status di web)
  • jumlah grup uji & asersi  → DIHITUNG dari kode, bukan dihafal
  • status tiap halaman web
  • jebakan & akar yang wajib diingat
  • cara uji yang benar

Pakai:
    .venv/bin/python sot.py            # cetak ringkasan
    .venv/bin/python sot.py --periksa  # cetak + periksa KONSISTENSI (exit code)
    .venv/bin/python sot.py --json     # keluaran mesin (untuk alat lain)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

KONTAINER = 'simulasi-olah-data'
PORT = 8120
DOMAIN = 'statistik.bikinaja.id'
NAMA_TAMPIL = 'Penelitian STATISTIK Lab.'


def _baca(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except Exception:                                   # noqa: BLE001
        return ''


def _hitung_grup_gerbang() -> int:
    return len(re.findall(r'^\s{4}\(', _baca(BASE / 'gerbang_uji.py'), re.M))


def _hitung_kemampuan() -> dict:
    """Peta bentuk model → sudah bisa dipilih di web atau belum.

    ⚠️ AKAR CACAT YANG DITUTUP (20Sep26) — SOT DULU SALAH UKUR:
    (1) `jenis_analisis_di_web` dulu **DITULIS MATI** (`['sederhana','berganda',
        'keduanya']`) — tidak pernah dihitung. Sejak Tahap 1.3 membuka
        **13 bentuk**, angka itu BASI dan SOT tetap melaporkan
        "BELUM: mediasi, moderasi" padahal SUDAH ADA di web.
    (2) SOT membaca `buat_data.html` dengan pola `data-cara="..."`, padahal
        **kartu model** (sumber kebenaran bentuk yang bisa dipilih user)
        ada di **`kuantitatif.html`** sebagai `href="/buat-data?model=<slug>"`.
        `data-cara` di buat_data.html cuma 3 nilai (cara MENGUJI), bukan daftar model.

    PERBAIKAN: hitung slug model SUNGGUHAN dari `href="/buat-data?model=<slug>"`
    di `kuantitatif.html`.  ➜  daftar selalu ikut kode, tidak bisa basi.
    """
    web = _baca(BASE / 'app' / 'templates' / 'buat_data.html')
    kuant = _baca(BASE / 'app' / 'templates' / 'kuantitatif.html')

    # ── Slug model SUNGGUHAN: dari kartu di /kuantitatif ────────────────
    slug_web = sorted(set(re.findall(
        r'/buat-data\?model=([a-z0-9-]+)', kuant)))

    # ── Jalur model di buat_data.html (bentuk yang punya pengaturan) ────
    jalur_web = sorted(set(re.findall(r"^\s*'([a-z0-9-]+)':\s*\{", web,
                                      re.M)))

    # ⚠️ JANGAN CAMPUR DUA HAL BERBEDA (pelajaran 20Sep26):
    #   `slug_web` (14) = SEMUA kartu klik-able di /kuantitatif —
    #       termasuk `gabungan` yang MASIH LANGSUNG (belum punya sub-pilihan).
    #   `sub_pilihan` (13) = bentuk yang punya sub-pilihan sendiri —
    #       Regresi 3 + Mediasi 4 + Moderasi 6. Angka INI yang dipakai dokumen.
    # Dulu SOT melaporkan 14 sebagai "bentuk yang sudah bisa" → tampak
    # bertentangan dengan dokumen (13) padahal dua-duanya BENAR.
    INDUK = {'sederhana', 'berganda', 'berantai', 'mediasi', 'mediasi-paralel',
             'mediasi-berjenjang', 'mediasi-campuran', 'moderasi',
             'moderasi-dual', 'moderasi-jalur-a', 'moderasi-jalur-b',
             'moderasi-keduanya', 'moderasi-3jalur'}
    sub_pilihan = sorted(set(slug_web) & INDUK)
    belum_punya_sub = sorted(set(slug_web) - INDUK)

    return {
        'mesin_terbukti': [
            ('regresi_sederhana', 'Regresi sederhana (1 X → Y)', 0.0067),
            ('regresi_berganda', 'Regresi berganda (n X → Y)', 0.0026),
            ('mediasi_tunggal', 'Mediasi tunggal (X → M → Y)', 0.0171),
            ('dual_mediasi_paralel', 'Dual mediasi paralel', 0.0049),
            ('mediasi_berjenjang', 'Mediasi berjenjang (X→M1→M2→Y)', 0.0092),
            ('moderasi_mra', 'Moderasi MRA (X, Z, X×Z → Y)', 0.0081),
            ('dual_moderasi', 'Dual moderasi (X×Z1 & X×Z2 → Y)', 0.0130),
            ('moderated_mediation', 'Moderated mediation (M×Z → Y)', 0.0258),
            ('moderasi_jalur_a', 'Moderasi jalur-a (X×Z → M)', 0.0075),
            ('model_bertingkat', 'Model 4 tingkat, 2 keluaran', 0.0044),
        ],
        'halaman_web': {
            '/': 'beranda — 6 kartu modul',
            '/kuantitatif': 'pilih model (4 kartu induk → sub-pilihan)',
            '/belajar': 'kamus interaktif berslider + 3 tab',
            '/buat-data': 'setelan + pagar signifikansi',
            '/diagnosis': 'ALAT — unggah data → 6 uji SPSS + 5 uji PLS',
            '/pengaturan': 'saklar AI ON/OFF',
            '/segera/<slug>': 'halaman modul belum siap',
        },
        'slug_model_web': slug_web or ['(tidak terbaca)'],
        'sub_pilihan': sub_pilihan or ['(tidak terbaca)'],
        'belum_punya_sub': belum_punya_sub,
        'jalur_di_buat_data': jalur_web or ['(tidak terbaca)'],
        'jenis_analisis_di_web': slug_web or ['(tidak terbaca)'],
    }


def _hitung_jebakan() -> list[tuple[str, str]]:
    return [
        ('Uji dari HALAMAN SUNGGUHAN',
         'Halaman dibuka file:// → tautan /static/gaya.css jadi '
         'file:///static/gaya.css → CSS TIDAK termuat → semua temuan PALSU '
         '(mis. display:inline). SUNTIK CSS-nya, jangan buka file://.'),
        ('Ukur KATA, bukan KOTAK elemen',
         'getBoundingClientRect() pada <span> grid-item selalu selebar kolom '
         '→ tampak "sudah benar" padahal kata di dalamnya melayang. '
         'Pakai document.createRange() untuk mengukur KATA-nya.'),
        ('Tanya CSSOM siapa yang MENANG',
         'Spesifisitas menang atas urutan. `.medan label` (0,1,1) mengalahkan '
         '.pilih-cara (0,1,0) walau ditulis belakangan. Pakai `label.pilih-cara`.'),
        ('JANGAN percaya nilai BAWAAN',
         'item_per bawaan 4 padahal data dibangun item_per=3 → IndexError. '
         'Ukur item_per dari bentuk matriks item.'),
        ('Chrome menolak lebar < 500px',
         '--window-size=390 tetap dirender 500px → "uji HP" PALSU. '
         'Pakai CDP Device.setDeviceMetricsOverride.'),
        ('Gerbang yang tak bisa membaca = GAGAL',
         'Gerbang yang membaca kontainer LAMA memberi temuan palsu. '
         'Uji dari BERKAS; kalau tak terbaca → GAGAL, bukan lolos.'),
        ('curl 127.0.0.1:8120 dari Wulan SELALU gagal',
         'Wulan di dalam container Hermes — loopback berbeda. '
         'Pakai IP kontainer atau docker exec.'),
        ('Nilai LULUS/GAGAL dari EXIT CODE',
         'JANGAN grep teks — "GAGAL" cocok juga di "0 GAGAL".'),
    ]


def _baca_urutan_tahap(p: Path) -> dict[int, str]:
    """Ambil daftar tahap dari dokumen. DUA BENTUK didukung:

    1. **Baris tabel** — `| 4 | Pemilih alat | ... |`  (dipakai MASTER_PLAN §9)
    2. **Judul bab**  — `# 🎯 TAHAP 4 — PEMILIH ALAT (tujuan akhir Bos)`
       (dipakai TAHAP_PENYELESAIAN.md)

    ⚠️ MENGAPA ADA (20Sep26): sebelum ini SOT HANYA memeriksa jumlah grup uji.
    Akibatnya `MASTER_PLAN.md §9` dan `TAHAP_PENYELESAIAN.md` bisa memuat
    URUTAN TAHAP yang SALING BERLAWANAN (Ujian/Pemilih alat/Login/Kualitatif
    tertukar) dan SOT tetap bilang "SELARAS". Itu cacat SOT yang NYATA.

    Yang dibandingkan adalah **INTI tahap** (kata kunci dinormalkan), bukan
    kalimat penuh — kalimat boleh berbeda, MAKNA tahapnya harus sama.
    """
    teks = _baca(p)
    hasil: dict[int, str] = {}

    # Bentuk 1 — baris tabel `| <n> | <isi> |`
    for baris in teks.splitlines():
        m = re.match(r'^\|\s*(\d+)\s*\|\s*(.+?)\s*\|', baris)
        if m:
            no = int(m.group(1))
            if 1 <= no <= 9:
                inti = _inti_tahap(m.group(2))
                if inti:
                    hasil[no] = inti

    # Bentuk 2 — judul `# ... TAHAP <n> — <isi>`
    for m in re.finditer(r'^#+[^\n]*?TAHAP\s*(\d+)\s*[—–-]\s*([^\n]+)',
                         teks, re.M | re.I):
        no = int(m.group(1))
        if not (1 <= no <= 9):
            continue
        inti = _inti_tahap(m.group(2))
        if inti:
            hasil.setdefault(no, inti)

    return hasil


# Kata kunci → nama tahap yang dinormalkan.
#
# ⚠️ PELAJARAN 20Sep26: pembanding ini TIDAK BOLEH menuntut kata yang sama.
# Tahap 1 MASTER_PLAN menyebut "Kontainer + beranda + BELAJAR + BUAT DATA",
# sedangkan TAHAP_PENYELESAIAN menyebut "LEBARKAN PINTU (mesin → layar)" —
# DUA SEBUTAN untuk HAL YANG SAMA. Pembanding yang menuntut kata identik
# akan melaporkan "bertentangan" palsu. Yang dibandingkan = MAKNA.
#
# Urutan kunci MENENTUKAN: yang paling khas diperiksa lebih dulu.
_KUNCI_TAHAP: list[tuple[str, str]] = [
    ('kualitatif', 'kualitatif'),
    ('login', 'login'),
    ('pemilih alat', 'pemilih-alat'),
    ('pilih spss', 'pemilih-alat'),
    ('smartpls', 'pemilih-alat'),
    ('tujuan akhir', 'pemilih-alat'),
    ('ujian', 'ujian'),
    ('klinik', 'klinik'),
    ('data sakit', 'klinik'),
    ('periksa syarat', 'syarat'),
    ('baca grafik', 'syarat'),
    ('grafik hidup', 'syarat'),
    ('mediasi', 'mesin-model'),
    ('lebarkan pintu', 'mesin-model'),
    ('mesin → layar', 'mesin-model'),
    ('mesin ke layar', 'mesin-model'),
    ('buat data', 'buat-data'),
    ('belajar', 'buat-data'),
    ('kontainer', 'buat-data'),
    ('beranda', 'buat-data'),
]


def _inti_tahap(isi: str) -> str:
    """Normalkan isi sel tabel jadi satu nama tahap (untuk dibandingkan)."""
    t = re.sub(r'[*`⭐✅⬜⏭️⚠️]', '', isi).lower()
    for kunci, nama in _KUNCI_TAHAP:
        if kunci in t:
            return nama
    return ''


def _periksa_urutan_tahap() -> list[str]:
    """Periksa apakah kedua dokumen SEPAKAT soal URUTAN TAHAP BESAR.

    ⚠️ KEPUTUSAN BOS 20Sep26 (penting — jangan diubah tanpa ACC):
    Kedua dokumen **TAKARANNYA BERBEDA dan itu SAH**:
      • `MASTER_PLAN §9`      = **7 TAHAP BESAR** (peta kasar)
      • `TAHAP_PENYELESAIAN`  = **rincian** (bab tahap + sub-langkah 1.1–1.6,
                                2.1–2.5, dst.) — sengaja lebih halus

    Jadi penjaga ini **TIDAK** menuntut kata/nomor sama. Yang diperiksa:
    **tiga tahap besar terakhir harus di URUTAN yang sama di kedua dokumen**,
    karena di situlah dulu terjadi tabrakan nyata
    (Ujian / Pemilih alat / Login / Kualitatif tertukar posisi).

    Yang diperiksa = **URUTAN KEMUNCULAN** tahap besar, bukan nomor baris.
    """
    masalah: list[str] = []
    a_path = BASE / 'MASTER_PLAN.md'
    b_path = BASE / 'TAHAP_PENYELESAIAN.md'
    if not a_path.exists() or not b_path.exists():
        return masalah

    # ── Kumpulkan nomor tahap per-inti, per dokumen ─────────────────────
    a = _baca_urutan_tahap(a_path)      # MASTER_PLAN §9 (7 tahap besar)
    b = _baca_urutan_tahap(b_path)      # TAHAP_PENYELESAIAN (bab tahap)

    if not a:
        masalah.append('MASTER_PLAN.md: tabel URUTAN TAHAP (§9) tidak terbaca')
    if not b:
        masalah.append('TAHAP_PENYELESAIAN.md: daftar tahap tidak terbaca')
    if not a or not b:
        return masalah

    # ── 1) Cek satu-satu nomor yang SAMA di kedua dokumen ───────────────
    # ⚠️ PETA TERJEMAHAN (ACC Bos 20Sep26): nomor tahap di dua dokumen
    # BUKAN hal yang sama — takarannya beda dan itu SAH.
    #   MASTER_PLAN (7 besar)        TAHAP_PENYELESAIAN (rinci)
    #   T1 buat-data      ←→  T1 mesin-model  (13 bentuk ke layar)
    #   T2 syarat         ←→  T2 syarat       ✅ sama
    #   T3 klinik         ←→  T3 klinik       ✅ sama
    #   T4 pemilih-alat   ←→  T4 pemilih-alat ✅ sama
    #   T5 ujian          ←→  T5 ujian        ✅ sama
    #   T6 kualitatif     ←→  T6 kualitatif   ✅ sama
    #   T7 login          ←→  T7 login        ✅ sama
    # Pasangan T1↔T1 BEDA ISI karena "bikin wadah" (MASTER_PLAN) memang
    # tahap besar tersendiri, sedangkan TAHAP_PENYELESAIAN memecahnya jadi
    # sub-langkah 1.1–1.6. KEDUANYA BENAR — jangan dipaksa sama.
    PASANGAN_BEDA_SAH = {(1, 'buat-data', 'mesin-model')}

    for no in sorted(set(a) & set(b)):
        if a[no] == b[no]:
            continue
        if (no, a[no], b[no]) in PASANGAN_BEDA_SAH:
            continue
        masalah.append(
            f'TAHAP {no} BERTENTANGAN — '
            f'MASTER_PLAN: {a[no]} · TAHAP_PENYELESAIAN: {b[no]}')

    # ── 2) Cek URUTAN (inti `pemilih-alat` harus sebelum `ujian`, dst.) ──
    def _posisi(d: dict[int, str], inti: str) -> int | None:
        for no in sorted(d):
            if d[no] == inti:
                return no
        return None

    for lebih_dulu, kemudian in (('klinik', 'pemilih-alat'),
                                 ('pemilih-alat', 'ujian'),
                                 ('ujian', 'kualitatif'),
                                 ('kualitatif', 'login')):
        pa, pb = _posisi(a, lebih_dulu), _posisi(a, kemudian)
        if pa is not None and pb is not None and pa > pb:
            masalah.append(
                f'MASTER_PLAN: {lebih_dulu} (tahap {pa}) muncul SETELAH '
                f'{kemudian} (tahap {pb}) — urutan terbalik')

    return masalah


def kumpulkan() -> dict:
    kem = _hitung_kemampuan()
    return {
        'proyek': NAMA_TAMPIL,
        'kontainer': KONTAINER,
        'port': PORT,
        'domain': DOMAIN,
        'direktori': str(BASE),
        'grup_gerbang': _hitung_grup_gerbang(),
        'kemampuan': kem,
        'jebakan': _hitung_jebakan(),
        'deploy': 'bash jalankan.sh  (gerbang uji → build → ganti kontainer → /health)',
    }


def cetak(d: dict) -> None:
    print('═' * 74)
    print(f'  SOT — {d["proyek"]}')
    print('═' * 74)
    print(f'  Kontainer  : {d["kontainer"]}  (port {d["port"]} → 8000)')
    print(f'  Domain     : {d["domain"]}')
    print(f'  Direktori  : {d["direktori"]}')
    print(f'  Deploy     : {d["deploy"]}')
    print(f'  Grup gerbang uji : {d["grup_gerbang"]}  (DIHITUNG dari kode, '
          f'bukan dihafal)')

    k = d['kemampuan']
    print(f'\n  ── BENTUK MODEL YANG SUDAH TERBUKTI DI MESIN ──')
    for kode, nama, galat in k['mesin_terbukti']:
        print(f'     ✅ {nama:44} galat {galat:.4f}')

    print(f'\n  ── HALAMAN WEB ──')
    for rute, isi in k['halaman_web'].items():
        print(f'     {rute:16} {isi}')

    print(f'\n  ── JENIS ANALISIS DI WEB ──')
    print(f'     KARTU klik-able   : {len(k["jenis_analisis_di_web"])} '
          f'slug (dari /kuantitatif)')
    print(f'     PUNYA SUB-pilihan : {len(k["sub_pilihan"])} bentuk  '
          f'← angka yang dipakai dokumen')
    if k['belum_punya_sub']:
        print(f'     belum punya sub   : {", ".join(k["belum_punya_sub"])}')
    print(f'     jalur di buat_data: {", ".join(k["jalur_di_buat_data"])}')

    print(f'\n  ── JEBAKAN WAJIB DIINGAT ──')
    for judul, isi in d['jebakan']:
        print(f'     ⚠️  {judul}')
        print(f'         {isi}')


def _periksa_kartu_regresi() -> list[str]:
    """Periksa: KARTU REGRESI di pintu sesuai KEPUTUSAN BOS 21Sep26 (N1+R1+P1).

    ATURAN (ACC Bos 21Sep26):
      · Kartu ① = PARSIAL (banyak X → Y, satu-satu)
      · Kartu ② = BERGANDA (Parsial + Simultan)
      · Kartu "berantai" DIARSIPKAN → TIDAK boleh tampil di pintu
      · Kode `cara='berantai'` TETAP ADA di mesin (R1) → JANGAN dihapus

    ⚠️ KENAPA PENJAGA INI ADA: 21Sep26 kartu "berganda-berantai" ditemukan
    MENYESATKAN (gambar panah rantai bermata + hanya X terakhir ke Y, padahal
    teks bilang "semua X bersama-sama"). Akarnya: kartu "berantai" lahir dari
    kebingungan mencari PARSIAL yang tak pernah ditampilkan. Tanpa penjaga,
    kartu bisa muncul lagi diam-diam setelah diarsipkan.
    """
    masalah = []
    pintu = BASE / 'app' / 'templates' / 'buat_data.html'
    if not pintu.exists():
        return ['buat_data.html tidak terbaca — penjaga kartu regresi BUTA']

    isi = _baca(pintu)

    # ⚠️ PELAJARAN 21Sep26 (penjaga ini sendiri sempat SALAH ALARM):
    #    versi pertama memakai `re.findall(r'data-cara="(\w+)"')` — itu
    #    menemukan SEMUA kartu termasuk yang sudah `class="pilih-cara
    #    sembunyi"` → protes "berantai masih tampil" padahal sudah disembunyikan.
    #    ATURAN: penjaga harus mengukur KARTU YANG TAMPIL, bukan sekadar ada.
    #    Jadi: ambil tiap blok <label ... data-cara="X" ...> lalu periksa
    #    apakah blok itu memuat kelas 'sembunyi'.
    kartu_tampil, kartu_arsip = [], []
    for m in re.finditer(
            r'<label\b[^>]*class="([^"]*)"[^>]*data-cara="(\w+)"', isi):
        kelas, nama = m.group(1), m.group(2)
        (kartu_arsip if 'sembunyi' in kelas else kartu_tampil).append(nama)

    # (a) berantai TIDAK boleh TAMPIL di pintu (arsip, bukan hapus)
    if 'berantai' in kartu_tampil:
        masalah.append(
            'buat_data.html: kartu "berantai" masih TAMPIL di pintu — '
            'ACC Bos 21Sep26 = DIARSIPKAN (R1), tidak ditampilkan')
    # (a2) kartu berantai HARUS tetap ADA (arsip, bukan hapus)
    if 'berantai' not in kartu_arsip:
        masalah.append(
            'buat_data.html: kartu "berantai" HILANG dari pintu — '
            'ACC Bos 21Sep26 = DIARSIPKAN (kartu tetap ada, ditutup dengan '
            'class "sembunyi"). Menghapusnya = melanggar R1')

    # (b) kode cara='berantai' HARUS masih ada di mesin (R1 = arsip, bukan hapus)
    # ⚠️ PELAJARAN 21Sep26 (penjaga sempat BUTA di sini):
    #    versi pertama cuma cek `"'berantai'" not in isi` — mesin punya 10
    #    kemunculan, jadi menghapus 3 saja TIDAK tertangkap. Penjaga yang
    #    cuma bertanya "ada kata?" tidak bisa mengukur "masih berfungsi?".
    #    FIX: tuntut TIGA tanda yang membuat mesin benar-benar MASIH bekerja
    #    untuk urusan berantai — kalau salah satu hilang, penjaga protes.
    mesin = BASE / 'app' / 'berkas_kerja.py'
    if mesin.exists():
        isi_mesin = _baca(mesin)
        tanda_wajib = [
            ("cara == 'berantai'", 'cabang hitung berantai (jap + rantai)'),
            ("ranta = [0.55]", 'setelan korelasi antar-X (ranta)'),
            ("'rantai'", 'kunci keluaran "rantai" untuk halaman hasil'),
        ]
        hilang = [ket for pola, ket in tanda_wajib if pola not in isi_mesin]
        if hilang:
            masalah.append(
                'app/berkas_kerja.py: mesin berantai TIDAK LENGKAP — '
                f'hilang: {"; ".join(hilang)}. ACC Bos 21Sep26 = DIARSIPKAN '
                '(kode tetap UTUH, hanya pintu yang menyembunyikan). '
                'Menghapusnya = melanggar R1')

    # (c) label kartu di pintu harus memakai istilah keputusan (Parsial/Simultan)
    # ⚠️ PELAJARAN 21Sep26 (penjaga sempat BUTA 2 putaran di sini):
    #    (i)  cek `'Parsial' not in isi` LOLOS walau istilahnya dibuang dari
    #         judul kartu — karena kata itu juga muncul di komentar/keterangan.
    #    (ii) setelah diperbaiki jadi "ada 'Parsial' di SALAH SATU judul",
    #         masih LOLOS — sebab kartu ② ("Berganda (Parsial + Simultan)")
    #         juga memuat kata "Parsial".
    #    ATURAN: ukur JUDUL KARTU YANG BENAR-BENAR DIMAKSUD, bukan "ada kata
    #    di mana saja". Kartu ① = data-cara="sederhana"; kartu ② = "berganda".
    judul_per_kartu = {}
    for m in re.finditer(
            r'data-cara="(\w+)"[^>]*>.*?<span class="cara-judul">(.*?)</span>',
            isi, re.S):
        nama, judul = m.group(1), m.group(2)
        judul_per_kartu[nama] = re.sub(r'<[^>]+>', '', judul).strip()

    if 'Parsial' not in judul_per_kartu.get('sederhana', ''):
        masalah.append(
            'buat_data.html: JUDUL KARTU ① (data-cara="sederhana") tidak '
            f'memuat "Parsial" — judulnya: '
            f'{judul_per_kartu.get("sederhana", "TIDAK KETEMU")!r}. '
            'ACC Bos 21Sep26 mewajibkan kartu ① = "Parsial (Sederhana)"')
    if 'Simultan' not in judul_per_kartu.get('berganda', ''):
        masalah.append(
            'buat_data.html: JUDUL KARTU ② (data-cara="berganda") tidak '
            f'memuat "Simultan" — judulnya: '
            f'{judul_per_kartu.get("berganda", "TIDAK KETEMU")!r}. '
            'ACC Bos 21Sep26 mewajibkan kartu ② = "Berganda (Parsial + Simultan)"')

    return masalah


def periksa(d: dict) -> int:
    """Periksa KONSISTENSI dokumen vs KODE. 0 = selaras."""
    masalah = []

    # 0) URUTAN TAHAP — MASTER_PLAN §9 vs TAHAP_PENYELESAIAN (BARU 20Sep26)
    # Sebelum ini TIDAK diperiksa → dua dokumen bisa bertabrakan (Ujian /
    # Pemilih alat / Login / Kualitatif tertukar) dan SOT tetap "SELARAS".
    masalah.extend(_periksa_urutan_tahap())

    # 0b) KARTU REGRESI — pintu vs KEPUTUSAN BOS 21Sep26 (N1+R1+P1)
    masalah.extend(_periksa_kartu_regresi())

    # 1) sisa bug item_per=4
    for p in sorted((BASE / 'app' / 'hitung').glob('*.py')):
        for i, baris in enumerate(_baca(p).splitlines(), 1):
            if 'rl = dict' in baris and re.search(r'item_per\s*=\s*4', baris):
                masalah.append(f'{p.name}:{i} sisa bawaan item_per=4')

    # 2) jumlah grup di dokumen vs kode
    #
    # ⚠️ AKAR (20Sep26) — MENGAPA ADA PENGECUALIAN RIWAYAT, DAN KENAPA
    #    CARA LAMA (jendela jarak) SALAH DUA KALI:
    # Dokumen riwayat tahap WAJAR menyebut jumlah grup pada masa itu
    # ("19Sep26: 23 grup LULUS") — itu CATATAN SEJARAH, bukan klaim kini.
    # Percobaan 1: jendela 160 char → tidak menjangkau penanda blok → protes.
    # Percobaan 2: jendela 700 char + pola 'keadaan 20\d\d' → MALAH LOLOS
    #   dari suntikan '99 grup' karena (a) "keadaan **sekarang**" cocok pola
    #   itu, dan (b) "**Tanggal mulai: 17 September 2026**" di KEPALA dokumen
    #   berada dalam jarak 700 char dari §Gerbang. Jarak = cara yang rapuh.
    #
    # PERBAIKAN DI AKAR: penanda harus MENYATU dengan angkanya dalam SATU
    # kalimat. Jadi kita ambil KALIMAT yang memuat "<n> grup", bukan jendela
    # karakter. Riwayat dikenali bila kalimat itu memuat tanggal/bulan, atau
    # berada tepat sesudah penanda "catatan sejarah".
    POLA_DALAM_KALIMAT = re.compile(
        r'saat itu|kode punya|catatan sejarah|sudah usang|'
        r'CATATAN KEADAAN|jangan dibaca sebagai keadaan kini|'
        # Riwayat PERKEMBANGAN: "menangkap 17→19→23→25 grup" — deretan angka
        # berpemindah. Jelas catatan sejarah, BUKAN klaim keadaan kini
        # (keadaan kini selalu ditulis satu angka, tanpa panah).
        r'\d+\s*→\s*\d+|perkembangan|menangkap \d|\bdulu\b|\bsebelumnya\b|'
        r'\b\d{1,2}\s*(?:Sep|September|Okt|Nov|Des|Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu)',
        re.I)

    def _angka_riwayat(teks: str, pos: int) -> bool:
        """True bila angka grup di `pos` berada di KALIMAT berciri riwayat.

        Kalimat = potongan antara pemisah baris/titik terdekat. Ini tahan
        terhadap jarak: kepala dokumen ("Tanggal mulai: 17 September 2026")
        TIDAK lagi menjangkau §Gerbang karena berbeda kalimat.
        """
        kiri = max(teks.rfind('\n', 0, pos), teks.rfind('. ', 0, pos))
        kanan = len(teks)
        for tanda in ('\n', '. '):
            k = teks.find(tanda, pos)
            if k != -1:
                kanan = min(kanan, k)
        kalimat = teks[kiri + 1:kanan + 1]

        # (a) kalimat angkanya sendiri berciri riwayat?
        if POLA_DALAM_KALIMAT.search(kalimat):
            return True

        # (b) tepat SESUDAH penanda blok riwayat? Penanda biasanya berupa
        #     JUDUL blok ("### ✅ CATATAN KEADAAN 19Sep26 — ...") yang berada
        #     beberapa baris DI ATAS kalimat angkanya. 1200 char ≈ satu blok
        #     riwayat penuh — cukup menjangkau judul, TIDAK sampai blok
        #     berikutnya (blok di dokumen ini ±1500–3000 char).
        awal_blok = teks[max(0, pos - 1200):pos]
        return bool(re.search(r'catatan sejarah|sudah usang|CATATAN KEADAAN|'
                              r'jangan dibaca sebagai keadaan kini', awal_blok, re.I))

    nyata = d['grup_gerbang']
    for nama in ('MASTER_PLAN.md', 'FLAG_LANJUT_DISINI.md'):
        t = _baca(BASE / nama)
        for m in re.finditer(r'(\d+)\s+grup', t):
            if int(m.group(1)) != nyata and not _angka_riwayat(t, m.start()):
                masalah.append(
                    f'{nama}: menyebut {m.group(1)} grup, kode punya {nyata}')

    # 3) klaim usang
    usang = {
        r'30[–-]500': 'rentang responden usang (sekarang 30–2000)',
        r'78 asersi': 'jumlah asersi usang',
        r'49 asersi': 'jumlah asersi usang',
    }
    for nama in ('MASTER_PLAN.md', 'FLAG_LANJUT_DISINI.md'):
        t = _baca(BASE / nama)
        for pola, pesan in usang.items():
            if re.search(pola, t):
                masalah.append(f'{nama}: {pesan}')

    print('\n' + '═' * 74)
    if masalah:
        print('  ❌ SOT TIDAK SELARAS — perbaiki dulu:')
        for m in masalah:
            print(f'     • {m}')
        return 1
    print('  ✅ SOT SELARAS — dokumen cocok dengan kode')
    return 0


def main() -> int:
    d = kumpulkan()
    if '--json' in sys.argv:
        print(json.dumps(d, indent=2, ensure_ascii=False))
        return 0
    cetak(d)
    if '--periksa' in sys.argv:
        return periksa(d)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
