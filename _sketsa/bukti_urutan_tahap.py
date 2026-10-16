"""BUKTIKAN: penjaga URUTAN TAHAP di sot.py BENAR-BENAR BERGIGI.

ATURAN BOS 20Sep26: "GERBANG WAJIB DIUJI BISA GAGAL".
Gerbang yang tak bisa gagal = tidak menjaga apa pun.

CARA: buat SALINAN repo mini berisi:
  - sot.py ASLI (bukan disalin ulang — supaya yang diuji kode yang dipakai)
  - MASTER_PLAN.md & TAHAP_PENYELESAIAN.md dalam 3 KEADAAN:
      (1) SEHAT        → harus EXIT 0
      (2) TAHAP 4 & 5 TERTUKAR (Ujian ⇄ Pemilih alat) → harus EXIT ≠ 0
      (3) TAHAP 6 & 7 TERTUKAR (Kualitatif ⇄ Login)   → harus EXIT ≠ 0

Jalankan: .venv/bin/python _sketsa/bukti_urutan_tahap.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PY = BASE / '.venv' / 'bin' / 'python3'


def _salinan(ttd: str, mp: str, tp: str) -> Path:
    """Buat repo mini: sot.py asli + 2 dokumen sesuai teks yang diberikan.

    ⚠️ CACAT SKRIP YANG DITUTUP (20Sep26): salinan mini ini TIDAK punya
    `gerbang_uji.py`, jadi `sot.py` menghitung 0 grup dan MELAPORKAN
    "MASTER_PLAN menyebut 31 grup, kode punya 0" → SEHAT pun jadi EXIT 1.
    Itu BUKAN cacat penjaga urutan tahap. Perbaikan: salin `gerbang_uji.py`
    yang ASLI ke salinan, supaya jumlah grupnya benar-benar terhitung.
    """
    d = Path(tempfile.mkdtemp(prefix=f'buktitahap_{ttd}_'))
    for sub in ('app', 'app/hitung'):
        (d / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy2(BASE / 'sot.py', d / 'sot.py')
    # jumlah grup WAJIB terhitung — kalau tidak, penjaga lain ikut marah
    if (BASE / 'gerbang_uji.py').exists():
        shutil.copy2(BASE / 'gerbang_uji.py', d / 'gerbang_uji.py')
    # symlink venv supaya `PY` yang dicari sot.py ada
    vv = d / '.venv' / 'bin'
    vv.mkdir(parents=True, exist_ok=True)
    (vv / 'python3').symlink_to(PY)
    (d / 'MASTER_PLAN.md').write_text(mp, encoding='utf-8')
    (d / 'TAHAP_PENYELESAIAN.md').write_text(tp, encoding='utf-8')
    return d


def _jalankan(d: Path) -> tuple[int, str]:
    p = subprocess.run([str(PY), 'sot.py', '--periksa'], cwd=str(d),
                       capture_output=True, text=True, timeout=120)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def _tukar(teks: str, a: str, b: str) -> str:
    """Tukar posisi dua kata kunci tahap di dalam teks (untuk menyuntik cacat)."""
    return teks.replace(a, '@@A@@').replace(b, '@@B@@') \
               .replace('@@A@@', b).replace('@@B@@', a)


def main() -> int:
    print('=' * 74)
    print(' BUKTI: penjaga URUTAN TAHAP bisa GAGAL')
    print('=' * 74)
    print()

    mp_asli = (BASE / 'MASTER_PLAN.md').read_text(encoding='utf-8')
    tp_asli = (BASE / 'TAHAP_PENYELESAIAN.md').read_text(encoding='utf-8')

    gagal_total = 0

    # ── 1. SEHAT — harus EXIT 0 ─────────────────────────────────────────
    d = _salinan('sehat', mp_asli, tp_asli)
    kode, kel = _jalankan(d)
    ok = (kode == 0)
    print(f'  {"✅" if ok else "❌"} SEHAT            EXIT={kode}  (harus 0)')
    if not ok:
        print('     ' + kel.strip().splitlines()[-1][:120])
        gagal_total += 1

    # ── 2. TAHAP 4 ⇄ 5 TERTUKAR di MASTER_PLAN ─────────────────────────
    mp_rusak = _tukar(mp_asli, 'Pemilih alat', 'Ujian (individual/kelompok)')
    d = _salinan('tukar45', mp_rusak, tp_asli)
    kode, kel = _jalankan(d)
    ok = (kode != 0)
    print(f'  {"✅" if ok else "❌"} TUKAR T4⇄T5      EXIT={kode}  (harus ≠ 0)')
    if not ok:
        print('     GERBANG LOLOS — cacat TIDAK tertangkap!')
        gagal_total += 1
    else:
        baris = [b.strip() for b in kel.splitlines() if 'BERTENTANGAN' in b
                 or 'terbalik' in b]
        print(f'     → {baris[0][:100] if baris else "(ada masalah dilaporkan)"}')

    # ── 3. TAHAP 6 ⇄ 7 TERTUKAR di TAHAP_PENYELESAIAN ──────────────────
    tp_rusak = _tukar(tp_asli, 'MODUL KUALITATIF', 'LOGIN + PENUTUP')
    d = _salinan('tukar67', mp_asli, tp_rusak)
    kode, kel = _jalankan(d)
    ok = (kode != 0)
    print(f'  {"✅" if ok else "❌"} TUKAR T6⇄T7      EXIT={kode}  (harus ≠ 0)')
    if not ok:
        print('     GERBANG LOLOS — cacat TIDAK tertangkap!')
        gagal_total += 1
    else:
        baris = [b.strip() for b in kel.splitlines() if 'BERTENTANGAN' in b
                 or 'terbalik' in b]
        print(f'     → {baris[0][:100] if baris else "(ada masalah dilaporkan)"}')

    print()
    print('=' * 74)
    if gagal_total == 0:
        print('  ✅ PENJAGA BERGIGI — cacat tertangkap, sehat tetap EXIT 0.')
        return 0
    print(f'  ❌ {gagal_total} pemeriksaan GAGAL — penjaga TIDAK bergigi.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
