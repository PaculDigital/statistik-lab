"""UJI E2E: Fornell-Larcker + HTMT sampai ke HALAMAN /klinik (mode PLS).

⚠️ ATURAN: uji WAJIB lewat jalur sungguhan (unggah → periksa), JANGAN
memanggil fungsi dalam lalu mengaku "sampai ke halaman".
Pelengkap `uji_fornell_htmt.py` (yang menguji rumusnya saja).

Jalankan: .venv/bin/python uji_web_fornell_htmt.py
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
PY = BASE / '.venv' / 'bin' / 'python3'
PORT = 8133

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, info: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}   {info}')


def main() -> int:
    srv = subprocess.Popen(
        [str(PY), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
         '--port', str(PORT)],
        cwd=str(BASE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/health', timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        else:
            print('❌ server tidak siap')
            return 1

        print('=' * 74)
        print(' UJI E2E: Fornell-Larcker + HTMT sampai /klinik')
        print('=' * 74)
        print()

        # ── 1. Bikin CSV: 2 konstruk PLS (butir + kode pendek) ──────────
        rng = np.random.default_rng(7)
        A = rng.normal(0, 1, 120)
        B = rng.normal(0, 1, 120)
        df = pd.DataFrame({
            'KP1': A + rng.normal(0, 0.5, 120),
            'KP2': A + rng.normal(0, 0.5, 120),
            'KP3': A + rng.normal(0, 0.5, 120),
            'H1': B + rng.normal(0, 0.5, 120),
            'H2': B + rng.normal(0, 0.5, 120),
            'H3': B + rng.normal(0, 0.5, 120),
            'Y1': (0.5 * A + 0.5 * B) + rng.normal(0, 0.6, 120),
            'Y2': (0.5 * A + 0.5 * B) + rng.normal(0, 0.6, 120),
            'Y3': (0.5 * A + 0.5 * B) + rng.normal(0, 0.6, 120),
        })
        isi = df.to_csv(index=False).encode()

        # ── 2. Unggah lewat HTTP (jalur sungguhan) ──────────────────────
        batas = '----wulanuji'
        raga = (
            f'--{batas}\r\nContent-Disposition: form-data; name="berkas"; '
            f'filename="uji_pls.csv"\r\nContent-Type: text/csv\r\n\r\n'
        ).encode() + isi + f'\r\n--{batas}--\r\n'.encode()

        req = urllib.request.Request(
            f'http://127.0.0.1:{PORT}/api/diagnosis/unggah', data=raga,
            headers={'Content-Type': f'multipart/form-data; boundary={batas}'})
        jawab = json.loads(urllib.request.urlopen(req, timeout=30).read())
        kunci = jawab.get('kunci')
        cek('unggah berhasil dapat kunci', bool(kunci), str(jawab)[:120])
        if not kunci:
            return 1

        # ── 3. Minta periksa mode PLS (konstruk dari kode pendek) ───────
        # ⚠️ BENTUK YANG BENAR (dibaca dari tanda tangan `periksa_pls`):
        #    konstruk   = DICT {nama: [butir, ...]}   ← BUKAN list of dict
        #    y_konstruk = LIST [butir, ...]           ← BUKAN list konstruk
        # Uji pertama Wulan kirim list of dict → AttributeError 'list' object
        # has no attribute 'items' → HTTP 500. Itu CACAT UJI, bukan app.
        permintaan = json.dumps({
            'kunci': kunci, 'mode': 'pls',
            'konstruk': {
                'Kualitas Produk': ['KP1', 'KP2', 'KP3'],
                'Harga': ['H1', 'H2', 'H3'],
            },
            'kolom_y_konstruk': 'Y1',   # nama aslinya di main.py
        }).encode()
        req2 = urllib.request.Request(
            f'http://127.0.0.1:{PORT}/api/diagnosis/periksa', data=permintaan,
            headers={'Content-Type': 'application/json'})
        hasil = json.loads(urllib.request.urlopen(req2, timeout=90).read())

        print()
        print(' ── isi jawaban server ──')
        f_list = hasil.get('fornell') or []
        h_list = hasil.get('htmt') or []
        print(f'     fornell: {len(f_list)} pasangan')
        for x in f_list:
            print(f'       {x}')
        print(f'     htmt   : {len(h_list)} pasangan')
        for x in h_list:
            print(f'       {x}')

        print()
        cek('server mengirim fornell (bukan kosong lagi)', len(f_list) >= 1,
            str(len(f_list)))
        cek('server mengirim htmt (FITUR BARU)', len(h_list) >= 1,
            str(len(h_list)))
        cek('catatan_belum KOSONG (tidak lagi mengaku belum)',
            hasil.get('catatan_belum') == [], str(hasil.get('catatan_belum')))

        if f_list:
            cek('tiap fornell punya kunci lulus',
                all('lulus' in x for x in f_list))
            cek('pasangan fornell = Kualitas Produk ↔ Harga',
                any('Kualitas Produk' in x['pasangan'] and 'Harga' in x['pasangan']
                    for x in f_list), str(f_list))
        if h_list:
            cek('tiap htmt punya lulus_ketat & lulus_longgar',
                all('lulus_ketat' in x and 'lulus_longgar' in x for x in h_list))
            cek('nilai HTMT masuk akal (0..1,5)',
                all(0 <= (x['nilai'] or 0) <= 1.5 for x in h_list), str(h_list))

        # ── 4. Halaman /klinik memuat kartu HTMT ───────────────────────
        html = urllib.request.urlopen(
            f'http://127.0.0.1:{PORT}/klinik', timeout=15).read().decode()
        cek('halaman /klinik memuat blok kartu HTMT',
            "kartuUji('HTMT'" in html or 'HTMT' in html)
        cek('halaman /klinik memuat nasihat HTMT (Cara membacanya)',
            'Cara membacanya' in html)

        print()
        print('=' * 74)
        print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
        print('=' * 74)
        return 1 if GAGAL else 0
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except Exception:
            srv.kill()


if __name__ == '__main__':
    sys.exit(main())
