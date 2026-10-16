import re

# 1. CSS: naikkan ukuran minimum di HP
p = 'app/static/gaya.css'
s = open(p).read()
lama = ("  .pilih span, .saklar-teks, .samar, .langkah-teks, table.data td::before,\n"
        "  nav.utama .tanda, .kaki, .kaki-isi, .angka-kecil, .catatan {\n"
        "    font-size: 13px !important;\n"
        "  }")
baru = ("  .pilih span, .saklar-teks, .samar, table.data td::before,\n"
        "  nav.utama .tanda, .kaki, .kaki-isi, .angka-kecil, .catatan,\n"
        "  .modul-kaki, .langkah-nomor, .eyebrow, .pita, .tb-kecil, .langkah-teks {\n"
        "    font-size: 13px !important;\n"
        "  }")
if lama in s:
    s = s.replace(lama, baru)
    open(p, 'w').write(s)
    print('CSS: daftar minimum terbaca diperluas')
else:
    print('CSS: pola TIDAK ketemu — periksa manual')

# 2. Alat ukur: ambang 12.9 (12,8px dari 12,5px tidak lagi salah tertangkap)
for q in ['app/static/ukur.html', 'app/static/ukur2.html']:
    t = open(q).read()
    t2 = t.replace('px < 13', 'px < 12.9')
    open(q, 'w').write(t2)
    print(f'{q}: ambang -> 12.9px ({t.count("px < 13")} tempat)')
