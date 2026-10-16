#!/usr/bin/env python3
"""GERBANG: tag penutup HTML mentah di dalam blok <script>.

AKAR yang dijaga: browser memakai parser "script data" — di dalam <script>,
urutan '</' + nama tag berisiko dibaca sebagai penanda penutup, dan sebagian
mesin/DOM memotong blok skrip di situ → kode tumpah jadi teks di halaman.

⚠️ PELAJARAN PENTING (17Sep26) — gerbang VERSI LAMA SALAH UKUR:
  Gerbang lama hanya mencari pola '</xxx>' mentah. Wulan lalu "memperbaiki"
  dengan  <' + '/div>  — itu LULUS gerbang, TAPI MERUSAK HALAMAN, karena di
  dalam template literal (`...`) tanda  ' + '  bukan penggabungan, melainkan
  TEKS BIASA → kode tumpah ke layar.
  Gerbang ini sekarang memeriksa KEDUA hal:
    (1) tag penutup mentah            </div>       → dilarang
    (2) penggabungan string gaya lama <' + '/div>  → dilarang
  Cara yang BENAR satu-satunya: escape garis miring  <\\/div>
  (JS membaca '<\\/div>' sebagai '</div>', dan browser tidak melihat '</').

Dipanggil gerbang_uji.sh. GAGAL (exit 1) bila ada pelanggaran.
"""
import glob
import re
import sys

POLA_MENTAH = re.compile(r'(?<!\\)</[a-z][a-z0-9]*>')
POLA_GABUNG = re.compile(r"<' \+ '/")


def blok_skrip(s: str):
    pos = 0
    while True:
        a = s.find('<script>', pos)
        if a == -1:
            break
        b = s.find('</script>', a)
        if b == -1:
            break
        yield a, b, s[a + 8:b]
        pos = b + 9


def main() -> int:
    print('═══ GERBANG: tag penutup & penggabungan di dalam <script> ═══')
    pelanggaran = []

    for P in sorted(glob.glob('app/templates/*.html')):
        s = open(P).read()
        for a, b, blok in blok_skrip(s):
            baris_awal = s[:a].count('\n') + 1
            for m in POLA_MENTAH.finditer(blok):
                no = baris_awal + blok[:m.start()].count('\n')
                pelanggaran.append(
                    (P, no, 'TAG MENTAH', m.group(0),
                     blok[max(0, m.start() - 40):m.end() + 6].replace('\n', ' ')))
            for m in POLA_GABUNG.finditer(blok):
                no = baris_awal + blok[:m.start()].count('\n')
                pelanggaran.append(
                    (P, no, 'GABUNG SALAH', "<' + '/…>",
                     blok[max(0, m.start() - 40):m.end() + 14].replace('\n', ' ')))

    if not pelanggaran:
        print('  ✅ 0 pelanggaran — semua template bersih')
        return 0

    print(f'  ❌ {len(pelanggaran)} pelanggaran:')
    for P, no, jenis, tag, konteks in pelanggaran[:20]:
        print(f'     {P}:{no}  [{jenis}] {tag}')
        print(f'        …{konteks}…')
    print()
    print('  CARA BENAR: escape garis miring →  <\\/div>')
    print('  (JANGAN pakai  <\\' + "/div>  — itu rusak di dalam template literal)")
    print()
    print('  Galat ini membuat KODE TUMPAH jadi teks di halaman, walaupun')
    print('  halaman tetap tampak "hidup" dan HTTP 200 tetap hijau.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
