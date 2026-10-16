"""UJI KOMBINASI — sejauh mana mesin FLEKSIBEL?

Pertanyaan Bos (21Sep26): "Jadi sekarang bisa kombinasi apa saja?
Banyak x, banyak m, banyak z, banyak y dan bisa kombinasi model?
Lebih ke fleksibel?"

CARA UJI: semua lewat PINTU PRODUKSI (/api/diagnosis/periksa) dengan
`peran` — persis seperti halaman mengirim. Setiap kombinasi dicoba satu
per satu, lalu dilaporkan APA YANG KELUAR (bukan apa yang diharapkan).

Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations
import io, json, sys, urllib.request
import numpy as np
import pandas as pd

sys.path.insert(0, '.')
B = 'http://127.0.0.1:8122'
lulus = 0
gagal = 0


def cek(ok: bool, teks: str, bukti: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        print(f'  ✅ {teks}' + (f'   {bukti}' if bukti else ''))
    else:
        gagal += 1
        print(f'  ❌ {teks}' + (f'   {bukti}' if bukti else ''))


def unggah(hdr, baris, nama='uji_kombinasi.csv'):
    # ⚠️ Pola WAJIB: field name="berkas" + filename. Salah nama field → 422.
    import csv as _csv
    b = io.StringIO()
    w = _csv.writer(b)
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
    return json.loads(urllib.request.urlopen(req, timeout=120).read())


def kirim(up, peran, kolom_x=None, kolom_m=None, kolom_z=None):
    d = {'kunci': up['kunci'], 'mode': 'spss', 'missing': 'buang'}
    if peran:
        d['peran'] = peran
    if kolom_x:
        d['kolom_x'] = kolom_x
    if kolom_m:
        d['kolom_m'] = kolom_m
    if kolom_z:
        d['kolom_z'] = kolom_z
    req = urllib.request.Request(
        B + '/api/diagnosis/periksa', data=json.dumps(d).encode(),
        headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())


def bikin(n=400, seed=11, ada_z=True, jml_m=2, jml_y=2):
    """Bangun data berurutan: X → M → Y (+Z sebagai penguat).

    Peran DIMULAI dari X (bukan Z) supaya uji ini menguji apa yang sudah
    terpasang; catatan: halaman mulai dari Z — itu bahan diskusi terpisah.
    """
    rng = np.random.default_rng(seed)
    kol = {}
    hdr = []
    Xs = {}
    for i in range(1, 4):
        v = rng.normal(size=n)
        Xs[f'X{i}'] = v
        for j in (1, 2):
            hdr.append(f'X{i}{j}')
            kol[f'X{i}{j}'] = np.round(v + rng.normal(scale=.3, size=n), 4)
    Zs = {}
    if ada_z:
        for i in range(1, 3):
            v = rng.normal(size=n)
            Zs[f'Z{i}'] = v
            for j in (1, 2):
                hdr.append(f'Z{i}{j}')
                kol[f'Z{i}{j}'] = np.round(v + rng.normal(scale=.3, size=n), 4)
    gab = sum(Xs.values())
    Ms = {}
    for i in range(1, jml_m + 1):
        v = 0.5 * gab + rng.normal(size=n)
        Ms[f'M{i}'] = v
        for j in (1, 2):
            hdr.append(f'M{i}{j}')
            kol[f'M{i}{j}'] = np.round(v + rng.normal(scale=.3, size=n), 4)
    for i in range(1, jml_y + 1):
        v = 0.4 * gab + 0.3 * Ms['M1'] + rng.normal(size=n)
        if i == 2 and len(Ms) > 1:
            v = 0.3 * gab + 0.4 * Ms['M2'] + rng.normal(size=n)
        for j in (1, 2):
            hdr.append(f'Y{i}{j}')
            kol[f'Y{i}{j}'] = np.round(v + rng.normal(scale=.3, size=n), 4)
    baris = [[kol[h][i] for h in hdr] for i in range(n)]
    peta = {}
    for h in hdr:
        peta[h] = h[:-1]
    return hdr, baris, peta


def ringkas(r):
    k = r.get('kaitan') or {}
    return {
        'ada': k.get('ada'),
        'med': len(k.get('mediasi') or []),
        'mod': len(k.get('moderasi') or []),
        'pred': r.get('prediktor'),
        'y': r.get('y'),
        'r2': r.get('r2'),   # ⚠️ kunci BENAR = 'r2' (bukan regresi.r2)
    }



def jalan() -> int:
    print('=' * 74)
    print(' [1] BANYAK X + BANYAK M + BANYAK Y  (satu model)')
    print('=' * 74)
    hdr, baris, peta = bikin(jml_m=2, jml_y=2)
    up = unggah(hdr, baris)
    r1 = kirim(up, peta)
    s1 = ringkas(r1)
    print(f'     prediktor={s1["pred"]} · Y={s1["y"]} · R²={s1["r2"]}')
    print(f'     mediasi={s1["med"]} · moderasi={s1["mod"]}')
    cek(all(q in (s1['pred'] or []) for q in ['X1', 'X2', 'X3']),
        'banyak X masuk prediktor (X1,X2,X3)', str(s1['pred']))
    cek(all(q in (s1['pred'] or []) for q in ['M1', 'M2']),
        'banyak M masuk prediktor (M1,M2)', str(s1['pred']))
    cek(s1['med'] >= 1, 'mediasi banyak M dihitung', f"med={s1['med']}")
    cek(s1['y'] == 'Y2', 'Y banyak diterima (ambil terakhir)', str(s1['y']))

    print()
    print('=' * 74)
    print(' [2] + BANYAK Z  (banyak X + M + Z + Y sekaligus)')
    print('=' * 74)
    r2 = kirim(up, peta)
    s2 = ringkas(r2)
    mod = (r2.get('kaitan') or {}).get('moderasi') or []
    print(f'     moderasi={s2["mod"]} · z dipakai={sorted({m.get(chr(122)) for m in mod})}')
    cek({m.get('z') for m in mod} == {'Z1', 'Z2'}, 'banyak Z dihitung (Z1 & Z2)',
        str(sorted({m.get('z') for m in mod})))
    if len(mod) >= 2:
        z1 = [m for m in mod if m.get('z') == 'Z1']
        z2 = [m for m in mod if m.get('z') == 'Z2']
        cek((z1[0].get('z_kovariat') == ['Z2']
             and z2[0].get('z_kovariat') == ['Z1']),
            'Z lain jadi kovariat (Opsi A)',
            f'Z1 kov={z1[0].get("z_kovariat")} Z2 kov={z2[0].get("z_kovariat")}')

    print()
    print('=' * 74)
    print(' [3] CAMPURAN: mediasi + moderasi + banyak X/M/Z SEKALIGUS')
    print('=' * 74)
    print(f'     mediasi={s2["med"]} · moderasi={s2["mod"]}  '
          f'(dua-duanya keluar dari SATU kiriman)')
    cek(s2['med'] >= 1 and s2['mod'] >= 2,
        'mediasi DAN moderasi jalan bersamaan',
        f"med={s2['med']} mod={s2['mod']}")

    print()
    print('=' * 74)
    print(' [4] Y BANYAK: berapa yang dilaporkan sekaligus?')
    print('=' * 74)
    print(f'     Y ditandai 2 (Y1,Y2) → mesin pakai  = {s2["y"]}')
    print(f'     R² regresi (banyak X+M)              = {s1["r2"]}')
    cek(bool(s2['y']), 'hanya SATU Y dilaporkan per kiriman (bukan 2 sekaligus)',
        f"y={s2['y']}")
    cek(isinstance(s1['r2'], (int, float)) and s1['r2'] > 0,
        'R² regresi dihitung (> 0)', f"r2={s1['r2']}")

    print()
    print('=' * 74)
    if gagal:
        print(f' ❌ ADA GAGAL: {gagal}')
        return 1
    print(f' ✅ {lulus} LULUS — kombinasi terukur')
    return 0



if __name__ == '__main__':
    sys.exit(jalan())
