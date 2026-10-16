"""DIAGNOSA 2: cetak isi geo_awal tepat saat blok tinggi dijalankan."""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
src = (DIR / 'diagram_svg.py').read_text(encoding='utf-8')

# sisipkan pencetakan setelah `_lo, _hi = min(_kandidat_y), max(_kandidat_y)`
sisip = ("    _lo, _hi = min(_kandidat_y), max(_kandidat_y)\n"
         "    import os as _os\n"
         "    if _os.environ.get('DIAG_TINGGI'):\n"
         "        print('DIAG geo_awal:', [(g[5], round(g[1]), round(g[2]), round(g[3]), round(g[4])) for g in geo_awal])\n"
         "        print('DIAG kandidat_y:', [round(v) for v in _kandidat_y])\n"
         "        print('DIAG tinggi_konten:', tinggi_konten, 'tinggi:', tinggi, '_lo:', _lo, '_hi:', _hi)\n")
assert '_lo, _hi = min(_kandidat_y), max(_kandidat_y)' in src
src2 = src.replace('    _lo, _hi = min(_kandidat_y), max(_kandidat_y)',
                   sisip, 1)
(DIR / '_diag_sementara.py').write_text(src2, encoding='utf-8')
print('OK tulis _diag_sementara.py')
