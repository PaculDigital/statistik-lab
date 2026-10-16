"""UKUR: apa saja yang SUDAH TAMPIL di /klinik (Tahap 2)?

⚠️ MENGAPA ADA (20Sep26): Wulan hampir mengerjakan ULANG hal yang sudah ada.
Dokumen (`TAHAP_PENYELESAIAN.md`) menandai 2.2 dan 2.4 sebagai ⬜ BELUM,
padahal kode + halaman SUDAH memuatnya. Pelajaran: SEBELUM mengerjakan
apa pun, UKUR dulu apa yang ada — jangan percaya tanda ⬜ di dokumen.

Jalankan: .venv/bin/python _sketsa/ukur_tahap2.py
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML = BASE / 'app' / 'templates' / 'diagnosis.html'
DIAG = BASE / 'app' / 'diagnosis.py'

# (nama fitur, penanda di HTML/kode, kata kunci di dokumen)
FITUR = [
    ('2.2 Linearitas — scatter X×Y',
     r'svgLinear', 'peta'),
    ('2.4 PLS — Outer Loading',
     r'Outer loading', 'peta'),
    ('2.4 PLS — AVE', r"'AVE'", 'peta'),
    ('2.4 PLS — Composite Reliability',
     r'Composite Reliability', 'peta'),
    ('2.4 PLS — VIF antar-variabel', r'vif_inner', 'peta'),
    ('2.4 PLS — Fornell-Larcker', r'fornell', 'peta'),
    ('2.3 VIF (SPSS)', r"'VIF'|VIF", 'peta'),
]


def main() -> int:
    html = HTML.read_text(encoding='utf-8')
    diag = DIAG.read_text(encoding='utf-8')
    gabung = html + '\n' + diag

    print('=' * 74)
    print(' APA SAJA YANG SUDAH TAMPIL — Tahap 2 (diukur dari BERKAS)')
    print('=' * 74)
    print()

    for nama, pola, _ in FITUR:
        ada = bool(re.search(pola, gabung))
        print(f'  {"✅ SUDAH" if ada else "❌ BELUM":10} {nama}')

    print()
    print('  ── catatan_belum (jujur disebut alat sendiri) ──')
    m = re.search(r'catatan_belum\s*=\s*\[(.*?)\]', diag, re.S)
    if m:
        isi = re.findall(r"'([^']+)'", m.group(1))
        for x in isi:
            print(f'     ⬜ {x}')
    else:
        print('     (tidak ditemukan)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
