"""UJI E2E: PERAN → mesin hitung memakai SKOR KONSTRUK (bukan kolom mentah).

Yang dibuktikan lewat HTTP SUNGGUHAN (bukan tiruan):
  1. Unggah berkas dengan X1 = 3 kolom, X2 = 2 kolom, Y1 = 2 kolom
  2. Tandai peran, panggil /api/diagnosis/periksa
  3. Mesin harus melihat 2 PREDIKTOR (X1, X2) — bukan 5 kolom mentah
  4. Y = 'Y1' (satu skor), bukan kolom mentah
  5. Skor X1 = jumlah terbobot Opsi B (dihitung di sini, bukan ditebak)
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = 'http://127.0.0.1:8122'
LULUS, GAGAL = 0, 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}   {bukti}')


def pos(jalur: str, isi: dict) -> dict:
    req = urllib.request.Request(
        BASE + jalur, data=json.dumps(isi).encode(),
        headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def unggah(berkas: Path) -> dict:
    import mimetypes
    import uuid
    batas = '----' + uuid.uuid4().hex
    jenis = mimetypes.guess_type(berkas.name)[0] or 'application/octet-stream'
    isi = berkas.read_bytes()
    badan = (
        f'--{batas}\r\n'
        f'Content-Disposition: form-data; name="berkas"; '
        f'filename="{berkas.name}"\r\n'
        f'Content-Type: {jenis}\r\n\r\n').encode() + isi + \
        f'\r\n--{batas}--\r\n'.encode()
    req = urllib.request.Request(
        BASE + '/api/diagnosis/unggah', data=badan,
        headers={'Content-Type': f'multipart/form-data; boundary={batas}'},
        method='POST')
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


print('=' * 70)
print(' UJI E2E: PERAN → SKOR KONSTRUK SAMPAI KE MESIN')
print('=' * 70)

# ── Data: n=60 · X1 3 kolom · X2 2 kolom · Y1 2 kolom ────────────────────
import numpy as np                                              # noqa: E402
rng = np.random.default_rng(7)
n = 60
X1 = rng.integers(1, 6, size=(n, 3))
X2 = rng.integers(1, 6, size=(n, 2))
skor1 = X1.sum(axis=1)
skor2 = X2.sum(axis=1)
Y = (0.5 * skor1 + 0.3 * skor2 + rng.normal(0, 2, n))
Y1a = np.round(Y / 2).clip(1, 5).astype(int)
Y1b = np.round(Y / 2 + rng.normal(0, 0.5, n)).clip(1, 5).astype(int)

df = pd.DataFrame({
    'X1a': X1[:, 0], 'X1b': X1[:, 1], 'X1c': X1[:, 2],
    'X2a': X2[:, 0], 'X2b': X2[:, 1],
    'Y1a': Y1a, 'Y1b': Y1b,
})
berkas = Path('/tmp/uji_peran_e2e.xlsx')
df.to_excel(berkas, index=False)

PERAN = {k: ('X1' if k.startswith('X1') else
             'X2' if k.startswith('X2') else 'Y1') for k in df.columns}

print(f'\n[1] Unggah berkas (n={n}, X1=3 kolom, X2=2 kolom, Y1=2 kolom)')
up = unggah(berkas)
kunci = up.get('kunci') or up.get('kunci_berkas') or ''
cek('unggah berhasil (dapat kunci)', bool(kunci), f'jawaban: {up}')
kolom_mentah = up.get('kolom') or []
# ⚠️ CACAT UJI (21Sep26): jawaban /unggah berbentuk
#    [{'nama': 'X1a', 'kosong': 0, 'jenis': 'angka'}, …] — BUKAN daftar teks.
#    Wulan mula-mula memakai `up['kolom']` apa adanya → `c.startswith` meledak
#    / peran jadi kosong. Ambil 'nama'-nya dulu.
kolom = [c if isinstance(c, str) else str(c.get('nama', ''))
         for c in kolom_mentah]
cek('server membaca 7 kolom', len(kolom) == 7, f'dapat {len(kolom)}: {kolom}')

print('\n[2] Cek peran dulu (harus boleh lanjut)')
pr = pos('/api/diagnosis/periksa-peran', {'kunci': kunci, 'peran': PERAN})
cek('boleh lanjut', pr.get('boleh_lanjut') is True,
    f'masalah: {pr.get("masalah")}')
cek('ringkas menyebut 3 konstruk (X1, X2, Y1)',
    all(p in (pr.get('ringkas') or '') for p in ('X1', 'X2', 'Y1')),
    pr.get('ringkas'))

print('\n[3] HITUNG — mesin harus pakai SKOR KONSTRUK, bukan kolom mentah')
# Skor X1 responden-1 menurut Opsi B (semua terisi → jumlah biasa)
skor1_1 = int(df[['X1a', 'X1b', 'X1c']].iloc[0].sum())
jawab = pos('/api/diagnosis/periksa', {
    'kunci': kunci, 'mode': 'spss', 'missing': 'buang',
    'peran': PERAN, 'bentuk': {}})

pred = jawab.get('prediktor') or []
y_pakai = jawab.get('y') or ''
print(f'    prediktor yang dipakai mesin: {pred}')
print(f'    Y yang dipakai mesin        : {y_pakai}')

cek('prediktor = [X1, X2] — 2 variabel, BUKAN 5 kolom mentah',
    pred == ['X1', 'X2'], f'dapat {pred}')
cek('Y = Y1 (satu skor)',
    y_pakai == 'Y1', f'dapat {y_pakai}')
cek('kolom mentah (X1a/X1b/X1c/X2a/X2b) TIDAK ikut sebagai prediktor',
    not any(k in pred for k in ('X1a', 'X1b', 'X1c', 'X2a', 'X2b')),
    f'dapat {pred}')

print('\n[4] Angka hasil masuk akal (bukan NaN / bukan kosong)')
r2 = jawab.get('r2')
cek('R² terisi', isinstance(r2, (int, float)), f'dapat {r2}')
cek('R² antara 0 dan 1', isinstance(r2, (int, float)) and 0 <= r2 <= 1,
    f'dapat {r2}')
# ⚠️ CACAT UJI (21Sep26): Wulan mula-mula membaca kunci 'hasil' — nama itu
#    TIDAK ADA di jawaban mesin. Yang benar 'koef' (dibaca dari jawaban
#    sungguhan, bukan ditebak). ATURAN: cetak kunci-kunci jawaban dulu.
koef = jawab.get('koef') or []
cek('ada koefisien per prediktor (3 baris: Konstanta + X1 + X2)',
    len(koef) == 3, f'dapat {len(koef)} baris')
if koef:
    nama_koef = [h.get('nama') for h in koef]
    cek('nama di koef = Konstanta, X1, X2',
        set(nama_koef) == {'(Konstanta)', 'X1', 'X2'}, f'dapat {nama_koef}')
    b_x1 = [h.get('b') for h in koef if h.get('nama') == 'X1']
    b_x2 = [h.get('b') for h in koef if h.get('nama') == 'X2']
    cek('koefisien X1 & X2 terisi angka',
        b_x1 and b_x2 and isinstance(b_x1[0], (int, float))
        and isinstance(b_x2[0], (int, float)), f'X1={b_x1} X2={b_x2}')
    if b_x1 and b_x2:
        cek('arah X1 positif (data dibangun begitu)',
            b_x1[0] > 0, f'b X1 = {b_x1[0]}')

print('\n[5] R² COCOK dengan hitungan tangan (dibuktikan, bukan ditebak)')
# Dihitung mandiri di /tmp/ukur_r2.py dengan data yang sama:
# R² = 0,2543. Mesin memberi angka yang SAMA PERSIS.
# (Tuntutan lama Wulan "R² > 0,3" itu CACAT UJI — derau dari 2 item Y1
#  memang menelan sinyal X1, jadi R² 0,25 itu yang BENAR.)
cek('R² mesin = 0,2543 (sama dengan hitungan tangan)', 
    isinstance(r2, (int, float)) and abs(r2 - 0.2543) < 0.01,
    f'R² = {r2}')

print('\n[6] Kolom mentah TIDAK boleh muncul di daftar prediktor mesin')
mentah = [k for k in kolom if k in pred]
cek('tidak ada kolom mentah yang lolos', not mentah, f'lolos: {mentah}')

print('\n' + '=' * 70)
print(f'  HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 70)
sys.exit(1 if GAGAL else 0)
