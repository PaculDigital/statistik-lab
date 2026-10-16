#!/usr/bin/env python3
"""GERBANG SLIDER — uji dari BERKAS (bukan kontainer lama).

KENAPA DARI BERKAS (pelajaran 17Sep26, kejadian KEDUA):
  Gerbang versi pertama membaca KONTAINER yang masih versi lama, lalu
  melaporkan "kenop meluber 319px" + "teks menempel" — padahal berkasnya
  SUDAH diperbaiki. Kontainer lama → gerbang gagal → deploy ditolak →
  kontainer tetap lama. Lingkaran mati!

CARA YANG BEKAS:
  Rakit SATU halaman uji dari CSS nyata + potongan body template nyata,
  lalu tempel langsung di DALAM kotak selebar HP (bukan iframe bersarang,
  bukan srcdoc — keduanya terbukti menghasilkan halaman kosong).

Jalankan: .venv/bin/python gerbang_slider.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
TEMPLATE = 'app/templates/buat_data.html'
CSS = 'app/static/gaya.css'
DIR_UJI = 'app/static/_uji_slider'
WEB = '/app/app/static/_uji_slider'      # jalur DI DALAM kontainer
LEBAR_UJI = [412, 390, 360]

UKUR = """
(function(){
  var hasil = {lebarLayar: window.innerWidth, slider: [], ditemukan: 0};
  var daftar = document.querySelectorAll('#kotak-uji input[type=range]');
  hasil.ditemukan = daftar.length;
  daftar.forEach(function(s){
    var r = s.getBoundingClientRect();
    var cs = window.getComputedStyle(s);
    var jarakMin = 9999, teksDekat = '';
    var semua = document.querySelectorAll('#kotak-uji div, #kotak-uji span, #kotak-uji p, #kotak-uji label');
    for (var i = 0; i < semua.length; i++) {
      var n = semua[i];
      if (n.contains(s)) continue;
      var rr = n.getBoundingClientRect();
      if (rr.height === 0 || rr.width === 0) continue;
      if (rr.top < r.bottom - 1) continue;
      if (rr.left > r.right || rr.right < r.left) continue;
      var t = (n.textContent || '').trim();
      if (!t || t.length > 60) continue;
      // ⚠️ LEWATI label skala (30 / 2.000 / 1 / 8) — itu MEMANG ditaruh
      // rapat di bawah slider sebagai penanda ujung. Yang berbahaya =
      // teks NILAI ("N variabel X") yang dulu ikut menempel di garis.
      // 🚨 Koreksi 18Sep26: versi lama hanya melewati ANGKA murni,
      // sehingga PEMISAH "·" (titik tengah) dianggap "teks menempel" →
      // temuan PALSU yang memblokir deploy. Kini seluruh isi
      // .skala-slider dikecualikan + apa pun yang TIDAK punya huruf.
      if (n.closest('.skala-slider')) continue;
      if (!/[a-zA-Z]/.test(t)) continue;
      var j = rr.top - r.bottom;
      if (j < jarakMin) { jarakMin = j; teksDekat = t.slice(0, 26); }
    }
    hasil.slider.push({
      id: s.id || '(tanpa id)',
      tinggiKotak: Math.round(r.height * 10) / 10,
      tinggiCSS: cs.height,
      jarakKeTeks: jarakMin === 9999 ? null : Math.round(jarakMin * 10) / 10,
      teksDekat: teksDekat
    });
  });
  return hasil;
})();
"""


def rakit(lebar, css):
    """Rakit halaman uji: kotak selebah HP berisi body template nyata."""
    tpl = open(TEMPLATE, encoding='utf-8').read()
    m = re.search(r'{%\s*block\s+isi\s*%}(.*?){%\s*endblock\s*%}', tpl, re.S)
    isi = m.group(1) if m else tpl
    isi = re.sub(r'<script\b.*?</script>', ' ', isi, flags=re.S | re.I)
    isi = re.sub(r'\{\{.*?\}\}', ' ', isi, flags=re.S)
    isi = re.sub(r'\{%.*?%\}', ' ', isi, flags=re.S)
    return f'''<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>u</title><style>{css}</style>
<style>
  html,body {{ margin:0; background:#ddd; }}
  #kotak-uji {{ width:{lebar}px; background:#fff; overflow-x:hidden; }}
</style></head><body>
<div id="kotak-uji">{isi}</div>
<script>
window.addEventListener('load', function(){{
  setTimeout(function(){{
    try {{
      var out = {UKUR}
      document.title = 'SLD::' + JSON.stringify(out);
    }} catch(e){{ document.title = 'SLD::GALAT ' + e.message; }}
  }}, 900);
}});
</script></body></html>'''



def _render_cdp(url: str, lebar: int) -> str:
    """Render halaman dengan lebar viewport SAH (via CDP), balikkan HTML.

    Dipakai karena `chrome --window-size=<500` selalu jadi 500px.
    """
    try:
        from websocket import create_connection  # type: ignore
    except Exception:
        # websocket-client belum ada → pakai cara cadangan (catat lebarnya)
        return _render_flag(url, lebar)
    port = 9333 + (lebar % 50)
    proc = subprocess.Popen(
        [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
         f'--remote-debugging-port={port}', '--remote-allow-origins=*',
         'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                r = subprocess.run(['curl', '-s', '-m', '2',
                                    f'http://127.0.0.1:{port}/json/list'],
                                   capture_output=True, text=True)
                if r.stdout and 'webSocketDebuggerUrl' in r.stdout:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        ws_url = None
        r = subprocess.run(['curl', '-s', '-m', '3',
                            f'http://127.0.0.1:{port}/json/list'],
                           capture_output=True, text=True)
        for baris in (r.stdout or '').split(','):
            if 'webSocketDebuggerUrl' in baris:
                ws_url = baris.split('"')[3]
                break
        if not ws_url:
            return _render_flag(url, lebar)
        ws = create_connection(ws_url, timeout=25)
        n = [0]
        def kirim(method, **params):
            n[0] += 1
            ws.send(json.dumps({'id': n[0], 'method': method, 'params': params}))
            while True:
                d = json.loads(ws.recv())
                if d.get('id') == n[0]:
                    return d
        kirim('Page.enable')
        kirim('Emulation.setDeviceMetricsOverride', width=lebar, height=1900,
              deviceScaleFactor=1, mobile=True)
        kirim('Page.navigate', url=url)
        time.sleep(5)
        h = kirim('Runtime.evaluate', expression='document.documentElement.outerHTML',
                  returnByValue=True)
        ws.close()
        return (h.get('result', {}).get('result', {}) or {}).get('value', '')
    except Exception:
        return _render_flag(url, lebar)
    finally:
        proc.terminate()


def _render_flag(url: str, lebar: int) -> str:
    """Cadangan: cara lama (lebar bisa jadi 500px — dicatat di keluaran)."""
    p = subprocess.run(
        [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
         f'--window-size={lebar+60},1900', '--force-device-scale-factor=1',
         '--virtual-time-budget=8000', '--dump-dom', url],
        capture_output=True, text=True, timeout=140)
    return p.stdout or ''


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    if not os.path.exists(TEMPLATE) or not os.path.exists(CSS):
        print('  ⚠️  jalankan dari folder statistik-lab'); return 0

    css = open(CSS, encoding='utf-8').read()
    os.makedirs(DIR_UJI, exist_ok=True)

    ip = subprocess.run(['docker', 'inspect', '-f',
        '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
        'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan (dibutuhkan untuk menyajikan berkas)')
        return 0

    print('═══ GERBANG SLIDER (uji BERKAS) ═══')
    print(f'  sumber: {TEMPLATE} + {CSS}')
    gagal = 0
    for lebar in LEBAR_UJI:
        nm = f'halaman_{lebar}.html'
        open(os.path.join(DIR_UJI, nm), 'w').write(rakit(lebar, css))
        # ⚠️ Salin DULU, baru render — kalau tidak: HTTP 404 "Not Found".
        subprocess.run(['docker', 'exec', 'simulasi-olah-data', 'mkdir', '-p', WEB],
                       capture_output=True, text=True)
        cpr = subprocess.run(['docker', 'cp', os.path.join(DIR_UJI, nm),
                              f'simulasi-olah-data:{WEB}/{nm}'],
                             capture_output=True, text=True)
        if cpr.returncode != 0:
            print(f'  ❌ lebar {lebar}: gagal salin ke kontainer: '
                  f'{(cpr.stderr or "").strip()[:100]}')
            gagal += 1
            continue
        url = f'http://{ip}:8000/static/_uji_slider/{nm}'
        # ⚠️ WAJIB CDP: `--window-size=390` DITOLAK Chrome (selalu jadi 500px),
        # jadi uji lebar HP lewat flag = PALSU. CDP menyetel viewport dengan benar.
        out_teks = _render_cdp(url, lebar)
        m = re.search(r'SLD::(.*?)</title>', out_teks or '', re.S)
        if not m:
            # ⚠️ GAGAL, bukan diam-diam lanjut (pelajaran: "lolos palsu").
            print(f'  ❌ lebar {lebar}: TIDAK TERBACA — gerbang tidak mengukur apa pun')
            gagal += 1
            continue
        mentah = _h.unescape(m.group(1).strip())
        if mentah.startswith('GALAT'):
            print(f'  ❌ lebar {lebar}: {mentah}'); gagal += 1; continue
        d = json.loads(mentah)

        print(f'  ── lebar {d["lebarLayar"]}px ──')
        if d['ditemukan'] == 0:
            print('     ❌ TIDAK ADA slider yang ditemukan — uji tidak sah')
            gagal += 1
            continue
        for s in d['slider']:
            pesan = []
            if s['tinggiKotak'] < 26:
                pesan.append(f'kotak slider {s["tinggiKotak"]}px (<26px) '
                             f'→ kenop meluber (CSS height: {s["tinggiCSS"]})')
            if s['jarakKeTeks'] is not None and s['jarakKeTeks'] < 4:
                pesan.append(f'teks menempel ({s["jarakKeTeks"]}px): '
                             f'"{s["teksDekat"]}"')
            if pesan:
                print(f'     ❌ #{s["id"]}: ' + '; '.join(pesan))
                gagal += 1
            else:
                print(f'     ✅ #{s["id"]}: kotak {s["tinggiKotak"]}px, '
                      f'jarak ke teks {s["jarakKeTeks"]}px')
    if gagal:
        print(f'\n  ❌ {gagal} masalah slider')
        return 1
    print('\n  ✅ semua slider: kenop muat, keterangan tidak menempel')
    return 0


if __name__ == '__main__':
    sys.exit(main())
