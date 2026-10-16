"""
PEMBANGKIT DARI SPEK — mendukung INTERAKSI di SEMBARANG TARGET.

═══════════════════════════════════════════════════════════════════════════
KENAPA DITULIS ULANG (17Sep26, temuan terukur):

  Versi lama HANYA menambah suku interaksi ke "Y" (hard-coded nama).
  Akibatnya moderasi di jalur-a (mis. X1 x Z1 -> M) TIDAK berpengaruh:
    terukur: X1xZ1->M minta 0,25 keluar -0,0122 (galat -0,2622)
  Sedangkan moderasi di jalur-b (M x Z2 -> Y) sudah benar:
    terukur: MxZ2->Y minta 0,15 keluar 0,1496 (galat -0,0004)

  Versi ini membangun SEMUA target yang punya suku interaksi SETELAH
  variabel sumber & moderatornya siap — jadi moderasi di jalur mana pun
  (a, b, c', atau kombinasi) bekerja.

ATURAN:
  1. Variabel tanpa sumber (mis. moderator Z) = EKSOGEN, dibangkitkan dulu.
  2. Urutan pembangunan mengikuti arah panah (induk -> anak), tapi target
     yang punya INTERAKSI ditunda sampai sumber + moderatornya ada.
  3. Suku interaksi = (x - rata2)(z - rata2), distandardisasi.
  4. Satu target = satu regresi: sumber biasa + semua suku interaksinya.
  5. Tiap konstruk pakai rng SENDIRI (akar putaran 17).
  6. Y dan anak TIDAK di-_std() setelah derau (akar putaran 16).
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import numpy as np

from .berurutan import (_std, _alpha_ke_rho, alpha_rencana,
                        bangun_berurutan, turunkan_item, tambah_rasa_lapangan)


def bangun_dari_spek(spek, n_resp: int = 187, item_per: int = 4, skala: int = 5,
                     korelasi_x: float = 0.2,
                     alpha_rentang: tuple[float, float] = (0.72, 0.90),
                     koreksi_atenuasi: bool = True, rasa_lapangan=None,
                     sd_derau: float | None = None, seed: int = 42) -> dict:
    """Bangun data lengkap dari spek (jalur + interaksi di target mana pun).

    spek = {
      "jalur": [{"target": "M", "dari": {"X1": 0.60}}, ...],
      "interaksi": [{"target": "M", "x": "X1", "z": "Z1", "bobot": 0.25}, ...]
    }
    """
    if isinstance(spek, dict):
        jalur = [dict(j) for j in spek.get("jalur", [])]
        interaksi = [dict(it) for it in (spek.get("interaksi") or [])]
    else:
        jalur = [dict(j) for j in spek]
        interaksi = []

    for it in interaksi:
        it.setdefault("bobot", 0.20)
        it.setdefault("sumber", f'{it["x"]}x{it["z"]}')

    # ── 0. pastikan tidak ada target ganda (satu target = satu regresi) ────
    peta: dict[str, dict] = {}
    for j in jalur:
        peta.setdefault(j["target"], {})
        peta[j["target"]].update(j["dari"])

    # ── 1. moderator / variabel tanpa sumber = eksogen ────────────────────
    eksogen = {t for t, d in peta.items() if not d}
    for it in interaksi:
        for nm in (it["x"], it["z"]):
            if nm not in peta:
                eksogen.add(nm)
    # sumber yang tidak pernah jadi target juga eksogen
    for t, d in peta.items():
        for s in d:
            if s not in peta:
                eksogen.add(s)

    # ── 2. interaksi per target ───────────────────────────────────────────
    inter_per_target: dict[str, list[dict]] = {}
    for it in interaksi:
        inter_per_target.setdefault(it["target"], []).append(it)

    # ── 3. urutan pembangunan (arah panah + tunda yang berinteraksi) ──────
    selesai: set[str] = set(eksogen)
    urutan: list[str] = []
    tersisa = {t: dict(d) for t, d in peta.items() if d}
    while tersisa:
        maju = False
        for t in list(tersisa):
            butuh = set(tersisa[t])
            for it in inter_per_target.get(t, []):
                butuh |= {it["x"], it["z"]}
            # moderator yang eksogen sudah selesai; sumber harus selesai
            if butuh <= selesai:
                urutan.append(t)
                selesai.add(t)
                del tersisa[t]
                maju = True
        if not maju:
            sisa = ', '.join(sorted(tersisa))
            raise ValueError(
                f'Spek tidak bisa dibangun — jalur melingkar atau sumber '
                f'tidak ada: {sisa}')

    # ── 4. alpha: tentukan DI AWAL & paksa tetap (kalau berubah, kalibrasi
    #      tidak pernah konvergen) ────────────────────────────────────────
    semua_nama = sorted(set(peta) | eksogen |
                        {it["sumber"] for it in interaksi})
    bobot_alpha = {t: max((abs(float(v)) for v in d.values()), default=0.0)
                   for t, d in peta.items()}
    al = alpha_rencana(semua_nama, alpha_rentang[0], alpha_rentang[1],
                       bobot_alpha, seed)

    sd = _derau_otomatis(peta, inter_per_target, sd_derau)

    # ── 5. bangun eksogen (terstandardisasi, saling berkorelasi) ──────────
    nilai: dict[str, np.ndarray] = {}
    rng_e = np.random.default_rng(seed + 31)
    eks_sorted = sorted(eksogen)
    k = len(eks_sorted)
    if k:
        R = np.full((k, k), float(korelasi_x))
        np.fill_diagonal(R, 1.0)
        try:
            L = np.linalg.cholesky(R)
        except np.linalg.LinAlgError:
            L = np.eye(k)
        Z = rng_e.normal(0, 1, (n_resp, k)) @ L.T
        for i, nm in enumerate(eks_sorted):
            nilai[nm] = _std(Z[:, i])

    # ── 6. bangun target berurutan (rng SENDIRI per konstruk) ─────────────
    for i_l, t in enumerate(urutan):
        rng_t = np.random.default_rng(seed * 100003 + 7919 * (i_l + 1))
        lin = np.zeros(n_resp)

        # (a) sumber biasa
        for src, bob in peta[t].items():
            b = float(bob)
            if koreksi_atenuasi and b != 0.0:
                rho = _alpha_ke_rho(float(al.get(src, 0.85))) * \
                      _alpha_ke_rho(float(al.get(t, 0.85)))
                b = b / max(0.30, rho)
            lin += b * nilai[src]

        # (b) suku interaksi target ini
        for it in inter_per_target.get(t, []):
            a_ = nilai[it["x"]] - nilai[it["x"]].mean()
            b_ = nilai[it["z"]] - nilai[it["z"]].mean()
            suku = _std(a_ * b_)
            nilai[it["sumber"]] = suku
            if it["sumber"] not in al:
                al[it["sumber"]] = float(np.clip(
                    al.get(it["x"], 0.85) * al.get(it["z"], 0.85), 0.60, 0.95))
            b = float(it["bobot"])
            if koreksi_atenuasi and b != 0.0:
                rho = _alpha_ke_rho(float(al.get(it["sumber"], 0.80))) * \
                      _alpha_ke_rho(float(al.get(t, 0.85)))
                b = b / max(0.30, rho)
            lin += b * suku

        # ⚠ JANGAN _std() pada anak (akar putaran 16)
        nilai[t] = lin + rng_t.normal(0, sd, n_resp)

    # ── 7. turunkan ke item Likert + rasa lapangan ────────────────────────
    it_l = turunkan_item(nilai, al, item_per=item_per, skala=skala, seed=seed)
    lap = tambah_rasa_lapangan(it_l, rasa_lapangan=rasa_lapangan, seed=seed)

    return {"nama_konstruk": list(nilai.keys()), "item": lap["item"],
            "n_resp": n_resp, "alpha_dipakai": al,
            "muat_dipakai": it_l["muat_dipakai"], "seed": seed,
            "responden_asal": lap["responden_asal"],
            "responden_outlier": lap["responden_outlier"],
            "rasa_lapangan": lap["rasa_lapangan"],
            "skor_konstruk": {k2: v.tolist() for k2, v in nilai.items()}}


def _derau_otomatis(peta: dict, inter_per_target: dict,
                    sd_derau: float | None) -> float:
    """Derau dari STRUKTUR: makin banyak 'saudara' (induk sama), makin besar.

    Temuan terukur: 2 saudara -> 1,0 ; 3 saudara -> 1,2 ; 1 -> 0,5.
    """
    if sd_derau is not None:
        return float(sd_derau)
    dari: dict[str, set] = {}
    for t, d in peta.items():
        for s in d:
            dari.setdefault(s, set()).add(t)
    for t, lst in inter_per_target.items():
        for it in lst:
            dari.setdefault(it["x"], set()).add(t)
    terbanyak = max((len(v) for v in dari.values()), default=1)
    if terbanyak <= 1:
        return 0.5
    return float(np.clip(0.5 + 0.25 * (terbanyak - 1), 0.5, 1.5))
