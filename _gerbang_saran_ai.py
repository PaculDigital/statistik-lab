"""Uji perbaikan saran AI /kualitatif — SEBAB jujur + coba-ulang + max_tokens.

Gerbang ini memakai BALASAN TIRUAN (tanpa biaya AI), lalu satu uji HIDUP.
Bagian G = uji BERGIGI: kembalikan akar lama, gerbang WAJIB gagal.
"""
import sys, json, re, types
sys.path.insert(0, '/app')
from app.main import _teks_dari_balasan, _sebab_kosong, SARAN_MAX_TOKEN

LULUS = GAGAL = 0
def cek(nama, ok, info=''):
    global LULUS, GAGAL
    if ok:
        LULUS += 1; print('  LULUS ' + nama)
    else:
        GAGAL += 1; print('  GAGAL ' + nama + (f'  -> {info}' if info else ''))

# ── balasan tiruan ────────────────────────────────────────────────────
def balasan(finish='stop', content='', pikir=''):
    m = {'content': content}
    if pikir: m['reasoning_content'] = pikir
    return json.dumps({'choices': [{'finish_reason': finish, 'index': 0, 'message': m}]})

KOSONG_PIKIR = balasan('length', '', 'The user wants short codes (2-4 words)...')
KOSONG_PLAIN = balasan('length', '')
FILTER = balasan('content_filter', '')
ISI = balasan('stop', 'Potongan 1: Responsivitas Staf')

print('=== A. _sebab_kosong: sebab DIBACA dari balasan ===')
s = _sebab_kosong(KOSONG_PIKIR)
cek('A1 kosong karena token + ada reasoning -> sebut jatah token & berpikir',
    'jatah token' in s and 'berpikir' in s, s)
cek('A2 sebab menyebut jalan keluar (mode manual)', 'manual' in s, s)
s2 = _sebab_kosong(KOSONG_PLAIN)
cek('A3 kosong token TANPA reasoning -> sebut jatah token, TIDAK bilang berpikir',
    'jatah token' in s2 and 'berpikir' not in s2, s2)
s3 = _sebab_kosong(FILTER)
cek('A4 content_filter -> sebut penyaring isi', 'penyaring' in s3, s3)
cek('A5 mentah kosong -> tidak meledak', bool(_sebab_kosong('')), '')
cek('A6 mentah bukan JSON -> tidak meledak', bool(_sebab_kosong('<html>502</html>')), '')
cek('A7 balasan berisi -> sebab tetap kalimat (tak dipakai)', isinstance(_sebab_kosong(ISI), str), '')

print()
print('=== B. Jatah token dinaikkan dari 800 ===')
cek('B1 SARAN_MAX_TOKEN > 800 (800 terbukti bisa kosong)', SARAN_MAX_TOKEN > 800, SARAN_MAX_TOKEN)
cek('B2 bisa diatur lewat env', 'SARAN_MAX_TOKEN' in open('/app/app/main.py').read(), 'tidak ada env')

print()
print('=== C. Rute: balasan kosong TIDAK lagi berbunyi "HTTP 502" polos ===')
src = open('/app/app/main.py').read()
cek('C1 rute memakai _sebab_kosong', '_sebab_kosong(mentah)' in src, 'tidak dipakai')
cek('C2 ada coba-ulang SEKALI saat kehabisan token',
    "if 'jatah token' in sebab" in src and 'SARAN_MAX_TOKEN * 2' in src, 'tidak ada coba-ulang')
cek('C3 max_tokens=800 tidak ada lagi di rute saran',
    "'max_tokens': 800" not in src, 'masih 800')

print()
print('=== D. Layar: galat non-JSON dibaca sebagai SEBAB ===')
layar = open('/app/app/templates/kualitatif.html').read()
cek('D1 layar periksa content-type', "content-type" in layar, 'tidak diperiksa')
cek('D2 ada kalimat sebab untuk 502/503/504', 'r.status === 502' in layar, 'tidak ada')
cek('D3 tidak lagi "d.sebab || (HTTP + status)" polos',
    "d.sebab || ('HTTP ' + r.status)" not in layar, 'masih polos')

print()
print('=== F. MATIKAN BERPIKIR (putusan Bos 21Okt26: "reasoning = false aja") ===')
#  AKAR: model reasoning memakai token untuk `reasoning_content` DULU.
#  Terukur: max_tokens=200 TANPA param -> content KOSONG finish=length.
#  Dengan enable_thinking=False -> content TERISI finish=stop, pikir=0.
cek('F1 payload utama memuat enable_thinking', "'enable_thinking': False" in src, 'tidak ada')
cek('F2 payload coba-ulang JUGA memuat (kalau lupa, coba-ulang tak menolong)',
    src.count("'enable_thinking': False") >= 2, f'hanya {src.count("enable_thinking")}×')

print()
print('=== E. Uji HIDUP: panggil rute dengan prompt asli layar ===')
try:
    import urllib.request as u
    prompt = ('KONTEKS PENELITIAN (jadikan acuan utama, jangan mengarang di luar ini):\\n'
              '- Judul: Pengaruh Mutu Layanan terhadap Kepuasan Pelanggan\\n'
              '- Fokus penelitian: mutu layanan\\n'
              '\\nBerikan USULAN KODE (nama pendek, 2-4 kata) untuk tiap potongan berikut. '
              'Format: "Potongan N: kode". Jangan menjelaskan panjang-panjang.\\n'
              'Potongan 1 (I1): Pelayanan cepat dan ramah, staf responsif\\n'
              'Potongan 2 (I2): Fasilitas ruang tunggu kurang memadai')
    req = u.Request('http://127.0.0.1:8000/api/kualitatif/saran',
                    data=json.dumps({'prompt': prompt}).encode(),
                    headers={'Content-Type': 'application/json'})
    r = u.urlopen(req, timeout=180)
    d = json.loads(r.read().decode())
    cek('E1 rute menjawab 200 + boleh', r.status == 200 and d.get('boleh') is True, str(d)[:150])
    cek('E2 saran ADA isinya', len((d.get('saran') or '').strip()) > 10, repr(d.get('saran'))[:120])
    cek('E3 saran menyebut Potongan/kode', 'Potongan' in (d.get('saran') or ''), (d.get('saran') or '')[:100])
except Exception as e:
    cek('E1 uji hidup', False, f'{type(e).__name__} {e}')

print()
print('=== G. UJI BERGIGI: kembalikan akar lama -> gerbang WAJIB GAGAL ===')
#  G1: kembalikan max_tokens=800 dan hapus coba-ulang -> C1/C2/C3 harus gagal
src_lama = src.replace('_sebab_kosong(mentah)', "'AI menjawab tapi isinya kosong.'") \
              .replace("'max_tokens': SARAN_MAX_TOKEN,", "'max_tokens': 800,")
c1 = '_sebab_kosong(mentah)' in src_lama
c3 = "'max_tokens': 800" not in src_lama
cek('G1 suntik akar lama (sebab polos + 800) -> C1 & C3 jadi GAGAL',
    (not c1) and (not c3), f'c1={c1} c3={c3}')
#  G2: kembalikan layar lama
layar_lama = layar.replace("const jenis = (r.headers.get('content-type') || '');", '')
cek('G2 suntik layar lama -> D1 jadi GAGAL', "content-type" not in layar_lama, 'tak tertangkap')
#  G3: sebab_kosong untuk kasus reasoning harus BERBEDA dari kasus biasa
beda = _sebab_kosong(KOSONG_PIKIR) != _sebab_kosong(KOSONG_PLAIN)
cek('G3 sebab reasoning != sebab biasa (tidak digabung buta)', beda, 'sama')

print()
print(f'RINGKAS: {LULUS} LULUS / {GAGAL} GAGAL')
sys.exit(1 if GAGAL else 0)
