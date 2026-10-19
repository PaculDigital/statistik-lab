"""Analis jalur UMUM untuk varian mediasi/moderasi lanjutan (Wulan, 19Okt26).

Fungsi bespoke di kaitan.py (mediasi, moderasi, mediasi_berjenjang) TERBUKTI
BENAR dan dilindungi gerbang — JANGAN diubah/diutak-atik. Modul ini menangani
varian yang analisnya BELUM ADA: mediasi paralel & campuran, moderasi dual,
moderasi jalur-a / jalur-b / keduanya / 3jalur, dan gabungan.

Prinsip (SAMA seperti kaitan.py):
  - df SUDAH terstandardisasi (z-score) oleh pemanggil — koefisien OLS = beta.
  - Suku interaksi = Xs × Zs (cara kaitan.moderasi — menghindari
    multikolinearitas palsu).
  - OLS + t/p cara kaitan._reg.
  - Pengaruh tak langsung = hasil kali koefisien sepanjang rantai,
    selang kepercayaan via bootstrap (cara kaitan.mediasi).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .kaitan import _reg, _std, AMBANG_P

N_BOOT = 500
SEED_BOOT = 721


def _siapkan(df: pd.DataFrame, kolom: list[str]):
    """Ambil kolom sebagai matriks numpy bersih (drop baris tak lengkap)."""
    d = df[kolom].apply(pd.to_numeric, errors='coerce').dropna()
    return d


def analisis_jalur_umum(df: pd.DataFrame, persamaan: list[dict],
                        rantai: list[dict] | None = None,
                        kondisional: list[dict] | None = None,
                        n_boot: int = N_BOOT,
                        seed: int = SEED_BOOT) -> dict:
    """Estimasi persamaan struktural generik + pengaruh tak langsung.

    persamaan: [{'target': 'M1', 'pred': ['X'],
                 'interaksi': [{'x': 'X', 'z': 'Z'}]}, ...]
      - 'pred': prediktor utama (efek langsung).
      - 'interaksi': tiap suku dibentuk Xs×Zs, masuk ke persamaan yang sama.
    rantai: [{'nama': 'X→M1→Y', 'jalur': ['X', 'M1', 'Y']}, ...]
      - pengaruh tak langsung = kali koefisien sepanjang rantai (bootstrap).
    kondisional: [{'nama': 'Z rendah (-1 SD)', 'rantai': ['X','M','Y'],
                   'mod': {('X','M'): ('X','Z', -1.0)}}]
      - pengaruh tak langsung BERSYARAT untuk mediasi termoderasi:
        tiap sisi rantai boleh diganti koefisien kondisional
        b_utama + b_int × nilai_z.
    """
    rantai = rantai or []
    kondisional = kondisional or []

    butuh = set()
    for p in persamaan:
        butuh.add(p['target'])
        butuh.update(p.get('pred', []))
        for it in p.get('interaksi', []):
            butuh.update([it['x'], it['z']])
    d = _siapkan(df, sorted(butuh))
    n = len(d)
    if n < 20:
        return {'boleh': False,
                'sebab': f'Setelah dibersihkan tinggal {n} baris. '
                         f'Butuh minimal 20 baris.'}
    arr = {c: d[c].to_numpy(float) for c in d.columns}
    std = {c: _std(v) for c, v in arr.items()}

    def rancang(pred: list[str], interaksi: list[dict]):
        """Matriks desain + nama kolom: prediktor lalu suku interaksi."""
        kol, nama = [], []
        for c in pred:
            kol.append(std[c]); nama.append(c)
        for it in interaksi:
            kol.append(std[it['x']] * std[it['z']])
            nama.append(f"{it['x']}×{it['z']}")
        return np.column_stack(kol), nama

    # ── 1. tiap persamaan: OLS penuh (+interaksi) & tereduksi (tanpa) ──
    hasil_eq = []
    for p in persamaan:
        t, pred = p['target'], list(p.get('pred', []))
        its = list(p.get('interaksi', []))
        Xf, nm_f = rancang(pred, its)
        Xr, nm_r = rancang(pred, [])
        yv = std[t]
        rf = _reg(yv, Xf)
        rr = _reg(yv, Xr)
        koef = []
        for i, nm in enumerate(nm_f):
            koef.append({'nama': nm, 'b': float(rf['b'][i]),
                         't': float(rf['t'][i]), 'p': float(rf['p'][i]),
                         'interaksi': i >= len(pred)})
        hasil_eq.append({
            'target': t, 'r2': float(rf['r2']),
            'r2_tanpa_interaksi': float(rr['r2']) if its else None,
            'delta_r2': float(rf['r2'] - rr['r2']) if its else None,
            'koef': koef,
        })

    # peta cepat: (dari, ke) -> koefisien pada data penuh
    def ambil(ke: str, dari: str) -> float:
        for eq in hasil_eq:
            if eq['target'] == ke:
                for k in eq['koef']:
                    if k['nama'] == dari and not k['interaksi']:
                        return k['b']
        return float('nan')

    def efek_rantai(jalur: list[str], ganti: dict | None = None) -> float:
        """Hasil kali koefisien sepanjang rantai (dengan modifikasi kondisional)."""
        ganti = ganti or {}
        total = 1.0
        for a, b_ in zip(jalur[:-1], jalur[1:]):
            if (a, b_) in ganti:
                total *= ganti[(a, b_)]
            else:
                total *= ambil(b_, a)
        return total

    # ── 2. pengaruh tak langsung + bootstrap ──
    def bootstrap(fx):
        rng = np.random.default_rng(seed)
        base = np.arange(n)
        vals = np.empty(n_boot)
        for i in range(n_boot):
            idx = rng.choice(base, n, replace=True)
            vals[i] = fx(idx)
        lo, hi = np.percentile(vals, [2.5, 97.5])
        return float(vals.mean()), float(lo), float(hi)

    def efek_boot(jalur: list[str], ganti_idx=None):
        # ganti_idx: {(a,b): (x_int, z_int, nilai_z)} untuk sisi termoderasi
        def satu(idx):
            tot = 1.0
            for a, b_ in zip(jalur[:-1], jalur[1:]):
                # cari persamaan target b_ (prediktor + suku interaksi)
                eq = next(e for e in hasil_eq if e['target'] == b_)
                pred = [k['nama'] for k in eq['koef'] if not k['interaksi']]
                its = []
                for k in eq['koef']:
                    if k['interaksi']:
                        x_, z_ = k['nama'].split('×')
                        its.append({'x': x_, 'z': z_})
                cols, _nm = [], []
                for c in pred:
                    cols.append(_std(arr[c][idx])); _nm.append(c)
                for it in its:
                    cols.append(_std(arr[it['x']][idx]) * _std(arr[it['z']][idx]))
                    _nm.append(f"{it['x']}×{it['z']}")
                Xb = np.column_stack(cols)
                yb = _std(arr[b_][idx])
                rb = _reg(yb, Xb)
                peta = dict(zip(_nm, rb['b']))
                if ganti_idx and (a, b_) in ganti_idx:
                    xi, zi, zv = ganti_idx[(a, b_)]
                    k_int = f"{xi}×{zi}"
                    tot *= float(peta[a] + peta.get(k_int, 0.0) * zv)
                else:
                    tot *= float(peta[a])
            return tot
        return satu

    tak_langsung = []
    for r in rantai:
        b = efek_rantai(r['jalur'])
        mean, lo, hi = bootstrap(efek_boot(r['jalur']))
        tak_langsung.append({
            'nama': r['nama'], 'b': float(b),
            'lo': lo, 'hi': hi,
            'signifikan': bool((lo > 0 and hi > 0) or (lo < 0 and hi < 0)),
        })

    kond = []
    for k in kondisional:
        g = {}
        for (a, b_), (xi, zi, zv) in k['mod'].items():
            eq = next(e for e in hasil_eq if e['target'] == b_)
            peta = {c['nama']: c['b'] for c in eq['koef']}
            g[(a, b_)] = float(peta[a] + peta.get(f"{xi}×{zi}", 0.0) * zv)
        b = efek_rantai(k['jalur'], g)
        kond.append({'nama': k['nama'], 'b': float(b)})

    return {'boleh': True, 'n': n, 'persamaan': hasil_eq,
            'tak_langsung': tak_langsung, 'kondisional': kond}
