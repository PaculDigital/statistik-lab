"""Periksa: apakah penyuntikan kerusakan A/B benar-benar mengubah PERILAKU?"""
import subprocess
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab')
JS = DIR / 'app' / 'static' / 'grafik_hidup.js'
asli = JS.read_text(encoding='utf-8')

RUMUS_ASLI = 'return gambarMin + t * (gambarMaks - gambarMin);'
print(f'  rumus asli ditemukan di berkas: {RUMUS_ASLI in asli}')

rusakA = asli.replace(RUMUS_ASLI, 'return gambarMaks - t * (gambarMaks - gambarMin);')
print(f'  berkas berubah setelah disuntik: {rusakA != asli}')

tmp = Path('/tmp/cek_A.js')
tmp.write_text(rusakA, encoding='utf-8')

skrip = f"""
const fs = require('fs'), vm = require('vm');
vm.runInThisContext(fs.readFileSync({str(tmp)!r}, 'utf8') +
  ';globalThis.petakan = petakan;');
console.log(JSON.stringify({{
  bawah: Math.round(petakan(9.1, 9.1, 26.5, 34, 300)),
  atas: Math.round(petakan(26.5, 9.1, 26.5, 34, 300)),
  tengah: Math.round(petakan(17.8, 9.1, 26.5, 34, 300))
}}));
"""
p = subprocess.run(['node', '-e', skrip], capture_output=True, text=True, cwd=str(DIR))
print(f'  hasil petakan() SETELAH dirusak: {p.stdout.strip() or p.stderr.strip()[:200]}')

# ── kerusakan B: apakah penggantian svgHetero benar-benar terjadi? ────────
POLA_B = ('const idx = indeksSebar(nAsli, BATAS_TITIK);\n'
          '  const zp = ambilPada(zpA, idx);\n'
          '  const zr = ambilPada(zrA, idx);')
print(f'\n  pola B ditemukan di berkas   : {POLA_B in asli}')
if POLA_B not in asli:
    # cari yang mendekati
    i = asli.find('const idx = indeksSebar')
    print('  yang ADA di berkas:')
    print('   ', repr(asli[i:i + 180]))
