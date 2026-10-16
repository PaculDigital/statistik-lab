#!/usr/bin/env python3
"""GERBANG BAHASA — cegah istilah karangan / tidak jelas di teks yang dibaca user.

KENAPA GERBANG INI ADA (pelajaran 17Sep26):
  Bos membaca halaman dan berkata: "Kata kata geser nilainya - pagar di kanan
  menunjukkan hasil uji. Ini apa maksudnya kata kata tidak jelas".

  Kalimat itu memakai dua istilah KARANGAN yang user tidak paham:
    • "pagar"   → maksudnya kolom prediksi hasil uji
    • "ramalan" → maksudnya prediksi hasil

  ⚠️ Padanan aturan memori: "PAKAI KATA YANG ADA DI KODE, jangan karang."
  Istilah karangan membuat user bingung dan bertanya — itu kerugian nyata.

CARA KERJA: pindai teks yang DILIHAT user (bukan kode internal), lalu
laporkan istilah terlarang beserta gantinya.

Jalankan: .venv/bin/python gerbang_bahasa.py
"""
import glob
import os
import re
import sys

# istilah terlarang → ganti yang benar
LARANGAN = {
    'ramalan': 'prediksi',
    'ramal': 'prediksi',
    'pagar': 'prediksi hasil uji',
    'geser nilainya': 'isi nilainya',
    'melebar': 'meluber',
    # ⚠️ DIKSI (ACC Bos 18Sep26): "Keandalan" & "R²" tanpa keterangan membuat
    # Bos bertanya "ini apa maksudnya". Pakai bahasa sehari-hari.
    'keandalan': 'konsistensi jawaban',
}

# Halaman yang teksnya dibaca user
BERKAS = sorted(glob.glob('app/templates/*.html'))


def ambil_teks_tampil(isi: str) -> str:
    """Ambil HANYA teks yang tampil: buang <script>, <style>, {{ }} kode,
    dan atribut HTML. Yang tersisa = yang dibaca user.

    ⚠️ BUG YANG DITUTUP 22Sep26 (gagal PALSU): komentar Jinja `{# … #}`
       TIDAK dibuang, padahal komentar itu HILANG saat template dirender —
       user tidak pernah melihatnya. Akibatnya kata di dalam komentar
       (mis. "PAGAR JUJUR" di catatan desain) dihitung sebagai teks tampil
       → gerbang menuduh halaman padahal bersih (DIBUKTIKAN: hasil render
       memuat 0 kata itu, sementara berkas mentah memuat 1).
       Uji yang menuntut hal mustahil = uji rusak, bukan halaman rusak.
    """
    # buang blok script & style
    isi = re.sub(r'<script\b.*?</script>', ' ', isi, flags=re.S | re.I)
    isi = re.sub(r'<style\b.*?</style>', ' ', isi, flags=re.S | re.I)
    # buang tag HTML, sisakan teks
    isi = re.sub(r'<[^>]+>', ' ', isi)
    # buang KOMENTAR Jinja dulu (paling luar), baru ekspresi/perintah
    isi = re.sub(r'\{#.*?#\}', ' ', isi, flags=re.S)
    # buang ekspresi Jinja
    isi = re.sub(r'\{\{.*?\}\}', ' ', isi, flags=re.S)
    isi = re.sub(r'\{%.*?%\}', ' ', isi, flags=re.S)
    return isi


def main() -> int:
    if not os.path.isdir('app/templates'):
        print('  ⚠️  jalankan dari folder statistik-lab'); return 0
    gagal = 0
    for berkas in BERKAS:
        isi = open(berkas, encoding='utf-8').read()
        teks = ambil_teks_tampil(isi)
        baris = teks.split('\n')
        for i, b in enumerate(baris, 1):
            rendah = b.lower()
            for kata, ganti in LARANGAN.items():
                if kata in rendah:
                    # tampilkan potongan kalimat sekitar
                    pos = rendah.find(kata)
                    cuplik = b[max(0, pos - 45):pos + 55].strip()
                    print(f'  ❌ {os.path.basename(berkas)}: istilah "{kata}" '
                          f'→ pakai "{ganti}"')
                    print(f'      …{cuplik}…')
                    gagal += 1
    if gagal:
        print(f'\n  ❌ {gagal} istilah tidak jelas — user akan bertanya.')
        print('  Aturan: PAKAI kata yang sudah ada di kode / bahasa sehari-hari.')
        return 1
    print('  ✅ tidak ada istilah karangan yang membingungkan')
    return 0


if __name__ == '__main__':
    sys.exit(main())
