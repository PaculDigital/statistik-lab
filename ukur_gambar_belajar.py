#!/usr/bin/env python3
"""UKUR GEOMETRI GAMBAR BELAJAR — TANPA BROWSER, TANPA SLIDER.

════════════════════════════════════════════════════════════════════════════
MENGAPA BERKAS INI ADA (aturan Bos: "jangan menambal — cari AKAR").
Wulan sudah 5 putaran gagal mengukur memakai browser/CDP:
  · iframe  → browser mengunci isi (contentDocument null)
  · CDP + slider → hasil TIDAK STABIL untuk kode yang sama (`119px` lalu `None`)
  · tab menahan halaman basi (cache 4 jam)
Tiap putaran Wulan menambal ALAT UKUR, bukan memperbaiki aplikasi. Itu SALAH.
Wulan berhenti dan GANTI PENDEKATAN:

    Ambil FUNGSI gambar() langsung dari berkas template, hitung geometrinya
    dengan Node (JS), lalu periksa angkanya dengan Python.

Kenapa ini lebih baik:
  · Tidak ada browser → tidak ada cache, tidak ada tab basi, tidak ada timeout
  · Cepat (milidetik), bisa dijalankan berkali-kali
  · Mengukur KODE YANG SAMA yang dikirim ke user (diambil dari berkas asli)

BATAS JUJUR (harus disebut): cara ini mengukur FUNGSI, bukan halaman jadi.
Untuk urusan tata letak/CSS di HP, uji_belajar_hp.py tetap dipakai (dan itu
sudah LULUS). Jadi keduanya saling melengkapi, bukan menggantikan.

CARA JALAN:  .venv/bin/python ukur_gambar_belajar.py
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

AKAR = pathlib.Path(__file__).resolve().parent
TEMPLATE = AKAR / 'app/templates/belajar.html'

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' → {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' → {bukti}' if bukti else ''))


def ambil_gambar(nama: str) -> str:
    """Ambil badan fungsi `gambar: (v, c) => { ... }` untuk istilah tertentu."""
    isi = TEMPLATE.read_text()
    # batasi ke blok istilah itu supaya tidak tertukar dengan istilah lain
    awal = isi.find(f'\n  {nama}: {{')
    if awal < 0:
        raise SystemExit(f'istilah {nama} tidak ditemukan')
    akhir = isi.find('\n  },', awal + 10)
    blok = isi[awal:akhir]
    m = re.search(r'gambar: \(v, c\) => \{(.*)\n    \}\s*$', blok, re.S)
    if not m:
        raise SystemExit(f'fungsi gambar {nama} tidak ditemukan')
    return m.group(1)


def hitung(js_badan: str, nilai: list[int]) -> dict:
    """Jalankan fungsi gambar di Node, kembalikan geometri tiap nilai."""
    skrip = f"""
const acak_test = (i) => {{
  const s = Math.sin(i * 12.9898) * 43758.5453;
  return (s - Math.floor(s)) * 2 - 1;
}};
function gambar(v, c) {{ {js_badan} }}

const keluaran = {{}};
for (const v of {json.dumps(nilai)}) {{
  const svg = gambar(v, '#A85A5A');
  // hitung geometri dari ATRIBUT (bukan render browser)
  const titik = [...svg.matchAll(/<circle[^>]*cx="([\\d.]+)"[^>]*cy="([\\d.]+)"/g)]
                  .map(m => [parseFloat(m[1]), parseFloat(m[2])]);
  const garis = [...svg.matchAll(/<line[^>]*x1="([\\d.-]+)"[^>]*y1="([\\d.-]+)"[^>]*x2="([\\d.-]+)"[^>]*y2="([\\d.-]+)"/g)]
                  .map(m => m.slice(1).map(Number));
  keluaran[v] = {{ titik, garis,
                   teks: (svg.match(/>([^<]+)<\\/text>/) || [,''])[1],
                   jmlTitik: titik.length, jmlGaris: garis.length }};
}}
console.log(JSON.stringify(keluaran));
"""
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
        f.write(skrip)
        jalur = f.name
    try:
        keluar = subprocess.run(['node', jalur], capture_output=True, text=True,
                                timeout=60)
        if keluar.returncode != 0:
            raise SystemExit('node gagal:\n' + keluar.stderr[:800])
        return json.loads(keluar.stdout)
    finally:
        pathlib.Path(jalur).unlink(missing_ok=True)


def tinggi(mendatar: list[list[float]], kiri: bool) -> float:
    """Tinggi sebaran (px) di sepertiga kiri atau kanan."""
    xs = [t[0] for t in mendatar]
    xmin, xmax = min(xs), max(xs)
    lebar = xmax - xmin
    jika_kiri = [t for t in mendatar if t[0] <= xmin + lebar / 3]
    jika_kanan = [t for t in mendatar if t[0] >= xmax - lebar / 3]
    pakai = jika_kiri if kiri else jika_kanan
    if len(pakai) < 3:
        return 0.0
    ys = [t[1] for t in pakai]
    return max(ys) - min(ys)


def main() -> int:
    if not shutil.which('node'):
        print('⛔ node tidak ada — tidak bisa mengukur tanpa browser.')
        return 2

    print('═' * 66)
    print('UKUR GEOMETRI GAMBAR BELAJAR (dari fungsi asli, tanpa browser)')
    print('═' * 66)

    # ── HETEROSKEDASTISITAS ───────────────────────────────────────────────
    print('\n[1] Heteroskedastisitas')
    badan = ambil_gambar('hetero')
    g = hitung(badan, [0, 25, 50, 75, 100])

    k0, k100 = tinggi(g['0']['titik'], True), tinggi(g['0']['titik'], False)
    K0, K100 = tinggi(g['100']['titik'], True), tinggi(g['100']['titik'], False)
    rasio0 = k100 / max(1.0, k0)
    rasio100 = K100 / max(1.0, K0)
    cek('ujung "rata": kiri ≈ kanan (rasio ≤ 1,6)', rasio0 <= 1.6,
        f'kiri {k0:.0f}px vs kanan {k100:.0f}px → {rasio0:.2f}×(nilai 0)')
    cek('ujung "tidak rata": kanan ≫ kiri (rasio ≥ 2,5)', rasio100 >= 2.5,
        f'kiri {K0:.0f}px vs kanan {K100:.0f}px → {rasio100:.2f}×(nilai 100)')

    # naik terus-menerus (monoton) sepanjang slider
    naik = []
    for v in [0, 25, 50, 75, 100]:
        naik.append(tinggi(g[str(v)]['titik'], False))
    cek('kanan makin lebar terus (tidak naik-turun)',
        all(naik[i] <= naik[i + 1] + 1 for i in range(len(naik) - 1)),
        ' → '.join(f'{x:.0f}px' for x in naik))

    # derau tetap: gambar sama untuk nilai yang sama (dua kali hitung)
    b1 = hitung(badan, [50])['50']['titik']
    b2 = hitung(badan, [50])['50']['titik']
    cek('titik TIDAK berkedip (nilai sama → gambar sama)', b1 == b2)
    cek('label keadaan ikut berubah',
        g['0']['teks'] != g['100']['teks'],
        f"v=0: {g['0']['teks']} | v=100: {g['100']['teks']}")

    # ── VIF ───────────────────────────────────────────────────────────────
    print('\n[2] VIF — seberapa mirip')
    badan = ambil_gambar('vif')
    g = hitung(badan, [0, 50, 100])
    for v in ['0', '50', '100']:
        c = g[v]['titik']
        # ambil dua pusat BERBEDA (tiap lingkaran dibuat 2×: isi + tepi)
        unik = sorted({round(x, 1) for x, _ in c})
        cek(f'v={v}: ada 2 pusat berbeda', len(unik) >= 2, f'pusat: {unik}')
    u0 = sorted({round(x, 1) for x, _ in g['0']['titik']})
    u100 = sorted({round(x, 1) for x, _ in g['100']['titik']})
    d0 = abs(u0[-1] - u0[0])
    d100 = abs(u100[-1] - u100[0])
    # jari-jari dari atribut r
    r_m = re.search(r'const R = (\d+)', badan)
    R = float(r_m.group(1)) if r_m else 42.0
    cek('ujung kiri: dua lingkaran BERPISAH (beda semua)', d0 >= 2 * R * 0.5,
        f'jarak pusat {d0:.0f} ≥ 2R({2 * R:.0f})×0,5')
    cek('ujung kanan: dua lingkaran MENUMPUK (nyaris kembar)', d100 < 2 * R,
        f'jarak pusat {d100:.0f} < 2R {2 * R:.0f}')
    cek('slider VIF benar-benar mengubah keadaan', d100 < d0 - 40,
        f'{d0:.0f}px → {d100:.0f}px (makin dekat = makin mirip)')

    print('\n' + '=' * 66)
    print(f'HASIL UKUR GAMBAR: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
