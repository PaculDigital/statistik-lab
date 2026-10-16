#!/usr/bin/env python3
"""GERBANG: halaman yang DILIHAT USER tidak boleh basi (cache), 18Sep26.

MENGAPA GERBANG INI ADA (akar yang ditutup, bukan tambalan):
Terukur 18Sep26 — sesudah Wulan menambah ~300 baris CSS baru dan deploy
sukses, DOMAIN PUBLIK masih menyajikan CSS LAMA:
    container  : 21 baris ".denah"   ✅ benar
    domain     :  0 baris ".denah"   ❌ basi
Sebabnya `cache-control: max-age=14400` (4 jam) pada berkas statis.
Akibatnya halaman tampak RUSAK bagi user (elips hitam pekat, kartu tanpa
bingkai) padahal berkasnya sudah benar. Wulan sempat hampir "memperbaiki"
HTML-nya — itu akan jadi TAMBALAN, karena HTML-nya memang sudah benar.

YANG DIUKUR (bukan tebakan):
  1. Halaman HTML menyebut gaya.css DENGAN cap versi (?v=...)
  2. Cap versi itu SAMA dengan cap waktu berkas CSS di server
     (kalau beda → cache user akan basi)
  3. CSS dari DOMAIN PUBLIK memuat kelas-kelas BARU
     (kalau tidak → user melihat versi lama walau deploy sudah jalan)
  4. CSS dari container SAMA dengan dari domain (bukti tidak ada basi)

CARA JALAN:  .venv/bin/python gerbang_cache.py
Keluar 0 = aman.
"""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.error
import urllib.request

LULUS = 0
GAGAL = 0

# kelas yang HARUS ada di CSS baru — penanda versi terbaru.
# Tambahkan di sini setiap kali menambah kelas baru yang penting.
PENANDA_BARU = ['.denah', '.kartu-pilih', '.grid-jenis', '.grid-syarat',
                '.pintu-kuant', '.kartu-syarat']

DOMAIN = 'https://statistik.bikinaja.id'


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' → {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' → {bukti}' if bukti else ''))


def ambil(url: str, timeout: float = 20) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:                                   # noqa: BLE001
        return 0, ''


def ip_kontainer() -> str:
    return subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'],
        capture_output=True, text=True).stdout.strip()


def main() -> int:
    print('═══ GERBANG: halaman user tidak boleh basi (cache) ═══\n')

    # ── 1. HTML menyebut CSS dengan cap versi ─────────────────────────
    print('[1] HTML memakai cap versi pada CSS')
    kode, html = ambil(f'{DOMAIN}/kuantitatif')
    cek('halaman terbaca', kode == 200, f'HTTP {kode}')
    if kode != 200:
        print(f'\nGERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
        return 1

    cocok = re.search(r'gaya\.css\?v=(\d+)', html)
    cek('tautan gaya.css punya cap versi', cocok is not None,
        cocok.group(0) if cocok else 'TIDAK ada ?v= — cache akan basi')
    if not cocok:
        print('\n  ⛔ Tanpa cap versi, user bisa melihat CSS lama sampai 4 jam.')
        print(f'\nGERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
        return 1

    # ── 2. cap versi = cap waktu berkas (satu sumber) ─────────────────
    print('\n[2] Cap versi cocok dengan cap waktu berkas CSS')
    import os
    from pathlib import Path
    css_path = Path(__file__).resolve().parent / 'app' / 'static' / 'gaya.css'
    cek('berkas CSS ada', css_path.exists())
    if css_path.exists():
        cap_berkas = str(int(os.stat(css_path).st_mtime))
        cek('cap versi == cap waktu berkas', cocok.group(1) == cap_berkas,
            f'halaman={cocok.group(1)} berkas={cap_berkas}')

    # ── 3. CSS dari DOMAIN memuat kelas BARU ──────────────────────────
    print('\n[3] CSS dari DOMAIN PUBLIK memuat kelas baru (tidak basi)')
    kode_d, css_domain = ambil(f'{DOMAIN}/static/gaya.css?v={cocok.group(1)}')
    cek('CSS domain terbaca', kode_d == 200, f'HTTP {kode_d}')
    for kelas in PENANDA_BARU:
        cek(f'{kelas} ada di CSS domain', kelas in css_domain)

    # ── 4. CSS domain SAMA dengan CSS container ───────────────────────
    print('\n[4] CSS domain == CSS container (bukti tidak ada basi)')
    ip = ip_kontainer()
    if not ip:
        cek('container ketemu', False, 'tidak jalan?')
    else:
        kode_c, css_kont = ambil(f'http://{ip}:8000/static/gaya.css')
        cek('CSS container terbaca', kode_c == 200, f'HTTP {kode_c}')
        cek('jumlah kelas .denah SAMA', css_domain.count('.denah')
            == css_kont.count('.denah'),
            f'domain={css_domain.count(".denah")} '
            f'container={css_kont.count(".denah")}')
        cek('panjang CSS SAMA', abs(len(css_domain) - len(css_kont)) < 40,
            f'domain={len(css_domain)} container={len(css_kont)}')

    print('\n' + '=' * 66)
    print(f'HASIL GERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
