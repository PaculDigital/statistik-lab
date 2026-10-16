#!/usr/bin/env python3
"""UKUR POSISI TEKS label slider — pakai titik tengah TEKS (bukan kotak span).

KENAPA (pelajaran 18Sep26):
  Mengukur `getBoundingClientRect()` pada `<span>` yang jadi grid-item itu
  MENIPU: span-nya membentang penuh kolomnya (144px), jadi kotaknya selalu
  pas di tepi walau TEKSNYA ada di tengah. Yang harus diukur adalah posisi
  TEKS di dalam span itu.

CARA UKUR YANG BENAR: pakai `Range` atas isi teks, lalu ambil
`getBoundingClientRect()` dari range tersebut — itulah kotak kata yang
benar-benar terlihat.

Jalankan: .venv/bin/python ukur_posisi_slider.py
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

CH = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
CSS = Path('/opt/data/services/statistik-lab/app/static/gaya.css').read_text()

JS = r"""
window.addEventListener('load', () => {
  // posisi KATA yang benar-benar terlihat (bukan kotak span)
  const kotakKata = (el) => {
    if (!el) return null;
    const n = el.firstChild;
    if (n && n.nodeType === 3) {
      const rg = document.createRange();
      rg.selectNodeContents(el);
      const r = rg.getBoundingClientRect();
      return {kiri: Math.round(r.left), kanan: Math.round(r.right),
              atas: Math.round(r.top), bawah: Math.round(r.bottom)};
    }
    const r = el.getBoundingClientRect();
    return {kiri: Math.round(r.left), kanan: Math.round(r.right),
            atas: Math.round(r.top), bawah: Math.round(r.bottom)};
  };
  const sk = document.querySelector('.skala-slider');
  const kotak = sk ? sk.getBoundingClientRect() : null;
  const out = {
    adaSkala: !!sk,
    kotakKiri: kotak ? Math.round(kotak.left) : null,
    kotakKanan: kotak ? Math.round(kotak.right) : null,
    kataPertama: sk ? kotakKata(sk.children[0]) : null,
    kataTerakhir: sk ? kotakKata(sk.children[sk.children.length - 1]) : null,
  };
  if (out.kataPertama) {
    out.geserKiri = out.kataPertama.kiri - out.kotakKiri;
  }
  if (out.kataTerakhir) {
    out.geserKanan = out.kotakKanan - out.kataTerakhir.kanan;
    out.sebaris = Math.abs(out.kataPertama.atas - out.kataTerakhir.atas) < 4;
  }
  document.title = 'PK::' + JSON.stringify(out) + '::E';
});
"""


def periksa(css: str, wadah: str = 'normal') -> dict:
    """Render dengan 2 kemungkinan wadah: normal / di dalam .hitung-var."""
    if wadah == 'normal':
        isi = """<div class="medan">
          <input type="range" min="1" max="8" value="3">
          <div class="skala-slider"><span class="samar">1</span>
            <span class="samar">8</span></div>
          <div class="nilai-slider"><strong>3</strong> variabel X</div>
        </div>"""
    else:
        isi = """<div class="medan"><div class="hitung-var">
          <button class="tb tb-kecil">−</button>
          <div class="hitung-var-tengah">
            <input type="range" min="1" max="8" value="3">
            <div class="skala-slider"><span class="samar">1</span>
              <span class="samar">8</span></div>
            <div class="nilai-slider"><strong>3</strong> variabel X</div>
          </div>
          <button class="tb tb-kecil">+</button>
        </div></div>"""

    html = f"""<!DOCTYPE html><meta charset="utf-8"><style>{css}
    html,body{{margin:0}} #w{{width:390px}}</style>
    <div id="w">{isi}</div>
    <script>{JS}</script>"""
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False,
                                     encoding='utf-8') as f:
        f.write(html)
        tmp = f.name
    try:
        p = subprocess.run([CH, '--headless=new', '--no-sandbox',
                            '--disable-gpu',
                            f'--user-data-dir={tempfile.mkdtemp()}',
                            '--window-size=700,600',
                            '--virtual-time-budget=2500',
                            '--dump-dom', f'file://{tmp}'],
                           capture_output=True, text=True, timeout=90)
        m = re.search(r'PK::(.*?)::E', p.stdout or '', re.S)
        return json.loads(m.group(1)) if m else {'galat': 'tidak terbaca'}
    finally:
        Path(tmp).unlink(missing_ok=True)


def main() -> int:
    print('═══ POSISI LABEL SLIDER (diukur dari KATA, bukan kotak span) ═══')
    gagal = 0
    for wadah, nama in (('normal', 'tanpa tombol −/+'),
                        ('hitung', 'DIAPIT tombol −/+ (seperti halaman)')):
        d = periksa(CSS, wadah)
        if d.get('galat'):
            print(f'  ❌ {nama} — {d["galat"]}')
            gagal += 1
            continue
        gk, gn = d.get('geserKiri'), d.get('geserKanan')
        ok = (gk is not None and gn is not None
              and gk <= 12 and gn <= 12 and d.get('sebaris'))
        tanda = '✅' if ok else '❌'
        print(f'  {tanda} {nama}')
        print(f'      kotak skala : {d["kotakKiri"]} … {d["kotakKanan"]}')
        print(f'      kata "1"    : {d["kataPertama"]["kiri"]} … '
              f'{d["kataPertama"]["kanan"]}')
        print(f'      kata "8"    : {d["kataTerakhir"]["kiri"]} … '
              f'{d["kataTerakhir"]["kanan"]}')
        print(f'      geser kiri={gk}px kanan={gn}px sebaris={d.get("sebaris")}')
        if not ok:
            gagal += 1
    print()
    if gagal:
        print('  ❌ MASIH ADA yang melayang — label tidak menempel tepi.')
        return 1
    print('  ✅ label slider menempel tepi kiri & kanan, sebaris')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
