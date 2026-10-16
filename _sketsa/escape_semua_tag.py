"""Escape SETIAP tag penutup HTML MENTAH yang berada DI DALAM <script>.

⚠️ AKAR (20Sep26) — kenapa harus otomatis, bukan satu-satu:
gerbang_tag_skrip.py menemukan pelanggaran BARU tiap kali Wulan membaiki satu.
Menambal per-titik = HARAM (aturan Bos). Akar sebenarnya: setiap `<strong>`
yang dibuka di dalam string JS TIDAK boleh memakai penutup mentah; penutup
WAJIB di-escape jadi `<\/strong>`. Jadi yang dikerjakan: pindai SELURUH isi
<script> di template, escape SEMUA penutup tag — sekali jalan.

YANG TIDAK DISENTUH:
  · Tag di LUAR <script> (HTML biasa) — memang harus mentah.
  · Penutup yang SUDAH ter-escape.
  · `<br>`, `<img>`, `<input>` dsb (void element, tanpa penutup).
"""
from pathlib import Path
import re
import shutil

BS = chr(92)        # garis miring terbalik
TEMPLAT = Path('app/templates')
POLA_SKRIP = re.compile(r'(<script\b[^>]*>)(.*?)(</script>)', re.S)
# penutup tag yang WAJIB di-escape (bukan void element)
POLA_TUTUP = re.compile(r'</(strong|em|b|i|u|span|div|p|h[1-6]|small|code|ul|li|ol|table|tr|td|th)>',
                        re.I)

total_berkas = 0
total_ganti = 0
penghitung = {'n': 0}      # dipakai lewat dict: `nonlocal` tidak boleh di scope modul


def olah(m):
    tag_buka, isi, tag_tutup = m.group(1), m.group(2), m.group(3)

    def ganti(mm):
        penghitung['n'] += 1
        return '<' + BS + '/' + mm.group(1) + '>'

    return tag_buka + POLA_TUTUP.sub(ganti, isi) + tag_tutup


for F in sorted(TEMPLAT.glob('*.html')):
    teks = F.read_text(encoding='utf-8')
    asli = teks
    penghitung['n'] = 0
    teks = POLA_SKRIP.sub(olah, teks)
    if teks != asli:
        shutil.copy(F, F.with_suffix('.html.cadangan_escape2'))
        F.write_text(teks, encoding='utf-8')
        total_berkas += 1
        total_ganti += penghitung['n']
        print(f'  \u2705 {F.name}: {penghitung["n"]} penutup di-escape')

print(f'\n  {total_berkas} berkas disentuh \u00b7 {total_ganti} penutup di-escape')
