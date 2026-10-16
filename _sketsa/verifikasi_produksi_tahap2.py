"""VERIFIKASI TAHAP 2 DI PRODUKSI — buktikan fitur baru benar-benar LIVE.

⚠️ MENGAPA ADA: `verifikasi_produksi.py` hanya memeriksa halaman HTTP 200.
Tahap 2 menambah fitur yang bisa HILANG walau halaman tetap 200 (skrip mati,
tab hilang, pengalihan hilang). Uji ini memeriksa ISI dari DALAM kontainer.

Jalankan: .venv/bin/python _sketsa/verifikasi_produksi_tahap2.py
"""
import sys
import urllib.request

KONT = 'simulasi-olah-data'


def isi(jalur: str) -> tuple[int, str]:
    """Baca halaman produksi DARI DALAM kontainer (loopback Wulan beda)."""
    import subprocess
    kode = (
        "import urllib.request,sys\n"
        f"try:\n"
        f"    r=urllib.request.urlopen('http://127.0.0.1:8000{jalur}',timeout=8)\n"
        f"    sys.stdout.write(str(r.status)+'|'+r.read().decode('utf-8','replace'))\n"
        f"except urllib.error.HTTPError as e:\n"
        f"    sys.stdout.write(str(e.code)+'|')\n"
        f"except Exception as e:\n"
        f"    sys.stdout.write('000|'+str(e))\n"
    )
    p = subprocess.run(['docker', 'exec', KONT, 'python', '-c', kode],
                       capture_output=True, text=True, timeout=40)
    keluar = p.stdout
    if '|' not in keluar:
        return 0, p.stderr[:300]
    status, badan = keluar.split('|', 1)
    try:
        return int(status), badan
    except ValueError:
        return 0, badan


def main() -> int:
    print('=' * 74)
    print(' VERIFIKASI TAHAP 2 DI PRODUKSI (bukan cuma HTTP 200)')
    print('=' * 74)
    print()

    hasil = []

    def cek(nama, syarat, catatan=''):
        hasil.append((nama, bool(syarat), catatan))
        print(f'  {"✅" if syarat else "❌"} {nama}')
        if catatan:
            print(f'      {catatan}')

    # ── 1. /syarat DIALIHKAN ke /belajar#tab-3 ────────────────────────────
    # ⚠️ CACAT UJI YANG DITUTUP (20Sep26): `urllib.urlopen` OTOMATIS MENGIKUTI
    # pengalihan → ia melaporkan 200, padahal server mengirim 308. Uji Wulan
    # sempat bilang "GAGAL, harus 308" padahal aplikasinya BENAR.
    # WAJIB pakai handler NoRedirect untuk MELIHAT pengalihannya.
    import subprocess as _sp
    kode_redir = (
        "import urllib.request\n"
        "class T(urllib.request.HTTPRedirectHandler):\n"
        "    def redirect_request(self,*a,**k): return None\n"
        "try:\n"
        "    urllib.request.build_opener(T).open("
        "'http://127.0.0.1:8000/syarat',timeout=8)\n"
        "    print('200|')\n"
        "except urllib.error.HTTPError as e:\n"
        "    print(str(e.code)+'|'+str(e.headers.get('Location')))\n"
    )
    _p = _sp.run(['docker', 'exec', KONT, 'python', '-c', kode_redir],
                 capture_output=True, text=True, timeout=40)
    _s, _, _lok = _p.stdout.strip().partition('|')
    cek('/syarat dialihkan 308', _s == '308', f'HTTP {_s} → {_lok}')
    cek('arah pengalihan benar', '/belajar#tab-3' in _lok, f'→ {_lok}')

    # ── 2. tab ke-3 "Baca Grafik" ada di /belajar ────────────────────────
    st, html = isi('/belajar')
    cek('/belajar HTTP 200', st == 200, f'HTTP {st}')
    cek('tab "Baca Grafik" ADA', 'Baca Grafik' in html)
    cek('panel tab-3 ADA', 'id="tab-3"' in html or "id='tab-3'" in html)
    cek('tombol tab pa-3 ADA', 'id="pa-3"' in html or "id='pa-3'" in html)

    # ── 3. grafik_hidup.js dimuat di <head> ──────────────────────────────
    cek('grafik_hidup.js dimuat', 'grafik_hidup.js' in html)
    i_head = html.find('</head>')
    i_js = html.find('grafik_hidup.js')
    cek('grafik_hidup.js di <head>', 0 <= i_js < i_head,
        f'posisi skrip {i_js} < </head> {i_head}')

    # ── 4. menu 7 (bukan 8) — KAMUS GRAFIK keluar ────────────────────────
    cek('menu 7 (KAMUS GRAFIK keluar)', 'KAMUS GRAFIK' not in html)

    # ── 5. tombol contoh di /klinik ──────────────────────────────────────
    # ⚠️ CACAT UJI YANG DITUTUP (20Sep26): uji mencari teks "Contoh sehat",
    # padahal teks tombol ASLI (diagnosis.html baris 81/84) = "Coba contoh
    # data yang sehat" / "Lihat contoh data bermasalah". Uji mencari teks yang
    # TIDAK PERNAH ADA → GAGAL PALSU. Periksa FUNGSI-nya (pakaiContoh), bukan
    # tebakan teks.
    st, kl = isi('/klinik')
    cek('/klinik HTTP 200', st == 200, f'HTTP {st}')
    cek('tombol contoh (pakaiContoh) ADA', kl.count('pakaiContoh') >= 2,
        f'pakaiContoh {kl.count("pakaiContoh")}x')
    cek('teks "Coba contoh data yang sehat" ADA',
        'Coba contoh data yang sehat' in kl)
    cek('teks "Lihat contoh data bermasalah" ADA',
        'Lihat contoh data bermasalah' in kl)

    # ── 6. grafik_hidup.js ada di berkas statis produksi ─────────────────
    import subprocess
    p = subprocess.run(['docker', 'exec', KONT, 'sh', '-c',
                        'wc -c < /app/app/static/grafik_hidup.js'],
                       capture_output=True, text=True, timeout=30)
    try:
        ukuran = int(p.stdout.strip())
    except ValueError:
        ukuran = 0
    cek('berkas grafik_hidup.js ADA di produksi', ukuran > 3000,
        f'{ukuran} byte')

    print()
    print('=' * 74)
    lulus = sum(1 for _, ok, _ in hasil if ok)
    gagal = len(hasil) - lulus
    print(f'  {lulus} LULUS / {gagal} GAGAL')
    print('=' * 74)
    if gagal == 0:
        print('  ✅ Produksi TERBUKTI memuat Tahap 2 — bukan cuma kata log.')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
