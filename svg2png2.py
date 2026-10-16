#!/usr/bin/env python3
"""svg2png2.py — render SVG -> PNG memakai ukuran VIEWBOX (bukan
getBoundingClientRect).

🚨 JEBAKAN terukur 18Sep26: `/tmp/svg2png.py` membaca
`document.querySelector('svg').getBoundingClientRect()` — untuk SVG
file://, SVG melebar 100% lebar jendela → hasil 1584 px padahal viewBox
470. Akibat: gambar tampak "gepeng"/salah rasio.
Cara benar: pakai width/height dari viewBox (atau atribut width/height).
"""
import base64
import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

CHROME = ('/opt/data/home/.cloakbrowser/'
          'chromium-146.0.7680.177.5/chrome')
PORT = 9352
svg = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()

# ukuran dari viewBox
teks = svg.read_text(encoding='utf-8')
vb = re.search(r'viewBox="([\d.\s-]+)"', teks)
if not vb:
    raise SystemExit('SVG tanpa viewBox')
_, _, w, h = [float(x) for x in vb.group(1).split()]
w, h = int(w), int(h)
print(f'viewBox {w}x{h}')

p = subprocess.Popen(
    [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
     '--hide-scrollbars', '--remote-allow-origins=*',
     f'--remote-debugging-port={PORT}',
     f'--window-size={w + 40},{h + 40}', 'about:blank'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws = None
for _ in range(60):
    try:
        with urllib.request.urlopen(
                f'http://127.0.0.1:{PORT}/json/list', timeout=2) as r:
            for t in json.load(r):
                if t.get('type') == 'page':
                    ws = t['webSocketDebuggerUrl']
                    break
        if ws:
            break
    except Exception:
        pass
    time.sleep(0.5)

c = websocket.create_connection(ws, timeout=30)
n = [0]


def k(m, **kw):
    n[0] += 1
    c.send(json.dumps({'id': n[0], 'method': m, 'params': kw}))
    while True:
        d = json.loads(c.recv())
        if d.get('id') == n[0]:
            return d.get('result', {})


k('Page.enable')
k('Runtime.enable')
k('Page.navigate', url=f'file://{svg}')
time.sleep(1.2)
# paksa ukuran persis viewBox (cegah SVG melar 100%)
k('Runtime.evaluate', expression=(
    "const s=document.querySelector('svg');"
    f"s.setAttribute('width','{w}');s.setAttribute('height','{h}');"
    "s.style.margin='0';document.body.style.margin='0';"))
time.sleep(0.3)
k('Emulation.setDeviceMetricsOverride', width=w + 20, height=h + 20,
  deviceScaleFactor=2, mobile=False)
time.sleep(0.5)
r = k('Page.captureScreenshot', format='png', captureBeyondViewport=True)
out.write_bytes(base64.b64decode(r['data']))
c.close()
p.terminate()
print(f'{out} ({out.stat().st_size} byte) {w}x{h}')
