
════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : server uji khusus
   Sebab                  : Menembak server uji khusus yang tidak lagi dinyalakan. Prasarana: :8122.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""Uji API buat-data dari DALAM kontainer — 3 mode."""
import json
import urllib.request

LULUS = GAGAL = 0


def kirim(n, x, beta, mode):
    d = json.dumps({'n': n, 'x': x, 'beta': beta, 'skala': 5,
                    'alpha': 0.85, 'mode': mode}).encode()
    r = urllib.request.Request('http://127.0.0.1:8000/api/buat-data', data=d,
                               headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(r, timeout=180).read())


UJI = [
    ('1X presisi  n=150', 150, 1, [0.35], 'presisi', 0.05),
    ('3X presisi  n=200', 200, 3, [0.32, 0.24, 0.15], 'presisi', 0.05),
    ('2X natural  n=120', 120, 2, [0.30, 0.12], 'natural', 0.35),
]

for nama, n, x, b, mode, tol in UJI:
    try:
        d = kirim(n, x, b, mode)
    except Exception as e:                                   # noqa: BLE001
        print(f'  ❌ {nama}: GAGAL panggil — {e}')
        GAGAL += 1
        continue
    kolom_ok = d['jumlah_item'] == (x + 1) * 3
    ok = d['galat_maks'] <= tol and d['n'] == n and kolom_ok
    tanda = '✅' if ok else '❌'
    print(f"  {tanda} {nama}: galat={d['galat_maks']:.4f} (tol {tol}) | "
          f"{d['jumlah_item']} kolom | R2={d['r2']:.3f} | mode={d['mode_label']}")
    LULUS += 1 if ok else 0
    GAGAL += 0 if ok else 1

# signifikansi benar-benar muncul sesuai ramalan
d = kirim(120, 2, [0.30, 0.12], 'natural')
ns = [j for j in d['jalur'] if j['label'] == 'Tidak signifikan']
ok = len(ns) >= 1
print(f"  {'✅' if ok else '❌'} β kecil (0,12) di n=120 benar-benar TIDAK SIGNIFIKAN")
LULUS += 1 if ok else 0
GAGAL += 0 if ok else 1

print(f"  HASIL: {LULUS} LULUS / {GAGAL} GAGAL")
raise SystemExit(0 if GAGAL == 0 else 1)
