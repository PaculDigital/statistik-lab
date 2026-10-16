"""GANTI nama id 'pagar-*' → 'perkiraan-*' + bersihkan kata 'pagar' di komentar.

KENAPA (temuan gerbang_bahasa.py 22Sep26):
  Gerbang melarang kata "pagar" karena Bos pernah membacanya di halaman dan
  bertanya ("Kata kata geser nilainya - pagar di kanan"). Kata itu memang
  TIDAK muncul sebagai teks tampil, tapi MUNCUL di dalam KODE yang dikirim ke
  browser: id elemen `pagar-${i}` dan komentar JS. Terukur: 6 kemunculan di
  HTML yang diterima mahasiswa (lihat _sketsa/cek_kata_pagar.py).

  ⚠️ Wulan awalnya MENDUGA ini cuma komentar Jinja yang dibuang — SALAH.
    Diperiksa dulu (curl + grep), baru diperbaiki. Pelajaran: buktikan, jangan
    menuduh gerbangnya rusak.

YANG DIUBAH: nama id + komentar saja. TIDAK ada logika yang disentuh.
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/app/templates/buat_data.html')
t = p.read_text()
asli = t

ganti = [
    ('<td id="pagar-${i}" data-label="Perkiraan hasil">',
     '<td id="perkiraan-${i}" data-label="Perkiraan hasil">'),
    ('const sel = el(`pagar-${i}`);', 'const sel = el(`perkiraan-${i}`);'),
    ('// ⚠️ WAJIB pakai backtick: `pagar-${i}` — getElementById tidak',
     '// ⚠️ WAJIB pakai backtick: `perkiraan-${i}` — getElementById tidak'),
    ("// mengevaluasi ${i} kalau ditulis dengan kutip biasa ('pagar-${i}')",
     "// mengevaluasi ${i} kalau ditulis dengan kutip biasa ('perkiraan-${i}')"),
    ('// 3. beta berat -> pagar harus memberi tahu',
     '// 3. beta berat -> kolom perkiraan harus memberi tahu'),
    ('// 6. setel angka wajar -> pagar hijau lagi',
     '// 6. setel angka wajar -> kolom perkiraan hijau lagi'),
]
for a, b in ganti:
    n = t.count(a)
    if n != 1:
        print(f'  ⚠️  TIDAK PAS ({n}×): {a[:56]}')
    t = t.replace(a, b)

# sisa 'pagar' (kalau ada) — laporkan jangan diam
sisa = t.count('pagar')
p.write_text(t)
print(f'  diubah   : {"YA" if t != asli else "TIDAK"}')
print(f'  sisa kata "pagar" di berkas: {sisa}')
