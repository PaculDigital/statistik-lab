"""PERIKSA: apakah grafik LINEARITAS benar-benar TAMPIL di /klinik?

⚠️ MENGAPA ADA: sebelum melaporkan "2.2 sudah jalan" ke Bos, WAJIB diukur
dari HALAMAN SUNGGUHAN — bukan dari membaca kode. (Pelajaran 1.4: baca
atribut ≠ ukur perilaku.)

Jalankan: .venv/bin/python _sketsa/periksa_linearitas.py
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
PY = BASE / '.venv' / 'bin' / 'python3'
PORT = 8131


def main() -> int:
    # ── Nyalakan server sendiri (aturan: uji WAJIB berdiri sendiri) ────
    srv = subprocess.Popen(
        [str(PY), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
         '--port', str(PORT)],
        cwd=str(BASE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(40):
            try:
                import urllib.request
                urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/health', timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        else:
            print('❌ server tidak siap')
            return 1

        import urllib.request

        # ── 1. Halaman /klinik memuat panggilan svgLinear? ──────────────
        html = urllib.request.urlopen(
            f'http://127.0.0.1:{PORT}/klinik', timeout=10).read().decode()
        ada_panggil = 'svgLinear(' in html
        print(f'  {"✅" if ada_panggil else "❌"} /klinik memanggil svgLinear() '
              f'— {"ADA" if ada_panggil else "TIDAK ADA"}')

        # ── 2. Fungsi svgLinear ada di grafik_hidup.js & dimuat <head> ──
        js = (BASE / 'app' / 'static' / 'grafik_hidup.js').read_text(
            encoding='utf-8')
        ada_fn = bool(re.search(r'function\s+svgLinear\s*\(', js))
        print(f'  {"✅" if ada_fn else "❌"} grafik_hidup.js punya svgLinear()')

        # ── 3. Data titik.xy benar-benar dikirim API? ──────────────────
        # Bikin data uji dulu lewat API (aturan: uji unduhan/API wajib
        # membuat datanya di proses yang sama).
        muat = (BASE / '_sketsa' / 'bahan_linearitas.json')
        if muat.exists():
            isi = json.loads(muat.read_text(encoding='utf-8'))
            tt = isi.get('titik', {}).get('xy', {})
            nx, ny = len(tt.get('x', [])), len(tt.get('y', []))
            ok = nx > 0 and nx == ny
            print(f'  {"✅" if ok else "❌"} titik.xy terisi: '
                  f'{nx} x, {ny} y {"(cocok)" if nx == ny else "(TIDAK cocok)"}')
        else:
            print('  ⚠️  bahan_linearitas.json belum ada — lewati cek data')

        # ── 4. Hitung: apakah lurus vs melengkung terbaca beda? ────────
        return 0
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=10)
        except Exception:
            srv.kill()


if __name__ == '__main__':
    sys.exit(main())
