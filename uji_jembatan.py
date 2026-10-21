"""
Uji JEMBATAN (Fase 1 BAB IV, 21 Okt 2026):
  1. Pintu baru /api/jembatan/hitung tahap utama memberi hasil yang SAMA
     dengan alur lama (unggah → periksa) untuk data yang sama — SPSS & PLS.
  2. Pintu menolak tanpa kunci (401), kunci salah (401), dan menolak
     tertutup (503) kalau kunci server belum dipasang.
  3. Mode pra-survei: butir sampah terdeteksi tidak lolos, butir baik
     lolos, alpha keluar.

Jalankan: .venv/bin/python uji_jembatan.py
"""
import io
import os
import sys

os.environ['JEMBATAN_KUNCI_LAYANAN'] = 'kunci-uji-rahasia'

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

c = TestClient(app, raise_server_exceptions=False)
KUNCI = {'X-Kunci-Layanan': 'kunci-uji-rahasia'}
gagal = []


def cek(nama, kondisi, detail=''):
    print(('  ✓ ' if kondisi else '  ✗ GAGAL ') + nama + (f' — {detail}' if detail and not kondisi else ''))
    if not kondisi:
        gagal.append(nama)


rng = np.random.default_rng(42)


def buat_data(n=80):
    x1 = rng.normal(0, 1, n); x2 = rng.normal(0, 1, n)
    y = 0.6 * x1 + 0.4 * x2 + rng.normal(0, 0.7, n)
    def lik(latent):
        v = np.clip(np.round(3 + latent + rng.normal(0, 0.5, n)), 1, 5).astype(int)
        return v
    d = {}
    for i in range(3):
        d[f'Keaslian_{i+1}'] = lik(x1)
        d[f'Interaksi_{i+1}'] = lik(x2)
        d[f'Impulsif_{i+1}'] = lik(y)
    return pd.DataFrame(d)


df = buat_data()
peran = {}
for col in df.columns:
    aw = col.split('_')[0]
    peran[col] = {'Keaslian': 'X1', 'Interaksi': 'X2', 'Impulsif': 'Y1'}[aw]

print('── 1. SPSS: alur lama vs jembatan ──')
buf = io.StringIO(); df.to_csv(buf, index=False)
r_up = c.post('/api/diagnosis/unggah',
              files={'berkas': ('data.csv', buf.getvalue(), 'text/csv')})
cek('unggah lama 200', r_up.status_code == 200, r_up.text[:200])
kunci = r_up.json()['kunci']
r_lama = c.post('/api/diagnosis/periksa',
                json={'kunci': kunci, 'mode': 'spss', 'peran': peran})
cek('periksa lama 200', r_lama.status_code == 200, r_lama.text[:200])
baris = df.to_dict(orient='records')
r_baru = c.post('/api/jembatan/hitung', headers=KUNCI,
                json={'mode': 'spss', 'tahap': 'utama',
                      'baris': baris, 'peran': peran})
cek('jembatan 200', r_baru.status_code == 200, r_baru.text[:200])
a, b = r_lama.json(), r_baru.json()
for k in ('r2', 'r2_adj', 'vif_maks', 'dw'):
    cek(f'sama: {k}', a.get(k) == b.get(k), f'{a.get(k)} vs {b.get(k)}')
ka = {x['nama']: (x['b'], x['p']) for x in a.get('koef', [])}
kb = {x['nama']: (x['b'], x['p']) for x in b.get('koef', [])}
cek('sama: koefisien b & p semua jalur', ka == kb and len(ka) > 0, f'{ka} vs {kb}')
cek('sama: daftar masalah', a.get('masalah') == b.get('masalah'))

print('── 2. PLS: alur lama vs jembatan ──')
konstruk = {'Keaslian': ['Keaslian_1', 'Keaslian_2', 'Keaslian_3'],
            'Interaksi': ['Interaksi_1', 'Interaksi_2', 'Interaksi_3'],
            'Impulsif': ['Impulsif_1', 'Impulsif_2', 'Impulsif_3']}
r_up2 = c.post('/api/diagnosis/unggah',
               files={'berkas': ('data.csv', buf.getvalue(), 'text/csv')})
r_lama2 = c.post('/api/diagnosis/periksa',
                 json={'kunci': r_up2.json()['kunci'], 'mode': 'pls',
                       'konstruk': konstruk, 'kolom_y_konstruk': 'Impulsif'})
r_baru2 = c.post('/api/jembatan/hitung', headers=KUNCI,
                 json={'mode': 'pls', 'tahap': 'utama', 'baris': baris,
                       'konstruk': konstruk, 'kolom_y_konstruk': 'Impulsif'})
cek('pls lama & baru 200', r_lama2.status_code == 200 and r_baru2.status_code == 200,
    f"{r_lama2.status_code}/{r_baru2.status_code}")
a2, b2 = r_lama2.json(), r_baru2.json()
al_a = {h['nama']: h['cr'] for h in a2.get('konstruk', [])}
al_b = {h['nama']: h['cr'] for h in b2.get('konstruk', [])}
cek('sama: CR/alpha per konstruk', al_a == al_b and len(al_a) == 3, f'{al_a} vs {al_b}')

print('── 3. Kunci antar-layanan ──')
r_tanpa = c.post('/api/jembatan/hitung', json={'baris': baris})
cek('tanpa kunci → 401', r_tanpa.status_code == 401, str(r_tanpa.status_code))
r_salah = c.post('/api/jembatan/hitung', headers={'X-Kunci-Layanan': 'salah'},
                 json={'baris': baris})
cek('kunci salah → 401', r_salah.status_code == 401, str(r_salah.status_code))
simpan = os.environ.pop('JEMBATAN_KUNCI_LAYANAN')
r_belum = c.post('/api/jembatan/hitung', headers=KUNCI, json={'baris': baris})
cek('kunci server belum dipasang → 503', r_belum.status_code == 503,
    str(r_belum.status_code))
os.environ['JEMBATAN_KUNCI_LAYANAN'] = simpan
r_st = c.get('/api/jembatan/status')
cek('status terbuka & kunci_terpasang', r_st.status_code == 200
    and r_st.json().get('kunci_terpasang') is True)

print('── 4. Pra-survei ──')
n = 25
lat = rng.normal(0, 1, n)
pra = pd.DataFrame({
    'Kualitas_1': np.clip(np.round(3 + lat + rng.normal(0, .4, n)), 1, 5).astype(int),
    'Kualitas_2': np.clip(np.round(3 + lat + rng.normal(0, .4, n)), 1, 5).astype(int),
    'Kualitas_3': rng.integers(1, 6, n),                      # butir sampah (acak)
    'Harga_1': np.clip(np.round(3 + lat + rng.normal(0, .4, n)), 1, 5).astype(int),
    'Harga_2': np.clip(np.round(3 + lat + rng.normal(0, .4, n)), 1, 5).astype(int),
})
r_pra = c.post('/api/jembatan/hitung', headers=KUNCI,
               json={'tahap': 'pra-survei',
                     'baris': pra.to_dict(orient='records')})
cek('pra-survei 200', r_pra.status_code == 200, r_pra.text[:300])
j = r_pra.json()
per_var = {v['nama']: v for v in j.get('variabel', [])}
cek('kelompok otomatis Kualitas & Harga', set(per_var) == {'Kualitas', 'Harga'},
    str(set(per_var)))
k3 = [x for x in per_var.get('Kualitas', {}).get('butir', []) if x['butir'] == 'Kualitas_3']
cek('butir sampah Kualitas_3 TIDAK lolos', bool(k3) and k3[0]['lolos'] is False,
    str(k3))
cek('alpha keluar untuk semua variabel',
    all(v.get('alpha') is not None for v in per_var.values()))
r_pra2 = c.post('/api/jembatan/hitung', json={'tahap': 'pra-survei', 'baris': []})
cek('pra-survei tanpa kunci → 401', r_pra2.status_code == 401)

print('── 5. Regresi 4 bug (temuan review agen Bos, 21 Okt) ──')
# BUG 2 — kunci non-ASCII tidak boleh 500, harus 401.
# httpx menolak mengirim header non-ASCII dari sisi klien uji, jadi
# penangan dipanggil langsung (jalur kode yang sama persis).
import asyncio
from fastapi import HTTPException as _HE
from app.jembatan import buat_router as _br
_rt = _br(lambda d, p: (d, p), lambda r, m: r)
_ep = [r.endpoint for r in _rt.routes if r.path == '/api/jembatan/hitung'][0]
try:
    asyncio.run(_ep({'baris': baris}, x_kunci_layanan='kunci-✓-salah-é'))
    _kode = 200
except _HE as e:
    _kode = e.status_code
except TypeError:
    _kode = 500
cek('BUG2 kunci non-ASCII → 401 (bukan 500)', _kode == 401, str(_kode))
# BUG 3 — kolom jadi X dan Y sekaligus harus ditolak 400
r_tumpang = c.post('/api/jembatan/hitung', headers=KUNCI,
                   json={'mode': 'spss', 'tahap': 'utama', 'baris': baris,
                         'kolom_x': ['Keaslian_1'], 'kolom_y': 'Keaslian_1'})
cek('BUG3 kolom X=Y → 400', r_tumpang.status_code == 400,
    f"{r_tumpang.status_code} {r_tumpang.text[:120]}")
r_tumpang2 = c.post('/api/jembatan/hitung', headers=KUNCI,
                    json={'mode': 'pls', 'tahap': 'utama', 'baris': baris,
                          'konstruk': {'A': ['Keaslian_1', 'Keaslian_2'],
                                       'B': ['Keaslian_1', 'Interaksi_1']},
                          'kolom_y_konstruk': 'B'})
cek('BUG3 butir di 2 konstruk → 400', r_tumpang2.status_code == 400,
    f"{r_tumpang2.status_code} {r_tumpang2.text[:120]}")
# BUG 4 — nama kolom tanpa nomor butir harus ditolak dengan pesan jelas
pra_buruk = pd.DataFrame({'Kualitas': [3, 4, 5, 4] * 5,
                          'Harga': [4, 3, 4, 5] * 5})
r_buruk = c.post('/api/jembatan/hitung', headers=KUNCI,
                 json={'tahap': 'pra-survei',
                       'baris': pra_buruk.to_dict(orient='records')})
cek('BUG4 kolom tanpa nomor → 400 + sebut polanya',
    r_buruk.status_code == 400 and 'pola nama butir' in r_buruk.text,
    f"{r_buruk.status_code} {r_buruk.text[:160]}")
# Catatan review — kunci dibaca dari env, bukan tertanam: rotasi harus berlaku
os.environ['JEMBATAN_KUNCI_LAYANAN'] = 'kunci-baru-hasil-rotasi'
r_rot_lama = c.post('/api/jembatan/hitung', headers=KUNCI, json={'baris': baris})
r_rot_baru = c.post('/api/jembatan/hitung',
                    headers={'X-Kunci-Layanan': 'kunci-baru-hasil-rotasi'},
                    json={'tahap': 'pra-survei',
                          'baris': pra.to_dict(orient='records')})
cek('rotasi env: kunci lama ditolak, kunci baru diterima',
    r_rot_lama.status_code == 401 and r_rot_baru.status_code == 200,
    f'{r_rot_lama.status_code}/{r_rot_baru.status_code}')
os.environ['JEMBATAN_KUNCI_LAYANAN'] = 'kunci-uji-rahasia'

print('── 6. BUG 3 bentuk peran (review kedua — uji harus bergigi) ──')
# (klien di atas memakai raise_server_exceptions=False: kalau pagar
# dicabut, kiriman jahat bisa membuat mesin 500 — uji harus mencatatnya
# sebagai GAGAL yang terbaca, bukan crash di tengah jalan.)
# Variabel Keaslian terbelah: 2 butir jadi X1, 1 butir jadi Y1.
# Tanpa pagar belah-variabel, kiriman ini lolos 200 — jadi uji ini
# GAGAL kalau pagarnya dicabut (bergigi, bukan hiasan).
peran_belah = dict(peran); peran_belah['Keaslian_3'] = 'Y1'
r_belah = c.post('/api/jembatan/hitung', headers=KUNCI,
                 json={'mode': 'spss', 'tahap': 'utama', 'baris': baris,
                       'peran': peran_belah})
cek('BUG3b peran: variabel terbelah X/Y → 400',
    r_belah.status_code == 400 and 'terbelah' in r_belah.text,
    f"{r_belah.status_code} {r_belah.text[:160]}")
# Campur dua bentuk penandaan sekaligus → ambigu, tolak
r_campur = c.post('/api/jembatan/hitung', headers=KUNCI,
                  json={'mode': 'spss', 'tahap': 'utama', 'baris': baris,
                        'peran': peran, 'kolom_y': 'Impulsif_1'})
cek('BUG3b campur peran + kolom eksplisit → 400',
    r_campur.status_code == 400, f"{r_campur.status_code} {r_campur.text[:120]}")
# Konstruk PLS: variabel yang sama terbelah dua konstruk
r_belah_pls = c.post('/api/jembatan/hitung', headers=KUNCI,
                     json={'mode': 'pls', 'tahap': 'utama', 'baris': baris,
                           'konstruk': {'A': ['Keaslian_1', 'Keaslian_2'],
                                        'B': ['Keaslian_3', 'Interaksi_1',
                                              'Interaksi_2']},
                           'kolom_y_konstruk': 'B'})
cek('BUG3b konstruk: variabel terbelah → 400',
    r_belah_pls.status_code == 400 and 'terbelah' in r_belah_pls.text,
    f"{r_belah_pls.status_code} {r_belah_pls.text[:160]}")
# Dan bentuk peran yang SAH harus tetap 200 (pagar tidak boleh buta arah)
r_sah = c.post('/api/jembatan/hitung', headers=KUNCI,
               json={'mode': 'spss', 'tahap': 'utama', 'baris': baris,
                     'peran': peran})
cek('bentuk peran sah tetap 200', r_sah.status_code == 200,
    f"{r_sah.status_code} {r_sah.text[:120]}")

print()
if gagal:
    print(f'❌ {len(gagal)} GAGAL: {gagal}'); sys.exit(1)
print('✅ SEMUA LULUS — jembatan Fase 1')
