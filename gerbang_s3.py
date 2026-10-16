#!/usr/bin/env python3
"""GERBANG S3: jangan sampai bentuk LAIN rusak gara-gara tambahan S3.

Yang diperiksa (semua lewat fungsi SUNGGUHAN app.berkas_kerja.buat_data):
  1. cara='sederhana'  → tetap jalan, 'rantai' KOSONG
  2. cara='berganda'   → tetap jalan, 'rantai' KOSONG
  3. cara='keduanya'   → tetap jalan, 'rantai' KOSONG
  4. cara='berantai'   → 'rantai' ADA sejumlah x-1
  5. cara='berantai' dengan x=1 → otomatis jadi 'sederhana' (tidak error)
  6. cara ngawur ('xyz') → jatuh ke 'sederhana' (tidak error)
  7. angka lama TIDAK berubah: cara='berganda' 3 X galat ≤ 0,05
"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from app.berkas_kerja import buat_data     # noqa: E402

lulus = 0
gagal = 0


def cek(nama, syarat, bukti=''):
    global lulus, gagal
    if syarat:
        lulus += 1
        print(f"  ✅ {nama} {bukti}")
    else:
        gagal += 1
        print(f"  ❌ {nama} {bukti}")


print("=" * 66)
print("GERBANG S3 — bentuk lain tidak boleh rusak")
print("=" * 66)

# ── 1-3: cara lama tetap jalan, rantai KOSONG ──
for cara in ('sederhana', 'berganda', 'keduanya'):
    d = buat_data(n=300, x=3, beta=[0.32, 0.27, 0.22], skala=5, alpha=0.85,
                  mode='presisi', cara=cara)
    print(f"\n[{cara}]")
    cek('cara tersimpan', d['cara'] == cara, f"→ {d['cara']}")
    cek('rantai KOSONG (bukan S3)', d['rantai'] == [], f"→ {d['rantai']}")
    cek('galat_maks <= 0.05', d['galat_maks'] <= 0.05,
        f"→ {d['galat_maks']:.4f}")
    cek('bersama ada 3 baris', len(d['bersama']) == 3)
    cek('terpisah ada 3 baris', len(d['terpisah']) == 3)

# ── 4: berantai punya rantai ──
print("\n[berantai 3 X]")
d = buat_data(n=300, x=3, beta=[0.32, 0.27, 0.22], skala=5, alpha=0.85,
              mode='presisi', cara='berantai')
cek('cara tersimpan', d['cara'] == 'berantai')
cek('rantai ada 2 ruas', len(d['rantai']) == 2, f"→ {len(d['rantai'])}")
cek('ranta_setel = 0.55', d['ranta_setel'] == 0.55)
cek('galat <= 0.06', d['galat_maks'] <= 0.06, f"→ {d['galat_maks']:.4f}")

# ── 5: x=1 dengan berantai → jadi sederhana, tidak error ──
print("\n[berantai 1 X — harus jatuh ke sederhana]")
d = buat_data(n=200, x=1, beta=[0.40], skala=5, alpha=0.85,
              mode='presisi', cara='berantai')
cek('cara jadi sederhana', d['cara'] == 'sederhana', f"→ {d['cara']}")
cek('rantai kosong', d['rantai'] == [])

# ── 6: cara ngawur → sederhana, tidak error ──
print("\n[cara ngawur 'xyz']")
d = buat_data(n=200, x=3, beta=[0.3, 0.25, 0.2], skala=5, alpha=0.85,
              mode='presisi', cara='xyz')
cek('jatuh ke sederhana', d['cara'] == 'sederhana', f"→ {d['cara']}")

# ── 7: berantai 8 X dengan β LAYAK tidak error ──
# 🚨 PELAJARAN 18Sep26 (Opsi C): β=0,20×8 → total 1,60 → PECAH (galat 0,0850).
#    Ternyata batasnya TOTAL β ≤ 1,20, BUKAN jumlah X. Dengan 0,14×8=1,12
#    mesin BERHASIL (galat 0,0080). Jadi uji ini memakai β yang benar-benar
#    layak — kalau tidak, yang salah adalah SETELAN UJInya, bukan mesin.
print("\n[berantai 8 X — β layak 0.14 (total 1.12)]")
beta8 = [0.14] * 8
d = buat_data(n=300, x=8, beta=beta8, skala=5, alpha=0.85,
              mode='presisi', cara='berantai')
cek('rantai ada 7 ruas', len(d['rantai']) == 7, f"→ {len(d['rantai'])}")
cek('galat <= 0.06', d['galat_maks'] <= 0.06, f"→ {d['galat_maks']:.4f}")

# ── 7b: total β melebihi batas → DITOLAK dengan saran ──
print("\n[berantai total β 1.60 — harus DITOLAK + saran]")
try:
    buat_data(n=300, x=8, beta=[0.20] * 8, skala=5, alpha=0.85,
              mode='presisi', cara='berantai')
    cek('total β lewat batas ditolak', False, '— TIDAK ditolak')
except ValueError as e:
    pesan = str(e)
    cek('total β lewat batas ditolak', True)
    cek('pesannya menyebut batas + saran angka',
        'batas aman' in pesan and 'per variabel' in pesan,
        f'→ {pesan[:95]}...')
except Exception as e:                             # noqa: BLE001
    cek('total β lewat batas ditolak', False, f'— galat lain: {type(e).__name__}')

# ── 8: setelan MUSTAHIL harus DITOLAK JUJUR (cara berganda) ──
# 🚨 WULAN SALAH PILIH KASUS UJI (terukur 18Sep26): mula-mula dipakai
#    β=[0.40,0.36,0.32,0.28] (4 X) dan dianggap "mustahil" — TERNYATA
#    pagar hitung R²=0,7462 (AMAN) dan mesin memang berhasil (galat 0,0179).
#    Jadi uji itu SALAH KASUS, bukan pagar yang rusak.
#    Kasus yang BENAR-BENAR mustahil (terukur):
#      5 X β=[0.40,0.36,0.32,0.28,0.24] → R²=0,93  → hampir mustahil
#      8 X β=[0.40…0.12]                → R²>1,00  → mustahil
print("\n[setelan mustahil — cara berganda, harus DITOLAK]")
for nama_kasus, beta_mustahil in (
        ('5 X R²=0.93', [0.40, 0.36, 0.32, 0.28, 0.24]),
        ('8 X R²>1', [round(0.40 - 0.04 * i, 3) for i in range(8)])):
    try:
        buat_data(n=300, x=len(beta_mustahil), beta=beta_mustahil, skala=5,
                  alpha=0.85, mode='presisi', cara='berganda')
        cek(f'{nama_kasus} ditolak', False, '— TIDAK ditolak')
    except ValueError as e:
        pesan = str(e)
        jelas = ('tidak bisa dicapai' in pesan.lower()
                 or 'tidak mungkin' in pesan.lower()
                 or 'hampir mustahil' in pesan.lower())
        cek(f'{nama_kasus} ditolak', True)
        cek(f'{nama_kasus} pesannya jelas', jelas, f'→ {pesan[:70]}...')
    except Exception as e:                             # noqa: BLE001
        cek(f'{nama_kasus} ditolak', False, f'— galat lain: {type(e).__name__}')

# ── 8c: setelan yang NYATANYA BISA jangan ikut ditolak ──
print("\n[setelan yang memang bisa — JANGAN ditolak]")
try:
    d = buat_data(n=300, x=4, beta=[0.40, 0.36, 0.32, 0.28], skala=5,
                  alpha=0.85, mode='presisi', cara='berganda')
    cek('4 X β=[0.40…0.28] lolos (R²=0.75)', d['galat_maks'] <= 0.05,
        f"→ galat {d['galat_maks']:.4f}")
except ValueError as e:
    cek('4 X β=[0.40…0.28] lolos', False, f'— ditolak padahal bisa: {e}')

# ── 8b: cara berantai TIDAK boleh ditolak oleh pagar R² (yang asumsinya
#        X saling bebas). Pagar R² tetap dipakai untuk 'berganda'.
#        ⚠️ Batas TOTAL β (1,20) TETAP berlaku di berantai — itu pagar lain,
#        memang untuk model ini. Jadi uji ini pakai β yang lolos batas itu.
print("\n[berantai — pagar R² jangan memblokir; batas total β tetap berlaku]")
try:
    d = buat_data(n=300, x=8, beta=[0.14] * 8, skala=5, alpha=0.85,
                  mode='presisi', cara='berantai')
    cek('berantai 8 X (total β 1.12) lolos', len(d['rantai']) == 7,
        f"→ galat {d['galat_maks']:.4f}, rantai {len(d['rantai'])}")
except ValueError as e:
    cek('berantai 8 X (total β 1.12) lolos', False,
        f'— ditolak padahal bisa: {e}')

# ── 9: setelan β SEDERHANA tetap boleh (tidak ikut ditolak) ──
print("\n[setelan wajar tetap boleh]")
d = buat_data(n=300, x=3, beta=[0.35, 0.30, 0.25], skala=5, alpha=0.85,
              mode='presisi', cara='berganda')
cek('setelan wajar lolos', d['galat_maks'] <= 0.05,
    f"→ galat {d['galat_maks']:.4f}")

print("\n" + "=" * 66)
print(f"HASIL GERBANG: {lulus} LULUS / {gagal} GAGAL")
print("=" * 66)
raise SystemExit(0 if gagal == 0 else 1)
