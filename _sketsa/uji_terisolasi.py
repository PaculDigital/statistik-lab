#!/usr/bin/env python3
"""UJI TERISOLASI: apa yang bikin baris 141 gagal dibaca?

JANGAN menuduh. Ketika Node bilang baris 141 salah, tersangka yang harus
diperiksa satu-satu DALAM bentuk aslinya:
  A. Apakah 'normalitas: {' + isi entri bisa parse SENDIRI?
  B. Apakah masalahnya di penutup entri SEBELUMNYA (hetero) — kurung tidak
     seimbang sehingga normalitas jatuh di luar objek?
  C. Apakah ada masalah di dalam entri normalitas (template literal,
     komentar /* */, tanda kutip)?

Cara: ambil isi KAMUS saja (dari 'const KAMUS = {' sampai penutupnya),
lalu coba parse bertahap.

Pakai: .venv/bin/python _sketsa/uji_terisolasi.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

BERKAS = Path('/opt/data/tmp_sintaks/skrip_1.js')
TMP = Path('/opt/data/tmp_sintaks')
isi = BERKAS.read_text(encoding='utf-8')
baris = isi.split('\n')


def cek(kode: str, nama: str) -> bool:
    f = TMP / f'urai_{nama}.js'
    f.write_text(kode, encoding='utf-8')
    p = subprocess.run(['node', '--check', str(f)],
                       capture_output=True, text=True)
    if p.returncode == 0:
        print(f'  ✅ {nama}: sintaks OK')
        return True
    m = re.search(r'urai_\w+\.js:(\d+)', p.stderr)
    no = m.group(1) if m else '?'
    pesan = [l for l in p.stderr.splitlines() if 'Error' in l]
    print(f'  ❌ {nama}: baris {no} — {pesan[0] if pesan else p.stderr[:100]}')
    return False


print('══ A. Apakah entri normalitas SENDIRI bisa parse? ══')
# ambil blok normalitas dari berkas asli
mulai = None
for i, b in enumerate(baris):
    if re.match(r'\s{2}normalitas: \{', b):
        mulai = i
        break
print(f'  normalitas mulai di baris {mulai+1 if mulai is not None else "?"}')
if mulai is not None:
    # cari penutup: baris dengan '  },' pada indentasi 2
    akhir = None
    for j in range(mulai + 1, len(baris)):
        if re.match(r'\s{2}\},?\s*$', baris[j]):
            akhir = j
            break
    print(f'  penutup di baris {akhir+1 if akhir is not None else "?"}')
    if akhir:
        potong = '\n'.join(baris[mulai:akhir + 1])
        print(f'  panjang blok: {len(potong)} karakter')
        # bungkus jadi objek supaya bisa diperiksa sendiri
        cek('const uji = {\n' + potong + '\n};\n', 'normalitas_sendiri')

print('\n══ B. Berapa kurung { } dan ( ) di blok normalitas? ══')
if mulai is not None and akhir:
    blok = '\n'.join(baris[mulai:akhir + 1])
    print(f'  {{ = {blok.count("{")}   }} = {blok.count("}")}')
    print(f'  ( = {blok.count("(")}   ) = {blok.count(")")}')
    print(f'  ` (backtick) = {blok.count(chr(96))}   [harus GENAP]')
    print(f'  /* = {blok.count("/*")}   */ = {blok.count("*/")}')
    print(f'  jumlah baris blok: {akhir - mulai + 1}')

print('\n══ C. UJI SELURUH KAMUS — apakah kurung seimbang? ══')
awal = None
for i, b in enumerate(baris):
    if re.match(r'const KAMUS = \{', b):
        awal = i
        break
if awal is not None:
    print(f'  const KAMUS di baris {awal+1}')
    # cari penutup KAMUS: baris '};' pertama setelahnya
    tutup = None
    for j in range(awal + 1, len(baris)):
        if re.match(r'\};', baris[j]):
            tutup = j
            break
    print(f'  penutup KAMUS di baris {tutup+1 if tutup is not None else "?"}')
    if tutup:
        blok = '\n'.join(baris[awal:tutup + 1])
        print(f'  {{ = {blok.count("{")}   }} = {blok.count("}")}  '
              f'[SELISIH {blok.count("{") - blok.count("}")}]')
        print(f'  backtick = {blok.count(chr(96))} [harus GENAP]')
        # ambil daftar nama entri tingkat-1
        nama_entri = re.findall(r'^  ([a-zA-Z_][a-zA-Z0-9_]*): \{', blok, re.M)
        print(f'  entri: {nama_entri}')
        # coba tiap entri satu-satu
        print('\n══ D. Uji tiap entri SENDIRI-SENDIRI ══')
        for nama in nama_entri:
            pola = re.compile(r'^  ' + nama + r': \{', re.M)
            m = pola.search(blok)
            if not m:
                continue
            mulai2 = m.start()
            # hitung kurung untuk cari akhir entri dengan DEPTH
            depth = 0
            i2 = m.end() - 1
            while i2 < len(blok):
                if blok[i2] == '{':
                    depth += 1
                elif blok[i2] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                i2 += 1
            entri = blok[mulai2:i2 + 1]
            cek('const uji = {\n' + entri + '\n};\n', 'entri_' + nama)
    else:
        print('  ⚠️ penutup KAMUS tidak ketemu dengan pola };')
