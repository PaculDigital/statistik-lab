#!/usr/bin/env python3
"""Perbaiki AKAR: penggabungan string '<' + '/div>' yang SALAH.

APA YANG SALAH:
  Wulan dulu mengubah '</div>' menjadi  <' + '/div>
  Itu hanya benar di dalam string KUTIP BIASA ('...' atau "...").
  Di dalam TEMPLATE LITERAL (`...`),  ' + '  BUKAN penggabungan —
  ia menjadi TEKS BIASA → kode tumpah ke halaman.

CARA YANG BENAR (berlaku di SEMUA konteks):
  Ganti  </tag>  menjadi  <\/tag>   (garis miring di-escape)
  JS membaca '<\\/div>' sebagai string '</div>' (sama persis),
  tetapi browser TIDAK melihat urutan '</' di dalam blok <script>
  → blok skrip aman, tampilan bersih.

Perbaikan ini juga MEMBALIKKAN kerusakan yang Wulan buat sebelumnya.
"""
import glob
import re
import sys

TAG = r'(div|span|p|table|thead|tbody|tr|td|th|button|h1|h2|h3|h4|small|strong|em|option|datalist|svg|use|text|a|ul|li|section|label|br|i|b|code|pre)'

total = 0
for P in sorted(glob.glob('app/templates/*.html')):
    s = open(P).read()
    asli = s

    # 1) balikkan penggabungan SALAH:  <' + '/div>   →   <\/div>
    s = re.sub(r"<' \+ '/" + TAG + r'>', r'<\\/' + r'\1>', s)
    # 2) juga bentuk varian tanpa spasi
    s = re.sub(r"<'\+'/" + TAG + r'>', r'<\\/' + r'\1>', s)

    if s != asli:
        n = len(re.findall(r'<\\/', s)) - len(re.findall(r'<\\/', asli))
        open(P, 'w').write(s)
        print(f'  {P}: {n} diperbaiki')
        total += n

print(f'\nTOTAL {total} diperbaiki')

# ── VERIFIKASI ───────────────────────────────────────────────────────────
print('\n── VERIFIKASI ──')
masalah = 0
for P in sorted(glob.glob('app/templates/*.html')):
    s = open(P).read()
    pos = 0
    while True:
        a = s.find('<script>', pos)
        if a == -1:
            break
        b = s.find('</script>', a)
        if b == -1:
            break
        blok = s[a:b]
        # a) tag penutup mentah (BAHAYA) — di luar pola <\/ yang benar
        mentah = re.findall(r'(?<!\\)</[a-z][a-z0-9]*>', blok)
        # b) penggabungan salah yang tersisa
        salah = re.findall(r"<' \+ '/", blok)
        if mentah or salah:
            print(f'  ❌ {P}: {len(mentah)} tag mentah, {len(salah)} gabung salah')
            masalah += len(mentah) + len(salah)
        pos = b + 9

if masalah:
    print(f'\n  MASIH ADA {masalah} masalah — JANGAN deploy')
    sys.exit(1)
print('  ✅ 0 tag mentah, 0 penggabungan salah')
