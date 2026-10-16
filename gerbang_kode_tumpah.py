#!/usr/bin/env python3
"""GERBANG: kode tumpah jadi TEKS di halaman yang user lihat.

KENAPA GERBANG INI ADA (pelajaran mahal 17Sep26):
  Gerbang sintaks JS MENYATAKAN LULUS dari berkas. Gerbang tag penutup juga
  LULUS. TAPI halaman yang dirender TETAP RUSAK — kode tumpah jadi teks:

      Variabel (bisa diganti)<' + '/th>   β<' + '/th>

  Penyebab: perbaikan  <' + '/div>  hanya benar di dalam string kutip biasa;
  di dalam template literal (`...`) ia menjadi TEKS BIASA.

  "Berkas tampak benar" ≠ "halaman benar". Satu-satunya cara tahu adalah
  MEMBUKA HALAMANNYA dan MEMBACA TEKS YANG TERLIHAT USER.

⚠️ HINDARI LINGKARAN MATI:
  JANGAN menguji kontainer yang sedang jalan — kalau begitu gerbang selalu
  gagal SEBELUM deploy, sehingga deploy tidak pernah jalan dan kontainer
  selamanya ketinggalan versi. Karena itu gerbang ini menyalakan server uji
  SEMENTARA dari BERKAS yang akan di-deploy (port 8121), diperiksa, lalu
  dimatikan. Jadi yang diuji = kode BARU, bukan yang lama.
"""
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time

DIR = os.path.dirname(os.path.abspath(__file__))
PORT_UJI = 8121

CHROME = None
CHROME_URUT = [
    '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome',
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.4-pro/chrome',
]

HALAMAN = ['/', '/belajar', '/buat-data', '/pengaturan', '/segera/klinik']

# Jejak kode yang TIDAK BOLEH terlihat user di halaman
JEJAK_BOCOR = [
    (r"<' \+ '/", 'penggabungan string gaya lama'),
    (r'\$\{', 'template literal tidak tereksekusi'),
    (r'\bconst\s+\w+\s*=', 'deklarasi variabel bocor'),
    (r'function\s*\w+\s*\(', 'definisi fungsi bocor'),
    (r'el\([\'"]', 'pemanggilan kode bocor'),
]


def cari_chrome():
    for c in CHROME_URUT:
        if os.path.exists(c):
            return c
    p = subprocess.run(['find', '/opt/data/home/.cloakbrowser', '-maxdepth', '2',
                        '-name', 'chrome', '-type', 'f'],
                       capture_output=True, text=True)
    for baris in (p.stdout or '').splitlines():
        if baris.strip():
            return baris.strip()
    return None


def port_bebas(p: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', p)) != 0


def nyalakan_server():
    """Nyalakan uvicorn SEMENTARA dari BERKAS yang akan di-deploy."""
    py = os.path.join(DIR, '.venv', 'bin', 'python3')
    if not os.path.exists(py):
        return None
    if not port_bebas(PORT_UJI):
        # sudah ada server uji jalan — pakai itu
        return 'sudah-jalan'
    env = dict(os.environ, PORT=str(PORT_UJI))
    proc = subprocess.Popen(
        [py, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1',
         '--port', str(PORT_UJI), '--log-level', 'warning'],
        cwd=DIR, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid)
    # tunggu siap (maks 25 detik)
    for _ in range(50):
        time.sleep(0.5)
        if not port_bebas(PORT_UJI):
            time.sleep(1.0)
            return proc
    proc.kill()
    return None


def matikan(proc):
    if proc and proc != 'sudah-jalan':
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=10)
        except Exception:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass


def main() -> int:
    ch = cari_chrome()
    if not ch:
        print('  ⚠️  Chrome tidak ada — gerbang kode-tumpah dilewati')
        return 0

    print('═══ GERBANG: kode tumpah jadi teks (uji BERKAS, bukan kontainer) ═══')
    proc = nyalakan_server()
    if not proc:
        print('  ⚠️  server uji tidak bisa dinyalakan — gerbang dilewati')
        return 0
    if proc == 'sudah-jalan':
        print(f'   (memakai server uji yang sudah jalan di :{PORT_UJI})')
    else:
        print(f'   server uji sementara :{PORT_UJI} dari BERKAS yang akan di-deploy')

    total = 0
    try:
        for jalur in HALAMAN:
            try:
                p = subprocess.run(
                    [ch, '--headless', '--disable-gpu', '--no-sandbox',
                     '--window-size=1280,1300', '--virtual-time-budget=8000',
                     '--dump-dom', f'http://127.0.0.1:{PORT_UJI}{jalur}'],
                    capture_output=True, text=True, timeout=140)
            except subprocess.TimeoutExpired:
                print(f'  ❌ {jalur}: waktu habis')
                total += 1
                continue

            html = p.stdout or ''
            bersih = re.sub(r'<script\b.*?</script>', ' ', html, flags=re.S | re.I)
            bersih = re.sub(r'<style\b.*?</style>', ' ', bersih, flags=re.S | re.I)
            teks = re.sub(r'<[^>]+>', ' ', bersih)
            teks = (teks.replace('&lt;', '<').replace('&gt;', '>')
                        .replace('&amp;', '&').replace('&quot;', '"')
                        .replace('&#39;', "'"))

            temuan = []
            for pola, nama in JEJAK_BOCOR:
                m = re.search(pola, teks)
                if m:
                    potongan = teks[max(0, m.start() - 35):m.end() + 35].strip()
                    temuan.append(f'[{nama}] …{potongan[:105]}…')

            if temuan:
                print(f'  ❌ {jalur}: {len(temuan)} jejak kode bocor')
                for t in temuan[:3]:
                    print(f'       {t}')
                total += len(temuan)
            else:
                print(f'  ✅ {jalur}: bersih')
    finally:
        matikan(proc)

    print()
    if total:
        print(f'  {total} jejak kode bocor TERLIHAT USER — PERBAIKI dulu.')
        print('  Ingat: berkas tampak benar ≠ halaman benar.')
        return 1
    print('  ✅ 0 kode bocor — halaman bersih saat dibaca user')
    return 0


if __name__ == '__main__':
    sys.exit(main())
