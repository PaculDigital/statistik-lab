#!/usr/bin/env python3
"""Diagram model penelitian — TATA LETAK OTOMATIS, SVG murni Python.

KENAPA BUKAN GRAPHVIZ: biner `dot` tidak bisa dipasang di mesin ini
(tanpa root; paket Debian Trixie menyimpan `dot` sebagai symlink rusak).
Terukur 18Sep26: 5 cara gagal.

CARA INI: posisi kotak DIHITUNG dari struktur graf (kolom = kedalaman
dari akar). Wulan TIDAK menebak koordinat lagi — itu akar kegagalan lama.

Aturan gambar (sesuai contoh Bos):
  · elips, hitam-putih
  · nama variabel + (kode) di dalam elips
  · panah LURUS, label H di atas panah
  · kolom berurut otomatis (kiri → kanan)
"""
from __future__ import annotations

import sys
from collections import defaultdict, deque
from pathlib import Path

# ── Ukuran & warna (tema terang-warm aplikasi) ───────────────────────
KERTAS = '#FBF8F3'
TINTA = '#2B2722'
GARIS = '#6B6259'
ABU = '#9A9086'

LEBAR_ELIPS = 168      # px di koordinat viewBox
TINGGI_ELIPS = 78      # 🚨 dinaikkan dari 54 (ACC Bos 18Sep26): skala
                       #    LEBAR sudah betul, tapi gambar terasa GEPENG
                       #    karena elips terlalu pendek. 54 → 78 (×1,44).
                       #    JANGAN ubah LEBAR — Bos bilang lebar sudah pas.
JARAK_KOLOM = 210      # JANGAN diubah — skala lebar sudah betul
JARAK_BARIS = 132      # 🚨 dinaikkan dari 84 (ACC Bos 18Sep26): jarak
                       #    antar baris dinaikkan sebanding dengan tinggi
                       #    elips supaya tidak bertumpuk & terasa lega.
                       #    Rasio: 78/54 × 84 ≈ 121; dipakai 132 (×1,57)
                       #    supaya ruang label H di antara baris cukup.
PINGGIR = 46


class Model:
    """Model penelitian: daftar variabel + daftar panah."""

    def __init__(self):
        self.variabel: dict[str, dict] = {}   # kode → {nama, peran}
        self.panah: list[dict] = []           # {dari, ke, label, jenis}

    def tambah_variabel(self, kode: str, nama: str, peran: str = 'x'):
        self.variabel[kode] = {'nama': nama, 'peran': peran}
        return self

    def tambah_panah(self, dari: str, ke: str, label: str = '',
                     jenis: str = 'h'):
        """jenis: 'h' hipotesis (penuh) · 'nh' tidak diuji (putus-putus)
                  · 'mod' moderasi (masuk ke garis)"""
        self.panah.append({'dari': dari, 'ke': ke, 'label': label,
                           'jenis': jenis})
        return self


# ══════════════════════════════════════════════════════════════════════
# HITUNG KOLOM — inti: posisi DITURUNKAN dari struktur, bukan ditebak
# ══════════════════════════════════════════════════════════════════════
def hitung_kolom(m: Model) -> tuple[dict[str, int], int]:
    """Kedalaman tiap variabel = jarak terpanjang dari sumber (akar).

    Cara ini yang membuat model 4 tingkat otomatis tersusun berurut,
    tanpa Wulan menghitung satu koordinat pun.
    """
    masuk: dict[str, list[str]] = defaultdict(list)
    keluar: dict[str, list[str]] = defaultdict(list)
    for p in m.panah:
        # 🚨 Panah yang TIDAK menentukan kolom:
        #    · 'tl'     = efek tidak langsung (hasil hitungan, bukan jalur
        #                 baru). Kalau diikutkan, Y terdorong jauh ke kanan.
        #    · 'rantai'   = garis hubungan ANTAR X (S3 berganda-berantai,
        #                 ACC Bos 18Sep26). Kalau diikutkan, X2 akan
        #                 dipindah ke kolom berikutnya → model rusak,
        #                 padahal semua X harus SEJAJAR di kolom yang sama.
        #    · 'rantai_y' = garis X-TERAKHIR → Y (H4/H6). Sama: X harus
        #                 tetap sejajar, Y tetap di kolomnya.
        if p['jenis'] in ('tl', 'rantai', 'rantai_y'):
            continue
        masuk[p['ke']].append(p['dari'])
        keluar[p['dari']].append(p['ke'])

    akar = [k for k in m.variabel if not masuk[k]]
    if not akar:
        raise ValueError('Model melingkar — tidak ada titik awal')

    kolom = {k: 0 for k in akar}
    antre = deque(akar)
    while antre:
        kini = antre.popleft()
        for anak in keluar[kini]:
            baru = kolom[kini] + 1
            if kolom.get(anak, -1) < baru:
                kolom[anak] = baru
                antre.append(anak)

    for k in m.variabel:
        kolom.setdefault(k, 0)
    return kolom, max(kolom.values()) + 1


def hitung_baris(m: Model, kolom: dict[str, int],
                 jml_kolom: int) -> dict[str, int]:
    """Urutkan variabel dalam satu kolom.

    Pakai urutan KEMUNCULAN pada daftar variabel (stabil) supaya model
    yang sama selalu menghasilkan gambar yang sama.
    """
    kelompok: dict[int, list[str]] = defaultdict(list)
    for kode in m.variabel:
        kelompok[kolom[kode]].append(kode)

    baris: dict[str, int] = {}
    for k in range(jml_kolom):
        anggota = kelompok.get(k, [])
        tengah = (len(anggota) - 1) / 2
        for i, kode in enumerate(anggota):
            baris[kode] = i - tengah       # 0 = tengah, bisa negatif
    return baris


# ══════════════════════════════════════════════════════════════════════
# GAMBAR SVG
# ══════════════════════════════════════════════════════════════════════
def _esc(t: str) -> str:
    return (str(t).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def gambar_svg(m: Model, judul: str = '') -> str:
    kolom, jml_kolom = hitung_kolom(m)
    baris = hitung_baris(m, kolom, jml_kolom)

    # ── posisi pusat tiap elips ──
    pusat: dict[str, tuple[float, float]] = {}
    for kode in m.variabel:
        x = PINGGIR + LEBAR_ELIPS / 2 + kolom[kode] * JARAK_KOLOM
        y = 0
        pusat[kode] = (x, y)

    # cari min/max baris untuk tinggi gambar
    nilai_baris = list(baris.values()) or [0]
    y_min, y_max = min(nilai_baris), max(nilai_baris)
    tinggi_konten = (y_max - y_min) * JARAK_BARIS + TINGGI_ELIPS
    tinggi = tinggi_konten + 2 * PINGGIR
    lebar = PINGGIR * 2 + LEBAR_ELIPS + (jml_kolom - 1) * JARAK_KOLOM

    def ke_y(b: float) -> float:
        return PINGGIR + (b - y_min) * JARAK_BARIS + TINGGI_ELIPS / 2

    for kode in pusat:
        px, _ = pusat[kode]
        pusat[kode] = (px, ke_y(baris[kode]))

    # (blok perhitungan TINGGI dipindah ke bawah — lihat penanda
    #  "TINGGI (dipindah ke sini)". Alasan TERUKUR 18Sep26:
    #  blok itu butuh `geo_awal` (baru terisi setelah panah dihitung)
    #  TAPI juga harus SEBELUM SVG dibuka. Dulu ditaruh di ATAS panah →
    #  NameError; ditaruh di bawah pembukaan SVG → `tinggi` tak terpakai
    #  (viewBox tetap 170 padahal puncak busur 233 → gambar terpotong,
    #   label H4 seolah "hilang").

    # ⚠️ PEMBUKAAN SVG dipindah ke BAWAH (setelah blok TINGGI).
    #    Sebab TERUKUR 18Sep26: viewBox dibangun di sini memakai `tinggi`
    #    yang masih LAMA (170), tetapi `tinggi` baru diupdate (233)
    #    setelah blok tinggi di bawah → gambar terpotong.
    #    Urutan benar: panah dihitung → blok TINGGI → buka SVG.
    # (judul sudah digambar di blok PEMBUKAAN SVG di atas)

    # ── gambar PANAH dulu (supaya elips menutupi ujungnya) ──
    rx = LEBAR_ELIPS / 2
    ry = TINGGI_ELIPS / 2

    # 🚨 AKAR cacat terukur 18Sep26 (temuan Bos): panah digambar LURUS dari
    #    pusat ke pusat. Untuk panah LINTAS seperti X1→Y, garis lurus itu
    #    MELEWATI elips M yang ada di tengah → garis MENEMBUS elips.
    #    TERUKUR: garis H1 & H2 nilai-elips-min = 0,642 (di dalam elips).
    #    Bos: "H1 kurang atas, H2 garis panahnya kurang ke bawah".
    #    PERBAIKAN: panah yang menembus elips lain WAJIB MELENGKUNG
    #    menghindar (busur keluar), bukan lurus.
    def _nilai_elips(px, py, cx, cy, rxx, ryy):
        return ((px - cx) / rxx) ** 2 + ((py - cy) / ryy) ** 2

    def menembus(sx, sy, ex, ey, dari, ke, ambang=1.15):
        """True bila segmen (sx,sy)-(ex,ey) melewati elips SELAIN
        elips asal/tujuan."""
        for kode2, (cx2, cy2) in pusat.items():
            if kode2 in (dari, ke):
                continue
            for j in range(41):
                t = j / 40
                px, py = sx + (ex - sx) * t, sy + (ey - sy) * t
                if _nilai_elips(px, py, cx2, cy2, rx, ry) < ambang:
                    return True
        return False

    def _potong_elips_dari(cx, cy, arah):
        """Titik di tepi elips (cx,cy) searah `arah` (vektor satuan)."""
        t = 1 / (((arah[0] / rx) ** 2 + (arah[1] / ry) ** 2) ** 0.5)
        return cx + arah[0] * t, cy + arah[1] * t

    def _jarak_titik_ke_ruas(px, py, ax, ay, bx, by):
        """Jarak titik (px,py) ke segmen (ax,ay)-(bx,by)."""
        dx, dy = bx - ax, by - ay
        panjang2 = dx * dx + dy * dy
        if panjang2 == 0:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / panjang2))
        return ((px - (ax + dx * t)) ** 2 + (py - (ay + dy * t)) ** 2) ** 0.5

    def _jalur_siku(geo, i, j):
        """Ubah pasangan (asal,tujuan SAMA) jadi: satu diagonal + satu siku.

        🚨 ACC BOS 18Sep26 (contoh gambar img_694de79f46b4.jpg):
          "Garis rantai terakhir mulai dari ujung elips x3 sudut 90
           derajat menuju panah ke elips tengah variabel Y"

        Pasangan yang labelnya H PALING BESAR diberi bentuk SIKU:
          keluar kanan elips X → mendatar ke kanan → belok 90 ke atas
          → masuk bawah elips Y.
        Yang labelnya lebih kecil tetap diagonal biasa (seperti H1/H2).
        Disimpan di geo[i] sebagai busur bertipe teks 'siku:bx,by'.
        """
        def _nomor(gg):
            lab = (gg[0]['label'] or '').upper()
            mm = __import__('re').search(r'H\s*(\d+)', lab)
            return int(mm.group(1)) if mm else -1

        # indeks mana yang jadi siku (H terbesar)
        idx_siku = j if _nomor(geo[j]) > _nomor(geo[i]) else i
        gg = geo[idx_siku]
        pp = gg[0]
        c_asal = pusat[pp['dari']]
        c_ke = pusat[pp['ke']]

        # titik keluar: sisi KANAN elips X, sedikit di bawah pusat
        ax = c_asal[0] + rx
        ay = c_asal[1] + ry * 0.45
        # titik belok: segaris mendatar, tepat di bawah titik masuk
        bx = c_ke[0]
        by = ay
        # titik masuk: sisi BAWAH elips Y
        exx = c_ke[0]
        eyy = c_ke[1] + ry
        geo[idx_siku] = (pp, ax, ay, exx, eyy, f'siku:{bx:.1f},{by:.1f}')

    # 🚨 AKAR cacat terukur 18Sep26: label ditaruh di TITIK TENGAH panah.
    #    Karena M1→M4 dan M2→M4 punya kolom sama, titik tengahnya IDENTIK
    #    → label H4 dan H6 bertumpuk PERSIS (jarak 0,0 px) → yang satu
    #    menutupi yang lain → mata hanya lihat 1 label.
    #    PERBAIKAN: kalau ada beberapa panah yang titik tengahnya berdekatan,
    #    GESER posisi labelnya menyebar (t = 0.30 / 0.50 / 0.70).
    def titik_pada(sx, sy, ex, ey, t):
        return sx + (ex - sx) * t, sy + (ey - sy) * t

    # hitung dulu semua geometri panah
    # 🚨 Setiap panah menyimpan: titik potong tepi + apakah MELENGKUNG.
    #    Panah lurus yang MENEMBUS elips lain diganti BUSUR (melengkung
    #    menghindar) supaya tidak menembus/menempel elips Kepuasan.
    geo_awal = []   # daftar ruas panah (sebelum digeser)
    for p in m.panah:
        x1, y1 = pusat[p['dari']]
        x2, y2 = pusat[p['ke']]
        dx, dy = x2 - x1, y2 - y1
        jarak = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / jarak, dy / jarak

        sx, sy = _potong_elips_dari(x1, y1, (ux, uy))
        ex, ey = _potong_elips_dari(x2, y2, (-ux, -uy))

        # apakah garis lurus ini menembus elips lain?
        busur = 0.0
        if menembus(sx, sy, ex, ey, p['dari'], p['ke']):
            # cari jarak lengkung TERKECIL yang benar-benar keluar elips.
            # Terukur: 34 px cukup untuk elips rx=84 ry=39.
            for cobaan in (34.0, 46.0, 60.0, 76.0, 92.0, 110.0):
                # titik tengah digeser tegak lurus
                mx = (sx + ex) / 2 + (-uy) * cobaan
                my = (sy + ey) / 2 + (ux) * cobaan
                if not menembus(sx, sy, mx, my, p['dari'], p['ke']) and \
                   not menembus(mx, my, ex, ey, p['dari'], p['ke']):
                    busur = cobaan
                    break
                # coba arah sebaliknya
                mx2 = (sx + ex) / 2 + (uy) * cobaan
                my2 = (sy + ey) / 2 + (-ux) * cobaan
                if not menembus(sx, sy, mx2, my2, p['dari'], p['ke']) and \
                   not menembus(mx2, my2, ex, ey, p['dari'], p['ke']):
                    busur = -cobaan
                    break
            if busur == 0.0:
                busur = 34.0      # jaring pengaman: tetap lengkungkan

        # 🚨 EFEK TIDAK LANGSUNG ('tl') WAJIB lebih melengkung dari panah
        #    biasa yang punya asal/tujuan SAMA. Terukur 18Sep26: H6 punya
        #    busur yang PERSIS SAMA dengan H1 (M209.6,97.5 Q350.6,50.8
        #    470.4,138.5) → dua garis BERTUMPUK → tidak bisa dibedakan.
        #    ACC Bos: "H6 dan H7 adalah effek tidak langsung di gambar
        #    garis panah titik titik" → harus terlihat jalur tersendiri.
        if p['jenis'] == 'tl':
            busur = (busur if busur else (34.0 if menembus(sx, sy, ex, ey,
                                                           p['dari'],
                                                           p['ke'])
                                          else 26.0)) + 30.0

        # 🚨 GARIS MENYILANG (X-crossing) terukur 18Sep26 pada model 9
        #    konstruk: M2→M4 & M1→M5 BERHIMPITAN 0,0 px (M1/M2/M3 di kolom
        #    sama, M4 di atas & M5 di bawah → garis naik & turun menyilang).
        #    Ditandai di SINI, diproses di putaran KEDUA (geo belum lengkap).
        geo_awal.append((p, sx, sy, ex, ey, busur))

    # ── PUTARAN KEDUA: lengkungkan panah yang BERPOTONGAN ──
    # 🚨 Diproses setelah SEMUA ruas terkumpul (kalau diproses di dalam
    #    loop pertama, panah pasangannya belum ada di daftar → gagal).
    #
    #    AKAR terukur 18Sep26 (model 9 konstruk): M2→M4 & M1→M5 jarak min
    #    0,0 px. Sebab: M1/M2/M3 sekolom, M4 di atas & M5 di bawah →
    #    garis naik & turun BERPOTONGAN di satu titik.
    #
    #    ⚠️ PERCOBAAN YANG GAGAL (terukur, jangan diulang):
    #       melengkungkan SATU garis saja TIDAK PERNAH berhasil —
    #       busur 18px → 0,8px · 30px → 1,2px · 40px → 1,5px.
    #       Sebab: titik potong hanya BERGESER, tidak hilang.
    #
    #    ✅ YANG BERHASIL (terukur): KEDUA garis melengkung ke arah
    #       BERLAWANAN — busur 45px → jarak 11,2px (cukup, ambang 8px).
    BUSUR_POTONG = 45.0
    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo_awal):
        if busur:
            continue          # sudah melengkung / sudah jadi jalur siku
        for j, (p2, sx2, sy2, ex2, ey2, busur2) in enumerate(geo_awal):
            if i == j or busur2 or i > j:
                continue      # diproses sekali per pasangan (i < j)
            # ══ 🚨 KOREKSI BOS 18Sep26 (SANGAT PENTING) ══
            #   "H3 dan H5 atau H terakhir tidak perlu melengkung lurus
            #    saja seperti H1,H2,... Dst. Dan untuk rantai tidak perlu
            #    garis dari titik H terakhir bisa agak geser sedikit tidak
            #    perlu menempel H terakhir. Dan garis rantai panah ke Y
            #    agak geser yang penting menyentuh elips variabel Y, tidak
            #    perlu berdepetan dengan H terakhir"
            #  → ASAL & TUJUAN SAMA (mis. X3→Y punya H3 panah + H4 garis):
            #    JANGAN dilengkungkan (bikin panah H terakhir melengkung).
            #    Cukup GESER titik ujungnya sedikit di sepanjang tepi elips
            #    supaya tidak menempel. Garis tetap LURUS.
            if p['dari'] == p2['dari'] and p['ke'] == p2['ke']:
                _jalur_siku(geo_awal, i, j)
                continue
            d1 = _jarak_titik_ke_ruas(sx, sy, sx2, sy2, ex2, ey2)
            d2 = _jarak_titik_ke_ruas(ex, ey, sx2, sy2, ex2, ey2)
            d3 = _jarak_titik_ke_ruas(sx2, sy2, sx, sy, ex, ey)
            d4 = _jarak_titik_ke_ruas(ex2, ey2, sx, sy, ex, ey)
            mxa, mya = (sx + ex) / 2, (sy + ey) / 2
            mxb, myb = (sx2 + ex2) / 2, (sy2 + ey2) / 2
            dekat_pusat = ((mxa - mxb) ** 2 + (mya - myb) ** 2) ** 0.5 < 12.0
            if (min(d1, d2, d3, d4) < 3.0) or dekat_pusat:
                # ✅ KEDUA-DUANYA melengkung, arah BERLAWANAN (terukur
                #    busur 45px → jarak 11,2px; satu sisi saja → 1,5px)
                geo_awal[i] = (p, sx, sy, ex, ey, BUSUR_POTONG)
                geo_awal[j] = (p2, sx2, sy2, ex2, ey2, -BUSUR_POTONG)

    # ══ TINGGI (dipindah ke sini) ══
    #    AKAR TERUKUR 18Sep26: mediasi berjenjang -> viewBox 890×170
    #    padahal puncak busur X1→Y di y=233 → label H4 (y=233) DI LUAR
    #    gambar → terlihat "H4 hilang" (temuan vision + Bos).
    #    Sebab: tinggi dulu hanya dihitung dari posisi ELIPS.
    #    ⚠️ URUTAN WAJIB: setelah panah dihitung (butuh `geo_awal`),
    #       tetapi SEBELUM pembukaan SVG (butuh `tinggi` final).
    #    Rumus puncak kurva kuadratik Bézier (t=0,5): cari titik kontrol
    #    dulu, lalu puncak = (sy + 2·cy + ey) / 4.
    _kandidat_y = [0.0, tinggi_konten]
    for (_p2, _sx2, _sy2, _ex2, _ey2, _busur2) in geo_awal:
        _kandidat_y.append(_sy2)
        _kandidat_y.append(_ey2)
        if isinstance(_busur2, str) and _busur2.startswith('siku:'):
            # jalur SIKU ('siku:bx,by') — titik belok bisa lebih bawah
            _bx2, _by2 = (float(v) for v in _busur2[5:].split(','))
            _kandidat_y.append(_by2)
        elif _busur2:
            _dx2, _dy2 = _ex2 - _sx2, _ey2 - _sy2
            _L2 = (_dx2 * _dx2 + _dy2 * _dy2) ** 0.5 or 1
            _nx2, _ny2 = -_dy2 / _L2, _dx2 / _L2
            _cx2 = (_sx2 + _ex2) / 2 + _nx2 * _busur2
            _cy2 = (_sy2 + _ey2) / 2 + _ny2 * _busur2
            _kandidat_y.append(_cy2)
            _kandidat_y.append((_sy2 + 2 * _cy2 + _ey2) / 4)
    _lo, _hi = min(_kandidat_y), max(_kandidat_y)

    geser_y = PINGGIR - _lo if _lo < PINGGIR else 0.0
    butuh_bawah = _hi + PINGGIR
    if butuh_bawah > tinggi:
        tinggi = butuh_bawah
    if geser_y:
        # ⚠️ JANGAN `geo = ...` (nama `geo` jadi lokal → UnboundLocalError
        #    saat membaca `pusat`/`geo_awal` di atas). Pakai nama BARU.
        tinggi += geser_y
        pusat = {k: (x, y + geser_y) for k, (x, y) in pusat.items()}

        def _geser_busur(bb, dy):
            """Geser juga TITIK BELOK jalur siku ('siku:bx,by').

            🚨 AKAR terukur 18Sep26: `busur2` berupa teks 'siku:bx,by'
            TIDAK ikut digeser → ruas mendatar jadi MIRING
            (terukur: M214,412.6 L340,366.6 padahal harusnya L340,412.6).
            """
            if isinstance(bb, str) and bb.startswith('siku:'):
                bx_, by_ = bb[5:].split(',')
                return f'siku:{bx_},{float(by_) + dy:.1f}'
            return bb

        geo_pakai = [(p2, sx2, sy2 + geser_y, ex2, ey2 + geser_y,
                      _geser_busur(busur2, geser_y))
                     for (p2, sx2, sy2, ex2, ey2, busur2) in geo_awal]
    else:
        geo_pakai = geo_awal

    # ══ PEMBUKAAN SVG + defs (dipindah ke sini) ══
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
    # ahtl = mata panah EFEK TIDAK LANGSUNG (ACC Bos 18Sep26)
    s.append(f'<marker id="ahtl" markerWidth="9" markerHeight="9" refX="8" '
             f'refY="4.5" orient="auto" markerUnits="strokeWidth">'
             f'<path d="M0,0 L9,4.5 L0,9 z" fill="{TINTA}"/></marker>')
    s.append('</defs>')
    if judul:
        s.append(f'<text x="{lebar/2:.0f}" y="20" font-size="13" '
                 f'text-anchor="middle" fill="{TINTA}" '
                 f'font-weight="600">{_esc(judul)}</text>')

    # ── tentukan posisi label: hindari titik tengah yang bertabrakan ──
    # 🚨 AKAR SEJATI terukur 18Sep26: label ditaruh di TITIK TENGAH panah.
    #    Untuk panah LINTAS (X2 → Y yang melewati elips M di tengah),
    #    titik tengahnya JATUH DI DALAM elips M → elips digambar TERAKHIR
    #    → MENUTUPI label. Terukur: H2 di (340,176) nilai elips 0,411
    #    (di dalam) → "H2 HILANG". Inilah jawaban pertanyaan Bos
    #    "H5 kemana arahnya?" — persis gejala yang sama.
    #    PERBAIKAN: label WAJIB di LUAR semua elips + tidak bertumpuk.
    #    Terukur: untuk panah LINTAS yang MENEMBUS elips, SEMUA titik di
    #    sepanjang panah ada di dalam elips (contoh: X2→Y lewat persis
    #    pusat elips M di x=340). Maka TIDAK CUKUP geser sepanjang panah —
    #    WAJIB geser TEGAK LURUS sampai keluar elips. Dipakai rantai
    #    geser tegak lurus yang panjang (±110 px) & t di dekat ujung.
    KANDIDAT_T = (0.50, 0.34, 0.66, 0.24, 0.76, 0.16, 0.84, 0.10, 0.90)
    GESER_TEGAK = (0.0, -26.0, 26.0, -40.0, 40.0, -54.0, 54.0,
                   -70.0, 70.0, -86.0, 86.0, -104.0, 104.0,
                   -120.0, 120.0, -140.0, 140.0)
    dipakai: list[tuple[float, float]] = []
    posisi_label: list[tuple[float, float]] = []
    AMBANG = 26.0     # px — di bawah ini dianggap bertumpuk

    def _lebar(teks: str) -> float:
        """Lebar kotak label (sama dengan yang digambar)."""
        return len(teks) * 6.5 + 10

    def bentrok(mx: float, my: float, teks: str,
                lain: list[tuple[float, float, str]]) -> bool:
        """True bila KOTAK label bertumpuk dengan kotak label lain.

        🚨 AKAR terukur 18Sep26: dulu dicek jarak TITIK PUSAT saja.
        Label panjang seperti "H6 (tidak langsung)" (lebar 142 px)
        menutupi label "H1" walau titik pusatnya 42 px jauh (dy=3,1).
        → WAJIB diukur sebagai PERSEGI PANJANG, bukan titik.
        """
        w1 = _lebar(teks)
        for (ox, oy, oteks) in lain:
            w2 = _lebar(oteks)
            if (abs(mx - ox) < (w1 + w2) / 2 + 4
                    and abs(my - oy) < 14 + 4):
                return True
        return False

    def di_dalam_elips(px: float, py: float, cadangan: float = 0.16) -> bool:
        """True bila titik (px,py) jatuh di dalam elips mana pun.

        cadangan = margin supaya label TIDAK menempel garis elips.
        🚨 Dinaikkan 0.06 → 0.16 (18Sep26): pada 0.06 label masih
        MENEMPEL/MENYENTUH garis elips (terukur dari mata Bos & vision) →
        tidak cukup hanya 'tidak di dalam', harus ada JARAK.
        """
        for kode2 in pusat:
            ex, ey = pusat[kode2]
            rx2 = rx * (1 + cadangan)
            ry2 = ry * (1 + cadangan)
            if ((px - ex) / rx2) ** 2 + ((py - ey) / ry2) ** 2 <= 1.0:
                return True
        return False

    def titik_dengan_offset(sx, sy, ex, ey, t, geser):
        mx = sx + (ex - sx) * t
        my = sy + (ey - sy) * t
        if geser:
            # geser tegak lurus arah panah
            dx, dy = ex - sx, ey - sy
            panjang = (dx * dx + dy * dy) ** 0.5 or 1
            nx, ny = -dy / panjang, dx / panjang
            mx += nx * geser
            my += ny * geser
        # 🚨 AKAR terukur 18Sep26: label DIGESER NAIK -8 px untuk memberi
        #    jarak dari garis panah. Pergeseran ini DULU dilakukan SETELAH
        #    pemeriksaan elips → kandidat yang tadinya LUAR (y=191) menjadi
        #    DI DALAM elips (y=182,6) → label tertutup elips ("H2 HILANG").
        #    PERBAIKAN: terapkan pergeseran -8 DI SINI, SEBELUM diperiksa.
        return mx, my - 8.0

    for (p, sx, sy, ex, ey, busur) in geo_pakai:
        if not p['label']:
            posisi_label.append((0.0, 0.0))
            continue
        pilihan = None
        # titik tengah BUSUR (kalau melengkung) — label harus di busurnya
        def titik_busur(t):
            mx = sx + (ex - sx) * t
            my = sy + (ey - sy) * t
            if isinstance(busur, str) and busur.startswith('siku:'):
                # jalur SIKU: label di ruas MENDATAR (dekat titik belok)
                by_ = float(busur[5:].split(',')[1])
                my = sy + (by_ - sy) * (t / 0.5 if t < 0.5 else 1.0)
                return mx, my
            if busur:
                # geser tegak lurus sebesar busur (puncak di t=0.5)
                dx2, dy2 = ex - sx, ey - sy
                panjang2 = (dx2 * dx2 + dy2 * dy2) ** 0.5 or 1
                nx2, ny2 = -dy2 / panjang2, dx2 / panjang2
                faktor = 4 * t * (1 - t)      # puncak di tengah, 0 di ujung
                mx += nx2 * busur * faktor
                my += ny2 * busur * faktor
            return mx, my

        for geser in GESER_TEGAK:
            for t in KANDIDAT_T:
                mx, my = titik_busur(t)
                if geser:
                    dx2, dy2 = ex - sx, ey - sy
                    panjang2 = (dx2 * dx2 + dy2 * dy2) ** 0.5 or 1
                    mx += (-dy2 / panjang2) * geser
                    my += (dx2 / panjang2) * geser
                my -= 8.0
                if di_dalam_elips(mx, my):
                    continue      # 🚨 label tidak boleh di dalam elips
                if not bentrok(mx, my, p['label'], dipakai):
                    pilihan = (mx, my)
                    break
            if pilihan:
                break
        if pilihan is None:
            # semua penuh → pakai titik tengah (jujur: beri tanda di laporan)
            pilihan = titik_busur(0.5)
            pilihan = (pilihan[0], pilihan[1] - 8.0)
        dipakai.append((pilihan[0], pilihan[1], p['label']))
        posisi_label.append(pilihan)

    for i, (p, sx, sy, ex, ey, busur) in enumerate(geo_pakai):
        # ── gaya garis per jenis panah (ACC Bos 18Sep26) ──
        # · h  → hipotesis biasa        : garis penuh tebal
        # · nh → tidak dihipotesiskan   : putus-putus titik, abu
        # · tl → efek TIDAK LANGSUNG    : putus-putus titik, tipis
        #        (Bos: "H6 dan H7 adalah effek tidak langsung di gambar
        #         garis panah titik titik")
        if p['jenis'] == 'nh':
            warna, putus, ujung, tebal = ABU, ' stroke-dasharray="2 4"', 'ahn', '1.6'
        elif p['jenis'] == 'tl':
            warna, putus, ujung, tebal = TINTA, ' stroke-dasharray="2 3"', 'ahtl', '1.1'
        elif p['jenis'] in ('rantai', 'rantai_y'):
            # GARIS (bukan panah hipotesis biasa). ACC Bos 18Sep26:
            #   · "garis rantai ... tidak putus putus dan tidak ada panah
            #      antar x"  → garis PENUH, TANPA mata panah
            #   · "hanya ada panah x terakhir ke Y" → X-terakhir→Y PUNYA
            #      mata panah
            #   · "garisnya kurang tebal" → tebal 2.0 (sejelas panah H)
            ujung = 'ah' if p['jenis'] == 'rantai_y' else ''
            warna, putus, tebal = GARIS, '', '2.0'
        else:
            warna, putus, ujung, tebal = GARIS, '', 'ah', '1.6'
        if isinstance(busur, str) and busur.startswith('siku:'):
            # ✅ JALUR SIKU 90 DERAJAT (ACC Bos 18Sep26 + gambar contoh):
            #    keluar kanan elips X → mendatar → belok 90° ke atas →
            #    masuk bawah elips Y. Dua ruas GARIS LURUS (bukan kurva).
            _bx, _by = busur[5:].split(',')
            s.append(f'<path d="M{sx:.1f},{sy:.1f} L{_bx},{_by} '
                     f'L{ex:.1f},{ey:.1f}" fill="none" stroke="{warna}" '
                     f'stroke-width="{tebal}"{putus} '
                     f'marker-end="url(#{ujung})"/>')
        elif busur:
            # 🚨 BUSUR MENGHINDAR (18Sep26): panah yang menembus elips lain
            #    digambar melengkung (kuadratik) supaya TIDAK menembus.
            dx2, dy2 = ex - sx, ey - sy
            panjang2 = (dx2 * dx2 + dy2 * dy2) ** 0.5 or 1
            nx2, ny2 = -dy2 / panjang2, dx2 / panjang2
            cxt = (sx + ex) / 2 + nx2 * busur * 2
            cyt = (sy + ey) / 2 + ny2 * busur * 2
            s.append(f'<path d="M{sx:.1f},{sy:.1f} Q{cxt:.1f},{cyt:.1f} '
                     f'{ex:.1f},{ey:.1f}" fill="none" stroke="{warna}" '
                     f'stroke-width="{tebal}"{putus} '
                     f'marker-end="url(#{ujung})"/>')
        else:
            s.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" '
                     f'y2="{ey:.1f}" stroke="{warna}" stroke-width="{tebal}"'
                     f'{putus}'
                     f'{(chr(32) + "marker-end=" + chr(34) + "url(#" + ujung + ")" + chr(34)) if ujung else ""}/>')

        # LABEL H — kotak putih di atas panah supaya garis tidak menabrak
        # (pergeseran -8 px sudah diterapkan di titik_dengan_offset)
        # ⚠️ KOREKSI BOS 18Sep26: kata "rantai" TIDAK usah ditampilkan.
        #    TETAPI label H4/H6 pada garis X-terakhir→Y TETAP digambar
        #    (jawaban Bos "1 = B": X3 punya dua hubungan ke Y — panah H3
        #     + garis H4; "2 = A": garisnya sama seperti garis rantai).
        if p['label'] and p['label'].lower() != 'rantai':
            mx, my = posisi_label[i]
            w = len(p['label']) * 6.5 + 10
            s.append(f'<rect x="{mx - w/2:.1f}" y="{my - 10:.1f}" width="{w:.1f}" '
                     f'height="14" rx="3" fill="{KERTAS}"/>')
            s.append(f'<text x="{mx:.1f}" y="{my:.1f}" font-size="10.5" '
                     f'font-weight="700" fill="{warna}" text-anchor="middle">'
                     f'{_esc(p["label"])}</text>')

    # ── gambar ELIPS ──
    for kode in m.variabel:
        cx, cy = pusat[kode]
        info = m.variabel[kode]
        s.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.0f}" '
                 f'ry="{ry:.0f}" fill="#FFFFFF" stroke="{GARIS}" '
                 f'stroke-width="1.4"/>')
        nama = info['nama']
        ada_kode = bool(kode)
        font = 11 if len(nama) <= 18 else (9.5 if len(nama) <= 26 else 8.5)
        if ada_kode and nama:
            s.append(f'<text x="{cx:.1f}" y="{cy - 3:.1f}" font-size="{font}" '
                     f'fill="{TINTA}" text-anchor="middle" font-weight="600">'
                     f'{_esc(nama)}</text>')
            s.append(f'<text x="{cx:.1f}" y="{cy + 13:.1f}" font-size="10" '
                     f'fill="{GARIS}" text-anchor="middle">({_esc(kode)})</text>')
        else:
            s.append(f'<text x="{cx:.1f}" y="{cy + 4:.1f}" font-size="{font}" '
                     f'fill="{TINTA}" text-anchor="middle" font-weight="600">'
                     f'{_esc(nama)}</text>')

    # ── catatan kaki ──
    # ── catatan kaki — HANYA bila ada panah NH (18Sep26: dulu selalu
    #    tampil → bikin bingung karena "NH" tidak ada di gambar) ──
    if any(p['jenis'] == 'nh' for p in m.panah):
        s.append(f'<text x="{PINGGIR}" y="{tinggi - 12:.0f}" font-size="9.5" '
                 f'fill="{GARIS}" font-style="italic">Note: NH = Not '
                 f'hypothesized</text>')
    s.append('</svg>')
    return '\n'.join(s)


# ══════════════════════════════════════════════════════════════════════
# MODEL CONTOH BOS (uji): 9 konstruk · 12 H · 1 NH
# ══════════════════════════════════════════════════════════════════════
def model_contoh_bos() -> Model:
    m = Model()
    m.tambah_variabel('X1', 'Self-efficacy', 'x')
    m.tambah_variabel('M1', 'Mastery Goals', 'm')
    m.tambah_variabel('M2', 'Performance-Approach Goals', 'm')
    m.tambah_variabel('M3', 'Performance-Avoidance Goals', 'm')
    m.tambah_variabel('M4', 'Positive Affect', 'm')
    m.tambah_variabel('M5', 'Decision Confidence', 'm')
    m.tambah_variabel('M6', 'Decision Satisfaction', 'm')
    m.tambah_variabel('Y1', 'Attitudinal Loyalty Intention', 'y')
    m.tambah_variabel('Y2', 'Switching Likelihood', 'y')

    m.tambah_panah('X1', 'M1', 'H1')
    m.tambah_panah('X1', 'M2', 'H2')
    m.tambah_panah('X1', 'M3', 'NH', 'nh')
    m.tambah_panah('M1', 'M4', 'H3')
    m.tambah_panah('M2', 'M4', 'H4')
    m.tambah_panah('M3', 'M4', 'H5')
    m.tambah_panah('M1', 'M5', 'H6')
    m.tambah_panah('M2', 'M5', 'H7')
    m.tambah_panah('M3', 'M5', 'H8')
    m.tambah_panah('M4', 'M6', 'H9')
    m.tambah_panah('M5', 'M6', 'H10')
    m.tambah_panah('M6', 'Y1', 'H11')
    m.tambah_panah('M6', 'Y2', 'H12')
    return m


def main() -> int:
    keluar = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/model_svg.svg')
    svg = gambar_svg(model_contoh_bos(), 'Model contoh (12 hipotesis)')
    keluar.write_text(svg, encoding='utf-8')
    print(f'OK   {keluar} ({keluar.stat().st_size} byte)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
