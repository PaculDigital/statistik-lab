"""PERIKSA ISI PRODUKSI — khusus perbaikan MANOVA 22Sep26.

Deploy boleh bilang "SELESAI", tapi yang menentukan: apakah ISI halaman
produksi benar-benar memuat perbaikan? Diperiksa dari DALAM kontainer
(jaringan Docker; loopback Wulan ≠ loopback kontainer).

3 perubahan yang WAJIB ada:
  1. K-22 — kolom "Nilai" memakai NILAI STATISTIK (`nilaiStat`), kolom F
     memakai `q.F` → dua hal TERPISAH (dulu Nilai diisi q.F)
  2. K-23 — mesin MANOVA melaporkan `df1`/`df2` untuk keempat ukuran
  3. id `pagar-${i}` → `perkiraan-${i}` (kata terlarang hilang dari halaman)

⚠️ PELAJARAN 22Sep26: uji pertama Wulan mencari `r.statistik[` (SALAH —
   nama variabelnya `nilaiStat`) → laporan "produksi tidak memuat
   perbaikan" padahal KODE BENAR. **Cetak dulu bentuk sebenarnya,
   baru tulis syaratnya** — jangan menuntut bentuk yang ditebak.
"""
from __future__ import annotations

import subprocess
import sys

NAMA = 'simulasi-olah-data'
lulus = gagal = 0


def catat(ok: bool, teks: str, bukti: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        print(f'  ✅ {teks}' + (f'   {bukti}' if bukti else ''))
    else:
        gagal += 1
        print(f'  ❌ {teks}' + (f'   {bukti}' if bukti else ''))


def dalam(py: str) -> str:
    r = subprocess.run(['docker', 'exec', NAMA, 'python', '-c', py],
                       capture_output=True, text=True, timeout=180)
    return (r.stdout or '') + (r.stderr or '')


def main() -> int:
    print('═══ ISI PRODUKSI — perbaikan MANOVA 22Sep26 ═══')

    # ── 1. K-22: "Nilai" & "F" DUA HAL TERPISAH ────────────────────────
    kode = dalam(
        "import pathlib;"
        "t=pathlib.Path('/app/app/templates/buat_data.html').read_text();"
        "i=t.find('function kartuUjiManova');"
        "print(t[i:i+900])")
    catat('nilaiStat' in kode,
          'K-22: kolom "Nilai" memakai nilai statistik (nilaiStat)')
    # baris yang memuat nilaiStat TIDAK boleh juga memuat q.F
    # ⚠️ pecah pakai newline SUNGGUHAN (chr(10)) — menulis '\\n' memperlakukan
    #    seluruh keluaran sebagai SATU baris → selalu dianggap melanggar.
    baris_nilai = [b for b in kode.split(chr(10)) if 'nilaiStat' in b]
    catat(bool(baris_nilai) and all('q.F' not in b for b in baris_nilai),
          'K-22: baris kolom "Nilai" TIDAK memakai q.F',
          f'{len(baris_nilai)} baris diperiksa')
    catat("angkaMesin(q.F, 3)" in kode,
          'K-22: kolom F tetap memakai q.F (dipisah, tidak dihapus)')
    catat("q.df1" in kode and "q.df2" in kode,
          'K-23 (tampilan): kolom df memakai q.df1/q.df2')

    # ── 2. K-23: mesin melaporkan df1/df2 (kode + jalan nyata) ─────────
    manova = dalam(
        "import pathlib;"
        "print(pathlib.Path('/app/app/hitung/manova.py').read_text()"
        ".count(\"'df1'\"))")
    catat(int(manova.strip() or 0) >= 4,
          'K-23: kode MANOVA memuat df1 (keempat ukuran)',
          f"jumlah 'df1' = {manova.strip()}")

    hasil = dalam(
        "import sys;sys.path.insert(0,'/app');"
        "from app.hitung.kelompok import buat_data_kelompok;"
        "from app.hitung.manova import hitung_manova;"
        "d=buat_data_kelompok(n_per_kelompok=30,nama_y=['Minat','Nilai'],seed=7);"
        "Y=[v.tolist() for v in d['Y']];"
        "r=hitung_manova(Y,d['kelompok'],['Minat','Nilai']);"
        "print({k:(r['uji'][k].get('df1'),r['uji'][k].get('df2')) "
        "for k in ('wilks','pillai','hotelling','roy')})")
    catat('None' not in hasil, 'K-23: df1 & df2 TERISI saat mesin jalan di produksi',
          hasil.strip()[-100:])

    # ── 3. kata terlarang hilang dari halaman ──────────────────────────
    html = dalam(
        "import urllib.request;"
        "print(urllib.request.urlopen('http://127.0.0.1:8000/"
        "buat-data?model=banding-kelompok',timeout=20).read().decode()"
        ".count('pagar'))")
    catat(int(html.strip() or 0) == 0,
          'id pagar-* diganti → kata terlarang 0 di halaman',
          f"jumlah 'pagar' = {html.strip()}")

    # ── 4. halaman hidup di produksi ──────────────────────────────────
    for jalur in ('/kuantitatif', '/buat-data?model=banding-kelompok'):
        kode_http = dalam(
            "import urllib.request;"
            f"print(urllib.request.urlopen('http://127.0.0.1:8000{jalur}',"
            "timeout=20).status)")
        catat(kode_http.strip() == '200', f'{jalur} → HTTP 200', kode_http.strip())

    print()
    print('=' * 70)
    if gagal:
        print(f' ❌ {gagal} GAGAL (lulus {lulus}) — produksi TIDAK memuat perbaikan')
        return 1
    print(f' ✅ {lulus} LULUS / 0 GAGAL — produksi memuat perbaikan MANOVA')
    return 0


if __name__ == '__main__':
    sys.exit(main())
