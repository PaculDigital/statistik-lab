"""Uji atribusi "Powered by" di footer — SEMUA halaman wajib menampilkannya.

Aturan (skill statistik-lab):
  • ukur HALAMAN SUNGGUHAN, bukan grep berkas
  • curl 127.0.0.1:8120 dari Wulan SELALU gagal → pakai IP kontainer
  • nilai LULUS/GAGAL dari EXIT CODE
"""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.request

NAMA = 'Jizenji T Wirastomo, SSos, MM, DBA'
HALAMAN = [
    '/', '/kuantitatif', '/belajar', '/buat-data', '/diagnosis',
    '/pengaturan', '/segera/kualitatif', '/mulai',
]


def ip_kontainer() -> str:
    r = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'],
        capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def ambil(ip: str, jalur: str) -> tuple[int, str]:
    url = f'http://{ip}:8000{jalur}'
    try:
        with urllib.request.urlopen(url, timeout=30) as f:
            return f.status, f.read().decode('utf-8', 'replace')
    except Exception as e:  # noqa: BLE001
        return 0, f'GALAT: {e}'


def main() -> int:
    lulus = gagal = 0

    def cek(nama: str, ok: bool, info: str = '') -> None:
        nonlocal lulus, gagal
        if ok:
            lulus += 1
            print(f'LULUS  : {nama}')
        else:
            gagal += 1
            print(f'GAGAL  : {nama}  {info}')

    ip = ip_kontainer()
    cek('IP kontainer terbaca', bool(ip), ip)
    if not ip:
        print('\nHASIL: 0 LULUS / 1 GAGAL')
        return 1

    # 1) setiap halaman menampilkan atribusi TEPAT 1×
    for jalur in HALAMAN:
        kode, html = ambil(ip, jalur)
        if kode != 200:
            cek(f'{jalur} HTTP 200', False, f'dapat {kode}')
            continue
        n = len(re.findall(r'Powered by:', html))
        cek(f'{jalur} — "Powered by" tepat 1×', n == 1, f'dapat {n}')
        cek(f'{jalur} — nama lengkap tampil', NAMA in html)

    # 2) atribusi berada DI DALAM <footer>, bukan nyasar di tempat lain
    kode, html = ambil(ip, '/')
    if kode == 200:
        m = re.search(r'<footer class="kaki">(.*?)</footer>', html, re.S)
        cek('<footer> ketemu di beranda', bool(m))
        if m:
            isi = m.group(1)
            cek('atribusi ada DI DALAM <footer>', 'Powered by:' in isi)
            cek('nama di dalam <footer>', NAMA in isi)
            # 3) atribusi TIDAK ikut terbawa ke header (hindari berebut ruang)
            mh = re.search(r'<header class="puncak">(.*?)</header>', html, re.S)
            cek('atribusi TIDAK ada di <header>',
                bool(mh) and 'Powered by:' not in mh.group(1))

    # 4) kelas CSS-nya benar-benar ada di gaya.css (bukan kelas hantu)
    try:
        with urllib.request.urlopen(f'http://{ip}:8000/static/gaya.css',
                                    timeout=30) as f:
            css = f.read().decode('utf-8', 'replace')
        cek('kelas .kaki-atribusi ada di CSS', '.kaki-atribusi' in css)
        cek('aturan strong .kaki-atribusi ada di CSS',
            '.kaki-atribusi strong' in css)
    except Exception as e:  # noqa: BLE001
        cek('gaya.css terbaca', False, str(e))

    print(f'\nHASIL: {lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
