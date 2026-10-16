"""Lacak LIVE di peramban: kenapa #tab-3 tidak membuka tabnya."""
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
        return {'__galat': res['exceptionDetails'].get('text'),
                'desc': (res['exceptionDetails'].get('exception') or {}).get('description', '')[:400]}
    return res.get('result', {}).get('value')


try:
    cmd('Page.enable')
    cmd('Runtime.enable')
    cmd('Page.navigate', url=BASE + '/belajar#tab-3')
    time.sleep(4)

    print('  ── 1. elemen-elemen penting: ADA di DOM? ──')
    print('   ', js("""
    ({tab3: !!document.getElementById('tab-3'),
      pa3: !!document.getElementById('pa-3'),
      tab2: !!document.getElementById('tab-2'),
      bukaTab: typeof bukaTab,
      hash: location.hash})
    """))

    print('\n  ── 2. apa yang terjadi pada tab-3? (keadaan sekarang) ──')
    print('   ', js("""
    (() => {
      const p3 = document.getElementById('tab-3');
      if (!p3) return 'TAB-3 TIDAK ADA DI DOM';
      const gaya = getComputedStyle(p3);
      return {hiddenAttr: p3.hidden, display: gaya.display,
              tinggi: p3.getBoundingClientRect().height,
              ortu: p3.parentElement ? p3.parentElement.tagName + '.' + p3.parentElement.className : null,
              diDalamMain: !!p3.closest('main'),
              diDalamTabLain: !!p3.closest('#tab-1, #tab-2')};
    })()
    """))

    print('\n  ── 3. coba panggil bukaTab(3) manual ──')
    print('   ', js("""
    (() => {
      try { bukaTab(3); } catch(e) { return 'GALAT: ' + e; }
      const p3 = document.getElementById('tab-3');
      const pa3 = document.getElementById('pa-3');
      return {tab3Tampil: !p3.hidden, pa3Aktif: pa3.classList.contains('aktif'), hash: location.hash};
    })()
    """))

    print('\n  ── 4. kalau manual JALAN → masalahnya pemanggilan saat muat ──')
    print('     (skrip pemanggil ada di bawah, cek apakah dieksekusi)')
    print('   ', js("""
    (() => {
      const p3 = document.getElementById('tab-3');
      p3.hidden = true;              // reset
      document.getElementById('pa-3').classList.remove('aktif');
      // jalankan ulang logika pemuat hash
      const m = (location.hash || '').match(/tab-([123])/);
      return {hash: location.hash, cocok: m ? m[1] : null,
              tab3SetelahLogika: !p3.hidden};
    })()
    """))

    print('\n  ── 5. APA isi tab-3 sebenarnya? (induknya siapa) ──')
    print('   ', js("""
    (() => {
      const p3 = document.getElementById('tab-3');
      const jalan = [];
      let e = p3;
      while (e && e.tagName !== 'BODY') {
        jalan.push(e.tagName + (e.id ? '#' + e.id : '') + (e.className ? '.' + String(e.className).split(' ')[0] : ''));
        e = e.parentElement;
      }
      return jalan;
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
