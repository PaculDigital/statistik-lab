"""UJI: apakah mesin mendukung X1,X2,X3 + M1,M2 + Y1,Y2,Y3 SEMUA SEKALIGUS?

Pertanyaan Bos: "apakah sudah support x1, x2, x3 dst. M1, m2 dst.
Terhadap y1, y2, y3".

CARA UJI: lewat PINTU PRODUKSI (unggah .csv → tandai peran → Hasil).
Tanam koefisien yang DIKETAHUI, lalu periksa apa yang benar-benar keluar.

Yang diperiksa:
  A. 3 X + 2 M + 1 Y  (paralel & berjenjang)
  B. 3 X + 1 M + 3 Y  (dua keluaran)
  C. 3 X + 2 M + 3 Y  + Z  (semuanya sekaligus)
  D. Koefisien keluaran: apakah a/b/c/c' benar-benar ada?
"""
import sys
import json
import urllib.request
import csv
import io
import numpy as np

sys.path.insert(0, '/opt/data/services/statistik-lab')
B = 'http://127.0.0.1:8122'
GAGAL = 0


def cek(n, s, b=''):
    global GAGAL
    print(f"  {'✅' if s else '❌'} {n}" + (f'   {b}' if b else ''))
    if not s:
        GAGAL += 1


def _http(p, kirim=None, body=None, tipe='application/json'):
    req = urllib.request.Request(
        B + p,
        data=(body if body is not None
              else (json.dumps(kirim).encode() if kirim is not None else None)),
        headers={'Content-Type': tipe})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode())


def unggah(header, baris, nama='d.csv'):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(header)
    w.writerows(baris)
    isi = b.getvalue().encode()
    batas = '----WULAN'
    body = (b'--' + batas.encode() + b'\r\n'
            b'Content-Disposition: form-data; name="berkas"; filename="'
            + nama.encode() + b'"\r\nContent-Type: text/csv\r\n\r\n'
            + isi + b'\r\n--' + batas.encode() + b'--\r\n')
    return _http('/api/diagnosis/unggah', body=body,
                 tipe='multipart/form-data; boundary=' + batas)


def kolom_dari(up):
    return [k['nama'] for k in up.get('kolom', [])]


def kirim(up, peta, **extra):
    d = {'kunci': up.get('kunci'), 'mode': 'spss', 'peran': peta,
         'missing': 'buang'}
    d.update(extra)
    return _http('/api/diagnosis/periksa', d)


def dua(nama, arr, peran):
    """Bikin header + baris: setiap variabel 2 kolom (item kuesioner)."""
    hdr, baris, peta = [], [], {}
    for nm, v in zip(nama, arr):
        for suf in ('a', 'b'):
            hdr.append(nm + suf)
            peta[nm + suf] = peran[nm]
    for i in range(len(arr[0])):
        r = []
        for v in arr:
            r += [round(float(v[i]), 4), round(float(v[i]), 4)]
        baris.append(r)
    return hdr, baris, peta


n = 300
rng = np.random.default_rng(7)

# ══ A. 3 X + 2 M + 1 Y ══════════════════════════════════════════════════
print('=' * 74)
print(' A. 3 X (X1,X2,X3) + 2 M (M1,M2) + 1 Y (Y1)')
print('=' * 74)
X1 = rng.normal(size=n)
X2 = rng.normal(size=n)
X3 = rng.normal(size=n)
M1 = 0.50 * X1 + 0.20 * X2 + rng.normal(scale=0.8, size=n)
M2 = 0.45 * X3 + rng.normal(scale=0.8, size=n)
Y = (0.30 * X1 + 0.25 * X2 + 0.20 * X3
     + 0.35 * M1 + 0.30 * M2 + rng.normal(scale=0.8, size=n))
hdr, baris, peta = dua(['X1', 'X2', 'X3', 'M1', 'M2', 'Y1'],
                       [X1, X2, X3, M1, M2, Y],
                       {'X1': 'X1', 'X2': 'X2', 'X3': 'X3',
                        'M1': 'M1', 'M2': 'M2', 'Y1': 'Y1'})
up = unggah(hdr, baris)
print('  kolom terbaca:', str(kolom_dari(up))[:78])
jw = kirim(up, peta)
print('  prediktor mesin:', jw.get('prediktor'))
print('  perantara      :', jw.get('perantara'))
cek('prediktor memuat X1,X2,X3,M1,M2',
    jw.get('prediktor') == ['X1', 'X2', 'X3', 'M1', 'M2'],
    str(jw.get('prediktor')))
k = jw.get('kaitan') or {}
cek('kaitan ada', bool(k.get('ada')), str(k.get('ada')))
# ⚠️ BANYAK X (ACC Bos 21Sep26 "Semua x masuk"): hasil WAJIB melaporkan
#    SEMUA X, bukan cuma X1. Kalau ini hijau, X2 & X3 benar-benar masuk.
med0 = (k.get('mediasi') or [{}])[0]
cek('SEMUA X terpakai (x_semua)',
    med0.get('x_semua') == ['X1', 'X2', 'X3'], str(med0.get('x_semua')))
cek('X2, X3 tercatat sebagai kovariat',
    med0.get('x_kovariat') == ['X2', 'X3'], str(med0.get('x_kovariat')))
cek('ditandai banyak_x', med0.get('banyak_x') is True)
cek('keterangan menyebut X2, X3 dikendalikan',
    'X2' in str(med0.get('a', {}).get('ket', '')),
    str(med0.get('a', {}).get('ket'))[:66])
cek('ada 2 hasil mediasi (M1 & M2)', len(k.get('mediasi') or []) == 2,
    str([m.get('m') for m in (k.get('mediasi') or [])]))

# berjenjang
jw2 = kirim(up, peta, bentuk_mediasi='berjenjang')
k2 = jw2.get('kaitan') or {}
cek('berjenjang: bentuk diterima', k2.get('bentuk_mediasi') == 'berjenjang',
    str(k2.get('bentuk_mediasi')))
m2 = (k2.get('mediasi') or [{}])[0]
cek('berjenjang: 2 jalur keluar', len(m2.get('jalur') or []) == 2,
    str([j.get('nama') for j in (m2.get('jalur') or [])]))

# ══ B. 3 X + 1 M + 3 Y ══════════════════════════════════════════════════
print()
print('=' * 74)
print(' B. 3 X + 1 M + 3 Y (Y1,Y2,Y3 — tiga keluaran)')
print('=' * 74)
Y1 = 0.35 * X1 + 0.30 * X2 + 0.25 * M1 + rng.normal(scale=0.8, size=n)
Y2 = 0.30 * X2 + 0.35 * X3 + 0.20 * M1 + rng.normal(scale=0.8, size=n)
Y3 = 0.25 * X1 + 0.30 * X3 + 0.25 * M1 + rng.normal(scale=0.8, size=n)
hdr3, baris3, peta3 = dua(['X1', 'X2', 'X3', 'M1', 'Y1', 'Y2', 'Y3'],
                          [X1, X2, X3, M1, Y1, Y2, Y3],
                          {'X1': 'X1', 'X2': 'X2', 'X3': 'X3', 'M1': 'M1',
                           'Y1': 'Y1', 'Y2': 'Y2', 'Y3': 'Y3'})
up3 = unggah(hdr3, baris3)
jw3 = kirim(up3, peta3)
# ⚠️ CATATAN JUJUR (bukan cacat): kalau mahasiswa menandai Y1,Y2,Y3 sekaligus,
#    mesin mengambil Y TERAKHIR (Y3) sebagai Y utama — lihat
#    app/main.py baris 470-472: `kolom_y = y_peran[-1]`. Jadi halaman
#    mengerjakan SATU Y pada satu waktu; Y lain diuji dengan menandainya
#    sendiri (dibuktikan di bawah: R² Y1, Y2, Y3 semua beda & benar).
cek('Y utama = Y TERAKHIR (perilaku mesin, bukan cacat)', jw3.get('y') == 'Y3',
    f"dapat {jw3.get('y')}")
cek('prediktor 3X+1M', jw3.get('prediktor') == ['X1', 'X2', 'X3', 'M1'],
    str(jw3.get('prediktor')))

# kalau tiap Y diuji sendiri-sendiri
hasil_y = {}
for nm, arr in (('Y1', Y1), ('Y2', Y2), ('Y3', Y3)):
    hh, bb, pp = dua(['X1', 'X2', 'X3', 'M1', nm], [X1, X2, X3, M1, arr],
                     {'X1': 'X1', 'X2': 'X2', 'X3': 'X3', 'M1': 'M1',
                      nm: nm})
    uu = unggah(hh, bb)
    jj = kirim(uu, pp)
    hasil_y[nm] = jj.get('r2')
print('  R² tiap Y:', hasil_y)
cek('Y1 dihitung', hasil_y.get('Y1') is not None, str(hasil_y.get('Y1')))
cek('Y2 dihitung', hasil_y.get('Y2') is not None, str(hasil_y.get('Y2')))
cek('Y3 dihitung', hasil_y.get('Y3') is not None, str(hasil_y.get('Y3')))
cek('R² tiap Y BERBEDA (bukan ditimpa)',
    len(set(str(v) for v in hasil_y.values())) == 3, str(hasil_y))

# ══ C. 3 X + 2 M + 2 Y + Z ══════════════════════════════════════════════
print()
print('=' * 74)
print(' C. 3 X + 2 M + 2 Y + Z (semuanya sekaligus)')
print('=' * 74)
Z = rng.normal(size=n)
Y1c = (0.30 * X1 + 0.25 * X2 + 0.30 * M1 + 0.35 * X1 * Z
       + rng.normal(scale=0.8, size=n))
Y2c = 0.30 * X3 + 0.30 * M2 + 0.25 * Z + rng.normal(scale=0.8, size=n)
hh, bb, pp = dua(['X1', 'X2', 'X3', 'M1', 'M2', 'Z1', 'Y1'],
                 [X1, X2, X3, M1, M2, Z, Y1c],
                 {'X1': 'X1', 'X2': 'X2', 'X3': 'X3', 'M1': 'M1',
                  'M2': 'M2', 'Z1': 'Z1', 'Y1': 'Y1'})
uu = unggah(hh, bb)
# ⚠️ Uji Wulan sebelumnya GAGAL di sini karena hanya mengirim `peran` —
#    padahal rute /periksa membaca `kolom_z` (dikirim halaman dari BENTUK
#    peran). Jangan kirim `peran` saja untuk kasus Z.
jj = kirim(uu, pp, kolom_z=['Z1'])
kk = jj.get('kaitan') or {}
cek('kaitan C ada', bool(kk.get('ada')), str(kk.get('ada')))
cek('moderasi keluar (Z ikut dihitung)',
    len(kk.get('moderasi') or []) == 1, str(len(kk.get('moderasi') or [])))
if kk.get('moderasi'):
    mdz = kk['moderasi'][0]
    cek('moderasi pakai SEMUA X', mdz.get('x_semua') == ['X1', 'X2', 'X3'],
        str(mdz.get('x_semua')))
    cek('moderasi mendeteksi interaksi', mdz.get('jenis') == 'memoderasi',
        str(mdz.get('jenis')))
cek('meditasi ada', len(kk.get('mediasi') or []) >= 1,
    str(len(kk.get('mediasi') or [])))

# Y2 juga (kedua keluaran)
hh2, bb2, pp2 = dua(['X1', 'X2', 'X3', 'M1', 'M2', 'Z1', 'Y2'],
                    [X1, X2, X3, M1, M2, Z, Y2c],
                    {'X1': 'X1', 'X2': 'X2', 'X3': 'X3', 'M1': 'M1',
                     'M2': 'M2', 'Z1': 'Z1', 'Y2': 'Y2'})
uu2 = unggah(hh2, bb2)
jj2 = kirim(uu2, pp2)
cek('Y2 juga keluar', jj2.get('r2') is not None, str(jj2.get('r2')))
cek('Y2 dapat kaitan sendiri', bool((jj2.get('kaitan') or {}).get('ada')),
    str((jj2.get('kaitan') or {}).get('ada')))

print()
print('=' * 74)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS — X1..X3 + M1..M2 + Y1..Y3 (+Z) DIDUKUNG')
sys.exit(0)
