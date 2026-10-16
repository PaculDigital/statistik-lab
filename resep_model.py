#!/usr/bin/env python3
"""TEMPLATE MODEL PENELITIAN — format "resep" teks sederhana.

NAMA: `resep_model.py` — pembaca resep + penggambar diagram.

KENAPA FORMAT TEKS: supaya gambar model MUDAH DIUBAH-ubah. Bos (atau siapa
pun) cukup menulis 15 baris seperti ini, tanpa belajar pemrograman:

    judul: Gambar 2.1 Model Penelitian
    variabel:
      X1 = Variasi Produk
      X2 = Brand Image
      M  = Kepuasan
      Y  = Loyalitas Pelanggan
    indikator:
      X1 = Keberagaman Fitur; Keberagaman Ukuran; Keberagaman Desain
    panah:
      X1 -> Y  H1
      M  -> Y  H5

ATURAN PEMBACA:
  · baris kosong & baris berawalan '#' diabaikan (komentar)
  · bagian: `judul:`, `variabel:`, `indikator:`, `panah:`
  · variabel/panah ditulis menjorok (indent) di bawah bagiannya
  · INDIKATOR OPSIONAL — kalau tidak ada, diagram tetap jalan
  · panah: `ASAL -> TUJUAN  LABEL`  (label boleh kosong)
  · jenis panah: label 'NH' otomatis jadi garis putus-putus
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from diagram_svg import (Model, gambar_svg,               # noqa: E402
                         LEBAR_ELIPS, TINGGI_ELIPS, JARAK_KOLOM,
                         JARAK_BARIS, PINGGIR, GARIS, ABU, KERTAS,
                         TINTA)

# ── ukuran kotak indikator (segi empat di samping elips) ─────────────
LEBAR_KOTAK = 132
TINGGI_KOTAK = 30
JARAK_KOTAK = 38       # jarak elips ↔ kotak indikator


# ══════════════════════════════════════════════════════════════════════
# PEMBACA RESEP — dari teks jadi objek Model
# ══════════════════════════════════════════════════════════════════════
class ResepError(Exception):
    """Resep tidak bisa dibaca — pesan HARUS memberi tahu baris mana."""


def baca_resep(teks: str) -> tuple[Model, dict]:
    """Baca resep teks → (Model, info tambahan).

    info tambahan: {'judul': str, 'indikator': {kode: [nama, ...]}}
    """
    judul = ''
    variabel: dict[str, str] = {}
    indikator: dict[str, list[str]] = {}
    panah: list[tuple[str, str, str]] = []

    bagian = None
    for no, baris_asli in enumerate(teks.splitlines(), 1):
        baris = baris_asli.strip()
        if not baris or baris.startswith('#'):
            continue

        awal = baris.lower()
        if awal.startswith('judul:'):
            judul = baris.split(':', 1)[1].strip()
            bagian = None
            continue
        if awal in ('variabel:', 'indikator:', 'panah:'):
            bagian = awal[:-1]
            continue

        if bagian == 'variabel':
            m = re.match(r'^(\S+)\s*=\s*(.+)$', baris)
            if not m:
                raise ResepError(
                    f'baris {no}: "{baris}" — variabel harus '
                    f'`KODE = Nama Variabel`')
            variabel[m.group(1)] = m.group(2).strip()

        elif bagian == 'indikator':
            m = re.match(r'^(\S+)\s*=\s*(.+)$', baris)
            if not m:
                raise ResepError(
                    f'baris {no}: "{baris}" — indikator harus '
                    f'`KODE = nama1; nama2; nama3`')
            kode = m.group(1)
            if kode not in variabel:
                raise ResepError(
                    f'baris {no}: kode "{kode}" belum didefinisikan '
                    f'di bagian `variabel:`')
            isi = [x.strip() for x in m.group(2).split(';') if x.strip()]
            indikator[kode] = isi

        elif bagian == 'panah':
            # Bentuk yang diterima:
            #   `X1 -> Y  H1`     panah hipotesis (mata panah + label)
            #   `X1 - X2`         garis rantai antar X (tanpa label)
            #   `X1 - X2  rantai` (bentuk lama, label 'rantai' tidak digambar)
            m = re.match(r'^(\S+)\s*(->|-)\s*(\S+)\s*(.*)$', baris)
            if not m:
                raise ResepError(
                    f'baris {no}: "{baris}" — panah harus '
                    f'`ASAL -> TUJUAN  LABEL` atau garis `ASAL - TUJUAN`')
            asal, tanda, tujuan, label = (m.group(1), m.group(2),
                                          m.group(3), m.group(4).strip())
            # tanda '-' = GARIS (bukan panah). Dipakai untuk:
            #   · rantai antar X    : `X1 - X2`             (tanpa label)
            #   · X terakhir → Y    : `X3 - Y  H4`          (Bos "1 = B",
            #     "2 = A" — 18Sep26: garisnya sama dengan garis rantai)
            # Kata 'rantai' pada label TIDAK digambar (koreksi Bos).
            if tanda == '-':
                if not label:
                    label = 'rantai'   # penanda internal, tidak digambar
            for k in (asal, tujuan):
                if k not in variabel:
                    raise ResepError(
                        f'baris {no}: kode "{k}" belum didefinisikan '
                        f'di bagian `variabel:`')
            panah.append((asal, tujuan, label, tanda))

        else:
            raise ResepError(
                f'baris {no}: "{baris}" — di luar bagian mana pun. '
                f'Pakai `variabel:`, `indikator:`, `panah:`, atau `judul:`')

    if not variabel:
        raise ResepError('resep tidak punya satu pun variabel')
    if not panah:
        raise ResepError('resep tidak punya satu pun panah')

    m = Model()
    for kode, nama in variabel.items():
        m.tambah_variabel(kode, nama)

    for asal, tujuan, label, tanda in panah:
        # ── jenis panah dari LABEL / TANDA ──
        # · tanda '-'  → GARIS (tanpa mata panah, putus-putus tebal).
        #   Termasuk `X3 - Y  H4` (X terakhir → Y, Bos 18Sep26).
        # · NH  → tidak dihipotesiskan  (garis putus-putus abu)
        # · TL  → efek TIDAK LANGSUNG   (putus-putus tipis)
        # · sisanya → panah hipotesis biasa
        atas = label.upper()
        if tanda == '-':
            # Garis (bukan panah hipotesis). Dua kegunaan (ACC Bos 18Sep26):
            #   · `X1 - X2`        → rantai ANTAR X: tanpa mata panah
            #   · `X3 - Y  H4`     → X TERAKHIR ke Y: ADA mata panah
            jenis = 'rantai_y' if tujuan in ('Y', 'y') else 'rantai'
        elif atas.startswith('NH'):
            jenis = 'nh'
        elif atas.startswith('TL') or '(TL' in atas or 'TIDAK LANGSUNG' in atas:
            jenis = 'tl'
        else:
            jenis = 'h'
        m.tambah_panah(asal, tujuan, label, jenis)

    return m, {'judul': judul, 'indikator': indikator}


# ══════════════════════════════════════════════════════════════════════
# PERAN VARIABEL — diturunkan dari STRUKTUR, bukan diketik manual
# ══════════════════════════════════════════════════════════════════════
def turunkan_peran(m: Model) -> dict[str, str]:
    """Tentukan peran tiap variabel dari bentuk panahnya.

    x = tidak punya induk (eksogen)      m = punya induk & punya anak
    y = punya induk, tidak punya anak    kontrol = tidak terhubung
    """
    punya_induk = {p['ke'] for p in m.panah}
    punya_anak = {p['dari'] for p in m.panah}
    peran: dict[str, str] = {}
    for kode in m.variabel:
        if kode not in punya_induk:
            peran[kode] = 'x' if kode in punya_anak else 'kontrol'
        elif kode in punya_anak:
            peran[kode] = 'm'
        else:
            peran[kode] = 'y'
    return peran


# ══════════════════════════════════════════════════════════════════════
# GAMBAR — elips variabel + kotak indikator (opsional)
# ══════════════════════════════════════════════════════════════════════
def gambar_resep(m: Model, info: dict) -> str:
    """Gambar model + indikator. Kalau tak ada indikator → tetap jalan."""
    indikator = info.get('indikator') or {}
    judul = info.get('judul', '')

    # Kalau TIDAK ADA indikator sama sekali → pakai penggambar lama
    # (lebih sederhana, sudah terbukti). Ini yang bikin indikator
    # benar-benar OPSIONAL.
    if not indikator:
        return gambar_svg(m, judul)

    return _gambar_dengan_indikator(m, judul, indikator)


def _esc(t: str) -> str:
    return (str(t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def _potong_elips(cx, cy, ux, uy, rx, ry):
    """Titik di tepi elips searah (ux, uy) dari pusat."""
    t = 1 / (((ux / rx) ** 2 + (uy / ry) ** 2) ** 0.5)
    return cx + ux * t, cy + uy * t


def _gambar_dengan_indikator(m: Model, judul: str,
                             indikator: dict[str, list[str]]) -> str:
    """Versi lengkap: tiap variabel berindikator dapat kotak di samping.

    TATA LETAK: kotak indikator ditempatkan di sisi LUAR (X di kiri,
    Y/M di kanan) supaya tidak menabrak panah antar-variabel.
    """
    from diagram_svg import hitung_kolom, hitung_baris     # noqa: F401
    kolom, jml_kolom = hitung_kolom(m)
    baris = hitung_baris(m, kolom, jml_kolom)
    peran = turunkan_peran(m)

    rx, ry = LEBAR_ELIPS / 2, TINGGI_ELIPS / 2
    PINGGIR_KIRI = PINGGIR + (LEBAR_KOTAK + JARAK_KOTAK if any(
        indikator.get(k) and peran.get(k) == 'x' for k in m.variabel) else 0)
    PINGGIR_KANAN = PINGGIR + (LEBAR_KOTAK + JARAK_KOTAK if any(
        indikator.get(k) and peran.get(k) in ('y', 'm')
        for k in m.variabel) else 0)

    # 🚨 AKAR cacat terukur 18Sep26: variabel M di tengah yang punya kotak
    #    indikator butuh ruang (rx + JARAK_KOTAK + LEBAR_KOTAK) ke KANAN,
    #    tapi jarak antar kolom hanya JARAK_KOLOM=210 → kotak indikator M
    #    MENABRAK elips Y (terukur: butuh 254 px, tersedia 210 px).
    #    PERBAIKAN: kalau ada variabel ber-indikator yang BUKAN kolom
    #    terakhir, lebarkan jarak kolom SEBESAR KEBUTUHAN (bukan ditebak).
    butuh_kanan = (LEBAR_KOTAK + JARAK_KOTAK) if any(
        indikator.get(k) and peran.get(k) == 'm' for k in m.variabel) else 0
    JARAK_KOLOM_EFEKTIF = max(JARAK_KOLOM, rx + butuh_kanan + rx + 24)

    # posisi pusat elips
    pusat: dict[str, tuple[float, float]] = {}
    for kode in m.variabel:
        x = PINGGIR_KIRI + rx + kolom[kode] * JARAK_KOLOM_EFEKTIF
        pusat[kode] = (x, 0.0)

    nilai_baris = list(baris.values()) or [0]
    y_min, y_max = min(nilai_baris), max(nilai_baris)
    # tinggi: pakai kebutuhan kotak indikator TERBANYAK supaya tidak terpotong
    maks_kotak = max((len(v) for v in indikator.values()), default=0)
    tinggi_kotak_perlu = maks_kotak * TINGGI_KOTAK + (maks_kotak - 1) * 10 \
        if maks_kotak else 0
    tinggi = ((y_max - y_min) * JARAK_BARIS + TINGGI_ELIPS * 2.6
              + 2 * PINGGIR)
    tinggi = max(tinggi, tinggi_kotak_perlu + 120 + 2 * PINGGIR)
    lebar = PINGGIR_KIRI + PINGGIR_KANAN + LEBAR_ELIPS \
        + (jml_kolom - 1) * JARAK_KOLOM_EFEKTIF

    def ke_y(b: float) -> float:
        return PINGGIR + 34 + (b - y_min) * JARAK_BARIS + TINGGI_ELIPS / 2

    for kode in pusat:
        px, _ = pusat[kode]
        pusat[kode] = (px, ke_y(baris[kode]))

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lebar:.0f} '
         f'{tinggi:.0f}" width="{lebar:.0f}" height="{tinggi:.0f}" '
         f'font-family="Helvetica, Arial, sans-serif">']
    s.append(f'<rect width="100%" height="100%" fill="{KERTAS}"/>')
    s.append('<defs>')
    s.append(f'<marker id="ah" markerWidth="10" markerHeight="10" refX="9" '
             f'refY="5" orient="auto" markerUnits="strokeWidth">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{GARIS}"/></marker>')
    s.append(f'<marker id="ahn" markerWidth="10" markerHeight="10" refX="9" '
             f'refY="5" orient="auto" markerUnits="strokeWidth">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{ABU}"/></marker>')
    s.append('</defs>')

    if judul:
        s.append(f'<text x="{lebar/2:.0f}" y="22" font-size="13.5" '
                 f'font-weight="700" fill="{TINTA}" text-anchor="middle">'
                 f'{_esc(judul)}</text>')

    # ── KOTAK INDIKATOR (digambar dulu, di belakang) ──
    kotak_pos: dict[str, list[tuple[float, float]]] = {}
    for kode, daftar in indikator.items():
        if kode not in m.variabel or not daftar:
            continue
        cx, cy = pusat[kode]
        kiri = peran.get(kode) == 'x'      # X → kotak di KIRI
        n = len(daftar)
        tinggi_kolom = n * TINGGI_KOTAK + (n - 1) * 10
        y_awal = cy - tinggi_kolom / 2 + TINGGI_KOTAK / 2
        titik = []
        for i, isi in enumerate(daftar):
            ky = y_awal + i * (TINGGI_KOTAK + 10)
            kx = (cx - rx - JARAK_KOTAK - LEBAR_KOTAK / 2) if kiri else \
                 (cx + rx + JARAK_KOTAK + LEBAR_KOTAK / 2)
            titik.append((kx, ky))
            s.append(f'<rect x="{kx - LEBAR_KOTAK/2:.1f}" '
                     f'y="{ky - TINGGI_KOTAK/2:.1f}" width="{LEBAR_KOTAK}" '
                     f'height="{TINGGI_KOTAK}" rx="4" fill="#FFFFFF" '
                     f'stroke="{GARIS}" stroke-width="1.1"/>')
            font = 9.5 if len(isi) <= 20 else 8.5
            s.append(f'<text x="{kx:.1f}" y="{ky + 3.5:.1f}" '
                     f'font-size="{font}" fill="{TINTA}" '
                     f'text-anchor="middle">{_esc(isi)}</text>')
        kotak_pos[kode] = titik

    # ── PANAH VARIABEL ──
    for p in m.panah:
        x1, y1 = pusat[p['dari']]
        x2, y2 = pusat[p['ke']]
        dx, dy = x2 - x1, y2 - y1
        jarak = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / jarak, dy / jarak
        sx, sy = _potong_elips(x1, y1, ux, uy, rx, ry)
        ex, ey = _potong_elips(x2, y2, -ux, -uy, rx, ry)
        warna = ABU if p['jenis'] == 'nh' else GARIS
        putus = (' stroke-dasharray="2 4"' if p['jenis'] == 'nh' else '')
        ujung = 'ahn' if p['jenis'] == 'nh' else 'ah'
        s.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" '
                 f'y2="{ey:.1f}" stroke="{warna}" stroke-width="1.6"'
                 f'{putus} marker-end="url(#{ujung})"/>')

    # ── GARIS ELIPS ↔ KOTAK INDIKATOR (tanpa label H) ──
    for kode, titik in kotak_pos.items():
        cx, cy = pusat[kode]
        kiri = peran.get(kode) == 'x'
        for (kx, ky) in titik:
            ax = kx + (LEBAR_KOTAK / 2 if kiri else -LEBAR_KOTAK / 2)
            bx = cx + (-rx if kiri else rx)
            s.append(f'<line x1="{ax:.1f}" y1="{ky:.1f}" x2="{bx:.1f}" '
                     f'y2="{ky:.1f}" stroke="{GARIS}" stroke-width="1.0" '
                     f'marker-end="url(#ah)"/>')

    # ── LABEL H di panah variabel (digeser menghindari tumpukan) ──
    dipakai: list[tuple[float, float]] = []
    KANDIDAT_T = (0.5, 0.34, 0.66, 0.24, 0.76)
    GESER = (0.0, -22.0, 22.0)
    for p in m.panah:
        if not p['label']:
            continue
        x1, y1 = pusat[p['dari']]
        x2, y2 = pusat[p['ke']]
        dx, dy = x2 - x1, y2 - y1
        panjang = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / panjang, dy / panjang
        sx, sy = _potong_elips(x1, y1, ux, uy, rx, ry)
        ex, ey = _potong_elips(x2, y2, -ux, -uy, rx, ry)
        nx, ny = -uy, ux
        pilih = None
        for g in GESER:
            for t in KANDIDAT_T:
                mx = sx + (ex - sx) * t + nx * g
                my = sy + (ey - sy) * t + ny * g
                if all((mx - a) ** 2 + (my - b) ** 2 > 26 ** 2
                       for a, b in dipakai):
                    pilih = (mx, my)
                    break
            if pilih:
                break
        if pilih is None:
            pilih = ((sx + ex) / 2, (sy + ey) / 2)
        dipakai.append(pilih)
        mx, my = pilih
        warna = ABU if p['jenis'] == 'nh' else GARIS
        w = len(p['label']) * 6.5 + 10
        s.append(f'<rect x="{mx - w/2:.1f}" y="{my - 15:.1f}" '
                 f'width="{w:.1f}" height="14" rx="3" fill="{KERTAS}"/>')
        s.append(f'<text x="{mx:.1f}" y="{my - 4:.1f}" font-size="10.5" '
                 f'font-weight="700" fill="{warna}" text-anchor="middle">'
                 f'{_esc(p["label"])}</text>')

    # ── ELIPS (digambar terakhir supaya menutupi ujung garis) ──
    for kode in m.variabel:
        cx, cy = pusat[kode]
        nama = m.variabel[kode]['nama']
        s.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.0f}" '
                 f'ry="{ry:.0f}" fill="#FFFFFF" stroke="{GARIS}" '
                 f'stroke-width="1.4"/>')
        font = 11 if len(nama) <= 18 else (9.5 if len(nama) <= 26 else 8.5)
        s.append(f'<text x="{cx:.1f}" y="{cy - 3:.1f}" font-size="{font}" '
                 f'fill="{TINTA}" text-anchor="middle" font-weight="600">'
                 f'{_esc(nama)}</text>')
        s.append(f'<text x="{cx:.1f}" y="{cy + 13:.1f}" font-size="10" '
                 f'fill="{GARIS}" text-anchor="middle">({_esc(kode)})</text>')

    s.append(f'<text x="{PINGGIR}" y="{tinggi - 12:.0f}" font-size="9.5" '
             f'fill="{GARIS}" font-style="italic">Note: NH = Not hypothesized'
             f'</text>')
    s.append('</svg>')
    return '\n'.join(s)


# ══════════════════════════════════════════════════════════════════════
# RESEP CONTOH — 3 contoh Bos
# ══════════════════════════════════════════════════════════════════════
RESEP_CONTOH_3 = """
judul: Gambar 2.1 Model Penelitian

variabel:
  X1 = Variasi Produk
  X2 = Brand Image
  M  = Kepuasan
  Y  = Loyalitas Pelanggan

indikator:
  X1 = Keberagaman Fitur; Keberagaman Ukuran; Keberagaman Desain
  X2 = Brand Strength; Brand Favorability; Brand Uniqueness
  M  = Kesesuaian Harapan; Kepuasan Terhadap Kualitas; Kepuasan Terhadap Pelayanan; Kepuasan Terhadap Harga
  Y  = Pembelian Ulang; Kesediaan Merekomendasikan; Komitmen Jangka Panjang

panah:
  X1 -> Y  H1
  X2 -> Y  H2
  X1 -> M  H3
  X2 -> M  H4
  M  -> Y  H5
"""

# contoh TANPA indikator — bukti indikator benar-benar opsional
RESEP_TANPA_INDIKATOR = """
judul: Model tanpa indikator

variabel:
  X1 = Likuiditas
  X2 = Profitabilitas
  Z  = Kualitas Auditor
  Y  = OAGC

panah:
  X1 -> Z  H1
  X2 -> Z  H2
  X1 -> Y  H3
  X2 -> Y  H4
  Z  -> Y  H5
"""


def main() -> int:
    keluar = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/resep.svg')
    teks = RESEP_CONTOH_3
    if len(sys.argv) > 2 and Path(sys.argv[2]).exists():
        teks = Path(sys.argv[2]).read_text(encoding='utf-8')
    m, info = baca_resep(teks)
    svg = gambar_resep(m, info)
    keluar.write_text(svg, encoding='utf-8')
    print(f'OK   {keluar} ({keluar.stat().st_size} byte)')
    print(f'     variabel={len(m.variabel)} panah={len(m.panah)} '
          f'indikator={sum(len(v) for v in info["indikator"].values())}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
