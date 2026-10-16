#!/usr/bin/env python3
"""ESCAPE TAG PENUTUP di dalam <script> pada belajar.html.

MENGAPA PERLU:
Gerbang `gerbang_tag_skrip.py` melarang tag penutup mentah (</span>, </div>,
dst.) di dalam blok <script>, karena membuat KODE TUMPAH jadi teks di halaman
— halaman tetap HTTP 200 & tampak "hidup", jadi cacat ini tidak kelihatan
kecuali diuji dengan mata.

CARA BENAR: escape garis miringnya → <\\/span>. Di dalam template literal
JavaScript, <\\/span> menghasilkan teks </span> yang benar saat dirender.

CARA SALAH (jangan dipakai): menulis <\\/span> apa adanya dengan backslash
ganda — itu rusak di dalam template literal.

CARA JALAN: .venv/bin/python _sketsa/escape_tag_belajar.py
"""
from __future__ import annotations

import pathlib
import re

AKAR = pathlib.Path(__file__).resolve().parent.parent
# ⚠️ DIPERBAIKI 19Sep26 (Tahap 1): dulu BERKAS ini DIKUNCI ke belajar.html.
# Saat Wulan menambah kode di buat_data.html, alat ini bilang
# "di-escape: 0 tag" — PADAHAL gerbang_tag_skrip.py menemukan 3 tag mentah.
# AKAR: berkasnya tidak ikut diperiksa, jadi keluaran "0" itu MENIPU.
# Sekarang berkas bisa ditunjuk dari argumen:  escape_tag_belajar.py buat_data.html
BERKAS_BAWAAN = AKAR / 'app/templates/belajar.html'

TAG = ['span', 'div', 'b', 'strong', 'h2', 'h3', 'table', 'tr', 'td',
       'th', 'em', 'i', 'p', 'button', 'svg', 'text', 'section',
       # ⚠️ DITAMBAH 19Sep26: 'a' TERLEWAT, padahal tautan juga sering
       # ditulis di dalam template literal → gerbang tetap menemukannya.
       'a', 'ul', 'ol', 'li', 'label', 'input', 'select', 'option',
       'small', 'code', 'pre', 'br', 'tbody', 'thead']


def main() -> None:
    # Berkas bisa ditunjuk dari argumen; bawaannya belajar.html.
    import sys as _sys
    if len(_sys.argv) > 1:
        nama = _sys.argv[1]
        berkas = pathlib.Path(nama) if '/' in nama else AKAR / 'app/templates' / nama
    else:
        berkas = BERKAS_BAWAAN
    if not berkas.exists():
        print(f'  BERKAS TIDAK ADA: {berkas}')
        return

    teks = berkas.read_text(encoding='utf-8')
    penanda = '{% block skrip %}'
    if penanda not in teks:
        print(f'  TIDAK ADA {penanda} di {berkas.name} — tidak diapa-apakan')
        return
    awal = teks.index(penanda)
    kepala, skrip = teks[:awal], teks[awal:]

    # escape tag penutup yang BELUM di-escape (</span> → <\/span>)
    pola = re.compile(r'</(' + '|'.join(TAG) + r')>')
    # hindari yang sudah <\/span>
    def ganti(m):
        return '<\\/' + m.group(1) + '>'
    baru, n = pola.subn(ganti, skrip)
    # kembalikan yang tadinya sudah ter-escape (jangan dobel)
    baru = baru.replace('<\\\\/', '<\\/')

    berkas.write_text(kepala + baru, encoding='utf-8')
    print(f'{berkas.name} → di-escape: {n} tag penutup')


if __name__ == '__main__':
    main()
