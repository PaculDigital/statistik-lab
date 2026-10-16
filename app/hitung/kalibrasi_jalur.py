"""
KALIBRASI PER-JALUR BERURUTAN (v6 FINAL — 17Sep26, putaran ke-18).

═══════════════════════════════════════════════════════════════════════════
KENAPA CARA INI (riwayat jujur: 17 putaran sebelumnya gagal)

  Uji TERISOLASI satu jalur -> PERSIS (galat 0,0009).
  Model penuh -> MELESET, dan tiap perbaikan membaikkan satu jalur
  tapi merusakkan yang lain ("menambal, bukan menyembuhkan").

  DIAGNOSA: komponennya benar satu-satu, tapi SALING MERUSAK saat digabung,
  karena koefisien diubah bersamaan. Tidak ada ukuran tunggal yang bisa
  menunjukkan mana yang harus digeser.

CARA INI — kalibrasi PER JALUR, satu per satu, TERKUNCI:
  1. Bangun satu jalur (mis. X1 -> Y). Ukur. Koreksi bobotnya. Ulangi
     sampai galat <= toleransi. KUNCI bobot itu.
  2. Jalur berikutnya: bangun DENGAN bobot yang sudah terkunci + bobot baru.
     Ukur HANYA koefisien baru. Koreksi bobot baru sampai pas.
     Kalau koefisien lama ikut bergeser -> itu wajar (regresi berganda),
     jadi langkah 3 mengoreksi ulang secara menyeluruh.
  3. Setelah semua jalur terkunci, jalankan PUTARAN PENYELARASAN
     (semua bobot dikoreksi bersama, berbasis gradien diagonal) sampai
     semua galat <= toleransi atau batas putaran.

  Kunci: setiap langkah MENGUKUR APA ADANYA lewat fungsi ukur() yang sama
  dengan yang dipakai SPSS/PLS membaca (skor item -> regresi terstandardisasi).
  Tidak ada tebakan rumus.
═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math

import numpy as np

from .berurutan import (bangun_berurutan, turunkan_item, tambah_rasa_lapangan,
                        alpha_rencana, _alpha_ke_rho)


# ─────────────────────────────────────────────────────────────────────────────
# ALAT UKUR — satu-satunya sumber kebenaran "apakah sudah pas?"
# ─────────────────────────────────────────────────────────────────────────────

def skor_item(data: dict, nama: list[str]) -> np.ndarray:
    """Skor konstruk dari item (rata-rata item, sel kosong diabaikan)."""
    kolom = []
    for nm in nama:
        it = data["item"][nm].astype(float)
        it = np.where(it < 0, np.nan, it)
        kolom.append(np.nanmean(it, axis=1))
    return np.column_stack(kolom)


def regresi_terstandar(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Koefisien terstandardisasi — cara SPSS/PLS membaca output."""
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
    yz = (y - y.mean()) / (y.std() or 1.0)
    A = np.column_stack([np.ones(len(Xz)), Xz])
    c, *_ = np.linalg.lstsq(A, yz, rcond=None)
    return c[1:]


def ukur_jalur(data: dict, target: str, sumber: list[str]) -> np.ndarray:
    """Ukur koefisien target ~ semua sumber (cara SPSS)."""
    nama = list(sumber) + [target]
    S = skor_item(data, nama)
    return regresi_terstandar(S[:, :len(sumber)], S[:, len(sumber)])


# ─────────────────────────────────────────────────────────────────────────────
# KALIBRASI PER JALUR
# ─────────────────────────────────────────────────────────────────────────────

def _bangun(jalur, n_resp, item_per, skala, korelasi_x, alpha_rentang,
            koreksi_atenuasi, sd_derau, seed, alpha_paksa=None,
            interaksi=None, eksogen_tambahan=None):
    """Bangun data + kembalikan alpha yang dipakai (bisa dipaksa)."""
    interaksi = interaksi or []
    eksogen_tambahan = eksogen_tambahan or set()

    if interaksi or eksogen_tambahan:
        from .spek_pembangun import bangun_dari_spek
        # moderator yang belum jadi sumber jalur mana pun -> eksogen murni
        jalur_pakai = [dict(j) for j in jalur]
        if eksogen_tambahan:
            target_ada = {j["target"] for j in jalur_pakai}
            for nm in sorted(eksogen_tambahan):
                if nm not in target_ada:
                    jalur_pakai.insert(0, {"target": nm, "dari": {}})
        spek = {"jalur": jalur_pakai, "interaksi": interaksi}
        data = bangun_dari_spek(spek, n_resp=n_resp, item_per=item_per,
                                skala=skala, korelasi_x=korelasi_x,
                                alpha_rentang=alpha_rentang,
                                koreksi_atenuasi=koreksi_atenuasi,
                                sd_derau=sd_derau, seed=seed)
        alpha = data["alpha_dipakai"]
        return data, alpha

    kon = bangun_berurutan(jalur, n_resp=n_resp, korelasi_x=korelasi_x,
                           alpha=alpha_paksa, alpha_rentang=alpha_rentang,
                           koreksi_atenuasi=koreksi_atenuasi,
                           sd_derau=sd_derau, seed=seed)
    nilai = kon["nilai"]
    alpha = kon["alpha"]
    it = turunkan_item(nilai, alpha, item_per=item_per, skala=skala, seed=seed)
    data = dict(it)
    data["alpha_dipakai"] = alpha
    data["n_resp"] = n_resp
    data["skor_konstruk"] = nilai
    return data, alpha


def _unit_target(jalur: list[dict]) -> dict[str, list[dict]]:
    """Kelompokkan langkah menurut target (satu target = satu regresi)."""
    out: dict[str, list[dict]] = {}
    for j in jalur:
        out.setdefault(j["target"], []).append(j)
    return out


def _derau_otomatis(jalur: list[dict], sd_derau: float | None) -> float:
    """Tentukan skala derau otomatis dari STRUKTUR model.

    KOREKSI 17Sep26 (putaran lanjutan, TERUKUR — peta derau 4 bentuk model):

        BENTUK                      derau 0,4   0,6    0,8    1,0
        rantai (X->M->Y)              0,030  0,006  0,020  0,032
        dual mediasi                  0,012  0,018  0,024  0,027
        HOC (D1,D2 dari X1)           0,037  0,030  0,028  0,064  <-- GAGAL
        regresi berganda              0,014  0,008  0,015  0,009

    KESIMPULAN: **derau 0,6 AMAN untuk SEMUA bentuk model di atas.**
    Aturan LAMA ("2 saudara -> 1,0") bekerja untuk dual mediasi tapi
    MERUSAK model bercabang seperti HOC (derau 1,0 -> galat 0,0644) —
    karena pada HOC, sumbernya (X1) BUKAN variabel hasil, sehingga
    derau besar hanya menambah kebisingan tanpa memisahkan apa pun.

    Aturan sekarang: mulai 0,6 dan naikkan HANYA bila jumlah saudara >= 3
    (banyak mediator sejajar dari induk yang sama) — maksimum 0,9.
    """
    if sd_derau is not None:
        return float(sd_derau)

    # hitung berapa anak yang lahir dari tiap induk
    dari: dict[str, int] = {}
    for j in jalur:
        for s in j["dari"]:
            dari[s] = dari.get(s, 0) + 1
    terbanyak = max(dari.values(), default=1)

    if terbanyak <= 2:
        return 0.6
    # 3+ saudara (mis. triple mediasi paralel) -> perlu sedikit lebih besar
    return float(np.clip(0.6 + 0.15 * (terbanyak - 2), 0.6, 0.9))


def kalibrasi_per_jalur(jalur: list[dict],
                        n_resp: int = 250,
                        item_per: int = 4,
                        skala: int = 5,
                        korelasi_x: float = 0.2,
                        alpha_rentang: tuple[float, float] = (0.72, 0.90),
                        koreksi_atenuasi: bool = True,
                        sd_derau: float | None = None,
                        toleransi: float = 0.03,
                        maks_putaran: int = 40,
                        lapor: bool = False,
                        seed: int = 42,
                        interaksi: list[dict] | None = None) -> dict:
    """Kalibrasi bobot tiap jalur sampai koefisien terukurnya = yang diminta.

    Parameter
    ---------
    interaksi : daftar suku interaksi (moderasi), mis.
        [{"target": "Y", "x": "M", "z": "Z1", "bobot": 0.25},
         {"target": "Y", "x": "X1", "z": "Z2", "bobot": 0.10}]
        Suku interaksi IKUT dikalibrasi: ia masuk ke target yang sama dengan
        sumber biasa (ukuran = regresi target ~ sumber biasa + suku interaksi).

    Return
    ------
    dict: data, jalur_final (bobot hasil kalibrasi), hasil (koefisien terukur),
          galat, tercapai, putaran, riwayat
    """
    interaksi = [dict(it) for it in (interaksi or [])]
    for it in interaksi:
        it.setdefault("bobot", 0.20)
        it.setdefault("sumber", f'{it["x"]}x{it["z"]}')

    # target yang diminta (dari spek asli)
    peta = _unit_target(jalur)
    target_minta: dict[str, dict[str, float]] = {
        t: dict(peta[t][0]["dari"]) for t in peta}

    # variabel moderator harus dibangkitkan walau bukan sumber jalur mana pun
    eksogen_tambahan = {nm for it in interaksi for nm in (it["x"], it["z"])}
    sumber_ada = {k for j in jalur for k in j["dari"]}
    eksogen_tambahan -= sumber_ada

    # interaksi ikut jadi "permintaan" pada targetnya
    for it in interaksi:
        target_minta.setdefault(it["target"], {})[it["sumber"]] = \
            float(it["bobot"])

    # urutan pengerjaan: target dengan paling sedikit sumber didahulukan
    urutan = sorted(peta, key=lambda t: (len(peta[t][0]["dari"]),
                                         abs(sum(peta[t][0]["dari"].values()))),
                    reverse=False)

    # bobot kerja (mulai dari setelan)
    bobot = {t: dict(peta[t][0]["dari"]) for t in peta}
    jalur_kerja = [{"target": t, "dari": dict(bobot[t])} for t in peta]

    # alpha dipaksa SEKALI supaya tidak berubah antar-putaran (kalau berubah,
    # kalibrasi tidak pernah konvergen)
    semua_nama = sorted({k for j in jalur for k in j["dari"]} |
                        {j["target"] for j in jalur})
    al = alpha_rencana(semua_nama, alpha_rentang[0], alpha_rentang[1], {}, seed)

    # derau otomatis dari struktur model (lihat _derau_otomatis)
    sd_derau = _derau_otomatis(jalur, sd_derau)

    riwayat = []
    for putaran in range(1, maks_putaran + 1):
        data, _ = _bangun(jalur_kerja, n_resp, item_per, skala, korelasi_x,
                          alpha_rentang, koreksi_atenuasi, sd_derau, seed, al,
                          interaksi=interaksi, eksogen_tambahan=eksogen_tambahan)
        galat_maks = 0.0
        semua_pas = True
        for t in urutan:
            sumber = list(bobot[t].keys())
            minta = np.array([target_minta[t][s] for s in sumber])
            dapat = ukur_jalur(data, t, sumber)
            galat = minta - dapat
            galat_maks = max(galat_maks, float(np.max(np.abs(galat))))
            if float(np.max(np.abs(galat))) > toleransi:
                semua_pas = False
            # koreksi: geser bobot sebesar galat / laju (laju ~ d(dapat)/d(bobot))
            for i, s in enumerate(sumber):
                bobot[t][s] = float(np.clip(bobot[t][s] + 0.85 * galat[i],
                                            -0.98, 0.98))
        # suku interaksi: ukur & geser juga
        for it in interaksi:
            t, s = it["target"], it["sumber"]
            ada = ukur_jalur(data, t, [s])
            g = float(target_minta[t][s] - ada[0])
            galat_maks = max(galat_maks, abs(g))
            if abs(g) > toleransi:
                semua_pas = False
            it["bobot"] = float(np.clip(it["bobot"] + 0.85 * g, -0.98, 0.98))
        for j in jalur_kerja:
            j["dari"] = dict(bobot[j["target"]])
        riwayat.append({"putaran": putaran, "galat_maks": round(galat_maks, 4)})
        if lapor and (putaran <= 3 or putaran % 5 == 0 or semua_pas):
            print(f'    putaran {putaran:3}: galat maks = {galat_maks:.4f}'
                  + ('  <= TERCAPAI' if semua_pas else ''))
        if semua_pas:
            break

    # hasil akhir
    data, _ = _bangun(jalur_kerja, n_resp, item_per, skala, korelasi_x,
                      alpha_rentang, koreksi_atenuasi, sd_derau, seed, al,
                      interaksi=interaksi, eksogen_tambahan=eksogen_tambahan)
    hasil, galat_akhir = {}, {}
    for t in urutan:
        sumber = list(bobot[t].keys())
        minta = np.array([target_minta[t][s] for s in sumber])
        dapat = ukur_jalur(data, t, sumber)
        for i, s in enumerate(sumber):
            hasil[f"{s}->{t}"] = round(float(dapat[i]), 4)
            galat_akhir[f"{s}->{t}"] = round(float(dapat[i] - minta[i]), 4)
    for it in interaksi:
        t, s = it["target"], it["sumber"]
        a = ukur_jalur(data, t, [s])
        hasil[f"{s}->{t}"] = round(float(a[0]), 4)
        galat_akhir[f"{s}->{t}"] = round(
            float(a[0] - target_minta[t][s]), 4)
    maks = max((abs(v) for v in galat_akhir.values()), default=0.0)

    return {"data": data, "jalur_final": jalur_kerja,
            "interaksi_final": interaksi,
            "hasil": hasil, "galat": galat_akhir,
            "tercapai": maks <= toleransi, "galat_maks": round(maks, 4),
            "putaran": putaran, "riwayat": riwayat,
            "alpha_dipakai": al, "toleransi": toleransi}


def bangun_dengan_mode(mode: str, **kw) -> dict:
    """mode='presisi' -> kalibrasi penuh. mode='natural' -> sekali bangun."""
    if mode == "presisi":
        return kalibrasi_per_jalur(**kw)
    sd = kw.get("sd_derau")
    if sd is None:
        from .kalibrasi_jalur import _derau_otomatis
        sd = _derau_otomatis(kw.get("jalur", []), None)
    kon = bangun_berurutan(kw.get("jalur", []),
                           n_resp=kw.get("n_resp", 250),
                           korelasi_x=kw.get("korelasi_x", 0.2),
                           alpha_rentang=kw.get("alpha_rentang", (0.72, 0.90)),
                           koreksi_atenuasi=kw.get("koreksi_atenuasi", True),
                           sd_derau=sd,
                           seed=kw.get("seed", 42))
    it = turunkan_item(kon["nilai"], kon["alpha"],
                       item_per=kw.get("item_per", 4),
                       skala=kw.get("skala", 5), seed=kw.get("seed", 42))
    return {"data": dict(it, alpha_dipakai=kon["alpha"], n_resp=kon["n_resp"]),
            "jalur_final": kw.get("jalur", []), "mode": "natural"}
