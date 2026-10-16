#!/usr/bin/env python3
"""GERBANG: semua template Jinja bisa di-compile?

⚠️ MENGAPA GERBANG INI DIBUAT (19Sep26 — kejadian NYATA):
Wulan menambahkan blok skrip di `belajar.html` dan menulis tanda Jinja
(`block skrip`) DI DALAM KOMENTAR JavaScript. Maksudnya cuma menyebut nama
blok di komentar. Tapi **Jinja tidak menganggap itu komentar** — ia tetap
membacanya sebagai perintah block. Akibatnya Jinja mencari `endblock` yang
tidak ada:

    jinja2.exceptions.TemplateSyntaxError:
    Unexpected end of template. Jinja was looking for: 'endblock'.

DAMPAK: halaman `/belajar` **HTTP 500 total**. Dan yang LEBIH BERBAHAYA:
- `gerbang_tag_skrip.py` LULUS (ia memeriksa tag HTML, bukan Jinja)
- `gerbang_ikon.py` LULUS
- aplikasi bisa di-IMPOR (`from app.main import app` → OK, karena template
  baru dibaca saat REQUEST, bukan saat impor)
- gerbang-gerbang lama **tidak ada yang menyentuh Jinja**

⇒ Deploy LOLOS gerbang tapi halaman MATI. Gerbang ini menutup lubang itu.

CARA KERJA: compile SETIAP `app/templates/*.html` lewat Jinja.
Tidak perlu render (tidak perlu data) — cukup `get_template()`.

⚠️ ATURAN YANG DIJAGA: JANGAN pernah menulis tanda kurung Jinja di dalam
komentar JS atau komentar HTML di template. Satu tanda = halaman mati.
"""
import pathlib
import sys

from jinja2 import Environment, FileSystemLoader

DIR = pathlib.Path(__file__).resolve().parent
TPL = DIR / 'app' / 'templates'


def utama() -> int:
    print('═' * 70)
    print('GERBANG: semua template Jinja bisa di-compile')
    print('═' * 70)

    if not TPL.exists():
        print(f'❌ folder template tidak ada: {TPL}')
        return 1

    env = Environment(loader=FileSystemLoader(str(TPL)))
    berkas = sorted(TPL.glob('*.html'))
    rusak = []

    for p in berkas:
        try:
            env.get_template(p.name)
            print(f'  ✅ {p.name}')
        except Exception as e:                          # noqa: BLE001
            pesan = str(e).replace('\n', ' ')[:160]
            rusak.append((p.name, pesan))
            print(f'  ❌ {p.name}\n       {pesan}')

    print()
    print(f'  {len(berkas) - len(rusak)} dari {len(berkas)} template sehat')
    if rusak:
        print(f'  🚨 {len(rusak)} TEMPLATE RUSAK — halaman akan HTTP 500.')
        print('  PERBAIKI: cari tanda kurung Jinja yang salah tempat')
        print('            (paling sering di KOMENTAR JS / KOMENTAR HTML).')
        return 1

    print('  ✅ SEMUA TEMPLATE SEHAT')
    return 0


if __name__ == '__main__':
    sys.exit(utama())
