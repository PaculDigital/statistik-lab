"""UJI BAHAN GAMBAR (Tahap 2.1) — apakah bahan grafik dari mesin masuk akal.

⚠️ ATURAN: bukan cuma "kuncinya ADA", tapi juga "isinya WAJAR".
   Gerbang yang cuma cek keberadaan = gerbang yang tak menjaga apa pun.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

from app.diagnosis import periksa_spss                          # noqa: E402


def _data(sehat=True):
    """Data uji: sehat (derau tetap) atau sakit (corong hetero).

    ⚠️ PELAJARAN STATISTIK (terukur 20Sep26, jangan salah pilih lagi):
    derau yang membesar LINEAR (mis. `1 + 3|x1|`) TIDAK terdeteksi Glejser —
    Glejser menguji |sisa| lawan X secara LINEAR, sedangkan |x1| bukan bentuk
    linear. Terukur: `1+1,5|x1|` p=0,44 · `1+3|x1|` p=0,31 · `1+5|x1|` p=0,18
    → SEMUA masih "lulus" walau matanya sudah melihat corong.
    Yang BENAR-BENAR terdeteksi: derau membesar EKSPONENSIAL → `exp(1,2·x1)`
    → Glejser p=0,0000. Inilah bentuk corong yang sesungguhnya.
    """
    rng = np.random.default_rng(7)
    n = 120
    x1 = rng.normal(0, 1, n)
    x2 = rng.normal(0, 1, n)
    dasar = 0.45 * x1 + 0.30 * x2
    if sehat:
        y = dasar + rng.normal(0, 1, n)
    else:
        y = dasar + rng.normal(0, 1, n) * np.exp(1.2 * x1)
    return pd.DataFrame({'X1': x1, 'X2': x2, 'Y': y})


def main() -> int:
    gagal = 0
    total = 0

    def cek(nama, syarat, info=''):
        nonlocal gagal, total
        total += 1
        if syarat:
            print(f'  \u2705 {nama}')
        else:
            gagal += 1
            print(f'  \u274c {nama} {info}')

    for sehat in (True, False):
        label = 'sehat' if sehat else 'sakit (corong)'
        print(f'\n\u2500\u2500 data {label} \u2500\u2500')
        r = periksa_spss(_data(sehat), ['X1', 'X2'], 'Y')
        t = r['titik']

        cek('kunci titik lengkap',
            set(t) >= {'zpred', 'zresid', 'pp', 'hist', 'xy'}, sorted(t))

        # ── scatter hetero ──
        cek('zpred & zresid sama panjang',
            len(t['zpred']) == len(t['zresid']) == r['n'])
        # ⚠️ AKAR (20Sep26) — CACAT UJI WULAN, sama kelas seperti 19Sep26:
        # angka di `titik` sudah DIBULATKAN oleh `_f()` ke 6 desimal saat
        # dikirim ke halaman. Jadi rata-ratanya bukan persis 0, tapi sisa
        # pembulatan (~1e-6). Ambang 1e-6 terlalu ketat → GAGAL PALSU.
        # Ambang yang benar: 1e-4 (masih jauh lebih kecil dari simpangan 1,0).
        cek('zpred rata-rata \u2248 0 (distandarkan)',
            abs(float(np.mean(t['zpred']))) < 1e-4)
        cek('zresid rata-rata \u2248 0 (distandarkan)',
            abs(float(np.mean(t['zresid']))) < 1e-4)

        # ── P-P plot ──
        th, am = t['pp']['teori'], t['pp']['amati']
        cek('pp: teori & amati sama panjang = n',
            len(th) == len(am) == r['n'])
        cek('pp: amati NAIK monoton (diurutkan)',
            all(am[i] <= am[i + 1] for i in range(len(am) - 1)))
        cek('pp: teori NAIK monoton',
            all(th[i] <= th[i + 1] for i in range(len(th) - 1)))
        cek('pp: amati dalam 0\u20261 (peluang)',
            all(0 <= v <= 1 for v in am))
        cek('pp: teori median \u2248 0 (berpusat)',
            abs(float(np.median(th))) < 0.15, f'median={np.median(th):.4f}')

        # ── histogram ──
        h = t['hist']
        cek('hist: ada 5\u202614 bin', 5 <= h['n_bin'] <= 14, h['n_bin'])
        cek('hist: batas = n_bin + 1', len(h['batas']) == h['n_bin'] + 1)
        cek('hist: total tinggi = jumlah sisa',
            sum(h['tinggi']) == r['n'], f"{sum(h['tinggi'])} vs {r['n']}")
        cek('hist: batas menaik',
            all(h['batas'][i] < h['batas'][i + 1] for i in range(len(h['batas']) - 1)))

        # ── scatter linearitas ──
        cek('xy: x & y sama panjang', len(t['xy']['x']) == len(t['xy']['y']))
        cek('xy: semua angka sampai (tidak ada NaN)',
            all(np.isfinite(v) for v in t['xy']['x'] + t['xy']['y']))

        # ── ⭐ UJI BEDA NYATA: sehat vs sakit HARUS BEDA ──
        if not sehat:
            # data corong: |sisa| berkorelasi dengan predator → Glejser tangkap
            cek('data corong TERDETEKSI hetero', r['hetero']['lulus'] is False,
                f"glejser_p={r['hetero']['glejser_p']}")

    # ── sehat vs sakit: hasil hetero WAJIB berbeda ──
    print('\n\u2500\u2500 pembanding: sehat vs sakit HARUS BEDA \u2500\u2500')
    a = periksa_spss(_data(True), ['X1', 'X2'], 'Y')
    b = periksa_spss(_data(False), ['X1', 'X2'], 'Y')
    cek('hetero: sehat lulus, sakit tidak',
        a['hetero']['lulus'] is True and b['hetero']['lulus'] is False,
        f"sehat={a['hetero']['lulus']} sakit={b['hetero']['lulus']}")
    cek('zresid: sebaran sakit lebih lebar (corong)',
        float(np.std(np.abs(b['titik']['zresid']))) >
        float(np.std(np.abs(a['titik']['zresid']))))

    print()
    if gagal:
        print(f'  \u274c GAGAL: {gagal} dari {total}')
        return 1
    print(f'  \u2705 LULUS SEMUA: {total} pemeriksaan')
    return 0


if __name__ == '__main__':
    sys.exit(main())
