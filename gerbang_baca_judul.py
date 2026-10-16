#!/usr/bin/env python3
"""GERBANG: deteksi judul di APLIKASI SUNGGUHAN (ACC Bos 18Sep26).

MENGAPA GERBANG INI ADA (pelajaran EduAi: "uji fungsi lolos tapi dokumen
akhir tetap kotor"). Skrip ukur_deteksi_judul.py menguji FUNGSI di dalam
repo — belum tentu hasilnya sama di aplikasi yang benar-benar berjalan
(JSON beda bentuk, endpoint belum terpasang, halaman belum memuat CSS).
Jadi di sini Wulan menembak ENDPOINT SUNGGUHAN di dalam kontainer, dengan
42 judul yang sama, dan membandingkan hasilnya.

YANG DIUKUR (bukan klaim):
  1. /mulai hidup dan kotak judulnya ADA (bukan halaman kosong)
  2. CSS baru benar-benar terkirim (hasil-judul, daftar-riwayat)
  3. Endpoint /api/baca-judul menjawab untuk 42 judul
  4. Hasil endpoint SAMA dengan fungsi lokal → 0 salah tebak
  5. Jatah: judul SAMA tidak dipotong dua kali
  6. Judul kosong ditolak dengan sopan (bukan 500)
  7. Saklar AI mati → tetap menjawab (aplikasi tidak buntu)
  8. Halaman lama tidak rusak

CARA JALAN:  .venv/bin/python gerbang_baca_judul.py
Keluar 0 = aman.
"""
from __future__ import annotations

import json
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


def ip_kontainer() -> str:
    return subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'],
        capture_output=True, text=True).stdout.strip()


def ambil(url: str, timeout: float = 25) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception:                                   # noqa: BLE001
        return 0, ''


def kirim(url: str, muatan: dict, timeout: float = 25) -> tuple[int, dict]:
    try:
        data = json.dumps(muatan).encode()
        req = urllib.request.Request(
            url, data=data, headers={'Content-Type': 'application/json'},
            method='POST')
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode('utf-8', 'replace'))
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:                                   # noqa: BLE001
        return 0, {}


def main() -> int:
    ip = ip_kontainer()
    if not ip:
        print('❌ Container simulasi-olah-data tidak jalan.')
        return 1
    dasar = f'http://{ip}:8000'
    print(f'═══ GERBANG: deteksi judul di aplikasi sungguhan ({dasar}) ═══\n')

    # ── 1. halaman /mulai hidup & kotak judulnya ada ──────────────────────
    print('[1] Halaman /mulai memuat kotak judul')
    k, html = ambil(f'{dasar}/mulai')
    cek('/mulai → HTTP 200', k == 200, f'HTTP {k}')
    if k != 200:
        print('\n  ⛔ Halaman tidak hidup — sisanya tidak bisa diukur.')
        print(f'\nGERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
        return 1
    cek('kotak input judul ada', 'id="judul"' in html)
    cek('tombol "Cek rekomendasi" ada', 'tombol-cek' in html)
    cek('kotak riwayat ada', 'kartu-riwayat' in html)
    cek('penanda jatah ada', 'sisa-jatah' in html)
    cek('dua pintu tetap ada (tidak rusak)', 'pintu-kuant' in html)
    cek('jalur tanpa judul tetap ada', '/kuantitatif' in html)

    # ── 2. CSS baru benar-benar terkirim ──────────────────────────────────
    print('\n[2] CSS baru terkirim ke browser')
    kk, css = ambil(f'{dasar}/static/gaya.css')
    cek('gaya.css → HTTP 200', kk == 200, f'HTTP {kk}')
    for kelas in ['.hasil-judul', '.daftar-riwayat', '.baris-riwayat',
                  '.riwayat-judul', '.kotak-judul', '.isian-judul']:
        cek(f'{kelas} ada di CSS', kelas in css)

    # ⚠️ "5 judul terlihat" harus bisa DIBUKTIKAN dari CSS, bukan diklaim:
    # tinggi baris 62px × 5 + celah 8px × 4 = 342px.
    cek('riwayat dibatasi 5 baris (max-height 342px)',
        'max-height: 342px' in css)
    cek('riwayat bisa di-scroll (overflow-y: auto)',
        'overflow-y: auto' in css)
    cek('judul panjang dipotong 2 baris (line-clamp)', '-webkit-line-clamp: 2' in css)

    # ── 3. berkas skrip judul TIDAK hardcode batas jatah ─────────────────
    # Pelajaran EduAi 15Sep26: batas yang ditulis di dua tempat membuat
    # gerbang tak pernah tersentuh.
    print('\n[3] Angka jatah hanya ada di SATU tempat (server)')
    cek('template tidak menyebut angka 20 sebagai batas jatah',
        'JATAH' not in html and 'jatah: 20' not in html)
    cek('template mengambil jatah dari server', '/api/jatah-judul' in html)

    # ── 4. 42 judul lewat ENDPOINT SUNGGUHAN ─────────────────────────────
    print('\n[4] Uji 42 judul lewat endpoint sungguhan')
    sys.path.insert(0, '.')
    try:
        from ukur_deteksi_judul import UJI
    except Exception as e:                              # noqa: BLE001
        print(f'  ⛔ tidak bisa memuat daftar judul uji: {e}')
        print(f'\nGERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
        return 1

    benar = salah = lewat = 0
    rincian_salah: list[str] = []
    bentuk_beda: list[str] = []
    for judul, wajib in UJI:
        kode, d = kirim(f'{dasar}/api/baca-judul', {'judul': judul})
        if kode != 200 or not d.get('ok'):
            lewat += 1
            bentuk_beda.append(f'{judul[:48]}… → HTTP {kode}')
            continue
        model = d.get('model')
        if model == wajib:
            benar += 1
        elif model == 'ragu':
            benar += 1          # ragu = jalur ke AI, BUKAN salah tebak
        else:
            salah += 1
            rincian_salah.append(
                f'     {judul[:56]}\n       benar={wajib}  endpoint={model}')

    total = len(UJI)
    print(f'  diuji         : {total} judul')
    print(f'  benar/ragu    : {benar}')
    print(f'  SALAH TEBAK   : {salah}')
    print(f'  gagal dijawab : {lewat}')
    cek('semua judul dijawab endpoint', lewat == 0,
        f'{lewat} gagal' if lewat else 'semua terjawab')
    cek('SALAH TEBAK = 0 di aplikasi sungguhan', salah == 0,
        f'{salah} salah' if salah else 'nol')

    # ── 5. jatah: judul SAMA tidak dipotong dua kali ──────────────────────
    print('\n[5] Jatah: judul sama tidak dipotong dua kali')
    judul_uji = 'Pengaruh Harga terhadap Keputusan Pembelian Pengujian Jatah'
    _, d1 = kirim(f'{dasar}/api/baca-judul', {'judul': judul_uji})
    _, d2 = kirim(f'{dasar}/api/baca-judul', {'judul': judul_uji})
    j1 = d1.get('jatah', {}).get('terpakai')
    j2 = d2.get('jatah', {}).get('terpakai')
    cek('permintaan pertama memotong jatah', isinstance(j1, int))
    cek('permintaan kedua TIDAK memotong lagi', j1 == j2,
        f'pertama={j1} kedua={j2}')
    cek('endpoint melaporkan sisa jatah', 'sisa' in d1.get('jatah', {}))
    cek('batas jatah = 20 (sesuai ACC Bos)',
        d1.get('jatah', {}).get('batas') == 20,
        f"batas={d1.get('jatah', {}).get('batas')}")

    # ── 6. input aneh tidak boleh 500 ─────────────────────────────────────
    print('\n[6] Input aneh dijawab sopan (bukan galat server)')
    for nm, isi in [('judul kosong', ''),
                    ('spasi saja', '     '),
                    ('judul 1 kata', 'Harga'),
                    ('judul sangat panjang', 'Pengaruh ' + ' dan '.join(
                        [f'Variabel{i}' for i in range(1, 40)]))]:
        kode, d = kirim(f'{dasar}/api/baca-judul', {'judul': isi})
        cek(f'{nm} → HTTP 200', kode == 200, f'HTTP {kode}')

    # ── 7. saklar AI mati → tetap menjawab ────────────────────────────────
    print('\n[7] Saklar AI MATI → aplikasi tetap jalan (tidak buntu)')
    _, d_off = kirim(f'{dasar}/api/ai', {'aktif': False})
    kode, d_mati = kirim(f'{dasar}/api/baca-judul',
                         {'judul': 'Analisis Determinan Pendapatan Petani'})
    cek('Lapis 1 tetap menjawab saat AI mati', kode == 200 and d_mati.get('ok'),
        f'HTTP {kode}')
    cek('perlu_ai = False saat AI mati (tidak menjanjikan AI)',
        d_mati.get('perlu_ai') is False,
        f"perlu_ai={d_mati.get('perlu_ai')}")
    _, d_on = kirim(f'{dasar}/api/ai', {'aktif': True})
    cek('saklar AI dipulihkan hidup lagi', d_on.get('ai_aktif') is True)

    # ── 8. halaman lama tidak rusak ───────────────────────────────────────
    print('\n[8] Halaman lama TIDAK rusak')
    for p in ['/', '/kuantitatif', '/syarat', '/belajar', '/buat-data',
              '/pengaturan']:
        k, _ = ambil(f'{dasar}{p}')
        cek(f'{p} → HTTP 200', k == 200, f'HTTP {k}')

    # ── 9. /buat-data?model=... tetap hidup ───────────────────────────────
    print('\n[9] Tautan model ke halaman pengisian tetap hidup')
    for m in ['sederhana', 'berganda', 'mediasi', 'moderasi', 'gabungan']:
        k, _ = ambil(f'{dasar}/buat-data?model={m}')
        cek(f'/buat-data?model={m} → HTTP 200', k == 200, f'HTTP {k}')

    if rincian_salah:
        print('\nSALAH TEBAK DI APLIKASI (wajib diperbaiki):')
        for r in rincian_salah:
            print(r)
    if bentuk_beda:
        print('\nTIDAK TERJAWAB:')
        for r in bentuk_beda:
            print(f'     {r}')

    print('\n' + '=' * 66)
    print(f'HASIL GERBANG: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
