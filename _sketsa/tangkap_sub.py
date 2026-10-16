"""Tangkapan layar sub-pilihan Regresi (HP 390px) — untuk verifikasi mata."""
import base64, json, sys, time, urllib.request
sys.path.insert(0, '.')
from uji_jalur_tampilan import Tab

CDP = 'http://127.0.0.1:9333'
URL = 'https://statistik.bikinaja.id/kuantitatif'

daftar = json.load(urllib.request.urlopen(f'{CDP}/json/list', timeout=10))
hal = [t for t in daftar if t.get('type') == 'page']
t = Tab(hal[0]['webSocketDebuggerUrl'])
t.kirim('Page.enable')
t.kirim('Runtime.enable')
t.kirim('Emulation.setDeviceMetricsOverride',
        {'width': 390, 'height': 844, 'deviceScaleFactor': 2, 'mobile': True})
t.kirim('Page.navigate', {'url': URL})
time.sleep(6)

def simpan(nama):
    r = t.kirim('Page.captureScreenshot', {'format': 'png'})
    b64 = r.get('result', {}).get('data')
    if not b64:
        print(f"  ❌ {nama}: tangkapan GAGAL (data kosong)"); return
    p = f'/tmp/{nama}.png'
    open(p, 'wb').write(base64.b64decode(b64))
    import os
    uk = os.path.getsize(p)
    print(f"  {'✅' if uk > 10000 else '❌'} {p}  ({uk} byte)")

# 1. keadaan awal (4 kartu induk)
simpan('sub1_induk')

# 2. setelah klik kartu induk MODERASI
t.kirim('Runtime.evaluate', {'expression': 'document.querySelector(\'[data-induk="moderasi"]\').click()', 'returnByValue': True})
time.sleep(2)
simpan("sub4_moderasi")
t.s.close()
