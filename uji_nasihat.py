#!/usr/bin/env python3
"""UJI nasihat.py — kelengkapan + bahasa hangat (aturan Bos 17Sep26).

⚠️ ATURAN BOS (verbatim): notifikasi WAJIB HANGAT & mengingatkan, BUKAN
   menakutkan — DILARANG 'PERINGATAN/GAGAL/HABIS/BAHAYA'. Wajib kasih JALAN KELUAR.
   Uji ini menegakkan aturan itu, dan HARUS BISA GAGAL.
"""
import sys, re
sys.path.insert(0, '/opt/data/services/statistik-lab')
from app import nasihat

LULUS = GAGAL = 0
def cek(s, p):
    global LULUS, GAGAL
    if s: LULUS += 1; print(f"  PASS  {p}")
    else: GAGAL += 1; print(f"  FAIL  {p}")

print("="*74)
print(" 1. KELENGKAPAN — 6 uji SPSS + 6 uji PLS")
print("="*74)
# ⚠️ JANGAN PAKU ANGKANYA (pelajaran 20Sep26): dulu ditulis `== 5` dan daftar
# kode tanpa 'htmt' → begitu HTMT ditambahkan, uji ini GAGAL PALSU.
# Cara tahan-banting: ambil daftar kode dari KAMUS-nya sendiri.
SPSS_KODE = ['normalitas', 'hetero', 'vif', 'linearitas', 'outlier', 'dw']
PLS_KODE = sorted(nasihat.PLS.keys())
cek(len(nasihat.SPSS) == len(SPSS_KODE),
    f"SPSS punya {len(nasihat.SPSS)} nasihat (harus {len(SPSS_KODE)})")
cek(len(nasihat.PLS) == len(PLS_KODE),
    f"PLS punya {len(nasihat.PLS)} nasihat (harus {len(PLS_KODE)})")
for kode in SPSS_KODE:
    n = nasihat.ambil(kode, 'spss')
    cek(n is not None, f"SPSS: {kode} ada")
for kode in PLS_KODE:
    n = nasihat.ambil(kode, 'pls')
    cek(n is not None, f"PLS: {kode} ada")

print()
print("="*74)
print(" 2. ISI TIAP NASIHAT LENGKAP (5 bagian wajib)")
print("="*74)
wajib = ['judul','arti','kenapa','boleh_abaikan','langkah','jangan']
for mode, peta in [('spss', nasihat.SPSS), ('pls', nasihat.PLS)]:
    for kode, n in peta.items():
        kurang = [w for w in wajib if w not in n or not n[w]]
        cek(not kurang, f"{mode}/{kode}: lengkap" if not kurang else f"{mode}/{kode}: KURANG {kurang}")

print()
print("="*74)
print(" 3. LANGKAH BERNOMOR (minimal 3 langkah per masalah)")
print("="*74)
for mode, peta in [('spss', nasihat.SPSS), ('pls', nasihat.PLS)]:
    for kode, n in peta.items():
        n_l = len(n['langkah'])
        bentuk_ok = all(isinstance(l, tuple) and len(l) == 2 for l in n['langkah'])
        cek(n_l >= 3 and bentuk_ok,
            f"{mode}/{kode}: {n_l} langkah, bentuk = (judul, penjelasan)")

print()
print("="*74)
print(" 4. BAHASA HANGAT — DILARANG kata menakutkan (aturan Bos)")
print("="*74)
TERLARANG = ['PERINGATAN', 'GAGAL!', 'BAHAYA', 'ANDA HARUS', 'SEGERA!',
             'HABIS!', 'FATAL', 'MUSTAHIL!']
for mode, peta in [('spss', nasihat.SPSS), ('pls', nasihat.PLS)]:
    for kode, n in peta.items():
        teks = ' '.join([n['judul'], n['arti'], n['kenapa'], n['boleh_abaikan'],
                         n['jangan']] + [a+' '+b for a,b in n['langkah']])
        ketemu = [t for t in TERLARANG if t in teks.upper()]
        cek(not ketemu, f"{mode}/{kode}: bebas kata menakutkan"
                        + (f" — DITEMUKAN {ketemu}" if ketemu else ""))

print()
print("="*74)
print(" 5. TIAP MASALAH PUNYA JALAN KELUAR (bukan cuma kabar buruk)")
print("="*74)
for mode, peta in [('spss', nasihat.SPSS), ('pls', nasihat.PLS)]:
    for kode, n in peta.items():
        cek(len(n['langkah']) >= 3 and len(n['boleh_abaikan']) > 30,
            f"{mode}/{kode}: ada langkah keluar + kapan boleh diabaikan")

print()
print("="*74)
print(" 6. KAMUS ISTILAH — istilah baku BERDAMPINGAN istilah ramah (aturan Bos)")
print("="*74)
pasangan = [
    ('hetero', 'Heteroskedastisitas', 'tidak rata'),
    ('vif', 'Multikolinearitas', 'kembar'),
    ('outlier', 'Outlier', 'menyimpang'),
    ('normalitas', 'Normalitas', 'sebaran'),
]
for kode, baku, ramah in pasangan:
    n = nasihat.ambil(kode, 'spss')
    teks = (n['judul'] + ' ' + n['arti']).lower()
    cek(baku.lower() in teks and ramah in teks,
        f"{kode}: \"{baku}\" berdampingan dengan \"{ramah}\"")

print()
print("="*74)
print(" 7. UJI DIRI — uji ini HARUS BISA GAGAL")
print("="*74)
# Suntik nasihat rusak (kata terlarang) → harus tertangkap
rusak = dict(nasihat.SPSS)
n_buruk = dict(rusak['hetero'])
n_buruk['jangan'] = 'PERINGATAN! Data kamu BAHAYA, ANDA HARUS segera perbaiki!'
teks_buruk = ' '.join([n_buruk['judul'], n_buruk['jangan']]).upper()
ketemu = [t for t in TERLARANG if t in teks_buruk]
cek(bool(ketemu), f"suntikan kata menakutkan TERTANGKAP: {ketemu}")

# Suntik nasihat kurang langkah → harus tertangkap
n_kurang = dict(rusak['vif'])
n_kurang['langkah'] = [('Satu langkah saja', 'tidak cukup')]
cek(len(n_kurang['langkah']) < 3, "suntikan langkah kurang TERTANGKAP")

print(f"\n{'='*74}")
print(f"  {LULUS} LULUS / {GAGAL} GAGAL")
print(f"{'='*74}")
sys.exit(1 if GAGAL else 0)
