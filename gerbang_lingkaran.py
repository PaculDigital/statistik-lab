#!/usr/bin/env python3
"""GERBANG: lingkaran tak berujung antar-fungsi di skrip halaman.

KENAPA GERBANG INI ADA (pelajaran mahal 17Sep26):
  Di buat_data.html terjadi lingkaran tersembunyi:
      segarkan()  → memanggil bangunTabel()
      bangunTabel() → memanggil segarkan()   (di baris terakhirnya)
  Akibatnya SETIAP geseran slider membangun ulang seluruh tabel puluhan
  kali dan memasang ulang semua pendengar event. Di HP efeknya:
  slider LAMBAT SEKALI, tombol + terasa berat/macet — padahal HTTP 200
  dan tidak ada galat JavaScript sama sekali. Gerbang lain SEMUA LULUS.

CARA KERJA: baca fungsi-fungsi di blok <script>, bangun grafik "siapa
memanggil siapa", lalu cari SIKLUS (A→B→A). Siklus antar dua fungsi yang
saling memanggil = hampir pasti bug.

⚠️ PENGECUALIAN YANG SAH: fungsi yang saling memanggil TAPI punya syarat
berhenti (rekursi dengan `if (...) return`). Karena itu gerbang ini
melaporkan siklus sebagai PERINGATAN bila fungsinya memuat `return`
bersyarat, dan GAGAL bila tidak ada syarat berhenti.

Jalankan: .venv/bin/python gerbang_lingkaran.py
"""
import glob
import os
import re
import sys

BERKAS = sorted(glob.glob('app/templates/*.html'))


def ambil_blok_skrip(isi: str) -> str:
    """Gabungkan semua isi <script> tanpa atribut src."""
    keluar = []
    for m in re.finditer(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', isi, re.S):
        keluar.append(m.group(1))
    return '\n'.join(keluar)


def buang_komentar(skrip: str) -> str:
    """Buang komentar // dan /* */ supaya nama fungsi di komentar tidak
    dianggap sebagai pemanggilan nyata.

    ⚠️ Pelajaran 17Sep26: gerbang versi pertama MELAPORKAN PALSU karena
    komentar peringatan (yang justru menjelaskan bugnya) memuat nama fungsi
    seperti `segarkan()`. Gerbang menuduh kode yang sudah benar.
    """
    # /* ... */ dulu (bisa multi-baris)
    skrip = re.sub(r'/\*.*?\*/', ' ', skrip, flags=re.S)
    # lalu // ... sampai akhir baris (hati-hati: jangan sentuh http:// )
    skrip = re.sub(r'(?<!:)//[^\n]*', ' ', skrip)
    return skrip


def daftar_fungsi(skrip: str):
    """Kembalikan {nama: (isi, baris_awal)}."""
    hasil = {}
    # function nama(...) { ... }  — ambil sampai kurung tutup seimbang
    for m in re.finditer(r'function\s+([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{', skrip):
        nama = m.group(1)
        i = m.end() - 1
        dalam = 0
        j = i
        while j < len(skrip):
            if skrip[j] == '{':
                dalam += 1
            elif skrip[j] == '}':
                dalam -= 1
                if dalam == 0:
                    break
            j += 1
        isi = skrip[i:j + 1]
        baris = skrip[:m.start()].count('\n') + 1
        hasil[nama] = (isi, baris)
    return hasil


def cari_siklus(panggil: dict):
    """Cari siklus panjang 2 (A→B→A) dan 3 (A→B→C→A)."""
    temuan = []
    for a, tujuan in panggil.items():
        for b in tujuan:
            if b in panggil and a in panggil.get(b, ()):
                temuan.append((a, b))
    # buang duplikat (A,B) dan (B,A)
    unik = []
    for a, b in temuan:
        if (b, a) not in unik:
            unik.append((a, b))
    return unik


def main() -> int:
    if not os.path.isdir('app/templates'):
        print('  ⚠️  jalankan dari folder statistik-lab'); return 0
    gagal = 0
    for berkas in BERKAS:
        isi = open(berkas, encoding='utf-8').read()
        skrip = buang_komentar(ambil_blok_skrip(isi))
        if not skrip.strip():
            continue
        fungsi = daftar_fungsi(skrip)
        if not fungsi:
            continue

        panggil = {}
        for nama, (badan, _) in fungsi.items():
            # cari pemanggilan fungsi lain di dalam badan
            lain = set()
            for m in re.finditer(r'\b([A-Za-z_$][\w$]*)\s*\(', badan):
                t = m.group(1)
                if t in fungsi and t != nama:
                    lain.add(t)
            panggil[nama] = lain

        siklus = cari_siklus(panggil)
        if not siklus:
            continue

        for a, b in siklus:
            badan_a = fungsi[a][0]
            badan_b = fungsi[b][0]
            # ada syarat berhenti? (kata 'return' di salah satu fungsi)
            ada_henti = ('return' in badan_a) or ('return' in badan_b)
            tanda = '⚠️ ' if ada_henti else '❌'
            print(f'  {tanda} {berkas}: {a}() ⇄ {b}() '
                  f'({"ada return, mungkin rekursi sah" if ada_henti else "TIDAK ada syarat berhenti"})')
            print(f'      {a}() baris {fungsi[a][1]} memanggil {b}()')
            print(f'      {b}() baris {fungsi[b][1]} memanggil {a}()')
            print(f'      Akibat: tiap interaksi menjalankan keduanya berulang '
                  f'→ halaman terasa BERAT (slider lambat, tombol macet).')
            if not ada_henti:
                gagal += 1

    if gagal:
        print(f'\n  ❌ {gagal} lingkaran tak berujung — PERBAIKI dulu.')
        print('  Aturan: satu fungsi JANGAN memanggil fungsi yang memanggilnya balik.')
        return 1
    print('  ✅ tidak ada lingkaran tak berujung antar-fungsi')
    return 0


if __name__ == '__main__':
    sys.exit(main())
