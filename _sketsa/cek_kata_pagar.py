import re
import urllib.request

u = 'http://127.0.0.1:8122/buat-data?model=banding-kelompok'
html = urllib.request.urlopen(u, timeout=10).read().decode('utf-8', 'replace')
print('jumlah kata "pagar":', len(re.findall(r'pagar', html)))
print()
# cari konteks tiap kemunculan
for m in re.finditer(r'pagar', html):
    a, b = max(0, m.start() - 90), min(len(html), m.end() + 90)
    potong = html[a:b].replace('\n', ' ')
    print('…' + potong + '…')
    print('-' * 70)
