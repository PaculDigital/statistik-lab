"""UKUR lanjutan: cara melepas Chrome supaya PPID = 1 (diadopsi init).

TEMUAN percobaan-1 (terukur): `subprocess.Popen(start_new_session=True)`
→ CDP hidup saat skrip masih jalan, tapi PPID = 52642 (= skrip Python-nya
sendiri, karena Chrome jadi anaknya). Begitu skrip selesai → Chrome MATI.
⇒ `start_new_session` saja BELUM cukup. Pemilik sebenarnya adalah si skrip.

Uji 3 cara lanjutan yang benar-benar melepas:
  W1: fork → anak jadi session leader → fork LAGI → induk langsung keluar
      (double-fork klasik; anak diadopsi init → PPID 1)
  W2: W1 + setsid() di anak (memastikan session baru)
  W3: pakai `subprocess.Popen(..., start_new_session=True)` LALU
      `os._exit(0)` di induk cepat — pembanding

Diukur: PPID hasil, CDP hidup, dan apakah TAHAN 5 detik setelah skrip keluar.
"""
import json
import os
import subprocess
import sys
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
                return isi[3]
            except Exception:                              # noqa: BLE001
                return '?'
    return '-'


# ── W1/W2: double-fork — anak sungguhan, induk keluar ────────────────────
PIDFILE = '/tmp/ukur_doublefork.pid'


def spawn_double_fork(port: int, pakai_setsid: bool) -> int:
    """Jalankan Chrome lewat 2 fork; induk keluar → anak diadopsi init."""
    pid1 = os.fork()
    if pid1 > 0:
        # Induk asli: tunggu anak pertama (yang cuma jadi perantara), lalu keluar
        os.waitpid(pid1, 0)
        return 0

    # ── anak pertama ────────────────────────────────────────────────────
    if pakai_setsid:
        os.setsid()
    pid2 = os.fork()
    if pid2 > 0:
        os._exit(0)          # perantara keluar → cucu diadopsi init

    # ── cucu: dia yang menjalankan Chrome ───────────────────────────────
    os.chdir('/')
    hantu = f'/tmp/ukur_df_{port}'
    args = [CHROME] + BENDERA + [f'--remote-debugging-port={port}',
                                 f'--user-data-dir={hantu}']
    subprocess.Popen(args, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(PIDFILE, 'w') as f:
        f.write(str(os.getpid()))
    os._exit(0)


def ukur(nama: str, port: int, pakai_setsid: bool) -> dict:
    print(f'\n{"=" * 70}\n  {nama}  (port {port})\n{"=" * 70}')
    os.system('rm -f ' + PIDFILE)
    anak = os.fork()
    if anak == 0:
        spawn_double_fork(port, pakai_setsid)
        os._exit(0)
    os.waitpid(anak, 0)                  # tunggu fork pertama saja

    hidup = False
    for _ in range(16):
        time.sleep(1)
        if cdp_hidup(port):
            hidup = True
            break
    ppid = ppid_dari(port)
    print(f'  CDP hidup     : {hidup}')
    print(f'  PPID (saat ini): {ppid}   ← HARUS 1')
    return {'nama': nama, 'port': port, 'hidup': hidup, 'ppid': ppid}


print('=' * 70)
print('  UKUR LANJUTAN: DOUBLE-FORK → PPID 1')
print('=' * 70)

hasil = []
hasil.append(ukur('W1  double-fork (fork→fork→keluar)', 9461, False))
hasil.append(ukur('W2  double-fork + setsid', 9462, True))

with open('/tmp/ukur_lepas_hasil.json', 'w') as f:
    json.dump(hasil, f, indent=2)

print('\n' + '=' * 70)
print('  RINGKASAN (saat skrip MASIH jalan)')
print('=' * 70)
for h in hasil:
    print(f'{h["nama"]:<40} hidup={h["hidup"]}  PPID={h["ppid"]}')
print('\nYang menang = hidup=True DAN PPID=1.')
print('Bukti TAHAN diuji setelah skrip ini selesai (perintah terpisah).')
sys.stdout.flush()
