#!/usr/bin/env python3
"""Tangkap sketsa diagnosis + belajar tab (HP 390px) — supaya bisa DILIHAT.

⚠️ PELAJARAN 19Sep26: `Tab(ws_url)` — menerima URL websocket, BUKAN nomor port.
Dan hasil `kirim()` bentuknya {'id':.., 'result': {...}} → WAJIB `.get('result')`.
"""
import base64, json, os, sys, time, urllib.request
sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_jalur_tampilan import Tab

CDP = 'http://127.0.0.1:9444'
HAL = 'file:///opt/data/services/statistik-lab/_sketsa/'

d = json.load(urllib.request.urlopen(f'{CDP}/json/list', timeout=10))
hal = [x for x in d if x.get('type') == 'page']
t = Tab(hal[0]['webSocketDebuggerUrl'])
t.kirim('Page.enable')
t.kirim('Runtime.enable')

for nama in ['diagnosis_sketsa', 'belajar_tab_sketsa']:
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 900, 'deviceScaleFactor': 1, 'mobile': True})
    t.kirim('Page.navigate', {'url': HAL + nama + '.html'})
    time.sleep(3.5)
    h = t.kirim('Runtime.evaluate',
                {'expression': 'document.body.scrollHeight', 'returnByValue': True})
    tinggi = h.get('result', {}).get('result', {}).get('value') or 900
    print(f"  {nama}: tinggi {tinggi}px")
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': int(tinggi) + 30,
             'deviceScaleFactor': 1, 'mobile': True})
    time.sleep(2)
    r = t.kirim('Page.captureScreenshot', {'format': 'png'})
    data = r.get('result', {}).get('data')
    p = f'/tmp/{nama}.png'
    open(p, 'wb').write(base64.b64decode(data))
    uk = os.path.getsize(p)
    print(f"  {'OK ' if uk > 10000 else '⚠️ KECIL'} {p} ({uk} byte)")

t.s.close()
