#!/usr/bin/env python3
"""GERBANG: halaman /mulai & /kuantitatif (ACC Bos 18Sep26).

MENGAPA BERKAS INI ADA:
Dua halaman ini BARU. Belum pernah diuji. Gerbang lama (gerbang_uji.sh)
memeriksa halaman LAIN (beranda, belajar, buat-data) — jadi halaman baru
BISA rusak tanpa ketahuan. Ini gerbangnya.

YANG DIUKUR (bukan tebakan, bukan "kelihatannya bagus"):
  1. HTTP 200 untuk /mulai dan /kuantitatif
  2. Enam kartu model ADA semua (hitung dari HTML)
  3. Tiap kartu punya <svg> denah — supaya bahasa gambar benar-benar ada
  4. Nama TEKNIS muncul sebagai teks kecil (regresi/mediasi/moderasi)
  5. PINTU KUALITATIF benar-benar ada & menuju halaman "belum siap"
  6. TIDAK ADA tag HTML mentah yang tumpah jadi teks (pelajaran 18Sep26:
     3 tag </strong> mentah bikin kode tampil sebagai tulisan di layar)
  7. CSS baru (.grid-jenis / .kartu-pilih / .denah) benar-benar terkirim
  8. Pita S1/S2/S3 ada (penanda jenjang) — ACC Bos pakai itu
  9. Halaman LAMA tidak rusak (/, /belajar, /buat-data tetap 200)

CARA JALAN: .venv/bin/python gerbang_mulai.py
Keluar 0 = aman. Keluar 1 = ada yang gagal.
"""
from __future__ import annotations

import subprocess
import sys
import urllib.error
import urllib.request

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' → {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' → {bukti}' if bukti else ''))


def _ip_kontainer() -> str:
    """IP container — JANGAN 127.0.0.1 (itu loopback container, bukan host).

    ⚠️ JEBAKAN TERBUKTI (memory 17Sep26): `curl 127.0.0.1:8120` dari sesi
    Wulan SELALU gagal. Jadi ambil IP container dulu.
    """
    out = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'],
        capture_output=True, text=True).stdout.strip()
    return out


def ambil(url: str, timeout: float = 20) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:                                   # noqa: BLE001
        return 0, ''


def main() -> int:
    ip = _ip_kontainer()
    if not ip:
        print('❌ Container simulasi-olah-data tidak ketemu / tidak jalan.')
        return 1
    dasar = f'http://{ip}:8000'
    print(f'═══ GERBANG: halaman pilih jenis & pilih model ({dasar}) ═══\n')

    # ── 1. halaman baru hidup ──────────────────────────────────────────
    print('[1] Halaman baru hidup')
    kode_m, html_m = ambil(f'{dasar}/mulai')
    kode_k, html_k = ambil(f'{dasar}/kuantitatif')
    cek('/mulai → HTTP 200', kode_m == 200, f'HTTP {kode_m}')
    cek('/kuantitatif → HTTP 200', kode_k == 200, f'HTTP {kode_k}')

    if kode_m != 200 or kode_k != 200:
        print('\n  ⛔ Halaman tidak hidup — sisanya tidak bisa diukur.')
        print(f'\nGERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
        return 1

    # ── 2. dua pintu di /mulai ────────────────────────────────────────
    print('\n[2] Dua pintu di /mulai')
    cek('pintu Kuantitatif ada', 'pintu-kuant' in html_m)
    cek('pintu Kualitatif ada', 'pintu-kual' in html_m)
    cek('kuantitatif → /kuantitatif', 'href="/kuantitatif"' in html_m)
    cek('kualitatif → halaman belum siap',
        '/segera/kualitatif' in html_m)
    cek('ada contoh nyata (orang awam paham)', 'Contoh:' in html_m)

    # ── 3. enam kartu model ───────────────────────────────────────────
    print('\n[3] Kartu model di /kuantitatif')
    jml_kartu = html_k.count('class="kartu-pilih')
    cek('ada 6 kartu (5 siap + 1 terkunci)', jml_kartu == 6, f'{jml_kartu} kartu')

    print('\n[3b] Tiap kartu punya GAMBAR (bahasa universal)')
    jml_svg = html_k.count('<svg viewBox="0 0 150 60"')
    cek('6 kartu → 6 gambar denah', jml_svg == 6, f'{jml_svg} gambar')

    print('\n[3c] Nama teknik muncul sebagai teks kecil')
    for teknis in ['Regresi linear sederhana', 'Regresi linear berganda',
                   'Mediasi', 'Moderasi', 'Gabungan']:
        cek(f'tertulis "{teknis}"', teknis in html_k)

    # ── 4. tautan tiap kartu ke buat-data + model ─────────────────────
    print('\n[4] Tiap kartu membawa ke pengisian dengan MODEL-nya')
    for m in ['sederhana', 'berganda', 'mediasi', 'moderasi', 'gabungan']:
        cek(f'tautan ?model={m}', f'?model={m}' in html_k)

    # ── 5. pita jenjang S1/S2/S3 (ACC Bos) ────────────────────────────
    print('\n[5] Pita jenjang S1/S2/S3')
    for p in ['pita-s1', 'pita-s2', 'pita-s3']:
        cek(f'{p} ada', p in html_k)

    # ── 6. moderasi BEDA dari mediasi (jangan digambar sama) ──────────
    print('\n[6] Moderasi ≠ Mediasi (jangan tertukar)')
    cek('kartu moderasi pakai warna Z (merah)', 'kotak-z' in html_k)
    cek('kartu mediasi pakai warna M (teal)', 'kotak-m' in html_k)

    # ── 7. tag mentah tidak boleh tumpah jadi teks ────────────────────
    print('\n[7] Tidak ada tag HTML mentah di dalam <script>')
    for nm, h in (('/mulai', html_m), ('/kuantitatif', html_k)):
        ada_skrip = '<script' in h
        cek(f'{nm}: tidak ada <script> sama sekali', not ada_skrip,
            'memang tidak ada skrip' if not ada_skrip else 'ADA skrip — periksa')

    # ── 8. CSS baru benar-benar terkirim ──────────────────────────────
    print('\n[8] CSS baru terkirim ke browser')
    kode_c, css = ambil(f'{dasar}/static/gaya.css')
    cek('gaya.css → HTTP 200', kode_c == 200, f'HTTP {kode_c}')
    for kelas in ['.grid-jenis', '.pintu-kuant', '.kartu-pilih', '.denah',
                  '.pita-s1', '.kartu-kunci']:
        cek(f'{kelas} ada di CSS', kelas in css)

    # ── 9. halaman LAMA tidak rusak ───────────────────────────────────
    print('\n[9] Halaman lama TIDAK rusak')
    for p in ['/', '/belajar', '/buat-data', '/pengaturan']:
        k, _ = ambil(f'{dasar}{p}')
        cek(f'{p} → HTTP 200', k == 200, f'HTTP {k}')

    # ── 10. rute model diteruskan ke /buat-data ───────────────────────
    print('\n[10] /buat-data?model=... tetap hidup (belum dipakai, tapi jangan 500)')
    for m in ['sederhana', 'berganda', 'mediasi', 'moderasi', 'gabungan']:
        k, _ = ambil(f'{dasar}/buat-data?model={m}')
        cek(f'/buat-data?model={m} → HTTP 200', k == 200, f'HTTP {k}')

    print('\n' + '=' * 66)
    print(f'HASIL GERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
