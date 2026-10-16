"""BUKTI gerbang_bahasa.py BERGIGI + bukti komentar Jinja tidak lagi dihitung.

Aturan induk proyek: setiap GERBANG wajib terbukti BISA GAGAL. Gerbang yang
tak bisa gagal tidak menjaga apa pun.

Bukti yang dijalankan:
  1. SEHAT        → gerbang pada berkas asli harus EXIT 0
  2. CACAT SUNCIK → sisipkan kata terlarang ke TEKS TAMPIL → HARUS EXIT 1
  3. KOMENTAR {# #} → sisipkan kata terlarang HANYA di komentar Jinja → HARUS
     EXIT 0 (komentar hilang saat render; menuuduh = gagal palsu)
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

AKAR = Path('/opt/data/services/statistik-lab')
PY = str(AKAR / '.venv' / 'bin' / 'python')
BERKAS = AKAR / 'app' / 'templates' / 'buat_data.html'
CADANGAN = AKAR / '_sketsa' / 'buat_data_cadangan.html'


def jalankan() -> int:
    r = subprocess.run([PY, 'gerbang_bahasa.py'], cwd=AKAR,
                       capture_output=True, text=True, timeout=120)
    return r.returncode


def main() -> int:
    asli = BERKAS.read_text(encoding='utf-8')
    shutil.copy2(BERKAS, CADANGAN)
    lulus = gagal = 0

    def catat(ok: bool, teks: str, tambahan: str = '') -> None:
        nonlocal lulus, gagal
        if ok:
            lulus += 1
            print(f'  ✅ {teks}' + (f'   {tambahan}' if tambahan else ''))
        else:
            gagal += 1
            print(f'  ❌ {teks}' + (f'   {tambahan}' if tambahan else ''))

    try:
        # ── 1. SEHAT ────────────────────────────────────────────────────
        catat(jalankan() == 0, 'SEHAT: berkas asli LOLOS gerbang bahasa')

        # ── 2. CACAT DI TEKS TAMPIL → HARUS GAGAL ──────────────────────
        # 'pagar' = kata terlarang (Bos pernah bertanya). Sisipkan sebagai
        # teks yang BENAR-BENAR tampil (di dalam <p>, bukan komentar).
        cacat = asli.replace(
            '<h2 style="margin:6px 0 4px">Kelompok mana yang mau dibandingkan?',
            '<h2 style="margin:6px 0 4px">Pagar kelompok mana yang mau '
            'dibandingkan?', 1)
        catat(cacat != asli, 'cacat buatan tertanam di teks tampil')
        BERKAS.write_text(cacat, encoding='utf-8')
        catat(jalankan() != 0, 'CACAT di teks tampil → gerbang MENOLAK (EXIT≠0)')

        # ── 3. KATA TERLARANG HANYA DI KOMENTAR JINJA → HARUS LOLOS ────
        # Pelajaran 22Sep26: komentar {# #} HILANG saat render — menuuduh
        # halaman karena isi komentar = gagal PALSU.
        komentar = asli.replace(
            '  <div id="panel-manova" class="sembunyi">',
            '  {# catatan desain: ini pagar jujur untuk beda kelompok #}\n'
            '  <div id="panel-manova" class="sembunyi">', 1)
        catat(komentar != asli, 'kata terlarang tertanam HANYA di komentar Jinja')
        BERKAS.write_text(komentar, encoding='utf-8')
        catat(jalankan() == 0,
              'komentar Jinja TIDAK dihitung sebagai teks tampil (EXIT 0)')
    finally:
        shutil.copy2(CADANGAN, BERKAS)
        CADANGAN.unlink(missing_ok=True)

    # pastikan berkas kembali utuh
    catat(BERKAS.read_text(encoding='utf-8') == asli,
          'berkas dikembalikan UTUH seperti semula')

    print()
    print('=' * 70)
    if gagal:
        print(f' ❌ {gagal} GAGAL  (lulus {lulus}) — gerbang TIDAK sehat')
        return 1
    print(f' ✅ {lulus} LULUS / 0 GAGAL — gerbang BERGIGI & tidak gagal palsu')
    return 0


if __name__ == '__main__':
    sys.exit(main())
