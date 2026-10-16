"""UKUR: cara melepas Chrome dari induk (PPID 1) supaya tidak mati saat
gateway Hermes restart.

Masalah terukur 21Sep26: Chrome dijalankan lewat `terminal(background=true)`
→ PPID = 160 (Hermes gateway) → begitu gateway restart (sesi reset 04.00 UTC),
Chrome IKUT MATI → gerbang gagal 7 grup (browser), grup mesin tetap lolos.

3 variasi diuji:
  V1: subprocess.Popen biasa (tanpa start_new_session)
  V2: subprocess.Popen + start_new_session=True
  V3: subprocess.Popen + start_new_session=True + stdin/out/err DEVNULL

Yang diukur: PPID, CDP hidup?, apakah TAHAN setelah proses induk (skrip ini)
selesai → diuji dengan tidur lalu cek dari proses LAIN.
"""
import json
import os
import subprocess
import time
import urllib.request

CHROME = ('/opt/data/home/.cloakbrowser/'
          'chromium-151.0.7922.108.6-pro/chrome')
BENDERA = ['--headless=new', '--no-sandbox', '--disable-gpu',
           '--remote-allow-origins=*', '--window-size=390,900',
           '--hide-scrollbars']


def cdp_hidup(port: int) -> bool:
    try:
        with urllib.request.urlopen(
                f'http://127.0.0.1:{port}/json/version', timeout=4) as r:
            return r.status == 200
    except Exception:                                      # noqa: BLE001
        return False


def ppid_dari(port: int) -> str:
    """PPID proses chrome yang memegang `port` — dibaca dari /proc."""
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        try:
            with open(f'/proc/{pid}/cmdline', 'rb') as f:
                cmd = f.read().decode(errors='replace')
        except Exception:                                  # noqa: BLE001
            continue
        if f'remote-debugging-port={port}' in cmd and '--type=' not in cmd:
            try:
                with open(f'/proc/{pid}/stat') as f:
                    isi = f.read().split()
                return f'{isi[3]} (pid {pid})'
            except Exception:                              # noqa: BLE001
                return f'? (pid {pid})'
    return 'tidak ada'


def coba(nama: str, port: int, **popen_kw) -> dict:
    print(f'\n{"=" * 70}\n  {nama}  (port {port})\n{"=" * 70}')
    hantu = f'/tmp/ukur_lepas_{port}'
    args = [CHROME] + BENDERA + [f'--remote-debugging-port={port}',
                                 f'--user-data-dir={hantu}']
    kw = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
              stderr=subprocess.DEVNULL)
    kw.update(popen_kw)
    p = subprocess.Popen(args, **kw)
    print(f'  Popen PID {p.pid} · kw={sorted(popen_kw) or "kosong"}')

    hidup = False
    for _ in range(16):
        time.sleep(1)
        if cdp_hidup(port):
            hidup = True
            break
    ppid_awal = ppid_dari(port)
    print(f'  CDP hidup : {hidup}')
    print(f'  PPID      : {ppid_awal}   ← HARUS 1 supaya tahan restart')

    # ── Apakah tahan SESAAT setelah induk (skrip ini) masih ada? ─────────
    time.sleep(2)
    ppid_akhir = ppid_dari(port)
    hasil = {'nama': nama, 'port': port, 'hidup': hidup,
             'ppid': ppid_awal, 'ppid_akhir': ppid_akhir}
    print(f'  PPID (2s) : {ppid_akhir}')
    return hasil


print('=' * 70)
print('  UKUR: CARA MELEPAS CHROME DARI INDUK')
print('=' * 70)
print(f'PPID skrip ini: {os.getppid()} (Hermes gateway = 160?)')

hasil = []
# V1 — tanpa start_new_session (cara lama yang bikin mati)
hasil.append(coba('V1  Popen biasa (tanpa start_new_session)', 9451))
# V2 — dengan start_new_session
hasil.append(coba('V2  Popen + start_new_session=True', 9452,
                  start_new_session=True))
# V3 — + DEVNULL penuh (echo yang sudah ada di kw bawaan)
hasil.append(coba('V3  Popen + start_new_session + DEVNULL', 9453,
                  start_new_session=True))

print('\n' + '=' * 70)
print('  RINGKASAN')
print('=' * 70)
print(f'{"VARIASI":<44} {"HIDUP":<7} {"PPID"}')
for h in hasil:
    print(f'{h["nama"]:<44} {str(h["hidup"]):<7} {h["ppid"]}')

print('\nCARA BACA: yang menang = HIDUP=True DAN PPID=1.')
print('Chrome dipastikan masih hidup setelah skrip ini selesai lewat')
print('perintah terpisah (uji dari proses LAIN).')
