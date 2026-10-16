"""Tangkap bar 'Model kamu sekarang' — 2 keadaan: atas & setelah scroll."""
import base64, json, sys, time, urllib.request
sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_jalur_tampilan import Tab

CDP = 'http://127.0.0.1:9333'
d = json.load(urllib.request.urlopen(f'{CDP}/json/list', timeout=10))
hal = [x for x in d if x.get('type') == 'page']
t = Tab(hal[0]['webSocketDebuggerUrl'])
t.kirim('Page.enable'); t.kirim('Runtime.enable')
t.kirim('Emulation.setDeviceMetricsOverride',
        {'width': 390, 'height': 844, 'deviceScaleFactor': 2, 'mobile': True})

def simpan(nama):
    r = t.kirim('Page.captureScreenshot', {'format': 'png'})
    data = r.get('result', {}).get('data')
    p = f'/tmp/{nama}.png'
    open(p, 'wb').write(base64.b64decode(data))
    import os
    print(f"  {'OK ' if os.path.getsize(p) > 10000 else 'GAGAL'} {p} ({os.path.getsize(p)} byte)")

t.kirim('Page.navigate', {'url': 'https://statistik.bikinaja.id/buat-data?model=moderasi-3jalur'})
time.sleep(6)
t.kirim('Runtime.evaluate', {'expression': 'window.scrollTo(0,0)', 'returnByValue': True})
time.sleep(1)
simpan('bar1_atas')

# geser ke tengah halaman → bar harus tetap menempel
t.kirim('Runtime.evaluate', {'expression': 'window.scrollTo(0, 1400)', 'returnByValue': True})
time.sleep(1.5)
simpan('bar2_scroll')
t.s.close()
