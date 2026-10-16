#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : tampilan pita tab (pola lama)
   Sebab                  : Memakai elemen tampilan LAMA; bentuk peran sudah menggantikannya. Lihat uji_peran_web.py.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI KLIK PITA TAB di /belajar — pakai ALAT LAMA, bukan tulis baru.

⚠️ ATURAN (teguran Bos 19Sep26): "cek dulu alat yang dipakai kemarin, jangan
   buat-buat script, semua sudah ada." Skrip ini TIDAK menulis ulang kelas
   websocket — ia MENGIMPOR dari `uji_klik_mulai.py` yang sudah terbukti
   (socket mentah, tidak kirim header Origin → tidak kena 403).

YANG DIUJI (tab benar-benar bekerja, bukan cuma ada di HTML):
 1. /belajar memuat, judul baru muncul
 2. Pita tab ADA & berisi 2 tombol
 3. Tab 1 TERBUKA, Tab 2 TERSEMBUNYI (keadaan awal)
 4. KLIK tab 2 → Tab 2 terbuka, Tab 1 tersembunyi (perilaku sungguhan)
 5. KLIK tab 1 lagi → kembali
 6. Isi Ruang Uji: 2 kartu (Rusak Data + Kuis Pilih Alat)
 7. Tidak ada galat JavaScript saat klik
 8. #tab-2 bisa dibuka langsung lewat URL (tombol mundur/berbagi bekerja)

LULUS/GAGAL ditentukan dari EXIT CODE (0 = lulus), JANGAN grep teks.
"""
import importlib.util
import json
import pathlib
import sys
import time
import os
import urllib.request

DIR = pathlib.Path('/opt/data/services/statistik-lab')

# ── impor alat lama dengan cara AMAN (nama berkas ber-underscore aman) ──
spec = importlib.util.spec_from_file_location('ukm', DIR / 'uji_klik_mulai.py')
ukm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ukm)

WS = ukm.WS
tab_baru = ukm.tab_baru
CDP = ukm.CDP

HAL = os.environ.get('STATLAB_HAL', 'http://172.17.0.9:8000/belajar')

lulus = 0
gagal = 0


def cek(nama: str, syarat: bool, info: str = '') -> None:
    global lulus, gagal
    if syarat:
        lulus += 1
        print(f'  ✅ {nama}' + (f'  {info}' if info else ''))
    else:
        gagal += 1
        print(f'  ❌ {nama}' + (f'  {info}' if info else ''))


def utama() -> int:
    print('═' * 66)
    print('UJI KLIK PITA TAB /belajar')
    print('═' * 66)

    try:
        urllib.request.urlopen(f'{CDP}/json/version', timeout=6)
    except Exception:                                   # noqa: BLE001
        print('❌ Chrome debug (9333) tidak jalan.')
        return 1

    ws, tab_id = tab_baru('about:blank')
    no = 0
    galat_js: list = []

    def perintah(mtd: str, **kw):
        nonlocal no
        no += 1
        return ws.perintah(no, mtd, **kw)

    def js(ekspresi: str):
        d = perintah('Runtime.evaluate', expression=ekspresi,
                     returnByValue=True, awaitPromise=True)
        if d.get('result', {}).get('exceptionDetails'):
            return {'__galat__': d['result']['exceptionDetails']}
        return d.get('result', {}).get('result', {}).get('value')

    perintah('Runtime.enable')
    perintah('Page.enable')

    # ── [1] muat halaman ──
    print('\n[1] Halaman memuat')
    perintah('Page.navigate', url=HAL)
    for _ in range(50):
        st = js('document.readyState')
        if st == 'complete':
            break
        time.sleep(0.4)
    time.sleep(1.2)
    judul = js('document.title') or ''
    h1 = js("document.querySelector('h1') ? "
            "document.querySelector('h1').textContent.trim() : ''")
    cek('halaman terbuka', bool(judul), f'judul: {judul}')
    cek('H1 baru muncul', 'ruang uji' in (h1 or '').lower(),
        f'H1: {h1}')

    # ── [2] pita tab ada & 2 tombol ──
    print('\n[2] Pita tab ada')
    n_tab = js("document.querySelectorAll('.pita-tab a').length") or 0
    cek('pita tab ada', n_tab == 2, f'{n_tab} tombol tab')
    label = js("Array.from(document.querySelectorAll('.pita-tab a'))"
               ".map(a=>a.textContent.replace(/\\s+/g,' ').trim()).join(' | ')")
    cek('label tab benar',
        'Materi' in (label or '') and 'Ruang Uji' in (label or ''),
        label or '')

    # ── [3] keadaan awal: tab 1 buka, tab 2 tutup ──
    print('\n[3] Keadaan awal')
    t1 = js("document.getElementById('tab-1') ? "
            "document.getElementById('tab-1').hidden : null")
    t2 = js("document.getElementById('tab-2') ? "
            "document.getElementById('tab-2').hidden : null")
    cek('tab 1 TERBUKA', t1 is False, f'hidden={t1}')
    cek('tab 2 TERSEMBUNYI', t2 is True, f'hidden={t2}')

    # ── [4] KLIK tab 2 (perilaku sungguhan, bukan cek atribut) ──
    print('\n[4] KLIK tab 2 sungguhan')
    perintah('Runtime.evaluate',
             expression="document.getElementById('pa-2').click()")
    time.sleep(0.6)
    t1b = js("document.getElementById('tab-1').hidden")
    t2b = js("document.getElementById('tab-2').hidden")
    cek('tab 2 TERBUKA setelah klik', t2b is False, f'hidden={t2b}')
    cek('tab 1 tersembunyi setelah klik', t1b is True, f'hidden={t1b}')
    aktif = js("document.querySelector('.pita-tab a.aktif').id")
    cek('penanda aktif pindah ke tab 2', aktif == 'pa-2', f'aktif: {aktif}')

    # ── [5] isi Ruang Uji ──
    # ⚠️ DIUBAH 19Sep26 mengikuti DOKUMENTASI_KEPUTUSAN Bagian F:
    # Ruang Uji (Rusak Data + Kuis) = TAHAP 3, BELUM dikerjakan. Kartunya
    # DILEPAS supaya user tidak melihat janji kosong / tautan palsu (teguran
    # Bos 19Sep26: "kok rusak data belum ada tapi ke diagnosa data?").
    # Yang wajib ada sekarang: pemberitahuan jujur + pintu ke yang SUDAH jalan.
    print('\n[5] Isi Ruang Uji')
    teks2 = js("document.getElementById('tab-2').textContent"
               ".replace(/\\s+/g,' ')") or ''
    n_kartu = js("document.querySelectorAll('#tab-2 .kartu-alat').length") or 0
    n_pintu = js("document.querySelectorAll('#tab-2 a.pilih').length") or 0
    cek('TIDAK ada kartu janji kosong', n_kartu == 0, f'{n_kartu} kartu')
    cek('ada pemberitahuan "belum dibuka"', 'belum dibuka' in teks2)
    cek('tidak menyebut fitur yang belum jadi', 'Rusak Data' not in teks2)
    cek('ada 3 pintu ke yang sudah jalan', n_pintu == 3, f'{n_pintu} pintu')
    # ⚠️ AKAR (19Sep26, terukur): href BUKAN bagian textContent — memeriksa
    # `'/syarat' in teks` selalu GAGAL walau tautannya benar. WAJIB baca
    # atribut href-nya. Terbukti: hrefs = ["/belajar","/syarat","/klinik"].
    hrefs = js("JSON.stringify(Array.from(document.querySelectorAll"
               "('#tab-2 a.pilih')).map(a=>a.getAttribute('href')))") or '[]'
    cek('pintu Kamus istilah hidup', '"/belajar"' in hrefs, hrefs)
    cek('pintu Kamus Grafik hidup', '"/syarat"' in hrefs)
    cek('pintu Diagnosis Data hidup', '"/klinik"' in hrefs)

    # ── [6] klik balik ke tab 1 ──
    print('\n[6] Klik balik ke tab 1')
    perintah('Runtime.evaluate',
             expression="document.getElementById('pa-1').click()")
    time.sleep(0.6)
    t1c = js("document.getElementById('tab-1').hidden")
    t2c = js("document.getElementById('tab-2').hidden")
    cek('tab 1 kembali terbuka', t1c is False, f'hidden={t1c}')
    cek('tab 2 kembali tersembunyi', t2c is True, f'hidden={t2c}')

    # ── [7] galat JS ──
    print('\n[7] Galat JavaScript')
    g = js("window.__GALAT_JS ? window.__GALAT_JS.length : 0")
    cek('tidak ada galat JS', (g or 0) == 0, f'{g} galat')

    # ── [8] #tab-2 lewat URL ──
    print('\n[8] Buka #tab-2 langsung lewat URL')
    # ⚠️ AKAR (19Sep26, terukur): kalau tab SUDAH berada di URL yang sama dan
    # hanya hash-nya berbeda, browser TIDAK memuat ulang halaman → skrip
    # pembaca hash tidak jalan → tab 2 tetap tertutup → uji SALAH UKUR.
    # Terbukti: tab baru (about:blank → #tab-2) BERHASIL; tab yang sudah di
    # /belajar → #tab-2 GAGAL tanpa memuat ulang.
    # JALAN BENAR: paksa muat ulang beneran — navigate ke about:blank dulu.
    perintah('Page.navigate', url='about:blank')
    time.sleep(0.6)
    perintah('Page.navigate', url=HAL + '#tab-2')
    for _ in range(40):
        if js('document.readyState') == 'complete':
            break
        time.sleep(0.35)
    time.sleep(1.2)
    t2d = js("document.getElementById('tab-2') ? "
             "document.getElementById('tab-2').hidden : null")
    cek('#tab-2 langsung terbuka', t2d is False, f'hidden={t2d}')
    cek('#tab-2 hash terbaca benar', (js('location.hash') or '') == '#tab-2',
        f"hash={js('location.hash')}")
    cek('tab 1 ikut tertutup', js("document.getElementById('tab-1').hidden") is True)

    # ── bersihkan tab ──
    try:
        urllib.request.urlopen(
            urllib.request.Request(f'{CDP}/json/close/{tab_id}'), timeout=6)
    except Exception:                                   # noqa: BLE001
        pass

    print('\n' + '═' * 66)
    print(f'  HASIL: {lulus} LULUS / {gagal} GAGAL')
    print('═' * 66)
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(utama())
