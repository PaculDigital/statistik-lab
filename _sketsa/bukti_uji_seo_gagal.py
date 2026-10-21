"""Bukti uji_seo.py BERGIGI: suntik kerusakan ke SALINAN, uji HARUS gagal.

Pelajaran (skill statistik-lab, jebakan uji #1):
  jalankan dengan .venv dari SALINAN + cwd=SALINAN, jangan jalur absolut —
  kalau tidak, suntikan tak pernah terpakai dan uji tampak "buta".
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ASLI = Path(__file__).resolve().parent.parent
PERLU = ['app', 'uji_seo.py']
PORT = 8199


def siapkan(tmp: Path) -> None:
    for n in PERLU:
        s = ASLI / n
        if s.is_dir():
            shutil.copytree(s, tmp / n,
                            ignore=shutil.ignore_patterns('__pycache__'))
        elif s.exists():
            shutil.copy2(s, tmp / n)


def tunggu() -> bool:
    for _ in range(60):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{PORT}/health', timeout=3)
            return True
        except Exception:  # noqa: BLE001
            import time
            time.sleep(0.5)
    return False


def jalankan(tmp: Path) -> tuple[int, str]:
    import os
    env = dict(os.environ, BASE_UJI=f'http://127.0.0.1:{PORT}')
    srv = subprocess.Popen(
        [str(ASLI / '.venv' / 'bin' / 'python'), '-m', 'uvicorn',
         'app.main:app', '--host', '127.0.0.1', '--port', str(PORT),
         '--log-level', 'warning'], cwd=str(tmp),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if not tunggu():
            return 99, 'server uji tidak hidup'
        r = subprocess.run(
            [str(ASLI / '.venv' / 'bin' / 'python'), 'uji_seo.py'],
            cwd=str(tmp), capture_output=True, text=True, timeout=300, env=env)
        return r.returncode, r.stdout + r.stderr
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=15)
        except subprocess.TimeoutExpired:
            srv.kill()


def main() -> int:
    lulus = gagal = 0

    def cek(nama: str, tertangkap: bool, keluaran: str) -> None:
        nonlocal lulus, gagal
        if tertangkap:
            lulus += 1
            print(f'LULUS  : {nama} — tertangkap')
        else:
            gagal += 1
            print(f'GAGAL  : {nama} — LOLOS, padahal harus ditangkap')
            print('         ' + keluaran.strip()[-260:].replace('\n', '\n         '))

    # 0. DASAR: salinan bersih harus lulus
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        rc, out = jalankan(tmp)
        if rc == 0:
            lulus += 1
            print('LULUS  : salinan bersih → uji SEO hijau (EXIT 0)')
        else:
            gagal += 1
            print(f'GAGAL  : salinan bersih malah gagal (rc={rc})')
            print(out[-400:])

    # 1. favicon dihapus
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        (tmp / 'app' / 'static' / 'favicon.svg').unlink()
        rc, out = jalankan(tmp)
        cek('favicon.svg dihapus', rc != 0 and 'favicon' in out.lower(), out)

    # 2. meta description dibuang
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        p = tmp / 'app' / 'templates' / 'dasar.html'
        t = p.read_text()
        t = t.replace('<meta name="description"', '<!-- mati --><meta name="x"', 1)
        p.write_text(t)
        rc, out = jalankan(tmp)
        cek('meta description dibuang',
            rc != 0 and 'meta description' in out.lower(), out)

    # 3. sitemap tidak mendaftar halaman siap
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        siapkan(tmp)
        p = tmp / 'app' / 'main.py'
        t = p.read_text().replace(
            "jalur = ['/'] + [f'/{m[\"slug\"]}' for m in MODUL if m.get('siap')]",
            "jalur = ['/']", 1)
        p.write_text(t)
        rc, out = jalankan(tmp)
        cek('sitemap kosong (cuma beranda)',
            rc != 0 and 'halaman siap' in out.lower(), out)

    print(f'\nHASIL: {lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
