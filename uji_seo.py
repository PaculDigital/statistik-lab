"""Uji kelengkapan untuk mesin pencari (favicon · sitemap · robots · meta).

Aturan yang dipegang:
  • ukur HALAMAN SUNGGUHAN (kontainer), bukan grep berkas
  • nilai LULUS/GAGAL dari EXIT CODE
  • uji ini WAJIB bisa GAGAL — lihat _sketsa/bukti_uji_seo_gagal.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

HALAMAN = ['/', '/belajar', '/buat-data', '/diagnosis', '/kualitatif',
           '/pengaturan', '/mulai', '/kuantitatif']


def ip() -> str:
    r = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def dasar() -> str:
    """Alamat yang diuji.

    Default: KONTAINER (uji produksi).
    `BASE_UJI` diisi → uji SEBELUM deploy (server uji lokal :8122).
    ⚠️ Tanpa ini uji selalu menembak kontainer LAMA dan hasilnya menyesatkan
    (jebakan K-10: "server lama masih hidup → kesimpulan kacau").
    """
    import os
    return os.environ.get('BASE_UJI', f'http://{ip()}:8000').rstrip('/')


def ambil(url: str) -> tuple[int, bytes, dict]:
    try:
        with urllib.request.urlopen(url, timeout=40) as f:
            return f.status, f.read(), dict(f.headers)
    except Exception as e:  # noqa: BLE001
        return 0, b'', {'galat': str(e)}


def main() -> int:
    base = dasar()
    lulus = gagal = 0

    def cek(nama: str, ok: bool, info: str = '') -> None:
        nonlocal lulus, gagal
        if ok:
            lulus += 1
            print(f'LULUS  : {nama}')
        else:
            gagal += 1
            print(f'GAGAL  : {nama}  {info}')

    # ── 1. FAVICON ──────────────────────────────────────────────────────
    kode, isi, hdr = ambil(f'{base}/favicon.ico')
    cek('/favicon.ico HTTP 200', kode == 200, f'dapat {kode}')
    cek('/favicon.ico isinya SVG', b'<svg' in isi, f'{len(isi)} byte')
    cek('/favicon.ico punya Cache-Control',
        'cache-control' in {k.lower() for k in hdr}, str(hdr)[:80])

    kode2, isi2, _ = ambil(f'{base}/static/favicon.svg')
    cek('/static/favicon.svg HTTP 200', kode2 == 200, f'dapat {kode2}')
    cek('favicon.svg punya viewBox', b'viewBox' in isi2)

    # ── 2. SITEMAP ──────────────────────────────────────────────────────
    kode, isi, hdr = ambil(f'{base}/sitemap.xml')
    cek('/sitemap.xml HTTP 200', kode == 200, f'dapat {kode}')
    teks = isi.decode('utf-8', 'replace')
    cek('/sitemap.xml XML sah', teks.lstrip().startswith('<?xml'))
    try:
        akar = ET.fromstring(teks)
        ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
        loc = [e.text for e in akar.iter(f'{ns}loc')]
    except Exception as e:  # noqa: BLE001
        loc = []
        cek('/sitemap.xml bisa diurai', False, str(e)[:80])
    else:
        cek('/sitemap.xml bisa diurai', True)
    cek('/sitemap.xml memuat beranda',
        any(u.rstrip('/').endswith('8000') or u.endswith('/') for u in loc),
        str(loc[:3]))
    cek('/sitemap.xml memuat halaman siap', len(loc) >= 5, f'{len(loc)} url')
    # Halaman yang BELUM siap TIDAK boleh didaftar (jangan menyesatkan Google)
    for terlarang in ('/pemilih', '/ujian', '/segera'):
        cek(f'/sitemap.xml TIDAK memuat {terlarang}',
            not any(terlarang in u for u in loc))

    # ── 3. ROBOTS ───────────────────────────────────────────────────────
    kode, isi, _ = ambil(f'{base}/robots.txt')
    rt = isi.decode('utf-8', 'replace')
    cek('/robots.txt HTTP 200', kode == 200, f'dapat {kode}')
    cek('/robots.txt menunjuk sitemap', 'Sitemap:' in rt and 'sitemap.xml' in rt,
        rt[:80])
    cek('/robots.txt melarang /api/', 'Disallow: /api/' in rt)

    # ── 4. META DESCRIPTION + OG di TIAP halaman ────────────────────────
    for jalur in HALAMAN:
        kode, isi, _ = ambil(f'{base}{jalur}')
        if kode != 200:
            cek(f'{jalur} HTTP 200', False, f'dapat {kode}')
            continue
        html = isi.decode('utf-8', 'replace')
        m = re.search(r'<meta name="description" content="([^"]*)"', html)
        cek(f'{jalur} — meta description ada', bool(m))
        if m:
            cek(f'{jalur} — description cukup panjang (≥60 char)',
                len(m.group(1)) >= 60, f'{len(m.group(1))} char')
        cek(f'{jalur} — ada og:title',
            'property="og:title"' in html)
        cek(f'{jalur} — ada og:description',
            'property="og:description"' in html)
        cek(f'{jalur} — favicon tertaut',
            'favicon' in html)
        cek(f'{jalur} — theme-color ada', 'theme-color' in html)

    # ── 5. description BERBEDA antar halaman (bukan kalimat sama) ───────
    kumpul = {}
    for jalur in ('/belajar', '/buat-data', '/diagnosis', '/kualitatif'):
        kode, isi, _ = ambil(f'{base}{jalur}')
        if kode == 200:
            html = isi.decode('utf-8', 'replace')
            m = re.search(r'<meta name="description" content="([^"]*)"', html)
            if m:
                kumpul[jalur] = m.group(1)
    cek('deskripsi tiap modul BERBEDA (bukan baku semua)',
        len(set(kumpul.values())) == len(kumpul),
        f'{len(set(kumpul.values()))} unik dari {len(kumpul)}')

    print(f'\nHASIL: {lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
