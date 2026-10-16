"""BUKTIKAN: uji_alat_ukur_grafik.py MAMPU GAGAL (bukan hijau palsu).

ATURAN BOS (19Sep26): "GERBANG WAJIB DIUJI BISA GAGAL".

⚠️ CACAT CARA UKUR YANG SUDAH DITUTUP DI BERKAS INI (20Sep26, jangan ulang):
   Percobaan pertama melaporkan "petakan() dirusak → LOLOS" — padahal
   ujinya BENAR. Dua sebab, dua-duanya cacat cara ukur WULAN:
     ① skrip ini memakai `sys.executable`, yaitu Python LUAR (/opt/data/.venv)
        — bukan interpreter proyek. Akibatnya `import app.diagnosis` di dalam
        uji mengambil berkas dari /opt/data/... (asli), BUKAN dari salinan
        tersuntik. ⇒ WAJIB pakai `<TMP>/.venv/bin/python` (symlink ke venv
        proyek) dan `cwd=<TMP>`.
     ② Penyuntikan pertama gagal senyap: pola penggantinya beda dari isi
        berkas, sementara skrip tetap melaporkan "berkas berubah: True"
        untuk kasus lain. ⇒ WAJIB periksa `berkas berubah` PER KASUS dan
        BATALKAN kalau suntikan tidak mengubah apa pun.

CARA BENAR (dipakai di bawah): salin proyek ke /tmp → suntik kerusakan NYATA
ke salinan → jalankan UJI-nya dari dalam salinan itu → HARUS EXIT != 0.
"""
import shutil
import subprocess
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
TMP = Path('/tmp/bukti_uji_gagal_grafik')
PY = DIR / '.venv' / 'bin' / 'python'          # ⚠️ interpreter PROYEK, bukan luar

if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)
shutil.copy(DIR / 'uji_alat_ukur_grafik.py', TMP / 'uji_alat_ukur_grafik.py')
shutil.copytree(DIR / 'app', TMP / 'app')
(TMP / '_sketsa').mkdir()
try:
    (TMP / '.venv').symlink_to(DIR / '.venv')
except OSError:
    pass

JS = TMP / 'app' / 'static' / 'grafik_hidup.js'
OASLI = JS.read_text(encoding='utf-8')

# (label, pola_lama, pola_baru)
SUNTIKAN = [
    ('petakan() dirusak  (rumus dibalik)',
     'return gambarMin + t * (gambarMaks - gambarMin);',
     'return gambarMaks - t * (gambarMaks - gambarMin);'),
    ('pasangan titik dipisah  (indeks sendiri-sendiri)',
     'const idx = indeksSebar(nAsli, BATAS_TITIK);\n'
     '  const zp = ambilPada(zpA, idx);\n'
     '  const zr = ambilPada(zrA, idx);',
     'const zp = zpA;\n  const zr = zrA;   /* RUSAK SENGAJA: indeks terpisah */'),
    ('batas jaga titik hilang  (BATAS_TITIK 99.999)',
     'const BATAS_TITIK = 500;',
     'const BATAS_TITIK = 99999;'),
    ('warna tertukar  (aman digambar merah)',
     "const warna = aman ? '#2E7D6F' : '#A85A5A';",
     "const warna = aman ? '#A85A5A' : '#2E7D6F';"),
]


def jalankan():
    """Jalankan UJI dari dalam salinan — WAJIB pakai interpreter proyek."""
    p = subprocess.run([str(PY), str(TMP / 'uji_alat_ukur_grafik.py')],
                       capture_output=True, text=True, cwd=str(TMP))
    out = p.stdout or ''
    gagal_cek = [b.strip() for b in out.splitlines() if b.strip().startswith('FAIL')]
    ringkas = [b.strip() for b in out.splitlines() if 'LULUS /' in b and 'GAGAL' in b]
    return p.returncode, (ringkas[-1] if ringkas else '(tidak ada ringkasan)'), gagal_cek


print('=' * 76)
print(' BUKTI: uji_alat_ukur_grafik.py BISA GAGAL')
print('=' * 76)

print('\n  (0) salinan BERSIH — harus EXIT 0')
JS.write_text(OASLI, encoding='utf-8')
rc0, ringkas0, _ = jalankan()
print(f'      EXIT={rc0}   {ringkas0}')

hasil = [('salinan bersih (tidak disuntik)', rc0, 0)]

for label, pola_lama, pola_baru in SUNTIKAN:
    print(f'\n  ▸ {label}')
    baru = OASLI.replace(pola_lama, pola_baru, 1)
    berubah = baru != OASLI
    print(f'      suntikan benar-benar mengubah berkas: {berubah}')
    if not berubah:
        print('      ❌ DIBATALKAN — pola tidak cocok, hasil tidak sah')
        hasil.append((label, None, 1))
        continue
    JS.write_text(baru, encoding='utf-8')
    rc, ringkas, gagal_cek = jalankan()
    print(f'      EXIT={rc}   {ringkas}')
    for g in gagal_cek[:3]:
        print(f'        {g}')
    hasil.append((label, rc, 1))

JS.write_text(OASLI, encoding='utf-8')
shutil.rmtree(TMP, ignore_errors=True)

print()
print('=' * 76)
ok = True
for label, dapat, harap in hasil:
    if dapat is None:
        print(f'  ❌ {label:52} DIBATALKAN (suntikan tidak masuk)')
        ok = False
        continue
    tanda = '✅' if dapat == harap else '❌'
    if dapat != harap:
        ok = False
    print(f'  {tanda} {label:52} EXIT {dapat} (harap {harap})')
print()
print('  ✅ UJI TERBUKTI BERGIGI — tiap kerusakan nyata tertangkap (EXIT 1)' if ok
      else '  ❌ UJI TIDAK BERGIGI — ada kerusakan yang lolos')
print('=' * 76)
sys.exit(0 if ok else 1)
