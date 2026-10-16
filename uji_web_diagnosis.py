#!/usr/bin/env python3
"""UJI LIVE /diagnosis — lewat HTTP sungguhan, bukan impor fungsi.

⚠️ ATURAN (pelajaran 19Sep26): "BACA ATRIBUT ≠ UKUR PERILAKU".
   Wulan pernah lapor "sudah jalan" padahal cuma membaca kode. Uji ini
   MENJALANKAN aplikasi sungguhan lalu memanggilnya lewat HTTP.
"""
import io
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from urllib import request as _req
from urllib.error import HTTPError as _HTTPError


class _Jawab:
    """Pembungkus kecil supaya bentuknya mirip `requests` (status_code/json/text)."""
    def __init__(self, status, isi: bytes):
        self.status_code = status
        self._isi = isi
        self.text = isi.decode('utf-8', 'replace')

    def json(self):
        import json as _j
        return _j.loads(self.text)


def _get(url, timeout=10):
    try:
        with _req.urlopen(url, timeout=timeout) as f:
            return _Jawab(f.status, f.read())
    except _HTTPError as e:
        return _Jawab(e.code, e.read())


def _post_json(url, data, timeout=30):
    badan = json.dumps(data).encode()
    r = _req.Request(url, data=badan,
                     headers={'Content-Type': 'application/json'})
    try:
        with _req.urlopen(r, timeout=timeout) as f:
            return _Jawab(f.status, f.read())
    except _HTTPError as e:
        return _Jawab(e.code, e.read())


def _post_file(url, nama, isi, tipe, timeout=25):
    """Unggah multipart tanpa pustaka tambahan."""
    batas = '----WulanBatas9f3a'
    b = (f'--{batas}\r\n'
         f'Content-Disposition: form-data; name="berkas"; filename="{nama}"\r\n'
         f'Content-Type: {tipe}\r\n\r\n').encode() + isi + f'\r\n--{batas}--\r\n'.encode()
    r = _req.Request(url, data=b,
                     headers={'Content-Type': f'multipart/form-data; boundary={batas}'})
    try:
        with _req.urlopen(r, timeout=timeout) as f:
            return _Jawab(f.status, f.read())
    except _HTTPError as e:
        return _Jawab(e.code, e.read())

DIR = Path('/opt/data/services/statistik-lab')
PORT = 8131
BASE = f'http://127.0.0.1:{PORT}'

LULUS = GAGAL = 0


def cek(s, p):
    global LULUS, GAGAL
    if s:
        LULUS += 1
        print(f'  PASS  {p}')
    else:
        GAGAL += 1
        print(f'  FAIL  {p}')


def buat_csv(n=120, rusak=False, benih=11):
    """Data bersih atau data SAKIT (hetero kuat — TERBUKTI terdeteksi)."""
    rng = np.random.default_rng(benih)
    x1 = rng.uniform(0, 6, n)
    x2 = rng.normal(0, 1, n)
    if rusak:
        # corong: skala 1,5 pada X positif → rasio corong ~3× (terukur)
        e = rng.normal(0, 1, n) * (0.3 + 0.5 * x1)
    else:
        e = rng.normal(0, 1, n)
    y = 0.4 * x1 + 0.2 * x2 + e
    if rusak:
        # sempilkan outlier juga + buat X kembar (VIF tinggi)
        x2 = x1 * 0.99 + rng.normal(0, 0.02, n)
        y[0] = 99.0
    df = pd.DataFrame({'Harga': x1, 'Promosi': x2, 'Keputusan': y})
    return df.to_csv(index=False).encode()


def utama() -> int:
    # ── nyalakan aplikasi ──
    env = {'PATH': '/usr/bin:/bin', 'HOME': '/tmp'}
    proc = subprocess.Popen(
        [str(DIR / '.venv/bin/python'), '-m', 'uvicorn', 'app.main:app',
         '--host', '127.0.0.1', '--port', str(PORT), '--log-level', 'warning'],
        cwd=str(DIR), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    siap = False
    for _ in range(50):
        time.sleep(0.4)
        try:
            if _get(f'{BASE}/health', 2).status_code == 200:
                siap = True
                break
        except Exception:
            pass
    if not siap:
        print('GAGAL: aplikasi tidak menyala.'); proc.terminate(); return 1
    print(f'aplikasi menyala di {BASE}\n')

    try:
        # ═══ 1. halaman tampil ═══
        print('=' * 72)
        print(' 1. HALAMAN /diagnosis TAMPIL')
        print('=' * 72)
        r = _get(f'{BASE}/diagnosis', 10)
        cek(r.status_code == 200, f'HTTP {r.status_code}')
        html = r.text
        for tanda in ['Diagnosis Data', 'Unggah berkas', 'Tunjuk kolomnya',
                      'Mau diperiksa pakai cara yang mana', 'gambarHasil',
                      'cara membetulkan']:
            cek(tanda in html, f'ada bagian: "{tanda}"')
        cek(html.count('{{') == 0 and html.count('{%') == 0,
            'tidak ada sisa tag Jinja mentah')

        # ═══ 2. unggah CSV ═══
        print()
        print('=' * 72)
        print(' 2. UNGGAH CSV LEWAT HTTP')
        print('=' * 72)
        isi = buat_csv()
        r = _post_file(f'{BASE}/api/diagnosis/unggah', 'data.csv', isi, 'text/csv')
        cek(r.status_code == 200, f'HTTP {r.status_code}')
        d = r.json()
        cek('kunci' in d and len(d['kunci']) > 10, f"dapat kunci: {d.get('kunci','')[:12]}…")
        cek(d.get('n_baris') == 120, f"n_baris = {d.get('n_baris')} (harus 120)")
        nama_kolom = [k['nama'] for k in d.get('kolom', [])]
        cek(nama_kolom == ['Harga', 'Promosi', 'Keputusan'],
            f'kolom terbaca: {nama_kolom}')
        cek(all(k['jenis'] == 'angka' for k in d['kolom']),
            'semua kolom dikenali sebagai angka')
        kunci = d['kunci']

        # ═══ 3. unggah .xlsx ═══
        print()
        print('=' * 72)
        print(' 3. UNGGAH .xlsx LEWAT HTTP')
        print('=' * 72)
        buf = io.BytesIO()
        pd.read_csv(io.BytesIO(isi)).to_excel(buf, index=False)
        r = _post_file(f'{BASE}/api/diagnosis/unggah', 'data.xlsx',
                       buf.getvalue(), 'application/vnd.openxmlformats')
        cek(r.status_code == 200, f'HTTP {r.status_code}')
        if r.status_code == 200:
            cek(r.json().get('n_baris') == 120, f"n_baris = {r.json().get('n_baris')}")

        # ═══ 4. periksa SPSS pada data BERSIH ═══
        print()
        print('=' * 72)
        print(' 4. PERIKSA SPSS — DATA BERSIH (harus banyak "sudah benar")')
        print('=' * 72)
        r = _post_json(f'{BASE}/api/diagnosis/periksa', {
            'kunci': kunci, 'mode': 'spss',
            'kolom_x': ['Harga', 'Promosi'], 'kolom_y': 'Keputusan',
            'missing': 'buang'})
        cek(r.status_code == 200, f'HTTP {r.status_code}')
        db = r.json()
        cek(db.get('mode') == 'spss', 'mode = spss')
        cek(db.get('n') == 120, f"n = {db.get('n')} (harus 120)")
        cek('normalitas' in db, 'ada hasil normalitas')
        cek('nasihat_semua' in db, 'nasihat dikirim dari server')
        cek(len(db['nasihat_semua']) == 6, f"6 nasihat SPSS (dapat {len(db.get('nasihat_semua', {}))})")
        p_ks = (db.get('normalitas') or {}).get('ks_p')
        cek(p_ks is not None, f'KS p terhitung: {p_ks}')
        print(f"        R²={db.get('r2')}  VIF maks={db.get('vif_maks')}  "
              f"DW={db.get('dw')}  masalah={[m['kode'] for m in db.get('masalah', [])]}")

        # ═══ 5. periksa SPSS pada data SAKIT — harus BEDA jawabannya ═══
        print()
        print('=' * 72)
        print(' 5. PERIKSA SPSS — DATA SAKIT (harus menangkap masalah)')
        print('=' * 72)
        isi_sakit = buat_csv(rusak=True)
        r = _post_file(f'{BASE}/api/diagnosis/unggah', 'sakit.csv', isi_sakit, 'text/csv')
        kunci_sakit = r.json()['kunci']
        r = _post_json(f'{BASE}/api/diagnosis/periksa', {
            'kunci': kunci_sakit, 'mode': 'spss',
            'kolom_x': ['Harga', 'Promosi'], 'kolom_y': 'Keputusan',
            'missing': 'buang'})
        ds = r.json()
        kode_masalah = [m['kode'] for m in ds.get('masalah', [])]
        print(f"        R²={ds.get('r2')}  VIF maks={ds.get('vif_maks')}  "
              f"masalah={kode_masalah}")
        cek('vif' in kode_masalah, f'VIF tinggi TERTANGKAP (VIF maks={ds.get("vif_maks")})')
        cek(len(kode_masalah) > 0, f'data sakit memunculkan masalah: {kode_masalah}')
        cek(all(m['nasihat'] and m['nasihat'].get('langkah') for m in ds['masalah']),
            'tiap masalah punya nasihat + langkah')
        cek(len(db.get('masalah', [])) < len(kode_masalah),
            f'data bersih LEBIH SEDIKIT masalah ({len(db.get("masalah", []))}) '
            f'dari data sakit ({len(kode_masalah)})')

        # ═══ 6. periksa PLS ═══
        print()
        print('=' * 72)
        print(' 6. PERIKSA SmartPLS')
        print('=' * 72)
        r = _post_json(f'{BASE}/api/diagnosis/periksa', {
            'kunci': kunci, 'mode': 'pls',
            'konstruk': {'Harga': ['Harga'], 'Promosi': ['Promosi']},
            'kolom_target': 'Keputusan', 'missing': 'buang'})
        # konstruk butuh >1 butir untuk CR/AVE — beri 3 butir sintetis
        if r.status_code != 200:
            print(f"        (dengan 1 butir → {r.status_code}: {r.json().get('detail','')[:70]})")
            # coba lagi dengan butir lebih banyak
            df = pd.read_csv(io.BytesIO(isi))
            for i in range(3):
                df[f'H{i+1}'] = df['Harga'] + np.random.default_rng(i).normal(0, .4, len(df))
                df[f'P{i+1}'] = df['Promosi'] + np.random.default_rng(i+9).normal(0, .4, len(df))
                df[f'K{i+1}'] = df['Keputusan'] + np.random.default_rng(i+20).normal(0, .4, len(df))
            r2 = _post_file(f'{BASE}/api/diagnosis/unggah', 'pls.csv',
                            df.to_csv(index=False).encode(), 'text/csv')
            kunci2 = r2.json()['kunci']
            r = _post_json(f'{BASE}/api/diagnosis/periksa', {
                'kunci': kunci2, 'mode': 'pls',
                'konstruk': {'Harga': ['H1', 'H2', 'H3'],
                             'Promosi': ['P1', 'P2', 'P3']},
                'kolom_target': 'Keputusan', 'missing': 'buang'})
        cek(r.status_code == 200, f'HTTP {r.status_code}')
        if r.status_code == 200:
            dp = r.json()
            cek(dp.get('mode') == 'pls', 'mode = pls')
            cek(len(dp.get('konstruk', [])) == 2, f"2 konstruk diperiksa")
            # ⚠️ JANGAN PAKU ANGKANYA (pelajaran 20Sep26): uji ini dulu menulis
            # `== 5`, lalu HTMT ditambahkan (20Sep26) → PLS jadi 6 → GAGAL PALSU.
            #
            # Cara tahan-banting: baca KAMUS kode masalah dari sumbernya
            # (regex, bukan impor — uji ini sengaja TIDAK menyentuh modul app,
            # supaya tetap menguji lewat HTTP sungguhan).
            nasihat_pls = dp.get('nasihat_semua', {})
            sumber = (Path(__file__).resolve().parent / 'app'
                      / 'nasihat.py').read_text(encoding='utf-8')
            blok = sumber.split('PLS = {', 1)[-1].split('}', 1)[0]
            kode_pls = re.findall(r"'([a-z_]+)':", blok)
            kurang = [k for k in kode_pls if k not in nasihat_pls]
            cek(not kurang, f'nasihat PLS lengkap ({len(nasihat_pls)} dari '
                            f'{len(kode_pls)}) — kurang: {kurang}')
            for k in dp.get('konstruk', []):
                print(f"        {k['nama']}: loading min={k.get('loading_min')} "
                      f"AVE={k.get('ave')} CR={k.get('cr')}")

        # ═══ 7. PAGAR — pesan RAMAH, bukan traceback ═══
        print()
        print('=' * 72)
        print(' 7. PAGAR — berkas rusak harus ditolak dengan pesan RAMAH')
        print('=' * 72)
        r = _post_file(f'{BASE}/api/diagnosis/unggah', 'rusak.csv',
                       b'\x00\x01\x02bukan data', 'text/csv')
        cek(r.status_code == 400, f'berkas ngawur → HTTP {r.status_code}')
        pesan = r.json().get('detail', '')
        cek(len(pesan) > 15 and 'Traceback' not in pesan,
            f'pesan ramah: "{pesan[:70]}"')
        cek('PERINGATAN' not in pesan.upper() and 'BAHAYA' not in pesan.upper(),
            'pesannya tidak menakutkan')

        # kunci palsu → pesan ramah
        r = _post_json(f'{BASE}/api/diagnosis/periksa', {
            'kunci': 'kunci-yang-tidak-ada', 'mode': 'spss',
            'kolom_x': ['Harga'], 'kolom_y': 'Keputusan'})
        cek(r.status_code == 400, f'kunci palsu → HTTP {r.status_code}')
        cek('unggah ulang' in r.json().get('detail', '').lower(),
            f'pesannya mengarahkan: "{r.json().get("detail","")[:60]}"')

        # kolom yang tidak ada → pesan ramah
        r = _post_json(f'{BASE}/api/diagnosis/periksa', {
            'kunci': kunci, 'mode': 'spss',
            'kolom_x': ['KolomKarangan'], 'kolom_y': 'Keputusan'})
        cek(r.status_code == 400, f'kolom karangan → HTTP {r.status_code}')
        cek('Traceback' not in r.json().get('detail', ''), 'pesannya ramah')

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()

    print()
    print('=' * 72)
    print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 72)
    return 1 if GAGAL else 0


if __name__ == '__main__':
    sys.exit(utama())
