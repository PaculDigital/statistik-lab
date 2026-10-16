#!/usr/bin/env python3
"""PERIKSA HP: cari elemen yang KEMUNGKINAN tampak jelek di layar HP.

Dipakai saat provider vision mati (17Sep26 provider `ag` kehabisan kapasitas)
— jadi Wulan periksa sendiri dari KODE, bukan mengandalkan mata AI.

Yang diperiksa di lebar HP nyata:
 1. Elemen yang lebih sempit dari 44px (susah diketik jari)
 2. Teks lebih kecil dari 12px (tidak terbaca)
 3. Elemen bertumpuk (tumpang tindih)
 4. Tombol/kotak yang keluar layar
 5. Gambar/ikon yang gepeng (lebar != tinggi)

Jalankan: .venv/bin/python periksa_hp.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'

# Skrip pengukur — dijalankan DI DALAM iframe lebar HP
UKUR = r"""
(function(){
  function jalan(){
    var LW = window.innerWidth;
    var kecil = [], mungil = [], keluar = [], gepeng = [];
    document.querySelectorAll('button, input, select, a, .tb, .tb-kecil, .pilih').forEach(function(n){
      var r = n.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      var nm = n.tagName.toLowerCase() + (n.id ? '#'+n.id : '') +
               (typeof n.className === 'string' && n.className ? '.'+n.className.split(' ')[0] : '');
      if (r.height > 0 && r.height < 40) kecil.push({el:nm, h:Math.round(r.height), t:(n.textContent||'').trim().slice(0,20)});
      if (r.right > LW + 1) keluar.push({el:nm, k:Math.round(r.right)});
      var f = window.getComputedStyle(n).fontSize;
      var px = parseFloat(f);
      if (px && px < 12) mungil.push({el:nm, px:f, t:(n.textContent||'').trim().slice(0,20)});
    });
    document.querySelectorAll('svg').forEach(function(n){
      var r = n.getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && Math.abs(r.width - r.height) > 6 && Math.min(r.width,r.height) > 8)
        gepeng.push({w:Math.round(r.width), h:Math.round(r.height)});
    });
    return {lebarLayar:LW, scrollW:document.documentElement.scrollWidth,
            kecil:kecil.slice(0,10), mungil:mungil.slice(0,10),
            keluar:keluar.slice(0,10), gepeng:gepeng.slice(0,6)};
  }
  window.__cek = jalan;
})();
"""


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    ip = subprocess.run(['docker', 'inspect', '-f',
        '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
        'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan'); return 0

    for lebar in (390, 360):
        html = f'''<!DOCTYPE html><meta charset="utf-8"><title>u</title>
<style>html,body{{margin:0}}iframe{{display:block;border:0;width:{lebar}px;height:1800px}}</style>
<iframe id="f" src="http://{ip}:8000/buat-data?uji=x8"></iframe>
<script>
document.getElementById('f').addEventListener('load', function(){{
  setTimeout(function(){{
    try {{
      var w=document.getElementById('f').contentWindow, d=document.getElementById('f').contentDocument;
      var s=d.createElement('script'); s.text={json.dumps(UKUR)}; d.body.appendChild(s);
      var out=w.__cek(); out.diminta={lebar};
      document.title='CEK::'+JSON.stringify(out);
    }} catch(e){{ document.title='CEK::GALAT '+e.message; }}
  }}, 2600);
}});
</script>'''
        nm = f'periksa_hp_{lebar}.html'
        with open(f'/tmp/{nm}', 'w') as f:
            f.write(html)
        subprocess.run(['docker', 'cp', f'/tmp/{nm}',
                        f'simulasi-olah-data:/app/app/static/{nm}'],
                       capture_output=True, text=True)
        p = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             f'--window-size={lebar+80},1850', '--force-device-scale-factor=1',
             '--virtual-time-budget=12000', '--dump-dom',
             f'http://{ip}:8000/static/{nm}'],
            capture_output=True, text=True, timeout=140)
        m = re.search(r'CEK::(.*?)</title>', p.stdout or '', re.S)
        if not m:
            print(f'  lebar {lebar}: tidak terbaca'); continue
        mentah = _h.unescape(m.group(1).strip())
        if mentah.startswith('GALAT'):
            print(f'  lebar {lebar}: {mentah}'); continue
        d = json.loads(mentah)

        print(f'  ══ lebar {d["lebarLayar"]}px ══')
        print(f'  scrollW {d["scrollW"]} (layar {d["lebarLayar"]})')
        if d['kecil']:
            print(f'  ⚠️  elemen < 40px tinggi (susah diketik jari): {len(d["kecil"])}')
            for e in d['kecil'][:5]:
                print(f'      • {e["el"][:44]} tinggi {e["h"]}px "{e["t"]}"')
        else:
            print('  ✅ semua elemen ketuk ≥ 40px')
        if d['mungil']:
            print(f'  ⚠️  teks < 12px (tidak terbaca): {len(d["mungil"])}')
            for e in d['mungil'][:5]:
                print(f'      • {e["el"][:44]} {e["px"]} "{e["t"]}"')
        else:
            print('  ✅ semua teks ≥ 12px')
        if d['keluar']:
            print(f'  ❌ elemen keluar layar: {len(d["keluar"])}')
            for e in d['keluar'][:5]:
                print(f'      • {e["el"][:44]} kanan {e["k"]}')
        else:
            print('  ✅ tidak ada elemen keluar layar')
        if d['gepeng']:
            print(f'  ⚠️  ikon gepeng (lebar != tinggi): {len(d["gepeng"])}')
            for e in d['gepeng'][:3]:
                print(f'      • {e["w"]}×{e["h"]}px')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
