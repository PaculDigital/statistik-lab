"""BUKTI: penjaga SOT (jumlah grup + pengecualian riwayat) BERGIGI.

⚠️ MENGAPA ADA (20Sep26): saat menambahkan pengecualian "blok riwayat"
(agar catatan sejarah seperti "19Sep26: 25 grup LULUS" tidak diprotes),
Wulan DUA KALI salah: (1) jendela 160 char → terlalu sempit → SOT protes
palsu; (2) jendela 700 char + pola 'keadaan 20\\d\\d' → terlalu lebar →
angka PALSU "99 grup" malah LOLOS (SOT jadi BUTA). Pelajaran: pengecualian
harus diuji-sehat DAN diuji-suntik; kalau tidak, "perbaikan" bisa mengubah
penjaga jadi hissan.

CARA KERJA: menyalin repo mini ke tmp (sot.py + gerbang_uji.py + 3 dokumen
+ app/), lalu:
  A. salinan SEHAT                         → harus EXIT 0
  B. suntik '99 grup' di MASTER_PLAN       → harus EXIT 1
  C. suntik '99 grup' di FLAG blok teratas → harus EXIT 1
  D. hapus penanda riwayat satu blok       → harus EXIT 1 (bukti tidak buta)

Jalankan: .venv/bin/python _sketsa/bukti_sot_riwayat.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PY = BASE / '.venv' / 'bin' / 'python'
BERKAS = ['sot.py', 'gerbang_uji.py', 'MASTER_PLAN.md',
          'TAHAP_PENYELESAIAN.md', 'FLAG_LANJUT_DISINI.md']
lulus = gagal = 0


def cek(nama: str, harus: str):
    """Jalankan `sot.py --periksa` di salinan; bandingkan hasilnya."""
    global lulus, gagal
    r = subprocess.run([str(PY), 'sot.py', '--periksa'],
                       capture_output=True, text=True, timeout=120)
    keluaran = (r.stdout or '') + (r.stderr or '')
    selaras = 'SOT SELARAS' in keluaran
    dapat = 'SELARAS' if selaras else 'TIDAK SELARAS'
    ok = (dapat == harus)
    tanda = '✅' if ok else '❌'
    print(f'  {tanda} {nama}')
    print(f'     harus {harus:13} → dapat {dapat}')
    if not ok:
        for b in [x for x in keluaran.splitlines() if 'menyebut' in x]:
            print(f'       {b.strip()}')
    if ok:
        lulus += 1
    else:
        gagal += 1


def _salinan() -> Path:
    """Salinan mini repo — WAJIB ikut app/ & gerbang_uji.py (dipakai
    sot.py untuk MENGHITUNG grup; tanpa itu 'kode punya 0')."""
    t = Path(tempfile.mkdtemp(prefix='ujisot_'))
    for n in BERKAS:
        shutil.copy2(BASE / n, t / n)
    shutil.copytree(BASE / 'app', t / 'app',
                    ignore=shutil.ignore_patterns('__pycache__'))
    (t / '.venv').symlink_to(BASE / '.venv')
    return t


def suntik(f: Path, lama: str, baru: str):
    t = f.read_text(encoding='utf-8')
    assert lama in t, f'penanda tidak ketemu: {lama[:60]}'
    f.write_text(t.replace(lama, baru, 1), encoding='utf-8')


print('=' * 74)
print(' BUKTI PENJAGA SOT — jumlah grup & pengecualian riwayat')
print('=' * 74)
print(f'\n kata kunci: {BASE / "sot.py"}\n')

# ── A. SEHAT ─────────────────────────────────────────────────────────────
print(' A. Salinan SEHAT (banyak blok riwayat di dalamnya)')
import os
os.chdir(_salinan())
cek('salinan utuh — riwayat SAH tidak boleh diprotes', 'SELARAS')

# ── B. klaim KINI dipalsukan (MASTER_PLAN) ───────────────────────────────
print('\n B. Angka PALSU di klaim KINI (MASTER_PLAN §Gerbang)')
suntik(Path('MASTER_PLAN.md'), '**Gerbang uji: 33 grup**',
       '**Gerbang uji: 99 grup**')
cek('suntik 99 grup (tanpa penanda riwayat)', 'TIDAK SELARAS')

# ── C. klaim KINI dipalsukan (FLAG blok teratas) ─────────────────────────
print('\n C. Angka PALSU di blok TERATAS FLAG')
suntik(Path('FLAG_LANJUT_DISINI.md'),
       '**Gerbang:** **33 grup LULUS** · SOT **SELARAS**',
       '**Gerbang:** **99 grup LULUS** · SOT **SELARAS**')
cek('suntik 99 grup di FLAG blok teratas', 'TIDAK SELARAS')

# ── D. pengecualian riwayat TIDAK buta ───────────────────────────────────
print('\n D. Cabut penanda "catatan sejarah" dari SATU blok riwayat')
os.chdir(_salinan())
cek('D1 salinan utuh dulu (pembanding)', 'SELARAS')
os.chdir(_salinan())
suntik(Path('FLAG_LANJUT_DISINI.md'),
       '> 📌 Blok ini **catatan sejarah** — angka 31 grup benar untuk saat '
       'itu (sekarang 33).\n\n', '')
cek('D2 tanpa penanda → wajib diprotes (bukti tidak buta)', 'TIDAK SELARAS')

print('\n' + '=' * 74)
print(f'  HASIL: {lulus} LULUS · {gagal} GAGAL')
print('=' * 74)
sys.exit(0 if gagal == 0 else 1)
