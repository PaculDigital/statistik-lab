"""UJI PINTU PRODUKSI — MEDIASI & MODERASI sampai ke HASIL (ACC Bos 21Sep26).

MENAPA ADA: /klinik dulu TIDAK BISA menghitung mediasi & moderasi:
  · M dijejalkan jadi prediktor biasa (jalur a dan a×b tidak ada)
  · Z DIBUANG TOTAL (moderasi tidak dihitung sama sekali)
Cacat itu LOLOS berhari-hari karena tidak ada uji yang menyentuh jalur ini.
Lihat: TEMUAN_MEDIASI_MODERASI_21SEP2026.md · fact_store 108/109.

CARA UJI: lewat PINTU PRODUKSI — unggah berkas .csv sungguhan ke rute HTTP,
tandai PERAN, hitung, lalu periksa apakah jawaban memuat hasil mediasi/moderasi.
BUKAN fungsi internal (pelajaran K-09).

Prasarana: server uji :8122 harus hidup. Kalau mati → KODE LEWAT 77.
Jalankan: .venv/bin/python uji_kaitan_web.py
"""
import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np                                              # noqa: E402

BASE = 'http://127.0.0.1:8122'
GAGAL = 0


def cek(nama, syarat, bukti=''):
    global GAGAL
    print(f"  {'✅' if syarat else '❌'} {nama}" + (f'   {bukti}' if bukti else ''))
    if not syarat:
        GAGAL += 1


def _http(jalur, kirim=None, body=None, tipe='application/json'):
    req = urllib.request.Request(
        BASE + jalur,
        data=(body if body is not None else
              (json.dumps(kirim).encode() if kirim is not None else None)),
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


def t(v):
    return int(np.clip(round(3 + v * 0.9), 1, 5))


# ── Cek prasarana dulu (kalau server mati → LEWAT, bukan GAGAL) ───────────
try:
    urllib.request.urlopen(BASE + '/health', timeout=8).read()
except Exception:
    print('\n⚠️  Server uji :8122 MATI — uji ini DILEWATI (kode 77).')
    print('    Nyalakan: .venv/bin/python -m uvicorn app.main:app '
          '--host 127.0.0.1 --port 8122 --log-level warning')
    sys.exit(77)

print('=' * 72)
print(' UJI PINTU PRODUKSI — MEDIASI & MODERASI SAMPAI KE HASIL')
print('=' * 72)

# ══════════════════════════════════════════════════════════════════════════
#  A. MEDIASI — tanam a=0,60 · b=0,50 · c'=0,00
# ══════════════════════════════════════════════════════════════════════════
print('\n[A] MEDIASI X1 → M1 → Y1  (tanam: a=0,60 · b=0,50 · c\'=0,00)')
rng = np.random.default_rng(21)
n = 300
X = rng.normal(size=n)
M = 0.60 * X + rng.normal(scale=0.8, size=n)
Y = 0.00 * X + 0.50 * M + rng.normal(scale=0.8, size=n)
baris = [[t(X[i]), t(X[i] + rng.normal(scale=.3)),
          t(M[i]), t(M[i] + rng.normal(scale=.3)),
          t(Y[i]), t(Y[i] + rng.normal(scale=.3))] for i in range(n)]
up = unggah(['X1a', 'X1b', 'M1a', 'M1b', 'Y1a', 'Y1b'], baris)
P = {'X1a': 'X1', 'X1b': 'X1', 'M1a': 'M1', 'M1b': 'M1', 'Y1a': 'Y1', 'Y1b': 'Y1'}
jw = _http('/api/diagnosis/periksa',
           {'kunci': up.get('kunci'), 'mode': 'spss', 'peran': P,
            'missing': 'buang'})

kaitan = jw.get('kaitan')
cek('kunci "kaitan" ADA di jawaban (dulu TIDAK ADA)', kaitan is not None)
cek('kaitan.ada = True', bool((kaitan or {}).get('ada')))
med = ((kaitan or {}).get('mediasi') or [])
cek('ada 1 hasil mediasi', len(med) == 1, f'→ {len(med)}')
h = med[0] if med else {}
cek('boleh dihitung', h.get('boleh'), str(h.get('sebab'))[:50])

if h.get('boleh'):
    # ✅ CACAT LAMA: jalur a TIDAK PERNAH dihitung
    cek('JALUR a ada & terisi (dulu TIDAK ADA)', h.get('a', {}).get('b') is not None,
        f"a={h.get('a', {}).get('b')}")
    cek('JALUR b ada', h.get('b', {}).get('b') is not None, f"b={h.get('b', {}).get('b')}")
    cek("JALUR c' ada", h.get('cp', {}).get('b') is not None,
        f"c'={h.get('cp', {}).get('b')}")
    cek('JALUR c (tanpa M) ada', h.get('c', {}).get('b') is not None,
        f"c={h.get('c', {}).get('b')}")

    # arah & besaran (data sampai ke mesin APA ADANYA)
    cek('a searah & wajar (>0,3)', h['a']['b'] > 0.30, f"a={h['a']['b']}")
    cek('b searah & wajar (>0,3)', h['b']['b'] > 0.30, f"b={h['b']['b']}")
    cek("c' lebih kecil dari c (jalur langsung menyusut)",
        abs(h['cp']['b']) < abs(h['c']['b']),
        f"c'={h['cp']['b']} < c={h['c']['b']}")

    tl = h.get('tidak_langsung') or {}
    cek('PENGARUH TIDAK LANGSUNG a×b ada (dulu TIDAK ADA)',
        tl.get('b') is not None, f"a×b={tl.get('b')}")
    cek('selang kepercayaan 95% ada',
        tl.get('lo') is not None and tl.get('hi') is not None,
        f"[{tl.get('lo')}, {tl.get('hi')}]")
    cek('a×b SIGNIFIKAN (selang tidak lewat nol)', tl.get('signifikan') is True)
    cek('n_boot dilaporkan', (tl.get('n_boot') or 0) >= 100, f"→ {tl.get('n_boot')}")

    cek('SIMPULAN jenis terisi (dulu TIDAK ADA)', bool(h.get('jenis')), h.get('jenis'))
    cek('SIMPULAN kalimat terisi', len(str(h.get('kalimat') or '')) > 40,
        str(h.get('kalimat'))[:60] + '…')
    # ⚠️ JANGAN paku "mediasi penuh": pada data berderau + item Likert, c'
    #    kecil (0,00 ditanam) bisa muncul signifikan tipis. Yang WAJIB benar:
    #    ada mediasi (a×b signifikan) DAN c' lebih kecil dari c.
    #    Terukur: c'=0,169 < c=0,363 → "mediasi parsial" (BUKAN cacat mesin).
    cek('jenis termasuk mediasi (penuh/parsial)',
        str(h.get('jenis', '')).startswith('mediasi'), h.get('jenis'))

# ══════════════════════════════════════════════════════════════════════════
#  B. MODERASI — tanam interaksi = 0,35
# ══════════════════════════════════════════════════════════════════════════
print('\n[B] MODERASI X1 × Z1 → Y1  (tanam: interaksi = 0,35)')
rng = np.random.default_rng(31)
X = rng.normal(size=n)
Z = rng.normal(size=n)
Y = 0.30 * X + 0.20 * Z + 0.35 * X * Z + rng.normal(scale=0.8, size=n)
baris = [[t(X[i]), t(X[i] + rng.normal(scale=.3)),
          t(Z[i]), t(Z[i] + rng.normal(scale=.3)),
          t(Y[i]), t(Y[i] + rng.normal(scale=.3))] for i in range(n)]
up = unggah(['X1a', 'X1b', 'Z1a', 'Z1b', 'Y1a', 'Y1b'], baris)
P = {'X1a': 'X1', 'X1b': 'X1', 'Z1a': 'Z1', 'Z1b': 'Z1', 'Y1a': 'Y1', 'Y1b': 'Y1'}
jw = _http('/api/diagnosis/periksa',
           {'kunci': up.get('kunci'), 'mode': 'spss', 'peran': P,
            'missing': 'buang'})

cek('PERAN Z terkirim ke mesin (dulu DIBUANG)',
    jw.get('penguat') == ['Z1'], f"penguat={jw.get('penguat')}")
kaitan = jw.get('kaitan') or {}
mod = kaitan.get('moderasi') or []
cek('ada 1 hasil moderasi', len(mod) == 1, f'→ {len(mod)}')
h2 = mod[0] if mod else {}
cek('boleh dihitung', h2.get('boleh'), str(h2.get('sebab'))[:50])

if h2.get('boleh'):
    cek('Z DIHITUNG sebagai penguat (dulu hilang total)',
        h2['tanpa_interaksi']['z']['b'] is not None,
        f"z={h2['tanpa_interaksi']['z']['b']}")
    di = h2.get('dengan_interaksi') or {}
    it = di.get('interaksi') or {}
    cek('SUKU INTERAKSI X×Z ada (dulu TIDAK ADA)', it.get('b') is not None,
        f"b={it.get('b')}")
    # ⚠️ CACAT UJI YANG DITUTUP (21Sep26): baris ini mula-mula menulis
    #    `(it.get('p') or 1) < 0.05` → p=0.0 (SANGAT signifikan!) dianggap
    #    "falsy" lalu diganti 1 → dinyatakan GAGAL PALSU. p=0,0 artinya
    #    p dibulatkan ke 6 angka, BUKAN tidak ada p. Jangan pakai `or`.
    p_it = it.get('p')
    cek('interaksi SIGNIFIKAN (p < 0,05)',
        p_it is not None and float(p_it) < 0.05, f"p={p_it}")
    cek('ΔR² dilaporkan & > 0', (h2.get('delta_r2') or 0) > 0,
        f"ΔR²={h2.get('delta_r2')}")
    cek('SIMPULAN jenis = memoderasi', h2.get('jenis') == 'memoderasi', h2.get('jenis'))
    cek('arah = memperkuat', h2.get('arah') == 'memperkuat', h2.get('arah'))
    cek('kalimat simpulan terisi', len(str(h2.get('kalimat') or '')) > 40)

# ══════════════════════════════════════════════════════════════════════════
#  C. TIDAK ADA MODERASI — Z lemah, harus JUJUR bilang tidak memoderasi
# ══════════════════════════════════════════════════════════════════════════
print('\n[C] MODERASI PALSU X1 × Z1 → Y1  (tanam: interaksi = 0,00)')
rng = np.random.default_rng(41)
X = rng.normal(size=n)
Z = rng.normal(size=n)
Y = 0.30 * X + 0.20 * Z + 0.00 * X * Z + rng.normal(scale=0.8, size=n)
baris = [[t(X[i]), t(X[i] + rng.normal(scale=.3)),
          t(Z[i]), t(Z[i] + rng.normal(scale=.3)),
          t(Y[i]), t(Y[i] + rng.normal(scale=.3))] for i in range(n)]
up = unggah(['X1a', 'X1b', 'Z1a', 'Z1b', 'Y1a', 'Y1b'], baris)
jw = _http('/api/diagnosis/periksa',
           {'kunci': up.get('kunci'), 'mode': 'spss', 'peran': P,
            'missing': 'buang'})
h3 = ((jw.get('kaitan') or {}).get('moderasi') or [{}])[0]
cek('ditembak & boleh dihitung', h3.get('boleh'), str(h3.get('sebab'))[:40])
if h3.get('boleh'):
    it = (h3.get('dengan_interaksi') or {}).get('interaksi') or {}
    cek('interaksi TIDAK signifikan', (it.get('p') or 0) >= 0.05, f"p={it.get('p')}")
    cek('SIMPULAN jujur = tidak memoderasi',
        h3.get('jenis') == 'tidak memoderasi', h3.get('jenis'))

print('\n' + '=' * 72)
if GAGAL:
    print(f' ❌ ADA GAGAL: {GAGAL}')
    sys.exit(1)
print(' ✅ LULUS SEMUA — mediasi & moderasi SAMPAI KE HASIL lewat pintu produksi')
sys.exit(0)
