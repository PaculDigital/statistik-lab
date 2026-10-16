"""UJI skor_konstruk() — gabung kolom berperan sama jadi SATU skor.

Yang diuji:
  1. X1 = 3 kolom → jadi 1 kolom bernama 'X1' (bukan 3)
  2. Nilainya = JUMLAH (bukan rata-rata) — dihitung tangan, dibandingkan
  3. Y1 = 2 kolom → 1 skor
  4. Kolom tak ditandai → DILEWATI (tidak jadi kolom, tidak diisi 0)
  5. Urutan kolom peta ikut URUTAN BERKAS (bukan urutan dict)
  6. Tenggat: tidak ada peran → tabel kosong (jujur, bukan galat)
  7. Kolom hilang dari df → tidak meledak
  8. Nilai kosong/teks → jadi NaN, tidak meledak
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.diagnosis import skor_konstruk                    # noqa: E402

LULUS, GAGAL = 0, 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}   {bukti}')


print('=' * 70)
print(' UJI skor_konstruk() — GABUNG KOLOM SEPERAN')
print('=' * 70)

# ── Data uji: 4 responden ────────────────────────────────────────────────
df = pd.DataFrame({
    'X1a': [4, 5, 3, 4],
    'X1b': [5, 5, 4, 4],
    'X1c': [3, 4, 3, 5],
    'X2a': [2, 3, 2, 3],
    'X2b': [3, 3, 2, 2],
    'Y1a': [4, 4, 3, 5],
    'Y1b': [5, 4, 4, 4],
    'Umur': [21, 22, 20, 23],          # tak ditandai
    'Catatan': ['a', 'b', 'c', 'd'],   # tak ditandai (teks)
})

PERAN = {'X1a': 'X1', 'X1b': 'X1', 'X1c': 'X1',
         'X2a': 'X2', 'X2b': 'X2',
         'Y1a': 'Y1', 'Y1b': 'Y1'}

tabel, peta = skor_konstruk(df, PERAN)

print('\n[1] Bentuk hasil')
cek('kolom hasil = X1, X2, Y1 (3 konstruk, bukan 7 kolom)',
    list(tabel.columns) == ['X1', 'X2', 'Y1'], f'dapat {list(tabel.columns)}')
cek('baris tetap 4 (tiap responden 1 baris)', len(tabel) == 4)
cek('X1 cuma SATU kolom (bukan 3)', list(tabel.columns).count('X1') == 1)

print('\n[2] Nilai = JUMLAH (dihitung tangan, bukan ditebak)')
# Responden 1: X1a=4 + X1b=5 + X1c=3 = 12
cek('X1 responden-1 = 12 (4+5+3)',
    int(tabel['X1'].iloc[0]) == 12, f'dapat {tabel["X1"].iloc[0]}')
# Responden 4: X1a=4 + X1b=4 + X1c=5 = 13
cek('X1 responden-4 = 13 (4+4+5)',
    int(tabel['X1'].iloc[3]) == 13, f'dapat {tabel["X1"].iloc[3]}')
# X2 responden 1: 2 + 3 = 5
cek('X2 responden-1 = 5 (2+3)',
    int(tabel['X2'].iloc[0]) == 5, f'dapat {tabel["X2"].iloc[0]}')
# Y1 responden 4: 5 + 4 = 9
cek('Y1 responden-4 = 9 (5+4)',
    int(tabel['Y1'].iloc[3]) == 9, f'dapat {tabel["Y1"].iloc[3]}')
# Ini BUKTI jumlah, bukan rata-rata: rata-rata X1 responden-1 = 4
cek('BUKAN rata-rata (rata-rata X1-1 akan jadi 4, kita dapat 12)',
    int(tabel['X1'].iloc[0]) != 4)
# Nama kolom harus nama PERAN, bukan kolom asal
cek('kolom X1a/X1b/X1c TIDAK ada di tabel hasil',
    not any(k in tabel.columns for k in ('X1a', 'X1b', 'X1c')))

print('\n[3] Kolom tak ditandai DILEWATI (bukan diisi 0)')
cek('Umur tidak jadi kolom', 'Umur' not in tabel.columns)
cek('Catatan tidak jadi kolom', 'Catatan' not in tabel.columns)
cek('jumlah kolom hasil = 3 (bukan 9)', tabel.shape[1] == 3,
    f'dapat {tabel.shape[1]}')

print('\n[4] Peta (dipakai untuk tampilan)')
cek('peta X1 = [X1a, X1b, X1c]', peta.get('X1') == ['X1a', 'X1b', 'X1c'],
    f'dapat {peta.get("X1")}')
cek('peta Y1 = [Y1a, Y1b]', peta.get('Y1') == ['Y1a', 'Y1b'],
    f'dapat {peta.get("Y1")}')
cek('Umur/Catatan tidak masuk peta',
    'Umur' not in [k for v in peta.values() for k in v])

print('\n[5] Urutan ikut URUTAN BERKAS')
df2 = pd.DataFrame({'b': [1.0], 'a': [2.0]})
t2, p2 = skor_konstruk(df2, {'b': 'X2', 'a': 'X1'})
cek('kolom hasil urut berkas (X2 dulu, karena kolom b dulu)',
    list(t2.columns) == ['X2', 'X1'], f'dapat {list(t2.columns)}')

print('\n[6] Jujur: tidak ada peran → tabel KOSONG (bukan galat)')
t3, p3 = skor_konstruk(df, {})
cek('tabel kosong', t3.shape[1] == 0, f'dapat {t3.shape}')
cek('peta kosong', p3 == {})
cek('tidak meledak (tidak ada exception)', True)

print('\n[7] Kolom hilang dari df → tidak meledak')
t4, p4 = skor_konstruk(df, {'X1a': 'X1', 'TIDAK_ADA': 'X2'})
cek('X1 tetap terhitung', 'X1' in t4.columns)
cek('X2 dilewati (kolomnya tidak ada)', 'X2' not in t4.columns,
    f'dapat {list(t4.columns)}')

print('\n[8] Nilai kosong / teks → tidak jadi angka palsu')
# ⚠️ CACAT UJI (21Sep26): Wulan mula-mula menulis `''` lalu mengubahnya
#    sendiri jadi NaN SEBELUM memanggil skor_konstruk → kolom kosongnya
#    sudah hilang dari data → uji memprotes palsu. Yang benar: kirim nilai
#    APA ADANYA, biarkan MESIN yang mengubahnya.
#    Angka di bawah mengikuti Opsi B (lihat blok [9]).
df5 = pd.DataFrame({'a': [1, '', 3], 'b': [1, 2, 3]})
t5, _ = skor_konstruk(df5, {'a': 'X1', 'b': 'X1'})
# r0: lengkap 1+1 = 2 · r1: jawab 'b'=2 saja → (2/1)×2 = 4,0 ·
# r2: lengkap 3+3 = 6
cek('baris 0 (lengkap) → 2,0', abs(t5['X1'].iloc[0] - 2.0) < 1e-9,
    f'dapat {t5["X1"].iloc[0]}')
cek('baris 1 (jawab 1 dari 2) → 4,0 = (2/1)×2  [Opsi B]',
    abs(t5['X1'].iloc[1] - 4.0) < 1e-9, f'dapat {t5["X1"].iloc[1]}')
cek('baris 1 BUKAN 2,0 (itu Opsi C, seolah lengkap padahal tidak)',
    abs(t5['X1'].iloc[1] - 2.0) > 1e-9)
cek('baris 2 (lengkap) → 6,0', abs(t5['X1'].iloc[2] - 6.0) < 1e-9)

print('\n[9] ATURAN JAWABAN KOSONG = Opsi B (ACC Bos 21Sep26)')
print('    skor = rata-rata item TERJAWAB × jumlah item SELURUHNYA')
# X1 = 3 item (a, b, c).
#   responden-1: a=4, b=5, c=KOSONG → jawab 2 dari 3 → (9/2)×3 = 13,5
#   responden-2: a=KOSONG, b=2, c=3 → jawab 2 dari 3 → (5/2)×3 = 7,5
#   responden-3: jawab penuh 3,3,3     → (9/3)×3 = 9,0
# Opsi C (SPSS SUM) akan memberi 9,0 · 5,0 · 9,0 — responden-1 terlihat
# lebih rendah padahal cuma kurang 1 item. Opsi A akan membuang.
df6 = pd.DataFrame({'a': [4, '', 3], 'b': [5, 2, 3], 'c': ['', 3, 3]})
t6, _ = skor_konstruk(df6, {'a': 'X1', 'b': 'X1', 'c': 'X1'})
r0, r1, r2 = (t6['X1'].iloc[0], t6['X1'].iloc[1], t6['X1'].iloc[2])
cek('responden-1 (jawab 2 dari 3: 4 dan 5) → 13,5 = ((4+5)/2)×3',
    abs(r0 - 13.5) < 1e-9, f'dapat {r0}')
cek('BUKAN 9,0 — itu cara SPSS (Opsi C) yang bikin skor terlalu kecil',
    abs(r0 - 9.0) > 1e-9)
cek('BUKAN NaN — itu Opsi A yang membuang responden',
    not pd.isna(r0))
cek('responden-2 (jawab 2 dari 3: 2 dan 3) → 7,5 = ((2+3)/2)×3',
    abs(r1 - 7.5) < 1e-9, f'dapat {r1}')
cek('responden-3 (jawab penuh 3,3,3) → 9,0 = (9/3)×3',
    abs(r2 - 9.0) < 1e-9, f'dapat {r2}')
cek('responden LENGKAP tetap sama dengan Opsi C (tidak berubah perilaku)',
    abs(r2 - 9.0) < 1e-9)

print('\n[10] SEMUA item kosong → skor KOSONG (bukan 0)')
df7 = pd.DataFrame({'a': ['', 2], 'b': ['', 3]})
t7, _ = skor_konstruk(df7, {'a': 'X1', 'b': 'X1'})
cek('responden-1 (semua kosong) → NaN',
    pd.isna(t7['X1'].iloc[0]), f'dapat {t7["X1"].iloc[0]}')
cek('BUKAN 0 — nol itu nilai, bukan ketiadaan',
    not (not pd.isna(t7['X1'].iloc[0]) and t7['X1'].iloc[0] == 0))
cek('responden-2 (lengkap) tetap 5,0', abs(t7['X1'].iloc[1] - 5.0) < 1e-9)

print('\n[11] Sejalan dengan jalur PLS saat data LENGKAP (satu aturan)')
# PLS: sum(axis=1). Untuk data lengkap, rata-rata×jumlah = jumlah.
manual = df[['X1a', 'X1b', 'X1c']].apply(
    pd.to_numeric, errors='coerce').sum(axis=1)
cek('X1 data lengkap = sum(axis=1) persis sama dengan jalur PLS',
    (tabel['X1'] == manual).all())

print('\n' + '=' * 70)
print(f'  HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 70)
sys.exit(1 if GAGAL else 0)
