#!/usr/bin/env python3
"""ESCAPE tag penutup mentah di dalam <script> pada buat_data.html.

⚠️ KENAPA PERLU: `gerbang_tag_skrip.py` melarang tag penutup mentah
(</p>, </strong>, </h3>, …) di dalam blok <script>. Kalau dibiarkan, parser
HTML menyangka </script> sudah selesai -> KODE TUMPAH jadi teks di halaman,
padahal HTTP 200 dan halaman tampak "hidup".

CARA BENAR: escape garis miringnya -> tag penutup ditulis dengan backslash
tunggal sebelum garis miring.
CARA SALAH: backslash DOBEL — rusak di dalam template literal.
  Jebakan ini SUDAH 2x kena (19Sep26 Tahap 1.3, lalu 21Sep26). Skrip ini
  menormalkan: dobel dibetulkan jadi tunggal SEKALI JALAN.

HANYA menyentuh tag penutup DI DALAM <script>…</script>. HTML biasa & blok
Jinja TIDAK disentuh. Berkas asli dicadangkan ke .cadangan sebelum diubah.

Jalan: .venv/bin/python _sketsa/escape_tag_buat_data.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

BERKAS = Path('/opt/data/services/statistik-lab/app/templates/buat_data.html')
CADANGAN = BERKAS.with_suffix('.html.cadangan')

# daftar tag penutup yang berbahaya di dalam <script> (LENGKAP)
TAG = ['div', 'select', 'option', 'button', 'span', 'label', 'input', 'p',
       'strong', 'em', 'table', 'tr', 'td', 'th', 'ul', 'li', 'ol', 'a',
       'h1', 'h2', 'h3', 'h4', 'code', 'summary', 'details', 'thead',
       'tbody', 'small', 'b', 'i', 'u', 's', 'kbd', 'pre', 'blockquote',
       'figcaption', 'figure', 'nav', 'section', 'article', 'header',
       'footer', 'main', 'aside', 'form', 'textarea', 'script', 'style',
       'title', 'head', 'body', 'html', 'svg', 'path', 'g', 'tspan']

BS = chr(92)          # backslash
SLASH = '/'


def blok_skrip(isi: str) -> list[tuple[int, int]]:
    """Kembalikan rentang (mulai, akhir) tiap blok <script>…</script>."""
    rentang = []
    pos = 0
    while True:
        a = isi.find('<script', pos)
        if a < 0:
            break
        b = isi.find('</script>', a)
        if b < 0:
            break
        rentang.append((a, b + len('</script>')))
        pos = b + len('</script>')
    return rentang


def main() -> int:
    isi = BERKAS.read_text()
    if not CADANGAN.exists():
        shutil.copy2(BERKAS, CADANGAN)
        print(f'  cadangan dibuat: {CADANGAN.name}')
    else:
        # cadangan selalu diperbarui supaya = keadaan SEBELUM perbaikan ini
        shutil.copy2(BERKAS, CADANGAN)

    rentang = blok_skrip(isi)
    if not rentang:
        print('  TIDAK ada blok <script> — tidak ada yang dikerjakan')
        return 0

    # (1) NORMALKAN escape DOBEL jadi tunggal (di dalam skrip saja)
    dobel = '<' + BS + BS + SLASH
    tunggal = '<' + BS + SLASH
    n_dobel = 0
    potongan = []
    batas = 0
    for a, b in rentang:
        potongan.append(isi[batas:a])
        blok = isi[a:b]
        n_dobel += blok.count(dobel)
        potongan.append(blok.replace(dobel, tunggal))
        batas = b
    potongan.append(isi[batas:])
    isi = ''.join(potongan)

    # (2) ESCAPE tag penutup MENTAH di dalam skrip
    rentang = blok_skrip(isi)
    keluar = []
    batas = 0
    n_escape = 0
    for a, b in rentang:
        keluar.append(isi[batas:a])
        blok = isi[a:b]
        for t in TAG:
            mentah = '</' + t + '>'
            aman_ = '<' + BS + SLASH + t + '>'
            # jangan sentuh yang SUDAH ter-escape
            n = blok.count(mentah)
            if n:
                # hanya escape yang BUKAN </script> penutup asli blok
                blok = blok.replace(mentah, aman_)
                n_escape += n
        # kembalikan penutup blok yang sah
        blok = blok.replace('<' + BS + SLASH + 'script' + '>', '</script>')
        keluar.append(blok)
        batas = b
    keluar.append(isi[batas:])
    isi = ''.join(keluar)

    BERKAS.write_text(isi)
    print(f'  escape dobel dinormalkan : {n_dobel}')
    print(f'  tag penutup di-escape    : {n_escape}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
