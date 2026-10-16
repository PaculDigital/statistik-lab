#!/usr/bin/env python3
"""UKUR MASALAH HP DI HALAMAN SUNGGUHAN (bukan iframe).

⚠️ PELAJARAN 17Sep26: mengukur lewat IFRAME MENIPU. Iframe punya scroll
sendiri, jadi scrollWidth-nya tampak aman padahal halaman aslinya (yang
dilihat user) MELEBAR dan memotong tombol + serta preset 8.

Cara yang benar: sisipkan pengukur ke halaman ITU SENDIRI lewat endpoint
/static/ukur_suntik.js yang dimuat halaman, lalu baca hasilnya dari <title>.

Jalankan: .venv/bin/python ukur_hp_asli.py
"""
import html as _h
import json
import os
import re
import subprocess
import sys

CHROME = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
LEBAR = [412, 390, 375, 360]

# Skrip yang disuntikkan ke halaman: dijalankan DI DALAM halaman target.
SUNTIK = r"""
(function(){
  setTimeout(function(){
    try {
      var LW = window.innerWidth;
      var el = [];
      document.querySelectorAll('*').forEach(function(n){
        var r = n.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) return;
        if (r.right > LW + 1) {
          var c = (typeof n.className === 'string') ? n.className : '';
          el.push({
            tag: n.tagName.toLowerCase(),
            cls: c.slice(0, 50),
            id: n.id || '',
            kanan: Math.round(r.right),
            lebar: Math.round(r.width),
            teks: (n.textContent || '').trim().slice(0, 35)
          });
        }
      });
      var pr = [];
      document.querySelectorAll('.pilih-kecil').forEach(function(p){
        var r = p.getBoundingClientRect();
        pr.push({teks: p.textContent.trim(), x: Math.round(r.x),
                 cy: Math.round(r.y + r.height/2)});
      });
      var plus = document.getElementById('x-tambah');
      var out = {
        lebarLayar: LW,
        scrollW: document.documentElement.scrollWidth,
        bodyScrollW: document.body ? document.body.scrollWidth : null,
        pelaku: el,
        preset: pr,
        plusAda: !!plus,
        plusKanan: plus ? Math.round(plus.getBoundingClientRect().right) : null,
        plusX: plus ? Math.round(plus.getBoundingClientRect().x) : null
      };
      document.title = 'ASLI::' + JSON.stringify(out);
    } catch (e) {
      document.title = 'ASLI::GALAT ' + e.message;
    }
  }, 2600);
})();
"""


def main() -> int:
    if not os.path.exists(CHROME):
        print('  ⚠️  Chrome tidak ada'); return 0
    ip = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    if not ip:
        print('  ⚠️  kontainer tidak jalan'); return 0

    # tulis skrip suntik ke berkas statis di dalam kontainer
    with open('/tmp/_ukur_suntik.js', 'w') as f:
        f.write(SUNTIK)
    subprocess.run(['docker', 'cp', '/tmp/_ukur_suntik.js',
                    'simulasi-olah-data:/app/app/static/ukur_suntik.js'],
                   capture_output=True, text=True)

    for lebar in LEBAR:
        url = (f'http://{ip}:8000/buat-data?uji=x8'
               f'&suntik=/static/ukur_suntik.js')
        p = subprocess.run(
            [CHROME, '--headless', '--disable-gpu', '--no-sandbox',
             f'--window-size={lebar},1700',
             # ⚠️ WAJIB: Chrome menolak lebar jendela < ~500px kecuali
             # device-scale dipaksa. Tanpa baris berikut, `--window-size=390`
             # tetap dirender 500px → pengukuran TIDAK SAH (bug 17Sep26).
             '--force-device-scale-factor=1',
             '--virtual-time-budget=9000',
             '--dump-dom', url],
            capture_output=True, text=True, timeout=140)
        m = re.search(r'ASLI::(.*?)</title>', p.stdout or '', re.S)
        if not m:
            print(f'  lebar {lebar}: tidak terbaca (skrip belum terpasang?)')
            continue
        d = json.loads(_h.unescape(m.group(1).strip()))
        print(f'  ══ lebar {lebar}px (terukur {d["lebarLayar"]}) ══')
        melebar = d['scrollW'] - d['lebarLayar']
        if melebar > 1:
            print(f'  ❌ MELEBAR {melebar}px (scrollW {d["scrollW"]})')
        else:
            print(f'  ✅ tidak melebar (scrollW {d["scrollW"]})')
        print(f'  tombol + : {"ADA" if d["plusAda"] else "TIDAK ADA"}, '
              f'x={d["plusX"]}, kanan={d["plusKanan"]}')
        if d['pelaku']:
            print(f'  pelaku melebar ({len(d["pelaku"])}):')
            for e in d['pelaku'][:8]:
                nm = e['tag'] + (f'#{e["id"]}' if e['id'] else '') + \
                     (f'.{e["cls"]}' if e['cls'] else '')
                print(f'    • {nm[:64]} kanan={e["kanan"]} "{e["teks"]}"')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
