"""BUKTIKAN: batas waktu grup (BATAS_GRUP) BENAR-BENAR BEKERJA.

ATURAN BOS 20Sep26: "GERBANG WAJIB DIUJI BISA GAGAL".
Cara: suntik satu uji PALSU yang tidur 200 detik ke SALINAN gerbang_uji.py,
jalankan, dan pastikan gerbang TIDAK menunggu selamanya — ia berhenti di
batas waktu dan melaporkan TIMEOUT sebagai GAGAL.

Jangan menjalankan ini di gerbang asli (akan memakan waktu).
"""
import shutil
import subprocess
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
TMP = Path('/tmp/uji_batas_grup')
PY = DIR / '.venv' / 'bin' / 'python3'

if TMP.exists():
    shutil.rmtree(TMP)
TMP.mkdir(parents=True)

# salinan MINIMAL: gerbang + dua uji palsu (satu normal, satu tidur lama)
(TMP / 'app').mkdir()

# ⚠️ gerbang mencari interpreter di <salinan>/.venv/bin/python3 — WAJIB ada,
# kalau tidak gerbang keluar di gerbang-masuk (exit 2) dan buktinya palsu.
try:
    (TMP / '.venv').symlink_to(DIR / '.venv')
except OSError:
    pass

(TMP / 'uji_palsu_cepat.py').write_text(
    "print('  9 LULUS / 0 GAGAL')\nraise SystemExit(0)\n", encoding='utf-8')

(TMP / 'uji_palsu_tidur.py').write_text(
    "import time\n"
    "print('  mulai tidur...')\n"
    "time.sleep(200)\n"
    "print('  seharusnya tidak pernah sampai sini')\n", encoding='utf-8')

asli = (DIR / 'gerbang_uji.py').read_text(encoding='utf-8')

# Turunkan batas jadi 8 detik supaya bukti cepat, dan pakai hanya 2 uji palsu
uji_palsu = '''UJI = [
    ("PALSU — uji cepat (harus LULUS)", "uji_palsu_cepat.py", "kontrol: ini harus lulus"),
    ("PALSU — uji tidur 200 detik (harus TIMEOUT)", "uji_palsu_tidur.py",
     "membuktikan batas waktu benar-benar menghentikan grup yang menggantung"),
]
'''

# ganti blok UJI = [ ... ] dengan versi palsu
i = asli.index('UJI = [')
j = asli.index('\n]\n', i) + 3
diubah = asli[:i] + uji_palsu + asli[j:]
diubah = diubah.replace('BATAS_GRUP = 150', 'BATAS_GRUP = 8')

(TMP / 'gerbang_uji.py').write_text(diubah, encoding='utf-8')

print('=' * 72)
print(' BUKTI: batas waktu grup BENAR-BENAR menghentikan grup menggantung')
print('=' * 72)
print(f'  BATAS_GRUP dipaksa jadi 8 detik (asli 150)\n')

import time
t0 = time.time()
p = subprocess.run([str(PY), str(TMP / 'gerbang_uji.py')], cwd=str(TMP),
                   capture_output=True, text=True, timeout=120)
dt = time.time() - t0

print(p.stdout)
if p.stderr.strip():
    print('  --- stderr ---')
    print(p.stderr[:500])

print('=' * 72)
ok_tidur = 'TIMEOUT' in p.stdout or 'LEWAT BATAS' in p.stdout
ok_cepat = 'LULUS' in p.stdout
ok_exit = p.returncode != 0
ok_cepat_selesai = dt < 60

print(f'  {"✅" if ok_cepat else "❌"} uji cepat tetap dinilai LULUS')
print(f'  {"✅" if ok_tidur else "❌"} uji tidur dihentikan (TIMEOUT dilaporkan)')
print(f'  {"✅" if ok_exit else "❌"} gerbang EXIT != 0 (tidak lolos diam-diam)')
print(f'  {"✅" if ok_cepat_selesai else "❌"} gerbang SELESAI dalam {dt:.1f} detik '
      f'(tidak menunggu 200 detik)')
print('=' * 72)

shutil.rmtree(TMP, ignore_errors=True)
sys.exit(0 if (ok_tidur and ok_cepat and ok_exit and ok_cepat_selesai) else 1)
