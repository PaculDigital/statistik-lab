"""Bandingkan struktur div: cadangan (sebelum Wulan) vs sekarang."""
from pathlib import Path

FILES = [
    'app/templates/belajar.html.cadangan_tab3',
    'app/templates/belajar.html',
]

for f in FILES:
    t = Path(f).read_text(encoding='utf-8')
    print(f'  ── {f.split("/")[-1]} ──')
    print(f'     <div>={t.count("<div")}  </div>={t.count("</div>")}')
    # bagian tab-1 s/d penutup tab-2
    i = t.find('id="tab-1"')
    z = t.find('/tab-2')
    seg = t[i:z]
    print(f'     bagian tab-1..tab-2 : <div>={seg.count("<div")} </div>={seg.count("</div>")}')
    # bagian AKHIR setelah /tab-2 (tempat tab-3 baru disisip)
    akhir = t[z:]
    print(f'     setelah /tab-2      : <div>={akhir.count("<div")} </div>={akhir.count("</div>")}')
