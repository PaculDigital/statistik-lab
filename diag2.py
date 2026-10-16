"""DIAGNOSA LANGSUNG: jalankan gambar_svg dengan pencetakan nilai nyata."""
import sys
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
src = (DIR / 'diagram_svg.py').read_text(encoding='utf-8')

# sisipkan pencetakan TEPAT setelah _lo,_hi dihitung
sisip = ("    _lo, _hi = min(_kandidat_y), max(_kandidat_y)\n"
         "    print('[DIAG] tinggi_konten=', tinggi_konten, "
         "'tinggi(awal)=', tinggi, '_lo=', round(_lo), '_hi=', round(_hi))\n"
         "    print('[DIAG] jumlah geo_awal=', len(geo_awal), "
         "'berbusur=', sum(1 for g in geo_awal if g[5]))\n")
src2 = src.replace('    _lo, _hi = min(_kandidat_y), max(_kandidat_y)',
                   sisip, 1)
(DIR / '_diag2.py').write_text(src2, encoding='utf-8')

sys.path.insert(0, str(DIR))
import _diag2

from resep_model import baca_resep
from uji_pertanyaan_bos import R_BER

m, info = baca_resep(R_BER)
svg = _diag2.gambar_svg(m, 'tes')
import re
print('[DIAG] viewBox hasil:', re.search(r'viewBox="([^"]+)"', svg).group(1))
