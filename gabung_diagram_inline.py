#!/usr/bin/env python3
"""GABUNGKAN modul diagram ke DALAM mockup (satu berkas).

AKAR MASALAH (terukur 18Sep26): `<script src="diagram_model.js">` TIDAK
termuat ketika halaman dibuka lewat `file://` → "gambarDiagram is not
defined" → diagram KOSONG. Sama seperti jeabakan `/static/gaya.css`.

ATURAN: mockup satu-berkas WAJIB memuat seluruh JS-nya INLINE.
"""
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab/_arsip')
HAL = DIR / 'mockup_konfirmasi_model.html'

ISI = HAL.read_text(encoding='utf-8')
MODEL = (DIR / 'diagram_model.js').read_text(encoding='utf-8')
BENTUK = (DIR / 'diagram_bentuk.js').read_text(encoding='utf-8')

tag = '<script src="diagram_model.js"></script>\n<script src="diagram_bentuk.js"></script>\n'
if tag in ISI:
    ISI = ISI.replace(tag, '')
    print('tag <script src> dibuang')
elif tag.strip() in ISI:
    ISI = ISI.replace(tag.strip(), '')
    print('tag <script src> dibuang (varian)')
else:
    print('CATATAN: tag <script src> tidak ketemu persis — pindai manual')

def bersih(js: str) -> str:
    """Buang baris type-hint Python & docstring blok awal."""
    keluar = []
    for baris in js.splitlines():
        if baris.strip().startswith('from __future__'):
            continue
        keluar.append(baris)
    t = '\n'.join(keluar)
    # buang penanda Python yang tersisa
    t = t.replace('from __future__ import annotations', '')
    return t

INLINE = ('<script>\n/* ══ diagram_model.js (inline — WAJIB: file:// tidak memuat src) ══ */\n'
          + bersih(MODEL) +
          '\n/* ══ diagram_bentuk.js (inline) ══ */\n' + bersih(BENTUK) +
          '\n</script>\n')

if 'diagram_model.js (inline' not in ISI:
    ISI = ISI.replace('<script>\n/* ═══', INLINE + '<script>\n/* ═══', 1)
    if 'diagram_model.js (inline' not in ISI:
        # cadangan: sisipkan sebelum blok script utama
        ISI = ISI.replace('<script>', INLINE + '<script>', 1)

HAL.write_text(ISI, encoding='utf-8')
print('OK: modul digabung INLINE ke dalam HTML')
print('   inline model :', 'diagram_model.js (inline' in ISI)
print('   src tersisa  :', 'src="diagram' in ISI, '(harus False)')
print('   ukuran       :', len(ISI), 'byte')
