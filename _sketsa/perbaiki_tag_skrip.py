#!/usr/bin/env python3
"""Perbaiki tag penutup mentah di dalam <script> diagnosis.html.

⚠️ ATURAN (pelajaran 19Sep26): JANGAN patch buta — pakai skrip + cadangan +
   ast/parse ulang. Tag penutup di dalam string JS literal harus di-escape
   jadi <\\/tag> supaya parser HTML TIDAK menyangka </script> selesai.

HANYA mengubah tag penutup yang BERADA DI DALAM <script>...</script>.
Tag di luar skrip (HTML biasa) TIDAK disentuh.
"""
from pathlib import Path
import re
import shutil

BERKAS = Path('/opt/data/services/statistik-lab/app/templates/diagnosis.html')
CADANGAN = BERKAS.with_suffix('.html.cadangan')

TAG = ['div', 'select', 'option', 'button', 'span', 'label', 'input', 'p',
       'strong', 'em', 'table', 'tr', 'td', 'th', 'ul', 'li', 'a', 'h1',
       'h2', 'h3', 'h4', 'ol', 'code', 'summary', 'details', 'thead',
       'tbody', 'textarea', 'form', 'section', 'header', 'footer', 'small',
       'b', 'i', 'u', 'pre', 'dl', 'dt', 'dd', 'figure', 'figcaption']


def utama():
    s = BERKAS.read_text()
    n0 = len(s)

    # ── pisahkan bagian <script> dan bukan ──
    # cari blok {% block skrip %} ... {% endblock %} dan <script>...</script>
    keluaran = []
    pos = 0
    pola = re.compile(r'<script\b[^>]*>(.*?)</script>', re.S | re.I)
    jumlah = 0
    for m in pola.finditer(s):
        isi = m.group(1)
        # escape semua tag penutup di dalam isi
        baru = isi
        for t in TAG:
            # </div>  →  <\/div>   (hanya yang belum ter-escape)
            baru = re.sub(r'</' + t + r'\b', r'<\\/' + t, baru)
        if baru != isi:
            jumlah += m.group(0).count('</') - baru.count('<\\/')
        keluaran.append(s[pos:m.start()])
        keluaran.append(m.group(0)[:m.group(0).index('>') + 1])   # tag buka <script...>
        keluaran.append(baru)
        keluaran.append('</script>')
        pos = m.end()
    keluaran.append(s[pos:])
    hasil = ''.join(keluaran)

    if hasil == s:
        print('TIDAK ada perubahan — semua tag sudah ter-escape?')
        return 0

    shutil.copy2(BERKAS, CADANGAN)
    BERKAS.write_text(hasil)
    print(f'cadangan: {CADANGAN}')
    print(f'ukuran: {n0} → {len(hasil)} byte')

    # ⚠️ verifikasi: parse ulang (pastikan struktur <script> seimbang)
    buka = len(re.findall(r'<script\b', hasil, re.I))
    tutup = len(re.findall(r'</script>', hasil, re.I))
    print(f'<script> buka={buka} tutup={tutup} → {"SEIMBANG" if buka == tutup else "TIDAK SEIMBANG"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(utama())
