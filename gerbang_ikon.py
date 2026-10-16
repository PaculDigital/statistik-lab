#!/usr/bin/env python3
"""GERBANG IKON — pastikan setiap nama ikon yang dipakai template BENAR-BENAR
ada di sprite SVG.

⚠️ MENGAPA ADA (kejadian nyata 19Sep26): Wulan menulis `ikon('arrow-left-right')`
di 2 template, padahal sprite TIDAK punya `ik-arrow-left-right`. `ikon()` di
main.py hanya memvalidasi FORMAT nama (huruf/angka/strip), BUKAN keberadaannya
di sprite. Akibatnya:
    <use href="#ik-arrow-left-right"></use>   → elemen KOSONG
    ...dan TIDAK ADA galat apa pun (HTTP tetap 200, konsol bersih).
Ikonnya cuma tidak muncul. Persis pola `sed` gagal senyap: EXIT 0 tapi salah.

Ini kelas cacat "TAK TERLIHAT TAPI SALAH" — hanya ketemu kalau diperiksa
DENGAN CARA LAIN (di sini: membandingkan daftar nama, bukan membaca hasil).

📌 ATURAN UMUM (lihat skill statistik-lab): sebelum memakai NAMA apa pun
(kelas CSS, variabel CSS, nama ikon, nama fungsi) — BUKTIKAN dulu namanya ADA
di sumbernya. Jangan karang.
"""
import pathlib
import re
import sys

DIR = pathlib.Path(__file__).resolve().parent
SPRITE = DIR / 'app' / 'static' / 'ikon' / 'lucide.svg'
TPL = DIR / 'app' / 'templates'
MAIN = DIR / 'app' / 'main.py'   # daftar MODUL juga menyebut nama ikon


def nama_di_sprite() -> set:
    if not SPRITE.exists():
        return set()
    isi = SPRITE.read_text(encoding='utf-8')
    return set(re.findall(r'id="ik-([a-z0-9-]+)"', isi))


def nama_dipakai() -> list:
    """Kumpulkan (berkas, baris, nama) dari ikon('...') dan ikonKecil('...').

    ⚠️ CACAT YANG DIPERBAIKI 19Sep26 (ketemu dari UJI DIRI gerbang):
    pola pertama Wulan `ikonKecil?\\(...` SALAH TULIS. Itu berarti "ikonKecil"
    dengan huruf terakhir `l` OPSIONAL — jadi ia cocok `ikonKecil`/`ikonKecila`,
    TAPI TIDAK cocok `ikon`. Akibatnya semua `ikon('...')` LOLOS dari pemeriksaan
    → gerbang selalu berbunyi "semua ikon ADA" walau ada ikon palsu.
    Bukti terukur: `ikon('ikon-palsu-xyz', 14)` tidak tertangkap
    (`re.findall` mengembalikan []), padahal jelas ada.
    Pola BENAR: alternatif eksplisit `(ikonKecil|ikon)`.

    ⚠️ CACAT KEDUA YANG DIPERBAIKI 19Sep26 (ketemu saat ganti menu):
    gerbang HANYA memindai `app/templates/*.html`. Padahal nama ikon juga
    ditulis di `app/main.py` pada daftar MODUL (`'ikon': 'play-circle'`).
    Terukur: `play-circle` TIDAK ADA di sprite, tapi gerbang tetap bilang
    "semua ikon ADA — 94 pemakaian aman" ⇒ GERBANG PALSU. Sekarang main.py
    IKUT dipindai dengan pola `'ikon': 'nama'`.
    """
    hasil = []
    for p in sorted(TPL.glob('*.html')):
        for i, baris in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            for m in re.finditer(r"(ikonKecil|ikon)\(\s*'([a-z0-9-]+)'", baris):
                hasil.append((p.name, i, m.group(2)))
    # daftar MODUL di main.py — 'ikon': 'nama'
    if MAIN.exists():
        for i, baris in enumerate(MAIN.read_text(encoding='utf-8').splitlines(), 1):
            for m in re.finditer(r"'ikon'\s*:\s*'([a-z0-9-]+)'", baris):
                hasil.append(('main.py', i, m.group(1)))
    return hasil


def main() -> int:
    ada = nama_di_sprite()
    if not ada:
        print('❌ sprite ikon tidak ditemukan / kosong:', SPRITE)
        return 1

    dipakai = nama_dipakai()
    hilang = [(b, i, n) for b, i, n in dipakai if n not in ada]

    print('═══ GERBANG: nama ikon ada di sprite? ═══')
    print(f'  sprite : {len(ada)} ikon')
    print(f'  dipakai: {len(dipakai)} pemakaian di template')

    if hilang:
        print(f'\n  ❌ {len(hilang)} IKON TIDAK ADA di sprite '
              '(elemen kosong, TANPA galat):')
        for b, i, n in hilang:
            print(f'     {b}:{i}  ik-{n}')
        print('\n  PERBAIKI: pakai nama yang ada, atau tambahkan ikonnya ke '
              'sprite lewat scripts/bangun_sprite_ikon.py.')
        return 1

    print(f'\n  ✅ semua ikon ADA — {len(dipakai)} pemakaian aman')
    return 0


if __name__ == '__main__':
    sys.exit(main())
