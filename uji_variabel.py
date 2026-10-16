#!/usr/bin/env python3
"""Uji: 1–8 variabel + nama variabel + n sampai 2000.

Angka LULUS dari hasil hitung, bukan perasaan.
"""
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')

from app.berkas_kerja import buat_data, ke_csv

# ⚠️ UJI INI MENGUKUR CARA **BERGANDA** (ACC Bos 18Sep26).
# Alasannya: uji 1–8 variabel membandingkan jumlah PREDIKTOR, dan makna
# "β = pengaruh X setelah memperhitungkan X lain" (berganda) yang menjadi
# acuan galat. Kalau memakai 'sederhana', koefisiennya berbeda arti →
# membandingkan apel dengan jeruk.
CARA_UJI = 'berganda'

LULUS = GAGAL = 0


def cek(nama, syarat, info=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama} {info}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama} {info}')


# Pola β wajar — SAMA dengan yang dipakai halaman web (angkaWajar()).
# ⚠️ Penting: uji harus mengukur setelan yang WAJAR dipakai user, bukan
# setelan ekstrem yang memang mustahil. Batas nyata: Σβ² besar → koefisien
# mentok 0,98 → galat besar (hukum matematika, bukan bug).
POLA = {
    1: [0.38],
    2: [0.34, 0.24],
    3: [0.30, 0.22, 0.15],
    4: [0.28, 0.21, 0.15, 0.11],
    5: [0.27, 0.21, 0.16, 0.12, 0.10],
    6: [0.26, 0.20, 0.16, 0.12, 0.10, 0.08],
    7: [0.25, 0.20, 0.16, 0.13, 0.10, 0.08, 0.07],
    8: [0.24, 0.20, 0.16, 0.13, 0.11, 0.09, 0.08, 0.07],
}

print('═══ UJI 1–8 VARIABEL + NAMA VARIABEL + N SAMPAI 2000 ═══\n')

# ── 1. Semua jumlah X 1..8 bisa dibuat ──────────────────────────────────
print('── Jumlah variabel 1 sampai 8 (pola wajar, n=120) ──')
for x in range(1, 9):
    beta = POLA[x]
    d = buat_data(n=120, x=x, beta=beta, skala=5, alpha=0.85,
                  mode='presisi', cara=CARA_UJI)
    g = d['galat_maks']
    cek(f'{x} variabel', len(d['jalur']) == x and g < 0.05,
        f'| {len(d["jalur"])} jalur | galat maks {g:.4f} | R² {d["r2"]:.3f}')

# ── 1b. Setelan EKSTREM: harus JUJUR DITOLAK, bukan diam-diam salah ────
# ⚠️ CACAT UJI LAMA (ditemukan 18Sep26): uji ini dulu MENGHARAPKAN mesin
#    mengeluarkan galat besar untuk setelan mustahil ("jujur dilaporkan").
#    Setelah pagar kelayakan dipasang (ACC Bos 18Sep26), perilakunya BERUBAH
#    MENJADI LEBIH BAIK: setelan mustahil kini DITOLAK di depan dengan
#    pesan + saran, bukan dihasilkan lalu dilaporkan meleset.
#    Jadi uji ini diperbarui mengikuti perilaku yang BENAR — bukan pagarnya
#    yang dilonggarkan. Terukur: 8 X β=[0.30…0.125] (total 1,70) → R²=0,89
#    → tolak jujur (pesan menyebut batas wajar 0,65 + VIF).
print('\n── Setelan ekstrem 8 X β=0,30 (memang di luar batas) → harus DITOLAK ──')
try:
    buat_data(n=120, x=8, beta=[max(0.05, 0.30 - 0.025 * i) for i in range(8)],
              mode='presisi')
    cek('setelan mustahil ditolak jujur', False, '| TIDAK ditolak')
except ValueError as e:
    cek('setelan mustahil ditolak jujur', 'tidak bisa dicapai' in str(e).lower(),
        f'| {str(e)[:70]}...')
except Exception as e:                              # noqa: BLE001
    cek('setelan mustahil ditolak jujur', False, f'| galat lain {type(e).__name__}')

# ── 2. Nama variabel dipakai di hasil ───────────────────────────────────
print('\n── Nama variabel dari user ──')
NAMA = ['Tingkat Edukasi', 'Motivasi Belajar', 'Kualitas Layanan', 'Literasi Digital']
d = buat_data(n=150, x=4, beta=[0.28, 0.21, 0.15, 0.11],
              skala=5, alpha=0.85, mode='presisi', nama_x=NAMA,
              cara=CARA_UJI)
terpakai = [j['nama'] for j in d['jalur']]
cek('nama dipakai di hasil', terpakai == NAMA, f'| {terpakai}')
cek('kode internal tetap X1..X4', d['kode_x'] == ['X1', 'X2', 'X3', 'X4'],
    f'| {d["kode_x"]}')
cek('galat tetap kecil', d['galat_maks'] < 0.05, f'| {d["galat_maks"]:.4f}')

# ── 3. CSV/Excel pakai nama variabel, aman untuk SPSS ──────────────────
print('\n── Berkas unduhan ──')
csv = ke_csv(d).decode('utf-8')
hdr = csv.split('\n')[0].split(',')
cek('header pakai nama user', 'Tingkat_Edukasi_1' in hdr[0], f'| {hdr[:4]}')
cek('spasi jadi garis bawah', all(' ' not in h for h in hdr),
    f'| {len(hdr)} kolom, berspasi: {sum(" " in h for h in hdr)}')
cek('semua nama muncul', sum(1 for h in hdr if h.startswith('Literasi_Digital')) == 3,
    f'| kolom Literasi: {[h for h in hdr if h.startswith("Literasi")]}')

# ── 4. Nama kosong → kembali ke X1..Xn (tidak error) ───────────────────
print('\n── Nama kosong (tidak boleh error) ──')
d2 = buat_data(n=90, x=3, beta=[0.30, 0.22, 0.15], nama_x=['', '  ', None])
cek('kembali ke X1..X3', [j['nama'] for j in d2['jalur']] == ['X1', 'X2', 'X3'],
    f'| {[j["nama"] for j in d2["jalur"]]}')

# ── 5. n sampai 2000 ───────────────────────────────────────────────────
print('\n── Jumlah responden ──')
for n in (500, 1000, 2000):
    d3 = buat_data(n=n, x=3, beta=[0.30, 0.22, 0.15], mode='presisi', cara=CARA_UJI)
    cek(f'n={n}', d3['n'] == n and d3['galat_maks'] < 0.05,
        f'| n terbaca {d3["n"]} | galat {d3["galat_maks"]:.4f}')

# ── 6. Batas jaga: x=99 → 8, n=99999 → 2000 ────────────────────────────
print('\n── Batas jaga (jangan sampai error) ──')
d4 = buat_data(n=99999, x=99, beta=[0.2] * 20, mode='presisi')
cek('x=99 jadi 8', len(d4['jalur']) == 8, f'| {len(d4["jalur"])} jalur')
cek('n=99999 jadi 2000', d4['n'] == 2000, f'| {d4["n"]}')

print()
print('═══════════════════════════════════════════')
print(f'  TOTAL: {LULUS + GAGAL} uji | LULUS: {LULUS} | GAGAL: {GAGAL}')
print('  ✅ SEMUA LULUS' if GAGAL == 0 else '  ❌ MASIH ADA MASALAH')
sys.exit(0 if GAGAL == 0 else 1)
