"""Uji E2E PERAN KOLOM lewat web sungguhan (HTTP, bukan tiruan).

Menguji apa yang SUNGGUHAN terjadi:
  1. unggah berkas → dapat kunci + kolom
  2. rute /api/diagnosis/periksa-peran menjawab benar
  3. halaman memuat elemen peran (daftar-peran, ringkas-peran, tb-periksa-peran)
  4. rute MENOLAK kalau belum ada Y
  5. rute MENOLAK kalau peran ngawur
  6. rute TANYA kalau ada 2 M
"""
import io
import json
import sys
import urllib.request

BASE = 'http://127.0.0.1:8122'
LULUS = GAGAL = 0
CATAT: list[str] = []


def cek(nama: str, syarat: bool, catatan: str = ''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        CATAT.append(nama)
        print(f'  ❌ {nama}  {catatan}')


def _post_json(url: str, data: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or '{}')


def _get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _unggah_csv():
    """Bikin CSV kecil lalu unggah lewat multipart."""
    import uuid
    kolom = ['KP1', 'KP2', 'KP3', 'H1', 'H2', 'CM1', 'K1', 'K2']
    baris = [';'.join(kolom)]
    for i in range(40):
        baris.append(';'.join(str(3 + ((i + j) % 3)) for j in range(len(kolom))))
    isi = ('\n'.join(baris)).encode()

    batas = '----' + uuid.uuid4().hex
    tubuh = b''
    tubuh += f'--{batas}\r\n'.encode()
    tubuh += (b'Content-Disposition: form-data; name="berkas"; '
              b'filename="data_uji.csv"\r\n')
    tubuh += b'Content-Type: text/csv\r\n\r\n'
    tubuh += isi + b'\r\n'
    tubuh += f'--{batas}--\r\n'.encode()

    req = urllib.request.Request(
        BASE + '/api/diagnosis/unggah', data=tubuh,
        headers={'Content-Type': f'multipart/form-data; boundary={batas}'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


print('=' * 74)
print('  UJI E2E — PERAN KOLOM (web sungguhan)')
print('=' * 74)

# ── 1. Halaman /klinik memuat elemen peran ───────────────────────────────
print('\n[1] Halaman /klinik memuat elemen peran')
kode, html = _get(BASE + '/klinik')
cek('HTTP 200', kode == 200, str(kode))
for nama_id in ('daftar-peran', 'ringkas-peran', 'pesan-peran',
                'tb-periksa-peran', 'kotak-peran-baru'):
    cek(f'ada #{nama_id}', f'id="{nama_id}"' in html)
cek('ada fungsi periksaPeranSekarang', 'function periksaPeranSekarang' in html)
cek('ada fungsi bangunDaftarPeran', 'function bangunDaftarPeran' in html)
cek('tidak ada namaKolom dobel',
    html.count('function namaKolom()') == 1,
    f'jumlah={html.count("function namaKolom()")}')

# ── 2. Unggah berkas ─────────────────────────────────────────────────────
print('\n[2] Unggah berkas CSV (40 baris, 8 kolom)')
try:
    d = _unggah_csv()
    kunci = d.get('kunci')
    kolom = [k['nama'] for k in d.get('kolom', [])]
    cek('dapat kunci', bool(kunci))
    cek('8 kolom terbaca', len(kolom) == 8, str(kolom))
except Exception as e:                                    # noqa: BLE001
    cek('unggah berhasil', False, repr(e))
    print('\nTIDAK BISA LANJUT — unggah gagal.')
    sys.exit(1)

# ── 3. Peran SEHAT → boleh lanjut ────────────────────────────────────────
print('\n[3] Peran sehat (mediasi) → boleh lanjut')
sehat = {'KP1': 'X1', 'KP2': 'X1', 'KP3': 'X1', 'H1': 'X2', 'H2': 'X2',
         'CM1': 'M1', 'K1': 'Y1', 'K2': 'Y1'}
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': sehat})
cek('HTTP 200', kode == 200, f'{kode} {r}')
cek('boleh lanjut', r.get('boleh_lanjut') is True, str(r.get('masalah')))
cek('tanpa masalah', not r.get('masalah'), str(r.get('masalah')))
cek('ringkas sebut perantara', 'perantara (M)' in (r.get('ringkas') or ''))

# ── 4. Tanpa Y → DITOLAK ─────────────────────────────────────────────────
print('\n[4] Tanpa Y → server MENOLAK')
tanpa_y = {k: 'X1' for k in kolom}
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': tanpa_y})
cek('HTTP 200', kode == 200, str(kode))
cek('boleh_lanjut = False', r.get('boleh_lanjut') is False)
cek('masalah = tanpa_y',
    any(m['jenis'] == 'tanpa_y' for m in r.get('masalah', [])),
    str(r.get('masalah')))

# ── 5. Peran ngawur → DITOLAK ────────────────────────────────────────────
print('\n[5] Peran ngawur "A1" → server MENOLAK')
ngawur = dict(sehat)
ngawur['K1'] = 'A1'
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': ngawur})
cek('boleh_lanjut = False', r.get('boleh_lanjut') is False)
cek('masalah = peran_tak_dikenal',
    any(m['jenis'] == 'peran_tak_dikenal' for m in r.get('masalah', [])),
    str(r.get('masalah')))

# ── 6. Belum ditandai semua → DITOLAK ────────────────────────────────────
print('\n[6] Kolom belum ditandai → server MENOLAK')
kurang = {'KP1': 'X1', 'KP2': 'X1', 'KP3': 'X1'}
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': kurang})
cek('boleh_lanjut = False', r.get('boleh_lanjut') is False)
cek('masalah = belum_ditandai',
    any(m['jenis'] == 'belum_ditandai' for m in r.get('masalah', [])),
    str(r.get('masalah')))

# ── 7. Dua M → TANYA, tapi boleh lanjut ──────────────────────────────────
print('\n[7] Dua perantara → TANYA (boleh lanjut)')
dua_m = dict(sehat)
dua_m['H1'] = 'M1'
dua_m['H2'] = 'M2'
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': dua_m})
cek('boleh lanjut', r.get('boleh_lanjut') is True, str(r.get('masalah')))
cek('ada pertanyaan bentuk_mediasi',
    any(t['jenis'] == 'bentuk_mediasi' for t in r.get('tanya', [])),
    str(r.get('tanya')))

# ── 8. Kunci ngawur → pesan jujur, bukan 500 ─────────────────────────────
print('\n[8] Kunci ngawur → pesan jujur (bukan HTTP 500)')
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': 'ngawur123', 'peran': sehat})
cek('HTTP 400 (bukan 500)', kode == 400, str(kode))
cek('ada pesan jelas', 'detail' in r, str(r))

# ── 9. Peran bentuk daftar (bukan dict) → ditolak rapi ───────────────────
print('\n[9] Peran berbentuk daftar → ditolak rapi (bukan 500)')
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': ['X1', 'X2']})
cek('HTTP 400 (bukan 500)', kode == 400, str(kode))

# ── 10. Peran kosong → belum ditandai, bukan 500 ─────────────────────────
print('\n[10] Peran kosong → ditolak rapi')
kode, r = _post_json(BASE + '/api/diagnosis/periksa-peran',
                     {'kunci': kunci, 'peran': {}})
cek('HTTP 200', kode == 200, str(kode))
cek('boleh_lanjut = False', r.get('boleh_lanjut') is False)
cek('masalah belum_ditandai',
    any(m['jenis'] == 'belum_ditandai' for m in r.get('masalah', [])),
    str(r.get('masalah')))

print('\n' + '=' * 74)
print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
if CATAT:
    print('  Yang gagal: ' + ' · '.join(CATAT))
print('=' * 74)
sys.exit(1 if GAGAL else 0)
