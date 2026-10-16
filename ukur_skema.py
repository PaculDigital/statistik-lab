#!/usr/bin/env python3
"""UKUR: apakah kode yang jalan di browser = kode yang Wulan tulis?

🎯 KENAPA INI PERLU:
   3 versi perbaikan berturut-turut menghasilkan hasil VISUAL IDENTIK.
   Aturan Wulan: "hasil identik = perubahan tidak berpengaruh". Jadi ada
   kemungkinan besar berkas mesin_skema.js yang DIBACA BROWSER BUKAN yang
   Wulan tulis (mis. browser cache, atau SVG di-render sebelum skrip masuk).

CARA UKUR (bukan tebak):
   1. Baca variabel global di browser: apakah fungsi `gambarSkema` versi baru?
   2. Cetak SVG HASIL RENDER untuk 1 model, hitung: ada berapa <rect putih>
      (latar label) dan berapa <ellipse>?
   3. Bandingkan dengan jumlah yang SEHARUSNYA.
"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

import websocket

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
PORT = 9337
BASE = Path(__file__).resolve().parent
HAL = BASE / '_arsip' / 'uji_mesin_skema.html'


def main() -> int:
    proses = subprocess.Popen([
        CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
        '--hide-scrollbars', '--remote-allow-origins=*',
        f'--remote-debugging-port={PORT}', '--window-size=1200,900',
        'about:blank',
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    url = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(
                    f'http://127.0.0.1:{PORT}/json/list', timeout=2) as r:
                for t in json.load(r):
                    if t.get('type') == 'page':
                        url = t['webSocketDebuggerUrl']
                        break
            if url:
                break
        except Exception:                                   # noqa: BLE001
            pass
        time.sleep(0.5)
    if not url:
        print('❌ Chrome tidak siap')
        proses.kill()
        return 1

    n = 0
    ws = websocket.create_connection(url, timeout=30)

    def kirim(metode, **kw):
        nonlocal n
        n += 1
        ws.send(json.dumps({'id': n, 'method': metode, 'params': kw}))
        while True:
            d = json.loads(ws.recv())
            if d.get('id') == n:
                return d.get('result', {})

    def js(expr):
        r = kirim('Runtime.evaluate', expression=expr, returnByValue=True,
                  awaitPromise=True)
        return r.get('result', {}).get('value')

    kirim('Page.enable')
    kirim('Runtime.enable')
    kirim('Page.navigate', url=f'file://{HAL}')
    time.sleep(1.5)

    print('═' * 72)
    print('  UKUR: kode yang JALAN di browser vs kode yang WULAN tulis')
    print('═' * 72)

    # 1) apakah berkas terbaca (bukan versi cache)?
    ok_fn = js("typeof gambarSkema")
    print(f'  1. fungsi gambarSkema ada?      {ok_fn}')

    # 2) apakah patch label v3 ADA di sumber yang dibaca browser?
    src = js("(function(){var t='';var s=document.querySelectorAll('script');"
             "for(var i=0;i<s.length;i++){if(s[i].src&&s[i].src.indexOf('mesin_skema')>=0)"
             "{return s[i].src;}}return 'inline';})()")
    print(f'  2. sumber skrip                  {src}')

    # 3) panggil mesin langsung untuk 1 model mediasi, hitung isi SVG
    uji = """
    (function(){
      var sp=[
        {id:'x', nama:'Jam Belajar', peran:'x', simbol:'X'},
        {id:'z', nama:'Kebiasaan', peran:'m', simbol:'Z'},
        {id:'y', nama:'Nilai Ujian', peran:'y', simbol:'Y'}];
      var pn=[
        {dari:'x', ke:'z', jenis:'langsung', labelUtama:'PL = X,Z'},
        {dari:'z', ke:'y', jenis:'langsung', labelUtama:'PL = Z,Y'},
        {dari:'x', ke:'y', jenis:'langsung', labelUtama:'PL = X,Y'},
        {dari:'x', ke:'y', jenis:'taklangsung', labelUtama:'PT = X,Z,Y'}];
      var d=gambarSkema(sp,pn,{lebar:900,judul:'UJI',tampilkanAngka:true});
      var svg=d.svg||'';
      return JSON.stringify({
        adaRectPutih : (svg.match(/<rect[^>]*fill="#FFFFFF"/g)||[]).length,
        jumlahEllipse: (svg.match(/<ellipse/g)||[]).length,
        jumlahText   : (svg.match(/<text/g)||[]).length,
        jumlahPath   : (svg.match(/<path/g)||[]).length,
        panjangSvg   : svg.length
      });
    })()
    """
    hasil = js(uji)
    print(f'  3. hasil render 1 model mediasi:')
    if hasil:
        d = json.loads(hasil)
        for k, v in d.items():
            print(f'       {k:16} = {v}')
        print()
        print('  ── PENILAIAN ──')
        print(f'     label ada 4 → kotak putih harus 4  : {d["adaRectPutih"]}')
        print(f'     elips harus 3                       : {d["jumlahEllipse"]}')
        if d['adaRectPutih'] == 0:
            print('     ❌ TIDAK ADA kotak putih → patch label v3 TIDAK JALAN')
        elif d['adaRectPutih'] >= 4:
            print('     ✅ kotak putih ADA → patch label v3 JALAN')
            print('        (kalau gambar tetap tumpuk, masalahnya BUKAN di sini)')
    else:
        print('     ❌ gagal memanggil gambarSkema')

    ws.close()
    proses.kill()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
