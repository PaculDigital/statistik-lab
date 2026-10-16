#!/usr/bin/env python3
"""Pindahkan skrip bukaTab Wulan ke DALAM <script> yang benar.

⚠️ AKAR (19Sep26, TERUKUR): Wulan menaruh kode JS-nya di blok skrip TEPAT
   SETELAH `{% block skrip %}`, padahal `<script>` yang asli ada BEBERAPA
   BARIS SESUDAHNYA. Akibatnya kode Wulan berada DI LUAR <script> → tampil
   sebagai TEKS di halaman (user melihat kode!). Hanya ketangkap oleh
   gerbang_kode_tumpah.py (yang membuka halaman NYATA), bukan oleh gerbang
   Jinja maupun gerbang tag skrip.

CARA BENAR: cari `<script>` pertama di dalam blok skrip, lalu selipkan kode
tepat SESUDAHNYA.
"""
import pathlib
import shutil

BERKAS = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CADANGAN = pathlib.Path('/tmp/belajar_cadangan4.html')

KEPALA = '/* ══════ PITA TAB (19Sep26) ══════'
EKOR = '})();'


def utama():
    s = BERKAS.read_text(encoding='utf-8')
    CADANGAN.write_text(s, encoding='utf-8')
    print(f'cadangan → {CADANGAN} ({len(s)} byte)')

    # ambil blok skrip Wulan: dari KEPALA sampai EKOR pertama
    i0 = s.find(KEPALA)
    i1 = s.find(EKOR, i0)
    if i0 < 0 or i1 < 0:
        print('❌ tidak ketemu blok Wulan')
        return
    i1 += len(EKOR)
    blok = s[i0:i1]
    print(f'blok Wulan: {len(blok)} byte')

    # buang blok dari tempat lama (bersihkan baris kosong sisa)
    sisa = s[:i0] + s[i1:]
    sisa = sisa.replace('{% block skrip %}\n\n<script>', '{% block skrip %}\n<script>')
    sisa = sisa.replace('{% block skrip %}\n\n\n<script>', '{% block skrip %}\n<script>')

    # sisipkan TEPAT SESUDAH <script> pertama di dalam blok skrip
    j = sisa.find('{% block skrip %}')
    k = sisa.find('<script>', j)
    if k < 0:
        print('❌ tidak ketemu <script> setelah blok skrip — BATAL')
        return
    k += len('<script>')
    hasil = sisa[:k] + '\n' + blok + '\n' + sisa[k:]

    BERKAS.write_text(hasil, encoding='utf-8')

    print('\n── VERIFIKASI ──')
    print(f'  ukuran: {len(s)} → {len(hasil)} byte')
    print(f'  <script>: {hasil.count("<script>")} · '
          f'</script>: {hasil.count("</script>")} (harus 1 & 1)')

    # posisi: blok Wulan HARUS setelah <script>
    pos_script = hasil.find('<script>')
    pos_wulan = hasil.find(KEPALA)
    print(f'  <script> di {pos_script} · blok Wulan di {pos_wulan} → '
          + ('✅ DI DALAM script' if pos_wulan > pos_script else '❌ MASIH DI LUAR'))
    for kata in ['function bukaTab', 'pa-2', 'pa-1']:
        print(f'  {"✅" if kata in hasil else "❌"} {kata}')


if __name__ == '__main__':
    utama()
