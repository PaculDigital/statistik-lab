"""UJI MODERASI: banyak X + banyak Z + banyak M — sudah didukung?

Pertanyaan Bos (21Sep26): "ini baru mediasi ya? Belum yang moderasi,
support banyak x, banyak m dan banyak z".

CARA UJI: lewat PINTU PRODUKSI (rute /api/diagnosis/periksa) — bukan
fungsi internal. Kirim berkolom-kolom sungguhan, cetak APA ADANYA hasilnya.
"""
import csv, io, json, sys, urllib.request

B = 'http://127.0.0.1:8122'
GAGAL = 0


def cek(n, ok, b=''):
    global GAGAL
    print(f"  {'✅' if ok else '❌'} {n}" + (f"   {b}" if b else ''))
    if not ok:
        GAGAL += 1


def unggah(hdr, baris):
    b = io.StringIO()
    w = csv.writer(b)
    w.writerow(hdr)
    w.writerows(baris)
    isi = b.getvalue().encode()
    bd = '----W'
    body = (b'--' + bd.encode() + b'\r\nContent-Disposition: form-data; '
            b'name="berkas"; filename="d.csv"\r\nContent-Type: text/csv\r\n\r\n'
            + isi + b'\r\n--' + bd.encode() + b'--\r\n')
    req = urllib.request.Request(
        B + '/api/diagnosis/unggah', data=body,
        headers={'Content-Type': 'multipart/form-data; boundary=' + bd})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def kirim(up, peran, kolom_z=None, kolom_m=None, kolom_x=None):
    d = {'kunci': up['kunci'], 'mode': 'spss', 'peran': peran,
         'missing': 'buang'}
    if kolom_z:
        d['kolom_z'] = kolom_z
    if kolom_m:
        d['kolom_m'] = kolom_m
    if kolom_x:
        d['kolom_x'] = kolom_x
    req = urllib.request.Request(
        B + '/api/diagnosis/periksa', data=json.dumps(d).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())


def kolom(nama, n, jml_kolom=2):
    """Buat pasangan nama a/b (biar dibaca sebagai 1 konstruk)."""
    hdr, peta = [], {}
    for nm in nama:
        for s in 'ab'[:jml_kolom]:
            hdr.append(nm + s)
            peta[nm + s] = nm
    return hdr, peta


import numpy as np

print('=' * 74)
print(' [1] MODERASI — banyak X (X1,X2,X3) × banyak Z (Z1,Z2)')
print('=' * 74)
rng = np.random.default_rng(21)
n = 350
X1, X2, X3 = (rng.normal(size=n) for _ in range(3))
Z1, Z2 = (rng.normal(size=n) for _ in range(2))
# Y bergantung X1,X2,X3,Z1,Z2 + interaksi X1×Z1 (kuat) & X2×Z2 (sedang)
Y = (0.25*X1 + 0.20*X2 + 0.15*X3 + 0.20*Z1 + 0.15*Z2
     + 0.40*X1*Z1 + 0.30*X2*Z2 + rng.normal(scale=0.9, size=n))

nama = ['X1', 'X2', 'X3', 'Z1', 'Z2', 'Y1']
hdr = []
for nm in nama:
    for s in 'ab':
        hdr.append(nm + s)
baris = []
for i in range(n):
    b = []
    for v in (X1, X2, X3, Z1, Z2, Y):
        b += [round(float(v[i]), 4), round(float(v[i]), 4)]
    baris.append(b)
peta = {h: h[:-1] for h in hdr}

up = unggah(hdr, baris)
jw = kirim(up, peta, kolom_z=['Z1', 'Z2'], kolom_m=[])
k = jw.get('kaitan') or {}
print(f"     prediktor : {jw.get('prediktor')}")
print(f"     kaitan ada: {k.get('ada')}")
print(f"     moderasi  : {len(k.get('moderasi') or [])} hasil")
for md in (k.get('moderasi') or []):
    print(f"       · {md.get('z')}: x_semua={md.get('x_semua')} "
          f"jenis={md.get('jenis')} ΔR²={md.get('delta_r2')}")

cek('moderasi ada hasilnya', len(k.get('moderasi') or []) > 0,
    str(len(k.get('moderasi') or [])))
cek('banyak X terpakai di moderasi',
    all(m.get('x_semua') == ['X1', 'X2', 'X3'] for m in (k.get('moderasi') or [])),
    str([m.get('x_semua') for m in (k.get('moderasi') or [])]))
cek('kedua Z dihitung (Z1 & Z2)',
    {m.get('z') for m in (k.get('moderasi') or [])} == {'Z1', 'Z2'},
    str({m.get('z') for m in (k.get('moderasi') or [])}))

print()
print('=' * 74)
print(' [2] MODERASI + MEDIASI sekaligus — banyak X, banyak M, banyak Z')
print('=' * 74)
rng = np.random.default_rng(22)
n = 350
X1, X2, X3 = (rng.normal(size=n) for _ in range(3))
Z1 = rng.normal(size=n)
M1 = 0.50*X1 + 0.30*X2 + rng.normal(scale=0.8, size=n)
M2 = 0.45*X2 + 0.25*X3 + rng.normal(scale=0.8, size=n)
Yb = (0.15*X1 + 0.12*X2 + 0.10*X3 + 0.30*M1 + 0.28*M2
      + 0.20*Z1 + 0.35*X1*Z1 + rng.normal(scale=0.8, size=n))

nama2 = ['X1', 'X2', 'X3', 'M1', 'M2', 'Z1', 'Y1']
hdr2 = []
for nm in nama2:
    for s in 'ab':
        hdr2.append(nm + s)
baris2 = []
for i in range(n):
    b = []
    for v in (X1, X2, X3, M1, M2, Z1, Yb):
        b += [round(float(v[i]), 4), round(float(v[i]), 4)]
    baris2.append(b)
peta2 = {h: h[:-1] for h in hdr2}

up2 = unggah(hdr2, baris2)
jw2 = kirim(up2, peta2, kolom_z=['Z1'], kolom_m=['M1', 'M2'])
k2 = jw2.get('kaitan') or {}
print(f"     prediktor : {jw2.get('prediktor')}")
print(f"     mediasi   : {len(k2.get('mediasi') or [])} hasil "
      f"({k2.get('bentuk_mediasi')})")
print(f"     moderasi  : {len(k2.get('moderasi') or [])} hasil")
for md in (k2.get('moderasi') or []):
    print(f"       · {md.get('z')}: x_semua={md.get('x_semua')} "
          f"jenis={md.get('jenis')}")
for mm in (k2.get('mediasi') or []):
    print(f"       · M={mm.get('m')}: x_semua={mm.get('x_semua')} "
          f"jenis={mm.get('jenis')}")

cek('mediasi & moderasi MUNCUL BERSAMAAN',
    len(k2.get('mediasi') or []) > 0 and len(k2.get('moderasi') or []) > 0,
    f"med={len(k2.get('mediasi') or [])} mod={len(k2.get('moderasi') or [])}")
cek('banyak M (M1 & M2) dihitung',
    {mm.get('m') for mm in (k2.get('mediasi') or [])} == {'M1', 'M2'},
    str({mm.get('m') for mm in (k2.get('mediasi') or [])}))
cek('banyak X di moderasi',
    all(m.get('x_semua') == ['X1', 'X2', 'X3']
        for m in (k2.get('moderasi') or [])),
    str([m.get('x_semua') for m in (k2.get('moderasi') or [])]))
cek('banyak X di mediasi',
    all(m.get('x_semua') == ['X1', 'X2', 'X3']
        for m in (k2.get('mediasi') or [])),
    str([m.get('x_semua') for m in (k2.get('mediasi') or [])]))

print()
print('=' * 74)
print(' [3] BERJENJANG + banyak X + Z (campuran sulit)')
print('=' * 74)
rng = np.random.default_rng(23)
n = 350
X1, X2 = rng.normal(size=n), rng.normal(size=n)
Z1 = rng.normal(size=n)
M1 = 0.55*X1 + 0.20*X2 + rng.normal(scale=0.8, size=n)
M2 = 0.50*M1 + 0.10*X1 + rng.normal(scale=0.8, size=n)
Yc = (0.10*X1 + 0.10*X2 + 0.15*M1 + 0.40*M2 + 0.20*Z1
      + 0.30*X1*Z1 + rng.normal(scale=0.8, size=n))
nama3 = ['X1', 'X2', 'M1', 'M2', 'Z1', 'Y1']
hdr3 = []
for nm in nama3:
    for s in 'ab':
        hdr3.append(nm + s)
baris3 = []
for i in range(n):
    b = []
    for v in (X1, X2, M1, M2, Z1, Yc):
        b += [round(float(v[i]), 4), round(float(v[i]), 4)]
    baris3.append(b)
peta3 = {h: h[:-1] for h in hdr3}
up3 = unggah(hdr3, baris3)
jw3 = kirim(up3, peta3, kolom_z=['Z1'], kolom_m=['M1', 'M2'])
k3 = jw3.get('kaitan') or {}
print(f"     mediasi  : {len(k3.get('mediasi') or [])} "
      f"({k3.get('bentuk_mediasi')})")
print(f"     moderasi : {len(k3.get('moderasi') or [])}")
cek('campuran (berjenjang + moderasi) jalan',
    len(k3.get('mediasi') or []) > 0 and len(k3.get('moderasi') or []) > 0,
    f"med={len(k3.get('mediasi') or [])} mod={len(k3.get('moderasi') or [])}")

print()
print('=' * 74)
print(' [4] BUKTI PERGESERAN — apakah Z lain benar-benar dikendalikan?')
print('=' * 74)
# ⚠️ DUA PELAJARAN UJI DI SINI (K-17 + K-19), jangan ulang:
#  (a) K-17 — kalau Z1 & Z2 TIDAK berkorelasi, mengendalikan Z2 MEMANG tidak
#      mengubah apa pun → uji "harus bergeser" mustahil lulus. Pakai Z2 yang
#      BERKORELASI dengan Z1 (seperti data nyata).
#  (b) K-19 — JANGAN kirim `kolom_z` berisi NAMA KONSTRUK ('Z1','Z2') ke rute.
#      Rute memakai `peran` untuk menggabung kolom seperan; kalau `kolom_z`
#      ikut dikirim, nilainya MENIMPA hasil gabungan → server mencari kolom
#      bernama 'Z1' yang TIDAK ADA di data → moderasi dihitung tanpa
#      moderator sama sekali. Jalur BENAR = kirim `peran` (seperti halaman).
rng = np.random.default_rng(77)
n = 400
Xa = rng.normal(size=n)
Za = rng.normal(size=n)
Zb = 0.75 * Za + rng.normal(scale=0.6, size=n)      # Z2 ≈ 0,78 korelasi Z1
Ya = (0.20*Xa + 0.20*Za + 0.20*Zb + 0.35*Xa*Za
      + rng.normal(scale=0.9, size=n))
hdrb = ['X1a', 'X1b', 'Za1', 'Za2', 'Zb1', 'Zb2', 'Y1a', 'Y1b']
barisb = []
for i in range(n):
    barisb.append([round(float(Xa[i]), 4), round(float(Xa[i]), 4),
                   round(float(Za[i]), 4), round(float(Za[i]), 4),
                   round(float(Zb[i]), 4), round(float(Zb[i]), 4),
                   round(float(Ya[i]), 4), round(float(Ya[i]), 4)])
# Nama kolom Z sengaja BUKAN 'Z1…' (Za1/Za2 + Zb1/Zb2) supaya uji ini
# BENAR-BENAR membuktikan penggabungan peran, bukan kebetulan nama cocok.
petab = {'X1a': 'X1', 'X1b': 'X1',
         'Za1': 'Z1', 'Za2': 'Z1',
         'Zb1': 'Z2', 'Zb2': 'Z2',
         'Y1a': 'Y1', 'Y1b': 'Y1'}
upb = unggah(hdrb, barisb)
# TANPA Z2: mahasiswa hanya menandai Z1 sebagai penguat.
peta_z1 = dict(petab)
for kk in ('Zb1', 'Zb2'):
    peta_z1[kk] = ''
tanpa_z2 = kirim(upb, peta_z1)
# DENGAN Z2: Z1 dan Z2 sama-sama ditandai → Z1 diuji dengan Z2 dikendalikan.
dengan_z2 = kirim(upb, petab)
m_a = [x for x in ((tanpa_z2.get('kaitan') or {}).get('moderasi') or [])
       if x.get('z') == 'Z1']
m_b = [x for x in ((dengan_z2.get('kaitan') or {}).get('moderasi') or [])
       if x.get('z') == 'Z1']
if m_a and m_b:
    da, db = m_a[0].get('delta_r2'), m_b[0].get('delta_r2')
    ba = (m_a[0].get('dengan_interaksi') or {}).get('interaksi', {}).get('b')
    bb = (m_b[0].get('dengan_interaksi') or {}).get('interaksi', {}).get('b')
    kov = m_b[0].get('z_kovariat')
    print(f"     kolom Z mentah   : Za1,Za2 (→Z1) · Zb1,Zb2 (→Z2)")
    print(f"     ΔR² Z1 tanpa Z2  : {da}  (b interaksi {ba})")
    print(f"     ΔR² Z1 dengan Z2 : {db}  (b interaksi {bb})")
    print(f"     z_kovariat       : {kov}")
    cek('Z1 & Z2 DIGABUNG dari 2 kolom jadi 1 moderator (bukan 4)',
        {x.get('z') for x in ((dengan_z2.get('kaitan') or {})
                              .get('moderasi') or [])} == {'Z1', 'Z2'},
        str(sorted({x.get('z') for x in ((dengan_z2.get('kaitan') or {})
                                         .get('moderasi') or [])})))
    cek('hasil Z1 BERGESER saat Z2 dikendalikan (bukti Opsi A bekerja)',
        da != db, f"{da} → {db}")
    cek('z_kovariat menyebut Z2 (bukan kolom mentahnya)', kov == ['Z2'],
        str(kov))
else:
    cek('moderasi Z1 keluar di kedua cara', False,
        f"tanpa={len(m_a)} dengan={len(m_b)}")

print()
print('=' * 74)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS — moderasi didukung: banyak X, banyak Z, banyak M')
sys.exit(0)
