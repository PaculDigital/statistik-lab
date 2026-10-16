#!/usr/bin/env python3
"""DIAGNOSA: kenapa uji VIF & p-value selalu memberi hasil sama?

MENGAPA BERKAS INI ADA (aturan: JANGAN menambal — cari AKAR):
Kode di domain SUDAH baru (terbukti: `(1 - r) * 70` dan `p * 300` ada di
halaman yang terkirim), tapi hasil uji IDENTIK tiga putaran berturut-turut.
Ciri khas: bukan kode yang salah, tapi ALAT UKUR yang tidak mengukur apa
yang dikira. Di sini Wulan membongkar satu per satu:
  1. Apakah slider benar-benar berubah nilainya?
  2. Apakah gambar benar-benar dilukis ulang setelah slider digeser?
  3. Posisi lingkaran VIF untuk beberapa nilai slider (bukan cuma ujung)
  4. Posisi penanda p untuk beberapa nilai (bukan cuma 2 titik)

JANGAN pakai berkas ini sebagai gerbang — ini ALAT DIAGNOSA.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_klik_mulai import tab_baru                    # noqa: E402

HAL = 'https://statistik.bikinaja.id/belajar'


def main() -> int:
    ws, _ = tab_baru('about:blank')
    no = 0

    def perintah(m, **p):
        nonlocal no
        no += 1
        return ws.perintah(no, m, **p)

    def js(e):
        d = perintah('Runtime.evaluate', expression=e,
                     returnByValue=True, awaitPromise=True)
        if d.get('result', {}).get('exceptionDetails'):
            return {'__galat__': d['result']['exceptionDetails']
                    .get('exception', {}).get('description')}
        return d.get('result', {}).get('result', {}).get('value')

    perintah('Emulation.setDeviceMetricsOverride', width=390, height=900,
             deviceScaleFactor=2, mobile=True)
    perintah('Page.enable')
    perintah('Page.navigate', url=HAL)
    for _ in range(60):
        time.sleep(0.5)
        if js("document.readyState === 'complete' && "
              "document.querySelector('svg.grafik') !== null"):
            break

    print('═══ DIAGNOSA VIF ═══')
    js("document.querySelector('.kamus-tombol[data-k=\"vif\"]').click()")
    time.sleep(0.5)
    for n in [0, 25, 50, 75, 100]:
        r = js(f"""(() => {{
          const s = document.getElementById('slider');
          s.value = '{n}';
          s.dispatchEvent(new Event('input', {{ bubbles: true }}));
          const c = document.querySelectorAll('svg.grafik circle');
          const a = c[0].getBoundingClientRect(), b = c[1].getBoundingClientRect();
          const t = document.querySelector('svg.grafik').textContent;
          const m = t.match(/tumpang tindih (\\d+)%/);
          return {{ slider: s.value,
                    x1: Math.round(a.left), x2: Math.round(b.left),
                    tumpangGeometri: Math.round(a.right - b.left),
                    labelTumpang: m ? m[1] : '?' }};
        }})()""")
        print(f'  slider={r.get("slider"):>4} | x1={r.get("x1"):>4} x2={r.get("x2"):>4}'
              f' | tumpang(geo)={r.get("tumpangGeometri"):>5}px'
              f' | label={r.get("labelTumpang")}%')

    print('\n═══ DIAGNOSA p-value ═══')
    js("document.querySelector('.kamus-tombol[data-k=\"pvalue\"]').click()")
    time.sleep(0.5)
    for n in [0, 25, 50, 75, 100]:
        r = js(f"""(() => {{
          const s = document.getElementById('slider');
          s.value = '{n}';
          s.dispatchEvent(new Event('input', {{ bubbles: true }}));
          const g = document.querySelector('svg.grafik');
          const lines = g.querySelectorAll('line');
          const t = g.textContent;
          const mp = t.match(/p = ([\\d.]+)/);
          return {{ slider: s.value, jumlahGaris: lines.length,
                    x_garis2: lines[2] ? Math.round(lines[2].getBoundingClientRect().left) : -1,
                    x_garis3: lines[3] ? Math.round(lines[3].getBoundingClientRect().left) : -1,
                    p: mp ? mp[1] : '?' }};
        }})()""")
        print(f'  slider={r.get("slider"):>4} | garis={r.get("jumlahGaris")}'
              f' | x[2]={r.get("x_garis2"):>4} x[3]={r.get("x_garis3"):>4}'
              f' | p={r.get("p")}')

    ws.tutup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
