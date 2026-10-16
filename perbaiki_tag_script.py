"""Perbaiki AKAR: '</div>' mentah di dalam blok <script> menutup script.

AKAR: browser HTML memakai parser "script data" — urutan karakter '</' diikuti
nama tag apa pun (bukan hanya </script>) DIPERLAKUKAN KHUSUS. Di banyak kasus
mesin uji/DOM memotong blok script di '</div>' pertama sehingga separuh skrip
tumpah menjadi teks halaman. Ini rapuh dan salah walaupun tampak jalan.

PERBAIKAN PERMANEN (bukan menambal): ganti tiap '</' di dalam string JS
menjadi pemecahan string '...<' + '/div>...' sehingga urutan '</' TIDAK
PERNAH muncul utuh di dalam blok <script>.

Aman: hasilnya string HTML yang SAMA saat dijalankan JS.
"""
import re

P = 'app/templates/buat_data.html'
s = open(P).read()

i = s.find('<script>')          # blok skrip pertama (bagian atas)
j = s.find('<script>', i + 1)
if j == -1:
    j = len(s)
# ambil semua blok <script>...</script>
blok_semua = []
pos = 0
while True:
    a = s.find('<script>', pos)
    if a == -1:
        break
    b = s.find('</script>', a)
    if b == -1:
        break
    blok_semua.append((a + len('<script>'), b))
    pos = b + len('</script>')

print(f'blok <script> ditemukan: {len(blok_semua)}')

total = 0
# kerjakan dari BELAKANG supaya posisi tidak bergeser
for a, b in reversed(blok_semua):
    blok = s[a:b]
    # cari '</' diikuti nama tag (div, span, p, table, button, dsb) di dalam string
    def ganti(m):
        return "<' + '/" + m.group(1) + '>'
    baru, n = re.subn(r"</(div|span|p|table|thead|tbody|tr|td|th|button|h1|h2|h3|h4|small|strong)>",
                      ganti, blok)
    if n:
        s = s[:a] + baru + s[b:]
        total += n
        print(f'  blok @{a}: {n} penggantian')

open(P, 'w').write(s)
print(f'\nTOTAL {total} penulisan tag penutup dirapikan')

# verifikasi: tidak boleh ada lagi '</div>' mentah di dalam script
sisa = 0
pos = 0
while True:
    a = s.find('<script>', pos)
    if a == -1:
        break
    b = s.find('</script>', a)
    blok = s[a:b]
    for m in re.finditer(r'</(div|span|p|table|thead|tbody|tr|td|th|button|h1|h2|h3|h4|small|strong)>', blok):
        sisa += 1
    pos = b + len('</script>')
print('sisa tag penutup mentah di dalam script:', sisa)
