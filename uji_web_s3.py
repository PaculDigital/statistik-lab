#!/usr/bin/env python3
"""UJI NYATA: S3 berganda-berantai lewat app.berkas_kerja (fungsi yang
dipakai /api/buat-data). BUKAN mockup — memanggil kode sungguhan.
"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from app.berkas_kerja import buat_data     # noqa: E402


def main():
    lulus = 0
    gagal = 0

    for x in (2, 3, 5):
        beta = [round(0.32 - 0.05 * i, 3) for i in range(x)]
        print(f"\n{'='*66}")
        print(f"S3 BERGANDA-BERANTAI — {x} X   (mode presisi, n=400)")
        print('='*66)
        d = buat_data(n=400, x=x, beta=beta, skala=5, alpha=0.85,
                      mode='presisi', cara='berantai')

        print(f"cara       : {d['cara']}")
        print(f"cara_label : {d['cara_label']}")
        print(f"galat_maks : {d['galat_maks']:.4f}")
        print(f"kekuatan rantai setelan : {d['ranta_setel']}")

        print("\n  [BAGIAN 1] pengaruh tiap X ke Y (bersama-sama):")
        for j in d['bersama']:
            tanda = 'OK ' if abs(j['terbaca'] - j['diminta']) <= 0.05 else 'BEDA'
            print(f"     {j['nama']:>16} diminta {j['diminta']:.2f} "
                  f"terbaca {j['terbaca']:+.4f}  p={j['p']:.4f} "
                  f"[{j['label']}] {tanda}")

        print("\n  [BAGIAN 2] hubungan antar-X (berantai):")
        if not d['rantai']:
            print("     ❌ KOSONG — rantai tidak terbentuk")
            gagal += 1
        for j in d['rantai']:
            print(f"     {j['dari']:>16} → {j['ke']:<16} "
                  f"terbaca {j['terbaca']:+.4f}  p={j['p']:.4f} [{j['label']}]")

        # ── PEMERIKSAAN ──
        jml_rantai_harus = x - 1
        if len(d['rantai']) != jml_rantai_harus:
            print(f"  ❌ jumlah rantai {len(d['rantai'])} "
                  f"(harus {jml_rantai_harus})")
            gagal += 1
            continue
        # rantai harus CUKUP KUAT (bukan 0) — hubungan antar-X nyata
        lemah = [j for j in d['rantai'] if abs(j['terbaca']) < 0.35]
        if lemah:
            print(f"  ❌ ada rantai terlalu lemah: "
                  f"{[(j['kode_dari'], round(j['terbaca'],3)) for j in lemah]}")
            gagal += 1
            continue
        # galat koefisien → Y harus dalam toleransi
        g = max(abs(j['terbaca'] - j['diminta']) for j in d['bersama'])
        if g > 0.06:
            print(f"  ❌ galat X→Y terlalu besar: {g:.4f}")
            gagal += 1
            continue
        print(f"  ✅ LULUS ({x} X) — galat X→Y {g:.4f}, "
              f"rantai {len(d['rantai'])} ruas, terkuat "
              f"{max(abs(j['terbaca']) for j in d['rantai']):.3f}")
        lulus += 1

    print(f"\n{'='*66}")
    print(f"HASIL: {lulus} LULUS / {gagal} GAGAL")
    print('='*66)
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
