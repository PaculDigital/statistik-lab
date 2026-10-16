"""Buktikan: kegagalan uji #tab-3 = UJI WULAN TERLALU CEPAT, bukan cacat app."""
import json
import time
import urllib.request

import websocket

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'

t = json.loads(urllib.request.urlopen(urllib.request.Request(
    f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'), timeout=20).read())
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90)
n = [0]


def cmd(m, **p):
    n[0] += 1
    ws.send(json.dumps({'id': n[0], 'method': m, 'params': p}))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == n[0]:
            return r


def js(e):
    r = cmd('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
    res = r.get('result', {})
    if res.get('exceptionDetails'):
        return {'__galat': res['exceptionDetails'].get('text')}
    return res.get('result', {}).get('value')


try:
    cmd('Page.enable')
    cmd('Runtime.enable')

    print('  ── UKUR: berapa lama tab-3 muncul setelah halaman selesai? ──')
    cmd('Page.navigate', url=BASE + '/belajar#tab-3')
    for tunggu in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0):
        time.sleep(tunggu if tunggu == 0.5 else 0.5)
        v = js("(() => {const p=document.getElementById('tab-3');"
               "return p ? {ada:true, tampil: !p.hidden} : {ada:false};})()")
        print(f'     setelah ~{tunggu:.1f}s : {v}')

    print()
    print('  ── sekarang tunggu PASTI cukup (3 dtk penuh) ──')
    time.sleep(3)
    print('   ', js("""
    (() => {
      const p3 = document.getElementById('tab-3');
      return {tab3Tampil: p3 ? !p3.hidden : null,
              pa3Aktif: document.getElementById('pa-3').classList.contains('aktif'),
              hash: location.hash};
    })()
    """))
finally:
    try:
        ws.close()
    except Exception:
        pass
    try:
        urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/close/{t["id"]}'), timeout=15).read()
    except Exception:
        pass
