"""UJI MESIN MANOVA — 10 bagian + kekuatan + bisa gagal.

Dipakai untuk menjaga agar MANOVA tidak rusak tanpa ketahuan.
Setiap uji WAJIB terbukti BISA GAGAL (aturan induk proyek ini).
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, '/opt/data/services/statistik-lab')
from app.hitung.kelompok import (BEDA_MAKS, BEDA_MIN, buat_data_kelompok,
                                 periksa_beda, ukur_ulang)
from app.hitung.manova import bisa_manova, hitung_manova

lulus = gagal = 0
pesan: list[str] = []


def catat(ok: bool, teks: str, tambahan: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        pesan.append(f'  ✅ {teks}' + (f'   {tambahan}' if tambahan else ''))
    else:
        gagal += 1
        pesan.append(f'  ❌ {teks}' + (f'   {tambahan}' if tambahan else ''))


def main() -> int:
    # ═══ [1] SSCP: T = W + B (bukti pecahan variansi BENAR) ═══════════
    d = buat_data_kelompok(n_per_kelompok=60, nama_kelompok=['A', 'B'],
                           nama_y=['Y1', 'Y2'], beda=[0.9, 0.54], seed=7)
    r = hitung_manova(d['Y'], d['kelompok'], d['nama_y'])
    catat(r['boleh'], 'MANOVA menghitung (boleh=True)')
    catat(r['selisih_sscp'] < 1e-8,
          'SSCP sehat: T - (W+B) = 0', f"{r['selisih_sscp']:.2e}")

    # ═══ [2] EMPAT STATISTIK UJI keluar & masuk akal ═════════════════
    st = r['statistik']
    catat(0 < st['wilks'] <= 1, "Wilks' Lambda di (0,1]",
          f"{st['wilks']:.5f}")
    catat(0 <= st['pillai'] <= 1, "Pillai's Trace di [0,1]",
          f"{st['pillai']:.5f}")
    catat(st['hotelling'] >= 0, 'Hotelling-Lawley >= 0',
          f"{st['hotelling']:.5f}")
    catat(st['roy'] >= 0, "Roy's Largest Root >= 0", f"{st['roy']:.5f}")
    catat(st['roy'] <= st['hotelling'] + 1e-9,
          'Roy <= Hotelling (Roy = akar TERBESAR saja)')

    # ═══ [3] Konversi F & p — arah benar ════════════════════════════
    for nm in ('wilks', 'pillai', 'hotelling', 'roy'):
        q = r['uji'][nm]
        catat(q['p'] is not None and 0 <= q['p'] <= 1,
              f'{nm}: F & p terhitung', f"F={q['F']:.3f} p={q['p']:.6f}")

    # ═══ [4] KEKUATAN: beda BESAR → signifikan; beda NOL → tidak ════
    d_besar = buat_data_kelompok(n_per_kelompok=80, nama_kelompok=['A', 'B'],
                                 nama_y=['Y1', 'Y2'], beda=[1.20, 0.90],
                                 seed=11)
    r_besar = hitung_manova(d_besar['Y'], d_besar['kelompok'],
                            d_besar['nama_y'])
    p_besar = r_besar['uji']['pillai']['p']
    catat(p_besar < 0.05, 'Beda BESAR → MANOVA signifikan',
          f"p={p_besar:.6f}")

    d_nol = buat_data_kelompok(n_per_kelompok=80, nama_kelompok=['A', 'B'],
                               nama_y=['Y1', 'Y2'], beda=[0.0, 0.0], seed=11)
    r_nol = hitung_manova(d_nol['Y'], d_nol['kelompok'], d_nol['nama_y'])
    p_nol = r_nol['uji']['pillai']['p']
    catat(p_nol >= 0.05, 'Beda NOL → MANOVA TIDAK signifikan',
          f"p={p_nol:.4f}")

    # ═══ [5] Tambah kelompok → makin mudah terdeteksi ═══════════════
    d3 = buat_data_kelompok(n_per_kelompok=60,
                            nama_kelompok=['A', 'B', 'C'],
                            nama_y=['Y1', 'Y2'], beda=[0.0, 0.6], seed=13)
    r3 = hitung_manova(d3['Y'], d3['kelompok'], d3['nama_y'])
    catat(r3['boleh'] and r3['k'] == 3, 'MANOVA 3 kelompok jalan',
          f"k={r3['k']} p={r3['uji']['pillai']['p']:.6f}")

    # ═══ [6] ANOVA per-Y: Y yang berbeda ikut terdeteksi ════════════
    lanjut = {q['y']: q for q in r_besar['lanjut']}
    catat(all(q['p'] is not None for q in r_besar['lanjut']),
          'ANOVA per-Y terhitung semua', f"{len(r_besar['lanjut'])} Y")
    catat(all(q['label'] == 'Berbeda' for q in r_besar['lanjut']),
          'Y yang beda besar → semua berlabel "Berbeda"')
    catat(lanjut['Y1']['rerata'][0]['n'] == 80,
          'rerata per kelompok melaporkan n', f"n={lanjut['Y1']['rerata'][0]['n']}")

    # ═══ [7] ASUMSI terhitung (WAJIB — jangan sampai dilewat) ═══════
    a = r['asumsi']
    catat(a['box_m']['p'] is not None, "Box's M terhitung",
          f"M={a['box_m']['M']:.4f} p={a['box_m']['p']:.4f}")
    catat(len(a['levene']) == 2, 'Levene per-Y terhitung',
          f"{len(a['levene'])} Y")
    catat(a['pencilan']['jumlah'] == 0, 'Pencilan dihitung',
          f"jumlah={a['pencilan']['jumlah']}")
    catat(a['mardia']['p'] is not None, 'Normalitas multivariat (Mardia)',
          f"p={a['mardia']['p']:.4f}")

    # Box's M HARUS bisa menangkap pelanggaran (uji bisa-gagal)
    rng = np.random.default_rng(5)
    n = 60
    Ya = rng.normal(0, 1, (n, 2))
    Yb = rng.normal(0.6, 4.0, (n, 2))          # sebaran 4× lebih lebar
    Y_v = np.vstack([Ya, Yb])
    kel_v = np.array(['A'] * n + ['B'] * n)
    r_v = hitung_manova(Y_v, kel_v, ['Y1', 'Y2'])
    catat(r_v['asumsi']['box_m']['p'] < 0.05,
          "Box's M MENANGKAP sebaran yang beda (bisa gagal)",
          f"p={r_v['asumsi']['box_m']['p']:.6f}")

    # ═══ [8] Kalimat kesimpulan — bahasa manusia, ada isinya ════════
    catat(len(r_besar['kalimat']) >= 1, 'Kalimat kesimpulan ada',
          f"{len(r_besar['kalimat'])} baris")
    catat('perbedaan NYATA' in r_besar['kalimat'][0],
          'Kalimat beda besar: menyebut perbedaan NYATA')
    catat('TIDAK ada perbedaan' in r_nol['kalimat'][0],
          'Kalimat beda nol: menyebut TIDAK ada perbedaan')

    # ═══ [9] PAGAR syarat minimal ════════════════════════════════════
    g1 = bisa_manova(['A', 'A', 'B', 'B'], ['Y1'])
    catat(not g1['bisa'], 'Tolak kalau Y cuma 1', g1['sebab'][:40])
    g2 = bisa_manova(['A', 'A', 'A', 'A'], ['Y1', 'Y2'])
    catat(not g2['bisa'], 'Tolak kalau kelompok cuma 1', g2['sebab'][:40])
    g3 = bisa_manova(['A', 'A', 'B', 'B'], ['Y1', 'Y2'])
    catat(not g3['bisa'], 'Tolak kalau isi kelompok < 3',
          g3['sebab'][:40])
    g4 = bisa_manova(['A', 'A', 'A', 'B', 'B', 'B'], ['Y1', 'Y2'])
    catat(g4['bisa'], 'Terima kalau syarat terpenuhi')

    # ═══ [10] PAGAR beda (ACC Bos 21Sep26, Opsi A) ══════════════════
    catat(periksa_beda([0.6, 1.2])['boleh'], 'Beda dalam rentang → boleh',
          f"{BEDA_MIN}–{BEDA_MAKS}")
    catat(not periksa_beda([2.5])['boleh'], 'Beda 2,50 → DITOLAK')
    catat(not periksa_beda([0.10])['boleh'], 'Beda 0,10 → DITOLAK')
    catat('saran' in periksa_beda([2.5]), 'Penolakan menyertakan SARAN')

    # pagar BENAR-BENAR dipakai (bukan cuma ada)
    try:
        buat_data_kelompok(n_per_kelompok=30, nama_kelompok=['A', 'B'],
                           nama_y=['Y1', 'Y2'], beda=[2.5, 2.5], seed=1)
        catat(False, 'buat_data_kelompok MENOLAK beda 2,50', 'lolos!')
    except ValueError as e:
        # ⚠️ PELAJARAN (21Sep26): jangan pakai kata dari pesan yang bisa berubah
        #    ("rentang" hilang saat pesan diperbaiki) → gagal palsu.
        #    Pakai penanda yang PASTI: kata "akurat" + angka batasnya.
        catat('akurat' in str(e) and f'{BEDA_MAKS:.2f}' in str(e),
              'buat_data_kelompok MENOLAK beda 2,50', str(e)[:50])

    # ═══ [11] AKURASI kalibrasi (kunci jawaban) ═════════════════════
    galat = []
    for beda in (0.50, 0.90, 1.20):
        for s in (7, 33, 99):
            dd = buat_data_kelompok(n_per_kelompok=200,
                                    nama_kelompok=['A', 'B'], nama_y=['Y1'],
                                    beda=[beda], seed=s)
            Y = dd['Y'][:, 0]
            kel = dd['kelompok']
            t = Y[kel == 'B'].mean() - Y[kel == 'A'].mean()
            galat.append(abs(beda - t) / beda)
    rata = float(np.mean(galat))
    catat(rata < 0.15, 'Kalibrasi akurat (< 15% meleset)',
          f"rata meleset {rata * 100:.1f}%")

    # ukur_ulang mengakui hasilnya sendiri
    u = ukur_ulang(d)
    catat('galat_maks' in u, 'ukur_ulang melaporkan galat',
          f"galat={u['galat_maks']:.4f}")

    # ═══ [12] Kolom kelompok TERPISAH (R4 dipatuhi) ══════════════════
    catat(len(d['kelompok']) == d['n'], 'kolom kelompok sepanjang data',
          f"{d['n']}")
    catat(set(np.unique(d['kelompok'])) == {'A', 'B'},
          'kolom kelompok memuat nama kelompok')

    # ═══ [13] HASIL BISA DIKIRIM LEWAT HTTP (json) ═══════════════════
    # ⚠️ PELAJARAN 21Sep26: hasil mesin memuat ndarray → halaman dapat 500
    #    "Object of type ndarray is not JSON serializable". Uji ini menjaga
    #    supaya cacat itu tidak kembali tanpa ketahuan.
    import json as _json

    def _ada_numpy(o, jalur='') -> list:
        temuan = []
        if isinstance(o, np.ndarray):
            temuan.append(jalur)
        elif isinstance(o, (np.floating, np.integer, np.bool_)):
            temuan.append(jalur)
        elif isinstance(o, dict):
            for kk, vv in o.items():
                temuan += _ada_numpy(vv, f'{jalur}.{kk}')
        elif isinstance(o, (list, tuple)):
            for i, vv in enumerate(o[:5]):
                temuan += _ada_numpy(vv, f'{jalur}[{i}]')
        return temuan

    sisa = _ada_numpy(r)
    catat(not sisa, 'hasil MANOVA bersih dari numpy (bisa di-JSON)',
          f'{len(sisa)} sisa' if sisa else '')
    try:
        _json.dumps(r)
        catat(True, 'hasil MANOVA benar-benar bisa di-JSON-kan')
    except TypeError as e:
        catat(False, 'hasil MANOVA bisa di-JSON-kan', str(e)[:50])

    # pandas DataFrame juga harus jalan (halaman bisa kirim dari berkas)
    try:
        import pandas as pd
        Ydf = pd.DataFrame(d['Y'], columns=d['nama_y'])
        r_df = hitung_manova(Ydf, d['kelompok'])
        catat(r_df['boleh'] and r_df['nama_y'] == d['nama_y'],
              'terima pandas DataFrame + nama kolom otomatis')
    except ImportError:
        pass

    # ═══ [15] df LENGKAP untuk KEEMPAT ukuran (temuan MATA 22Sep26) ═══
    # 🔴 CACAT YANG DITUTUP: mesin HANYA menyimpan df untuk Wilks; Pillai,
    #    Hotelling, Roy tidak → kolom df di halaman jadi '—, —' (terlihat
    #    MATA, tidak tertangkap uji teks mana pun). Mesinnya sudah BENAR
    #    (p dihitung dengan df yang sama) — yang hilang cuma laporan df-nya.
    #    ⚠️ Jangan pernah kembalikan 'F'/'p' tanpa 'df1'/'df2'.
    for nm in ('wilks', 'pillai', 'hotelling', 'roy'):
        q = r['uji'][nm]
        catat(q.get('df1') is not None and q.get('df2') is not None,
              f'{nm}: df1 & df2 dilaporkan (bukan kosong)',
              f"df1={q.get('df1')} df2={q.get('df2')}")
        # df tidak boleh aneh: df1 > 0 dan df2 > 0
        d1, d2 = q.get('df1'), q.get('df2')
        catat((d1 or 0) > 0 and (d2 or 0) > 0,
              f'{nm}: df bernilai positif')

    # ═══ [14] MODE 'natural' TIDAK BOLEH MENGHAPUS BEDA ═══════════════
    #    → beda kelompok HILANG SEPENUHNYA → MANOVA tidak pernah menemukan
    #    perbedaan padahal kelompoknya memang dibuat berbeda. Menyesatkan.
    for md in ('presisi', 'natural', 'presisi_variasi'):
        dn = buat_data_kelompok(n_per_kelompok=120, nama_kelompok=['A', 'B'],
                                nama_y=['Y1', 'Y2'], beda=[1.20, 0.90],
                                seed=17, mode=md)
        Yn = dn['Y'][:, 0]
        kn = dn['kelompok']
        tn = float(Yn[kn == 'B'].mean() - Yn[kn == 'A'].mean())
        catat(tn > 0.5, f"mode '{md}': beda TETAP ada (tidak dihapus)",
              f'terbaca {tn:.3f} dari 1,20')

    # presisi harus LEBIH dekat ke setelan daripada natural
    dp = buat_data_kelompok(n_per_kelompok=200, nama_kelompok=['A', 'B'],
                            nama_y=['Y1'], beda=[1.20], seed=23, mode='presisi')
    dn2 = buat_data_kelompok(n_per_kelompok=200, nama_kelompok=['A', 'B'],
                             nama_y=['Y1'], beda=[1.20], seed=23, mode='natural')
    gp = abs(1.20 - float(dp['Y'][:, 0][dp['kelompok'] == 'B'].mean()
                          - dp['Y'][:, 0][dp['kelompok'] == 'A'].mean()))
    gn = abs(1.20 - float(dn2['Y'][:, 0][dn2['kelompok'] == 'B'].mean()
                          - dn2['Y'][:, 0][dn2['kelompok'] == 'A'].mean()))
    catat(gp < gn, "mode 'presisi' lebih akurat daripada 'natural'",
          f'galat presisi {gp:.3f} < natural {gn:.3f}')

    print('=' * 74)
    print(' UJI MESIN MANOVA')
    print('=' * 74)
    for p in pesan:
        print(p)
    print()
    print('=' * 74)
    if gagal:
        print(f' ❌ ADA GAGAL: {gagal}  (lulus {lulus})')
        return 1
    print(f' ✅ {lulus} LULUS / 0 GAGAL — MANOVA siap')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
