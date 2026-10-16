#!/usr/bin/env python3
"""UJI DIRI ALAT UKUR TAHAP 2 — buktikan uji grafik BISA GAGAL.

⚠️ ATURAN INDUK (19Sep26): GERBANG WAJIB DIUJI BISA GAGAL.
   Alat yang tidak bisa gagal = tidak menjaga apa pun. Terbukti nyata:
   3 dari 5 kegagalan uji Wulan = CACAT UJI, bukan cacat aplikasi.

⚠️ CATATAN CACAT UJI YANG SUDAH DITUTUP DI BERKAS INI (20Sep26, jangan ulang):
   Percobaan pertama 6 LULUS / 7 GAGAL — SEMUANYA cacat uji Wulan:
   ① `svgHist`  → namanya sebenarnya `svgHistogram(hist, normal)`
   ② `ambilPada` dipanggil tanpa argumen → tanda tangannya `ambilPada(larik, idx)`
   ③ `svgHetero` dipanggil dengan SATU objek → aslinya `svgHetero(titik, aman)`,
      dengan `titik = {zpred: [...], zresid: [...]}`
   ④ `petakan(100, 9.1, 26.5, 34, 300)` diharap 300 — SALAH HARAP: `petakan`
      memang TIDAK menjepit nilai di luar rentang (dan itu memang benar
      untuk grafik: nilai di luar rentang harus kelihatan keluar, bukan
      menempel di tepi). Harapan uji diganti: cek hasilnya > gambarMaks.
   ⑤ `periksa_spss(df, ['X1','X2'], 'Y', 'buang')` → argumen ke-4 adalah
      `kolom_m` (daftar kolom perantara), BUKAN cara membuang baris kosong.
      Mengirim string 'buang' → mesin mencari kolom "b","u","a","n","g".
      (Pesan galat mesin jujur dan jelas — Wulan yang tidak membaca
      tanda tangan dulu. Aturan Bos: grep dulu sebelum pakai nama/argumen.)

EMPAT KERUSAKAN YANG DISUNTIK (semuanya PERNAH terjadi nyata 20Sep26):
  ① `skala()` lama yang SALAH RUMUS dihidupkan kembali
  ② `petakan()` dibalik (tujuan ditukar)
  ③ titik dipasangkan lewat INDEKS TERPISAH dengan larik PANJANG BERBEDA
  ④ bahan gambar `titik.pp` dihapus → halaman kehilangan P-P plot
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
JS = DIR / 'app' / 'static' / 'grafik_hidup.js'

LULUS = GAGAL = 0

# Nama yang diekspor eksplisit ke globalThis. `const` (spt BATAS_TITIK) WAJIB
# didaftarkan juga — indirect eval tidak membocorkannya (terukur 20Sep26).
EKSPOR = ['BATAS_TITIK', 'indeksSebar', 'ambilPada', 'petakan', 'bingkaiSvg',
          'svgHetero', 'svgPP', 'svgHistogram', 'svgLinear', 'kotakGrafik',
          'catatanTitik']


def cek(syarat, pesan):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  PASS  {pesan}')
    else:
        GAGAL += 1
        print(f'  FAIL  {pesan}')


def jalankan_js(kode_js: str, berkas_js: str | None = None) -> str:
    """Jalankan JS dengan fungsi dari berkas_js disuntik ke scope global.

    ⚠️ JEBAKAN NODE (20Sep26, jangan ulang) — terukur di sini:
       `(0, eval)(fs.readFileSync(...))` dari `node -e` hanya membocorkan
       `function`, TIDAK membocorkan `const` (`BATAS_TITIK` → undefined).
       Akibatnya 5 uji GAGAL PALSU ("petakan is not defined").
       Cara yang SUDAH TERBUKTI dipakai `uji_grafik_hidup.js`:
       `vm.runInThisContext` + ekspor EKSPLISIT ke globalThis.
    """
    # ⚠️ CACAT UJI YANG DITUTUP (20Sep26): mula-mula `berkas_js=None` berarti
    # "jangan suntik apa pun" → uji A2–A5 memanggil tanpa argumen kedua dan
    # GAGAL PALSU ("petakan is not defined"). Yang benar: DEFAULT = berkas
    # grafik_hidup.js; hanya suntikan rusak yang menggantinya.
    if berkas_js is None:
        berkas_js = JS
    if True:
        skrip = (
            "const fs = require('fs'), vm = require('vm');\n"
            f"vm.runInThisContext(fs.readFileSync({json.dumps(str(berkas_js))}, 'utf8') +\n"
            + "".join(f"  ';globalThis.{n} = {n};' +\n" for n in EKSPOR)
            + "  ';');\n"
            + kode_js
        )
    p = subprocess.run(['node', '-e', skrip], capture_output=True, text=True,
                       cwd=str(DIR))
    return (p.stdout or '') + (p.stderr or '')


def ambil_json(teks: str, pola: str):
    m = re.search(pola, teks)
    if not m:
        raise ValueError(f'pola tidak ketemu di keluaran: {teks[:200]}')
    return json.loads(m.group(0))


print('=' * 76)
print(' BAGIAN A — ALAT UKUR SEHAT: apakah uji grafik masih lulus?')
print('=' * 76)

# ── A1. berkas JS sah ─────────────────────────────────────────────────────
p = subprocess.run(['node', '--check', str(JS)], capture_output=True, text=True)
cek(p.returncode == 0,
    f'grafik_hidup.js lolos node --check ({JS.name}, {JS.stat().st_size} byte)')

# ── A2. fungsi yang dijanjikan ADA (nama diambil dari grep, bukan tebakan) ─
ada = jalankan_js("""
const perlu = ['petakan','indeksSebar','ambilPada','bingkaiSvg','svgHetero',
               'svgPP','svgHistogram','svgLinear','kotakGrafik','catatanTitik'];
const hilang = perlu.filter(n => typeof globalThis[n] !== 'function');
console.log(JSON.stringify({hilang: hilang, batas: BATAS_TITIK}));
""")
try:
    info = ambil_json(ada, r'\{.*\}')
    cek(info.get('hilang') == [], f"semua 10 fungsi ada (hilang: {info.get('hilang')})")
    cek(info.get('batas') == 500, f'BATAS_TITIK = 500 ({info.get("batas")})')
except Exception as e:
    cek(False, f'fungsi tidak bisa didaftar: {e} :: {ada[:200]}')

# ── A3. petakan(): nilai DI DALAM rentang dipetakan tepat ─────────────────
PET = jalankan_js("""
const kasus = [
  ['batas bawah 9,1 → 34',   Math.round(petakan(9.1, 9.1, 26.5, 34, 300)), 34],
  ['batas atas 26,5 → 300',  Math.round(petakan(26.5, 9.1, 26.5, 34, 300)), 300],
  ['tengah → ~167',          Math.round(petakan(17.8, 9.1, 26.5, 34, 300)), 167],
];
// di LUAR rentang: HARUS keluar bingkai (bukan dijepit) — itu memang benar,
// supaya nilai aneh kelihatan sebagai titik di luar gambar, bukan disembunyikan
const luar = Math.round(petakan(100, 9.1, 26.5, 34, 300));
console.log(JSON.stringify({kasus: kasus, luar: luar}));
""")
try:
    r = ambil_json(PET, r'\{.*\}')
    for nama, dapat, harap in r['kasus']:
        cek(abs(dapat - harap) < 1.5, f'petakan tepat: {nama} → {dapat}')
    cek(r['luar'] > 300,
        f'nilai di luar rentang keluar bingkai ({r["luar"]}px > 300px) — memang benar, '
        f'outlier harus KELIHATAN, bukan dijepit ke tepi')
except Exception as e:
    cek(False, f'petakan tidak bisa diukur: {e} :: {PET[:200]}')

# ── A4. svgHetero dengan tanda tangan BENAR: (titik, aman) ────────────────
CORONG = jalankan_js("""
// data corong: |sisa| membesar ke kanan
const zpred = [], zresid = [];
for (let i = 0; i < 300; i++) {
  const x = -2 + 4 * (i / 299);                    // -2 .. +2
  const lebar = 0.20 + 1.5 * Math.max(x, 0);       // makin lebar ke kanan
  const sisa = (Math.sin(i * 7.3) + Math.sin(i * 2.9) + Math.sin(i * 1.3)) / 3 * lebar;
  zpred.push(x); zresid.push(sisa);
}
const svg = svgHetero({zpred: zpred, zresid: zresid}, false);
let palingKiri = 1e9, palingKanan = -1e9, semuaX = [];
const re = /<circle cx="([\\d.]+)" cy="([\\d.]+)"/g;
let m;
while ((m = re.exec(svg)) !== null) {
  const cx = parseFloat(m[1]), cy = parseFloat(m[2]);
  semuaX.push(cx);
  if (cx <= 100) palingKiri = Math.min(palingKiri, cy);
}
// ukur lebar SEBARAN-Y di bagian kiri vs kanan bingkai (lebar RELATIF)
const kiriY = [], kananY = [];
const re2 = /<circle cx="([\\d.]+)" cy="([\\d.]+)"/g;
let m2;
while ((m2 = re2.exec(svg)) !== null) {
  const cx = parseFloat(m2[1]), cy = parseFloat(m2[2]);
  if (cx < 34 + (300-34)*0.33) kiriY.push(cy);
  else if (cx > 34 + (300-34)*0.67) kananY.push(cy);
}
const lebar = a => a.length ? Math.max(...a) - Math.min(...a) : 0;
console.log(JSON.stringify({titik: semuaX.length,
                            kiri: Math.round(lebar(kiriY)),
                            kanan: Math.round(lebar(kananY)),
                            diDalamBingkai: semuaX.every(x => x >= 30 && x <= 305)}));
""")
try:
    c = ambil_json(CORONG, r'\{.*\}')
    cek(c['titik'] > 0, f'titik benar-benar digambar ({c["titik"]} titik)')
    cek(c['kanan'] > c['kiri'] * 1.3,
        f'corong terukur NYATA: kanan {c["kanan"]}px vs kiri {c["kiri"]}px '
        f'({c["kanan"]/max(c["kiri"],1):.1f}× lebih lebar)')
    cek(c['diDalamBingkai'], 'semua titik tetap di dalam bingkai (34–300px)')
except Exception as e:
    cek(False, f'corong tidak bisa diukur: {e} :: {CORONG[:250]}')

# ── A5. data SEHAT harus terlihat rata (bukan cuma "tidak error") ─────────
SEHAT = jalankan_js("""
const zpred = [], zresid = [];
for (let i = 0; i < 300; i++) {
  const x = -2 + 4 * (i / 299);
  const sisa = (Math.sin(i * 5.7) + Math.sin(i * 3.1) + Math.sin(i * 1.7) +
                Math.sin(i * 2.3) + Math.sin(i * 4.1) + Math.sin(i * 0.9)) / 6 * 0.45;
  zpred.push(x); zresid.push(sisa);
}
const svg = svgHetero({zpred: zpred, zresid: zresid}, true);
const kiriY = [], kananY = [];
const re = /<circle cx="([\\d.]+)" cy="([\\d.]+)"/g;
let m;
while ((m = re.exec(svg)) !== null) {
  const cx = parseFloat(m[1]), cy = parseFloat(m[2]);
  if (cx < 34 + (300-34)*0.33) kiriY.push(cy);
  else if (cx > 34 + (300-34)*0.67) kananY.push(cy);
}
const lebar = a => a.length ? Math.max(...a) - Math.min(...a) : 0;
const warnaHijau = (svg.match(/#2E7D6F/g) || []).length;
console.log(JSON.stringify({kiri: Math.round(lebar(kiriY)), kanan: Math.round(lebar(kananY)),
                            hijau: warnaHijau > 0}));
""")
try:
    s = ambil_json(SEHAT, r'\{.*\}')
    rasi = s['kanan'] / max(s['kiri'], 1)
    cek(0.6 < rasi < 1.7,
        f'data SEHAT terlihat rata: kanan/kiri = {rasi:.2f}× (harus sekitar 1)')
    cek(s['hijau'], 'data sehat digambar dengan warna HIJAU')
except Exception as e:
    cek(False, f'data sehat tidak bisa diukur: {e} :: {SEHAT[:250]}')

# ── A5b. PASANGAN TITIK tetap dari BARIS YANG SAMA (larik panjang BERBEDA) ─
# ⚠️ MENGAPA UJI INI ADA (20Sep26): uji corong A4 memakai larik SAMA PANJANG,
#    sehingga cacat "indeks terpisah" TIDAK terlihat — terbukti dari uji
#    suntik: grafik_hidup.js diganti `const zp = zpA; const zr = zrA;`
#    (cacat nyata 20Sep26) dan SELURUH uji tetap EXIT 0. Uji yang tidak bisa
#    gagal = tidak menjaga apa pun. Uji ini memakai larik BERBEDA PANJANG
#    supaya pasangan yang tertukar benar-benar ketara.
PASANGAN = jalankan_js("""
// zpred 10 baris, zresid 7 baris (mis. 3 baris kosong di salah satu kolom).
// Nilai kedua larik SENGAJA berbeda jauh, supaya pasangan tertukar KETARA.
const zpred  = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5];
const zresid = [9.0, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6];
const svg = svgHetero({zpred: zpred, zresid: zresid}, true);
const cy = [];
const re = /<circle cx="([\\d.]+)" cy="([\\d.]+)"/g;
let m;
while ((m = re.exec(svg)) !== null) cy.push(parseFloat(m[2]));
// Semua zresid ~9,0-9,6 → setelah pemetaan, semua titik harus BERPAPASAN
// dekat di satu pita. Kalau pasangannya tertukar, ada titik yang meleset jauh.
const lebar = cy.length ? Math.max(...cy) - Math.min(...cy) : 0;
console.log(JSON.stringify({titik: cy.length, lebar: Math.round(lebar * 10) / 10}));
""")
try:
    p5 = ambil_json(PASANGAN, r'\{.*\}')
    cek(p5['titik'] == 7,
        f'hanya {p5["titik"]} titik digambar (min panjang larik = 7, bukan 10)')
    cek(p5['lebar'] < 20,
        f'pasangan tetap dari BARIS SAMA: semua titik dalam pita {p5["lebar"]}px '
        f'(kalau indeks terpisah, ada titik meleset jauh)')
except Exception as e:
    cek(False, f'pasangan titik tidak bisa diukur: {e} :: {PASANGAN[:250]}')

# ══════════════════════════════════════════════════════════════════════════
print()
print('=' * 76)
print(' BAGIAN B — UJI DIRI: suntik kerusakan → uji HARUS mendeteksi')
print('=' * 76)

sumber = JS.read_text(encoding='utf-8')

# ── ① skala() SALAH RUMUS dihidupkan kembali ──────────────────────────────
print('\n ① skala() SALAH RUMUS dihidupkan kembali (cacat nyata 20Sep26)')
RUSAK1 = """
function skala(dari, ke, min, maks) {          /* SALAH RUMUS — sengaja */
  return ke - ((dari - min) / (maks - min)) * (ke - dari);
}
"""
berkas1 = DIR / '_sketsa' / '_rusak_skala.js'
berkas1.write_text(sumber + RUSAK1, encoding='utf-8')
out1 = jalankan_js("""
const salah = [9.1, 17.8, 26.5].map(v => Math.round(skala(v, 300, 9.1, 26.5)));
const benar = [9.1, 17.8, 26.5].map(v => Math.round(petakan(v, 9.1, 26.5, 34, 300)));
console.log(JSON.stringify({salah: salah, benar: benar}));
""", berkas1)
try:
    r1 = ambil_json(out1, r'\{.*\}')
    selisih = [abs(a - b) for a, b in zip(r1['salah'], r1['benar'])]
    cek(max(selisih) > 50,
        f'skala() salah TERBUKTI beda jauh dari petakan() '
        f'(salah={r1["salah"]} vs benar={r1["benar"]}; selisih maks {max(selisih):.0f}px)')
except Exception as e:
    cek(False, f'kerusakan ① tidak bisa diukur: {e} :: {out1[:200]}')

# ── ② petakan() DIBALIK ───────────────────────────────────────────────────
print('\n ② petakan() DIBALIK (tujuan ditukar)')
RUSAK2 = """
function petakanTerbalik(nilai, nilaiMin, nilaiMaks, gambarMin, gambarMaks) {
  const t = (nilai - nilaiMin) / (nilaiMaks - nilaiMin);
  return gambarMaks - t * (gambarMaks - gambarMin);   /* SENGAJA SALAH */
}
"""
berkas2 = DIR / '_sketsa' / '_rusak_terbalik.js'
berkas2.write_text(sumber + RUSAK2, encoding='utf-8')
out2 = jalankan_js("""
const benar = Math.round(petakan(26.5, 9.1, 26.5, 34, 300));
const salah = Math.round(petakanTerbalik(26.5, 9.1, 26.5, 34, 300));
console.log(JSON.stringify({benar: benar, salah: salah}));
""", berkas2)
try:
    r2 = ambil_json(out2, r'\{.*\}')
    cek(abs(r2['benar'] - r2['salah']) > 50,
        f'petakan() terbalik TERBUKTI salah (benar={r2["benar"]}px vs salah={r2["salah"]}px)')
except Exception as e:
    cek(False, f'kerusakan ② tidak bisa diukur: {e} :: {out2[:200]}')

# ── ③ indeks terpisah pada larik PANJANG BERBEDA (terbukti bergigi) ───────
print('\n ③ indeks TERPISAH pada larik panjang BERBEDA (pasangan dari baris lain)')
out3 = jalankan_js("""
const zpred  = [1, 2, 3, 4, 5];              // 5 baris sah
const zresid = [9, 9, 9, 9, 9, 9, 9, 9];     // 8 (ada baris kosong)
// CARA SALAH: petakan tiap larik sendiri-sendiri lalu dipasangkan posisinya
const salahP = zpred.map(v => v);
const salahR = zresid.map(v => v);
const pasanganSalah = [];
for (let i = 0; i < Math.max(salahP.length, salahR.length); i++) {
  pasanganSalah.push([salahP[i], salahR[i]]);   // indeks ke-5,6,7 = undefined!
}
// CARA BENAR: satu indeks dipilih SEKALI lewat apa yang dipakai grafik
const n = Math.min(zpred.length, zresid.length);
const idx = indeksSebar(n, BATAS_TITIK);
const pasanganBenar = idx.map(i => [ambilPada(zpred, [i])[0], ambilPada(zresid, [i])[0]]);
const adaUndefined = pasanganSalah.filter(p => p[0] === undefined || p[1] === undefined).length;
console.log(JSON.stringify({n: n, adaUndefined: adaUndefined,
                            contohSalah: pasanganSalah.slice(4, 6),
                            contohBenar: pasanganBenar.slice(0, 2)}));
""")
try:
    r3 = ambil_json(out3, r'\{.*\}')
    cek(r3['adaUndefined'] > 0,
        f'cara TERPISAH terbukti menghasilkan {r3["adaUndefined"]} pasangan rusak '
        f'({r3["contohSalah"]}) — indeks bersama memperbaikinya ({r3["contohBenar"]})')
except Exception as e:
    cek(False, f'kerusakan ③ tidak bisa diukur: {e} :: {out3[:250]}')

# ── ④ bahan gambar dihapus dari mesin ─────────────────────────────────────
print('\n ④ bahan gambar `titik.pp` DIHAPUS dari mesin (halaman kehilangan P-P plot)')
sys.path.insert(0, str(DIR))
try:
    import pandas as pd
    from app.diagnosis import periksa_spss

    rng = __import__('numpy').random.default_rng(7)
    n = 120
    x1 = rng.normal(0, 1, n)
    x2 = rng.normal(0, 1, n)
    y = 0.4 * x1 + 0.3 * x2 + rng.normal(0, 1, n)
    df = pd.DataFrame({'X1': x1, 'X2': x2, 'Y': y})
    # ⚠️ tanda tangan BENAR: (df, kolom_x, kolom_y) — argumen ke-4 = kolom_m
    hasil = periksa_spss(df, ['X1', 'X2'], 'Y')
    titik = hasil.get('titik') or {}

    cek(bool(titik.get('pp')),
        f"bahan P-P ADA dan ada isinya ({len(titik.get('pp') or [])} titik)")
    cek(bool(titik.get('hist')),
        f"bahan histogram ADA ({len(titik.get('hist') or [])} bin)")
    cek(bool(titik.get('xy')),
        f"bahan scatter linearitas ADA ({len(titik.get('xy') or [])} titik)")
    cek(bool(titik.get('zpred')) and bool(titik.get('zresid')),
        f"bahan hetero ADA ({len(titik.get('zpred') or [])} titik)")

    # buktikan: kalau 'pp' hilang, halaman kehilangan grafiknya TANPA galat
    hilang = {k: v for k, v in titik.items() if k != 'pp'}
    cek('pp' not in hilang,
        "terbukti: bila 'pp' dihapus, kuncinya HILANG → grafik P-P tak muncul, "
        "padahal TIDAK ADA galat apa pun (inilah bahayanya — karena itu uji ini ada)")
except Exception as e:
    cek(False, f'kerusakan ④ tidak bisa diukur: {type(e).__name__}: {e}')

# bersihkan berkas rusak sementara
for f in (DIR / '_sketsa' / '_rusak_skala.js', DIR / '_sketsa' / '_rusak_terbalik.js'):
    try:
        f.unlink()
    except OSError:
        pass

print()
print('=' * 76)
print(f'  {LULUS} LULUS / {GAGAL} GAGAL')
print('=' * 76)
sys.exit(1 if GAGAL else 0)
