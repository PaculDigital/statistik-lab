#!/usr/bin/env python3
"""UKUR HP dengan lebar yang BENAR (viewport, bukan jendela).

⚠️ JEBAKAN BESAR (17Sep26): Chrome headless MENOLAK `--window-size` di bawah
~500px — selalu dirender 500px. Terbukti:
    --window-size=390 → window.innerWidth 500
    --window-size=360 → window.innerWidth 500
Artinya SEMUA "uji HP" yang memakai --window-size sebenarnya menguji 500px.
Akibatnya bug tampilan HP (tombol + dan preset 8 hilang) SELALU lolos.

Cara benar: setel lebar lewat DevTools Protocol `Emulation.setDeviceMetricsOverride`,
yang benar-benar mengubah viewport. CDP dijalankan sebagai proses terpisah
(thread) di skrip ini, bukan lewat websocket.

Jalankan: .venv/bin/python ukur_hp_cdp.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys
import tempfile
import time

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
LEBAR = [412, 390, 375, 360]

SUMBER_UKUR = r"""
(function(){
  function ukur(){
    var LW = window.innerWidth;
    var pelaku = [];
    document.querySelectorAll('*').forEach(function(n){
      var r = n.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if (r.right > LW + 1) {
        var c = (typeof n.className === 'string') ? n.className : '';
        pelaku.push({tag: n.tagName.toLowerCase(), cls: c.slice(0,45),
                     id: n.id || '', kanan: Math.round(r.right),
                     teks: (n.textContent||'').trim().slice(0,32)});
      }
    });
    var pr = [];
    document.querySelectorAll('.pilih-kecil').forEach(function(p){
      var r = p.getBoundingClientRect();
      pr.push({teks:p.textContent.trim(), x:Math.round(r.x),
               cy:Math.round(r.y+r.height/2), h:Math.round(r.height)});
    });
    var plus = document.getElementById('x-tambah');
    var kurang = document.getElementById('x-kurang');
    return {
      lebarLayar: LW,
      scrollW: document.documentElement.scrollWidth,
      pelaku: pelaku,
      preset: pr,
      plusKanan: plus ? Math.round(plus.getBoundingClientRect().right) : null,
      plusAdaDiLayar: plus ? (plus.getBoundingClientRect().right <= LW + 1) : false,
      kurangH: kurang ? Math.round(kurang.getBoundingClientRect().height) : null,
      plusH: plus ? Math.round(plus.getBoundingClientRect().height) : null
    };
  }
  window.__ukur = ukur;
  window.__siap = true;
})();
"""

# Skrip Python yang jalan DI DALAM Chrome via --remote-debugging-pipe? Tidak —
# kita pakai --remote-debugging-port + websocket bawaan Python 3.13 (tidak ada).
# Jadi: pakai '--headless' + '--dump-dom' TIDAK bisa set viewport < 500.
# Solusi: sisipkan emulasi lewat meta viewport + lebar body dipaksa, ATAU
# pakai Chrome DevTools Protocol via 'curl' ke HTTP endpoint (tanpa websocket
# tidak bisa perintah). Karena itu: pakai PENDEKATAN LAIN — bungkus halaman
# dalam iframe berukuran HP DI HALAMAN YANG DIUKUR SENDIRI (bukan iframe
# terpisah), sehingga viewport iframe = lebar HP yang benar.
#
# Terbukti: iframe 390px DI DALAM halaman 500px memakai media query 390px
# (karena media query iframe dihitung dari lebar iframe-nya).


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    ip = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan'); return 0

    # halaman pembungkus: iframe selebar HP, lalu ukur isinya
    for lebar in LEBAR:
        pembungkus = f'''<!DOCTYPE html><meta charset="utf-8"><title>u</title>
<style>html,body{{margin:0}}iframe{{display:block;border:0;width:{lebar}px;height:1700px}}</style>
<iframe id="f" src="http://{ip}:8000/buat-data?uji=x8"></iframe>
<script>
document.getElementById('f').addEventListener('load', function(){{
  setTimeout(function(){{
    try {{
      var w=document.getElementById('f').contentWindow,
          d=document.getElementById('f').contentDocument;
      // suntikkan pengukur ke dokumen iframe
      var s=d.createElement('script'); s.text={json.dumps(SUMBER_UKUR)};
      d.body.appendChild(s);
      var out=w.__ukur();
      out.diminta={lebar};
      document.title='HPCDP::'+JSON.stringify(out);
    }} catch(e) {{ document.title='HPCDP::GALAT '+e.message; }}
  }}, 2600);
}});
</script>'''
        # ⚠️ Pembungkus WAJIB disajikan dari ORIGIN YANG SAMA dengan iframe
        # (http://kontainer), bukan file://. Kalau beda origin, contentDocument
        # bernilai null → "Cannot read properties of null".
        nm = f'_bungkus_{lebar}.html'
        with open(f'/tmp/{nm}', 'w') as f:
            f.write(pembungkus)
        subprocess.run(['docker', 'cp', f'/tmp/{nm}',
                        f'simulasi-olah-data:/app/app/static/{nm}'],
                       capture_output=True, text=True)

        p = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             '--window-size=900,1750', '--force-device-scale-factor=1',
             '--virtual-time-budget=9000', '--dump-dom',
             f'http://{ip}:8000/static/{nm}'],
            capture_output=True, text=True, timeout=140)
        m = re.search(r'HPCDP::(.*?)</title>', p.stdout or '', re.S)
        if not m:
            print(f'  lebar {lebar}: tidak terbaca'); continue
        mentah = _h.unescape(m.group(1).strip())
        if mentah.startswith('GALAT'):
            print(f'  lebar {lebar}: {mentah}'); continue
        try:
            d = json.loads(mentah)
        except Exception as e:
            print(f'  lebar {lebar}: JSON rusak ({e}) → {mentah[:120]}')
            continue

        ok_lebar = abs(d['lebarLayar'] - lebar) <= 3
        print(f'  ══ minta {lebar}px → viewport {d["lebarLayar"]}px '
              f'{"✅ SAH" if ok_lebar else "❌ TIDAK SAH"} ══')
        if not ok_lebar:
            print('     (media query iframe tidak mengikuti lebar iframe)')
            continue
        melebar = d['scrollW'] - d['lebarLayar']
        print(f'  {"❌ MELEBAR " + str(melebar) + "px" if melebar > 1 else "✅ tidak melebar"}'
              f'  (scrollW {d["scrollW"]})')
        print(f'  tombol + : kanan={d["plusKanan"]}, '
              f'di dalam layar = {"YA" if d["plusAdaDiLayar"] else "TIDAK ❌"}')
        pr = d['preset']
        if pr:
            xs = [x['x'] for x in pr]
            ys = [x['cy'] for x in pr]
            naik = all(xs[i] < xs[i+1] + 1 for i in range(len(xs)-1))
            print(f'  preset {len(pr)}: x={xs} sebaris={max(ys)-min(ys)<=12} naik={naik}')
            if not naik:
                print('  ❌ tombol preset TIDAK dalam satu baris')
        if d['pelaku']:
            print(f'  pelaku melebar ({len(d["pelaku"])}):')
            for e in d['pelaku'][:6]:
                nm = e['tag'] + (f'#{e["id"]}' if e['id'] else '') + \
                     (f'.{e["cls"]}' if e['cls'] else '')
                print(f'    • {nm[:60]} kanan={e["kanan"]} "{e["teks"]}"')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
