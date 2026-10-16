"""Uji pemeriksa peran kolom — WAJIB TERBUKTI BISA GAGAL.

Aturan induk: setiap uji harus terbukti bisa gagal. Di akhir, fungsi SENGAJA
dirusak → uji HARUS menangkapnya.
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from app.diagnosis import periksa_peran, rapikan_peran  # noqa: E402

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


KOLOM = ['KP1', 'KP2', 'KP3', 'H1', 'H2', 'CM1', 'CM2', 'K1', 'K2']

print('=' * 72)
print('  UJI — PEMERIKSA PERAN KOLOM (X / M / Z / Y)')
print('=' * 72)

# ── 1. Kasus SEHAT: mediasi sederhana ────────────────────────────────────
print('\n[1] Kasus sehat — mediasi (3 X-indikator, 2 M, 2 Y)')
p = {'KP1': 'X1', 'KP2': 'X1', 'KP3': 'X1',
     'H1': 'X2', 'H2': 'X2',
     'CM1': 'M1', 'CM2': 'M1',
     'K1': 'Y1', 'K2': 'Y1'}
r = periksa_peran(KOLOM, p)
cek('boleh lanjut', r['boleh_lanjut'] is True)
cek('tanpa masalah', len(r['masalah']) == 0, str(r['masalah']))
cek('tanpa tanya', len(r['tanya']) == 0, str(r['tanya']))
cek('kelompok X1 = 3 kolom', len(r['kelompok']['X1']) == 3)
cek('kelompok M1 = 2 kolom', len(r['kelompok']['M1']) == 2)
cek('ringkas menyebut perantara', 'perantara (M)' in r['ringkas'])
cek('istilah X = "penyebab" (satu bahasa dengan halaman)',
    'penyebab (X)' in r['ringkas'], r['ringkas'])

# ── 2. Ada kolom belum ditandai → DITOLAK ────────────────────────────────
print('\n[2] Kolom belum ditandai → harus DITOLAK')
kurang = dict(p)
del kurang['K2']
r = periksa_peran(KOLOM, kurang)
cek('TIDAK boleh lanjut', r['boleh_lanjut'] is False)
cek('jenis = belum_ditandai',
    any(m['jenis'] == 'belum_ditandai' for m in r['masalah']))
cek('pesannya sebut kolomnya', 'K2' in r['ringkas'])

# ── 3. Tidak ada Y → DITOLAK ─────────────────────────────────────────────
print('\n[3] Tanpa Y → harus DITOLAK')
tanpa_y = {k: ('X1' if k != 'K2' else 'X1') for k in KOLOM}
r = periksa_peran(KOLOM, tanpa_y)
cek('TIDAK boleh lanjut', r['boleh_lanjut'] is False)
cek('jenis = tanpa_y', any(m['jenis'] == 'tanpa_y' for m in r['masalah']))

# ── 4. Tidak ada X → DITOLAK ─────────────────────────────────────────────
print('\n[4] Tanpa X → harus DITOLAK')
tanpa_x = {k: 'Y1' for k in KOLOM}
r = periksa_peran(KOLOM, tanpa_x)
cek('TIDAK boleh lanjut', r['boleh_lanjut'] is False)
cek('jenis = tanpa_x', any(m['jenis'] == 'tanpa_x' for m in r['masalah']))

# ── 5. Peran ngawur → DITOLAK ────────────────────────────────────────────
print('\n[5] Peran ngawur ("A1") → harus DITOLAK')
ngawur = dict(p)
ngawur['K1'] = 'A1'
r = periksa_peran(KOLOM, ngawur)
cek('TIDAK boleh lanjut', r['boleh_lanjut'] is False)
cek('jenis = peran_tak_dikenal',
    any(m['jenis'] == 'peran_tak_dikenal' for m in r['masalah']))

# ── 6. Kolom asing (bukan dari berkas) → DITOLAK ─────────────────────────
print('\n[6] Kolom asing → harus DITOLAK')
asing = dict(p)
asing['TIDAK_ADA'] = 'X9'
r = periksa_peran(KOLOM, asing)
cek('TIDAK boleh lanjut', r['boleh_lanjut'] is False)
cek('jenis = kolom_asing',
    any(m['jenis'] == 'kolom_asing' for m in r['masalah']))

# ── 7. >1 M → TANYA paralel/berjenjang (boleh lanjut) ────────────────────
print('\n[7] 2 perantara → TANYA, tapi boleh lanjut')
dua_m = dict(p)
dua_m['CM2'] = 'M2'
r = periksa_peran(KOLOM, dua_m)
cek('boleh lanjut', r['boleh_lanjut'] is True)
cek('ada pertanyaan bentuk_mediasi',
    any(t['jenis'] == 'bentuk_mediasi' for t in r['tanya']))
cek('pilihannya paralel & berjenjang',
    any(t.get('pilihan') == ['paralel', 'berjenjang'] for t in r['tanya']))

# ── 8. Nomor melompat (X1, X3 — X2 TIDAK ADA) → TANYA ────────────────────
print('\n[8] Nomor X melompat (X1, X3 — tanpa X2) → TANYA')
lompat = {'KP1': 'X1', 'KP2': 'X1', 'KP3': 'X3',
          'H1': 'X3', 'H2': 'X3', 'CM1': 'M1', 'CM2': 'M1',
          'K1': 'Y1', 'K2': 'Y1'}
r = periksa_peran(KOLOM, lompat)
cek('nomor X benar-benar melompat',
    sorted(int(p[1:]) for p in r['kelompok'] if p.startswith('X')) == [1, 3],
    str(sorted(r['kelompok'])))
cek('boleh lanjut', r['boleh_lanjut'] is True)
cek('ada pertanyaan nomor_melompat',
    any(t['jenis'] == 'nomor_melompat' for t in r['tanya']),
    str([t['jenis'] for t in r['tanya']]))

# ── 8b. Nomor TIDAK melompat (X1, X2, X3) → JANGAN tanya ────────────────
print('\n[8b] Nomor X urut (X1, X2, X3) → JANGAN protes')
urut = dict(p)
r = periksa_peran(KOLOM, urut)
cek('TIDAK ada nomor_melompat',
    not any(t['jenis'] == 'nomor_melompat' for t in r['tanya']),
    str([t['jenis'] for t in r['tanya']]))

# ── 9. Konstruk 1 kolom → TANYA (ringan) ─────────────────────────────────
print('\n[9] Konstruk cuma 1 kolom → TANYA ringan')
tipis = {'KP1': 'X1', 'KP2': 'X1', 'KP3': 'X1',
         'H1': 'X2', 'H2': 'X2', 'CM1': 'M1', 'CM2': 'M1',
         'K1': 'Y1', 'K2': 'Y2'}
r = periksa_peran(KOLOM, tipis)
cek('boleh lanjut', r['boleh_lanjut'] is True)
cek('ada pertanyaan satu_kolom',
    any(t['jenis'] == 'satu_kolom' for t in r['tanya']))

# ── 10. rapikan_peran: 'x1' → 'X1', buang kosong ─────────────────────────
print('\n[10] rapikan_peran — huruf kecil & entri kosong')
r = rapikan_peran({'KP1': 'x1', 'KP2': '', 'KP3': None, 'H1': '-'})
cek('huruf kecil jadi besar', r.get('KP1') == 'X1')
cek('kosong dibuang', 'KP2' not in r and 'KP3' not in r and 'H1' not in r)

# ── 11. Urutan kolom ikut BERKAS, bukan urutan dict ──────────────────────
print('\n[11] Urutan kelompok ikut urutan berkas')
acak = {'K2': 'Y1', 'K1': 'Y1', 'CM2': 'M1', 'CM1': 'M1',
        'H2': 'X2', 'H1': 'X2', 'KP3': 'X1', 'KP2': 'X1', 'KP1': 'X1'}
r = periksa_peran(KOLOM, acak)
cek('X1 urut sesuai berkas', r['kelompok']['X1'] == ['KP1', 'KP2', 'KP3'])
cek('Y1 urut sesuai berkas', r['kelompok']['Y1'] == ['K1', 'K2'])

# ── 12. Z (penguat) diterima ─────────────────────────────────────────────
print('\n[12] Z (penguat) diterima mesin')
z = dict(p)
z['H2'] = 'Z1'
r = periksa_peran(KOLOM, z)
cek('boleh lanjut', r['boleh_lanjut'] is True)
cek('Z1 terbaca', 'Z1' in r['kelompok'])
cek('ringkas sebut penguat', 'penguat (Z)' in r['ringkas'])

# ── 13. Tag HTML MENTAH di dalam string JS = kode tumpah jadi teks ───────
# Terukur 21Sep26: Wulan tulis '</div>' langsung di dalam string JS →
# gerbang_tag_skrip menangkap 4 pelanggaran → kode TUMPAH jadi teks di
# halaman walaupun HTTP 200 tetap hijau. HARUS '<\/div>'.
# CATATAN PENTING: yang dicari HANYA di dalam <script> (bukan HTML biasa,
# yang memang punya tag mentah dan itu WAJAR).
print('\n[13] Tidak ada tag HTML mentah di dalam string JS (template)')
import re as _re
_tpl = Path(__file__).resolve().parent / 'app' / 'templates' / 'diagnosis.html'
_isi = _tpl.read_text()
_awal = _isi.find('<script')
_akhir = _isi.rfind('</script>')
_js = _isi[_awal:_akhir] if _awal >= 0 and _akhir > _awal else ''
_pola = _re.compile(r"'[^'\n]*<(?P<tag>/[a-zA-Z][^<>]*)>")
_temuan = []
for _m in _pola.finditer(_js):
    _temuan.append('<' + _m.group('tag') + '>')
cek('tidak ada tag penutup mentah di string JS', not _temuan,
    ' · '.join(_temuan[:5]))

print('\n' + '=' * 72)
print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
if CATAT:
    print('  Yang gagal: ' + ' · '.join(CATAT))
print('=' * 72)

sys.exit(1 if GAGAL else 0)
