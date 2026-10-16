#!/usr/bin/env python3
"""Sisipkan API diagnosis ke app/main.py — dengan PEMERIKSAAN (jangan patch buta).

⚠️ PELAJARAN 19Sep26: Wulan 3× merusak app/main.py dengan `patch` karena
   mencari teks yang TIDAK unik (akhirannya "async def ..." ikut terpotong).
   ATURAN: untuk menyisipkan blok besar, pakai PENANDA + VERIFIKASI:
     ① baca berkas
     ② pastikan penanda ADA dan HANYA SEKALI
     ③ sisipkan
     ④ parse ulang (ast.parse) — WAJIB
     ⑤ kalau parse gagal → TULIS ULANG berkas asli, jangan simpan
"""
import ast
import shutil
import sys
from pathlib import Path

BERKAS = Path('/opt/data/services/statistik-lab/app/main.py')
CADANGAN = Path('/tmp/main.py.bak')

KODE = '''

# ── DIAGNOSIS DATA: unggah → periksa → cara membetulkan (ACC Bos 19Sep26) ──
# Inilah ALAT yang Bos minta: user mengunggah data dari SPSS/SmartPLS,
# alat memeriksa syaratnya, bilang BENAR kalau benar dan SALAH kalau salah,
# lalu memberi panduan cara membetulkan.
#
# Pagar yang dipasang di sini:
#   · Ukuran maksimal 10 MB — DIPERIKSA DI SERVER, bukan cuma di JS
#     (pelajaran EduAi 15Sep26: batas yang hanya ada di JS bisa dilewati).
#   · Format diperiksa dari ISI berkas, bukan dari namanya saja.
#   · Pesan galat SELALU ramah (GagalBaca), tidak pernah traceback.
@app.post('/api/diagnosis/unggah')
async def api_diagnosis_unggah(berkas: UploadFile = File(...)):
    """Terima berkas → kembalikan daftar kolom + pratinjau.

    HANYA membaca. Perhitungan dijalankan di /api/diagnosis/periksa supaya
    user bisa MENUNJUK KOLOM dulu (keputusan Bos 2A), bukan ditebak mesin.
    """
    from fastapi import HTTPException
    from app.diagnosis import baca_berkas, GagalBaca, MAX_BYTE

    isi = await berkas.read()
    if len(isi) > MAX_BYTE:
        raise HTTPException(status_code=413, detail=(
            f'Berkasnya {len(isi)/1_048_576:.1f} MB — melebihi batas '
            f'{MAX_BYTE/1_048_576:.0f} MB. Coba simpan sebagian data dulu ya.'))
    try:
        df, ket = baca_berkas(berkas.filename or 'data.csv', isi)
    except GagalBaca as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Simpan sementara supaya tidak perlu unggah dua kali. Kunci dari nama
    # berkas + ukuran — cukup untuk satu sesi pemakaian, tanpa basis data.
    from app.diagnosis import simpan_sementara
    kunci = simpan_sementara(df)

    kolom = [{'nama': str(c), 'kosong': int(df[c].isna().sum()),
              'jenis': ('angka' if pd.api.types.is_numeric_dtype(df[c])
                        else 'teks')} for c in df.columns]
    return JSONResponse({
        'kunci': kunci,
        'nama_berkas': berkas.filename,
        'n_baris': int(len(df)),
        'n_kolom': int(len(df.columns)),
        'kolom': kolom,
        'keterangan': ket,
        'pratinjau': df.head(5).astype(str).values.tolist(),
    })


@app.post('/api/diagnosis/periksa')
async def api_diagnosis_periksa(payload: dict):
    """Hitung syarat dari data yang sudah diunggah.

    payload:
      kunci     : kunci dari /unggah
      mode      : 'spss' | 'pls'
      kolom_x   : [nama kolom X…]     (SPSS)
      kolom_y   : nama kolom Y        (SPSS)
      kolom_m   : [nama kolom M…]     (SPSS, opsional)
      konstruk  : {nama: [butir…]}    (PLS)
      kolom_target : nama konstruk endogen (PLS)
      missing   : 'buang' | 'rata'    cara menangani sel kosong
    """
    from fastapi import HTTPException
    from app.diagnosis import ambil_sementara, periksa_spss, periksa_pls, GagalBaca
    from app import nasihat

    df = ambil_sementara(payload.get('kunci', ''))
    if df is None:
        raise HTTPException(status_code=400, detail=(
            'Datanya sudah tidak ada di server (mungkin sesi terlalu lama). '
            'Coba unggah ulang ya — sekali klik saja.'))

    mode = str(payload.get('mode', 'spss'))
    missing = str(payload.get('missing', 'buang'))
    try:
        if mode == 'pls':
            r = periksa_pls(df, payload.get('konstruk') or {},
                            str(payload.get('kolom_target') or ''), missing=missing)
        else:
            r = periksa_spss(df, payload.get('kolom_x') or [],
                             str(payload.get('kolom_y') or ''),
                             kolom_m=payload.get('kolom_m') or [],
                             missing=missing)
    except GagalBaca as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Tempelkan nasihat "cara membetulkan" untuk tiap masalah yang muncul.
    # WAJIB dari server: kalau ditaruh di JS, teksnya harus dijaga di dua
    # tempat (pelajaran EduAi 15Sep26 — batas/teks yang ditulis dua kali
    # membuat yang satu tak pernah tersentuh).
    kode_masalah = []
    if mode == 'pls':
        for h in r.get('konstruk', []):
            if not h.get('lulus_cl', True):   kode_masalah.append('outer_loading')
            if not h.get('lulus_ave', True):  kode_masalah.append('ave')
            if not h.get('lulus_cr', True):   kode_masalah.append('cr')
        if r.get('vif_inner_maks') and r['vif_inner_maks'] > 5:
            kode_masalah.append('vif_inner')
        if r.get('fornell_ada_masalah'):
            kode_masalah.append('fornell')
    else:
        if r.get('normalitas', {}).get('lulus') is False:  kode_masalah.append('normalitas')
        if r.get('hetero', {}).get('lulus') is False:      kode_masalah.append('hetero')
        if r.get('vif_maks') and r['vif_maks'] > 10:       kode_masalah.append('vif')
        if r.get('linearitas', {}).get('lulus') is False:  kode_masalah.append('linearitas')
        if r.get('outlier', {}).get('n_y', 0) >= 3:        kode_masalah.append('outlier')
        if r.get('dw') is not None and not (1.5 <= r['dw'] <= 2.5):
            kode_masalah.append('dw')
    r['masalah'] = [{'kode': k, 'nasihat': nasihat.ambil(k, mode)}
                    for k in dict.fromkeys(kode_masalah)]
    r['nasihat_semua'] = {k: nasihat.ambil(k, mode)
                          for k in nasihat.daftar_kode(mode)}
    return JSONResponse(r)


@app.get('/api/unduh')
'''


def utama() -> int:
    asli = BERKAS.read_text()
    CADANGAN.write_text(asli)
    print(f'cadangan ditulis ke {CADANGAN} ({len(asli)} byte)')

    penanda = "@app.get('/api/unduh')"
    n = asli.count(penanda)
    print(f'penanda "{penanda}" ditemukan {n}×')
    if n != 1:
        print('GAGAL: penanda tidak unik — batal.')
        return 1

    baru = asli.replace(penanda, KODE.lstrip('\n'), 1)

    # ⚠️ WAJIB: parse ulang. Kalau gagal, JANGAN simpan.
    try:
        ast.parse(baru)
    except SyntaxError as e:
        print(f'GAGAL parse: {e} — berkas TIDAK disimpan.')
        return 1

    BERKAS.write_text(baru)
    print(f'berhasil disisipkan. {len(asli)} → {len(baru)} byte '
          f'(+{len(baru)-len(asli)})')

    # Verifikasi kedua: baca ulang dari disk.
    ulang = ast.parse(BERKAS.read_text())
    nama = [n.name for n in ulang.body if isinstance(n, (ast.FunctionDef,
                                                         ast.AsyncFunctionDef))]
    for perlu in ('api_diagnosis_unggah', 'api_diagnosis_periksa', 'api_unduh'):
        assert perlu in nama, f'{perlu} TIDAK ADA setelah disisipkan!'
    print('verifikasi: api_diagnosis_unggah ✓  api_diagnosis_periksa ✓  api_unduh ✓')
    return 0


if __name__ == '__main__':
    sys.exit(utama())
