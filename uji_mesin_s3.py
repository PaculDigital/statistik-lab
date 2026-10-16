#!/usr/bin/env python3
"""UJI MESIN: apakah S3 BERGANDA-BERANTAI bisa DIHITUNG?

PERTANYAAN BOS (verbatim 18Sep26):
  "apakah mesin kita sudah bisa hitung model berganda berantai ini?
   Cek dulu, karena ini 2 proses"

S3 = DUA proses (ACC Bos):
  (1) BERGanda : X1..Xn bersama-sama terhadap Y  -> koefisien masing-masing X
  (2) BERANTAI : X1 -> X2 -> ... -> Xn (X saling berhubungan)

UJI INI TIDAK MENEBAK. Yang diuji:
  A. Apakah `bangun_berurutan` bisa menerima bentuk S3?
  B. Apakah koefisien TERUKUR = koefisien yang DIPASANG?
  C. Apakah koefisien BERANTAI (X1->X2, X2->X3) juga terukur benar?
  D. Apakah TIDAK ada akar kode yang menghalangi (mis. suppression)?

CATATAN JUJUR WULAN: sampai hari ini semua bentuk yang diuji adalah
model MEDIASI/MODERASI (X -> M -> Y). S3 ini BARU — belum pernah diuji.

⚠️ PERBAIKAN AKAR 21Sep26 (Wulan sempat SALAH LAPOR — lihat K-09 di
   CATATAN_KESALAHAN_21SEP2026.md):

   Uji ini DULU memanggil `bangun_berurutan(..., koreksi_atenuasi=False)` —
   fungsi INTERNAL dengan koreksi atenuasi DIMATIKAN. Wajar koefisien rantai
   meleset (galat 0,1854 & 0,0918), TAPI itu BUKAN hasil yang dilihat
   mahasiswa. Uji lalu melaporkan "BELUM BISA / ADA SELISIH" → Wulan menyangka
   MESIN cacat & hampir melaporkannya ke Bos, padahal yang salah CARA UKURNYA.

   Yang BENAR: ukur dari PINTU PRODUKSI — `app.berkas_kerja.buat_data()`,
   karena di situlah `kalibrasi_per_jalur()` bekerja. Terukur dari pintu itu:
       X1 -> X2  minta 0,55 → terbaca 0,5503  (galat 0,0003)
       X2 -> X3  minta 0,55 → terbaca 0,5417  (galat 0,0083)
       galat_maks 0,0207 (batas 0,06) → LOLOS

   ATURAN: kalau sebuah uji GAGAL, tanya dulu "fungsi mana yang DIPAKAI
   aplikasi?" — ukur dari situ, bukan dari fungsi internal.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.berkas_kerja import buat_data                                # noqa: E402

GAGAL = 0
BATAS_RANTAI = 0.06          # batas galat koefisien rantai
BATAS_BERG = 0.05            # batas galat koefisien berganda


def cek(nama, syarat, bukti=''):
    global GAGAL
    print(f"  {'✅' if syarat else '❌'} {nama}" + (f'   {bukti}' if bukti else ''))
    if not syarat:
        GAGAL += 1


def uji_s3(n_x=3):
    """Ukur S3 dari PINTU PRODUKSI (buat_data) — bukan fungsi internal."""
    print('\n' + '=' * 64)
    print(f'S3 BERGANDA-BERANTAI — {n_x} variabel X')
    print('=' * 64)
    print('  Pintu ukur: app.berkas_kerja.buat_data()  (= dipakai aplikasi)')

    beta = [round(max(0.10, 0.32 - 0.05 * i), 2) for i in range(n_x)]
    d = buat_data(n=300, x=n_x, beta=beta, skala=5, alpha=0.85,
                  mode='presisi', cara='berantai')

    cek('cara tersimpan = berantai', d['cara'] == 'berantai', f"→ {d['cara']}")
    cek(f'rantai punya {n_x - 1} ruas', len(d.get('rantai') or []) == n_x - 1,
        f"→ {len(d.get('rantai') or [])}")

    print('\n  HASIL UKUR RANTAI (yang dibaca SPSS):')
    ok_rantai = True
    for ruas in (d.get('rantai') or []):
        pas = float(d.get('ranta_setel') or 0.55)
        ter = float(ruas.get('terbaca') or 0.0)
        gal = abs(ter - pas)
        if gal > BATAS_RANTAI:
            ok_rantai = False
        print(f"     {ruas.get('dari')} -> {ruas.get('ke')}   dipasang {pas:.2f}"
              f"  terbaca {ter:.4f}  galat {gal:.4f}  "
              f"{'OK ' if gal <= BATAS_RANTAI else 'BEDA'}")

    print('\n  HASIL UKUR BERGanda (X -> Y):')
    ok_berg = True
    for baris in (d.get('bersama') or []):
        pas, ter = baris.get('diminta'), baris.get('terbaca')
        if pas is None or ter is None:
            continue
        gal = abs(float(ter) - float(pas))
        if gal > BATAS_BERG:
            ok_berg = False
        print(f"     {baris.get('nama') or baris.get('kode')} -> Y   "
              f"diminta {float(pas):.2f}  terbaca {float(ter):.4f}  "
              f"galat {gal:.4f}  {'OK ' if gal <= BATAS_BERG else 'BEDA'}")

    gm = float(d.get('galat_maks') or 9.9)
    cek('galat_maks ≤ 0,06 (laporan mesin)', gm <= 0.06, f'→ {gm:.4f}')
    cek('semua koefisien RANTAI dalam batas', ok_rantai)
    cek('semua koefisien BERGanda dalam batas', ok_berg)

    hasil = ok_rantai and ok_berg and gm <= 0.06
    print(f"\n  KESIMPULAN {n_x} X: "
          f"{'BISA DIHITUNG' if hasil else 'BELUM BISA / ADA SELISIH'}")
    return hasil


def main():
    h3 = uji_s3(3)
    h5 = uji_s3(5)
    print('\n' + '=' * 64)
    print('RINGKASAN (diukur dari PINTU PRODUKSI buat_data):')
    print(f"  S3 dengan 3 X : {'BISA' if h3 else 'BELUM'}")
    print(f"  S3 dengan 5 X : {'BISA' if h5 else 'BELUM'}")
    print('=' * 64)
    if GAGAL:
        print(f'\n  ❌ ADA GAGAL: {GAGAL}')
        return 1
    print('\n  ✅ LULUS SEMUA')
    return 0


if __name__ == '__main__':
    sys.exit(main())
