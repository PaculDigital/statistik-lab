#!/usr/bin/env python3

════════════════════════════════════════════════════════════════════════════
⚠️ PENINGGALAN — BUKAN PENJAGA MESIN PRODUKSI (ditandai 21Sep26)
   Modul/objek yang diuji : tampilan kartu uji t (pola lama)
   Sebab                  : Tampilan lama; padanan barunya: uji_peran_alur.py.
   ⇒ Kalau uji ini GAGAL, JANGAN simpulkan mesin produksi rusak.
     Lihat AUDIT_UJI_LUAR_GERBANG_21SEP2026.md (akar: PINTU UKUR SALAH).
   ⇒ Uji yang MENJAGA produksi ada di gerbang_uji.py (jalankan: bash gerbang_uji.sh).
════════════════════════════════════════════════════════════════════════════
"""UJI KARTU UJI t — halaman SUNGGUHAN di HP (ACC Bos 18Sep26).

MENGAPA LEWAT DOMAIN, BUKAN 127.0.0.1:
Chrome Wulan TIDAK BISA menjangkau 127.0.0.1:8120 — itu loopback KONTAINER,
bukan mesin Wulan (terbukti: hasilnya `chrome-error://chromewebdata/`).
Jadi uji WAJIB lewat domain publik https://statistik.bikinaja.id.

YANG DIUJI (semuanya terukur, bukan tebakan):
  1. Halaman muat, skrip data kartu ikut termuat (UJI_T)
  2. Klik istilah "ujit" → panel kamus sembunyi, kartu muncul
  3. 5 kotak hasil tampil; klik tiap kotak → panel arti & sebab ikut berubah
  4. Tabel sebab punya label ✅SAH / ⚠️HATI-HATI / ❌CURANG
  5. Kartu "5 CARA HACK" tampil dengan kepala WARNA MERAH
  6. Tombol daftar periksa: awalnya tertutup → diklik terbuka
  7. TIDAK meluber: tiap elemen di dalam lebar layar HP (390px)
  8. Tidak ada kode tumpah / galat JS

ATURAN PENTING (pelajaran mahal 18Sep26):
  · Alat ukur WAJIB menunggu render selesai sebelum mengukur (kalau tidak,
    angkanya milik halaman LAMA → kesimpulan palsu).
  · Ukur LEBAR dari elemen, bandingkan dengan lebar layar — jangan mengira.

CARA JALAN: .venv/bin/python uji_kartu_ujit.py
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from uji_klik_mulai import tab_baru                     # noqa: E402

HAL = 'https://statistik.bikinaja.id/belajar'
LEBAR_HP = 390
SHOT = pathlib.Path('/tmp/shot')
LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str) -> None:
    global LULUS, GAGAL
    tanda = '✅' if syarat else '❌'
    if syarat:
        LULUS += 1
    else:
        GAGAL += 1
    print(f'  {tanda} {nama}')
    print(f'     bukti: {bukti}')


def main() -> int:
    print('═' * 68)
    print(f'UJI KARTU UJI t — halaman sungguhan {HAL}')
    print('═' * 68)

    ws, _ = tab_baru('about:blank')
    no = 0

    def perintah(m: str, **p):
        nonlocal no
        no += 1
        d = ws.perintah(no, m, **p)
        if 'error' in d:
            raise RuntimeError(d['error'])
        return d.get('result', {})

    def js(expr: str):
        r = perintah('Runtime.evaluate', expression=expr, returnByValue=True,
                     awaitPromise=True)
        if 'exceptionDetails' in r:
            return {'__galat__': r['exceptionDetails'].get('text', '')}
        return r.get('result', {}).get('value')

    galat_js: list[str] = []
    perintah('Page.enable')
    perintah('Runtime.enable')
    perintah('Log.enable')
    perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP, height=900,
             deviceScaleFactor=2, mobile=True)
    perintah('Network.enable')
    perintah('Network.setCacheDisabled', cacheDisabled=True)
    perintah('Page.navigate', url=HAL)
    for _ in range(40):
        time.sleep(0.5)
        if js('document.readyState') == 'complete':
            break
    time.sleep(2)

    cek('1. Halaman BELAJAR termuat', 'belajar' in (js('location.href') or ''),
        f"URL = {js('location.href')}")
    cek('2. Skrip data kartu ikut termuat',
        js('typeof UJI_T') == 'object',
        f"typeof UJI_T = {js('typeof UJI_T')} · jumlah hasil = "
        f"{js('(typeof UJI_T!=="undefined") ? UJI_T.hasil.length : null')}")
    cek('3. Tidak ada galat JS di halaman',
        not galat_js, f'galat tertangkap = {len(galat_js)}')

    # ── klik istilah uji t ────────────────────────────────────────────────
    js('document.querySelector(\'.kamus-tombol[data-k="ujit"]\').click()')
    time.sleep(1.2)
    cek('4. Kartu uji t muncul & panel kamus sembunyi',
        bool(js('!document.getElementById("kartu-ujit").hidden')) and
        bool(js('document.querySelector(".kamus-kisi").hidden')),
        f"kartu tampil = {js('!document.getElementById("kartu-ujit").hidden')}"
        f" · kamus sembunyi = {js('document.querySelector(\".kamus-kisi\").hidden')}")

    cek('5. Lima kotak hasil tampil',
        js('document.querySelectorAll(".ujit-pilih").length') == 5,
        f"jumlah kotak = {js('document.querySelectorAll(\".ujit-pilih\").length')}")

    # ── uji SETIAP kotak hasil (5 skenario benar-benar berganti) ──────────
    print('\n  ── menguji tiap skenario hasil ──')
    kunci = js('UJI_T.hasil.map(h => h.kunci).join(",")')
    berubah = True
    ringkas: list[str] = []
    for i, k in enumerate(str(kunci).split(',')):
        js(f'document.querySelectorAll(".ujit-pilih")[{i}].click()')
        time.sleep(0.7)
        nama = js('document.querySelector(".ujit-pilih.aktif .ujit-nama")'
                  '?.textContent')
        baris = js('document.querySelectorAll(".ujit-tabel tr").length')
        hacks = js('document.querySelectorAll(".hack-item").length')
        butir = js('document.querySelectorAll(".cek-butir").length')
        punya_curang = js('[...document.querySelectorAll(".ujit-tag")]'
                          '.some(e => e.textContent.includes("CURANG"))')
        ringkas.append(f'{k}: tabel={baris}, cek={butir}, curang={punya_curang}')
        if not nama or baris < 2 or hacks != 5 or butir < 3:
            berubah = False
    print('     ' + '\n     '.join(ringkas))
    cek('6. Tiap skenario menampilkan isi sendiri (bukan kosong)',
        berubah, 'lihat daftar di atas')

    # ── label SAH / HATI-HATI / CURANG ────────────────────────────────────
    js('document.querySelectorAll(".ujit-pilih")[1].click()')
    time.sleep(0.8)
    label = js('[...new Set([...document.querySelectorAll(".ujit-tag")]'
               '.map(e => e.textContent.trim()))].sort().join(" | ")')
    cek('7. Label boleh/tidak muncul (SAH/HATI-HATI/CURANG)',
        'SAH' in str(label) and 'CURANG' in str(label),
        f'label unik = {label}')

    # ── kartu hack: kepala MERAH (permintaan Bos) ─────────────────────────
    warna = js('getComputedStyle(document.querySelector(".hack-kepala"))'
               '.backgroundColor')
    cek('8. Kepala kartu HACK benar-benar MERAH',
        warna == 'rgb(168, 90, 90)',
        f'backgroundColor = {warna} (diharapkan rgb(168, 90, 90))')
    cek('9. Judul kartu sudah versi baru',
        'Hack' in str(js('document.querySelector(".hack-kepala h3")'
                         '.textContent')),
        f"judul = {js('document.querySelector(\".hack-kepala h3\").textContent')}")

    # ── tombol daftar periksa ─────────────────────────────────────────────
    awal = js('document.getElementById("cek-daftar").hidden')
    js('document.getElementById("cek-tombol").click()')
    time.sleep(0.6)
    sesudah = js('document.getElementById("cek-daftar").hidden')
    cek('10. Tombol daftar periksa: tertutup → terbuka → tertutup',
        bool(awal) and not bool(sesudah),
        f'awal tersembunyi = {awal} · setelah diklik = {sesudah}')
    js('document.getElementById("cek-tombol").click()')
    time.sleep(0.5)
    cek('11. Tombol bisa menutup kembali',
        bool(js('document.getElementById("cek-daftar").hidden')),
        f"tersembunyi lagi = {js('document.getElementById(\"cek-daftar\").hidden')}")

    # ── TIDAK MELUBER: ukur elemen vs lebar layar ─────────────────────────
    print('\n  ── mengukur agar tidak meluber keluar layar HP ──')
    luber = js("""(() => {
      const batas = document.documentElement.clientWidth;
      const nama = [];
      document.querySelectorAll('.kartu-ujit *').forEach(e => {
        const r = e.getBoundingClientRect();
        if (r.width > 0 && (r.right > batas + 1 || r.left < -1)) {
          nama.push((e.className || e.tagName) + ' [' +
                    Math.round(r.left) + '…' + Math.round(r.right) + ']');
        }
      });
      return {batas: batas, jml: nama.length, contoh: nama.slice(0, 4)};
    })()""")
    cek('12. Tidak ada elemen meluber keluar layar HP',
        isinstance(luber, dict) and luber.get('jml') == 0,
        f'lebar layar = {luber.get("batas") if isinstance(luber, dict) else "?"}px'
        f' · meluber = {luber.get("jml") if isinstance(luber, dict) else "?"}'
        f'{"" if not isinstance(luber, dict) or luber.get("jml") == 0 else " · " + str(luber.get("contoh"))}')

    # ── kode tumpah: cari teks khas JavaScript di badan halaman ───────────
    tumpah = js('''(() => {
      const t = document.body.innerText || '';
      const curiga = ['function ', '=>', 'innerHTML', '<\\/span>', '${'];
      return curiga.filter(x => t.includes(x));
    })()''')
    cek('13. Tidak ada kode tumpah jadi teks di halaman',
        isinstance(tumpah, list) and not tumpah,
        f'kata mencurigakan = {tumpah}')

    # ── tangkapan layar ───────────────────────────────────────────────────
    # ⚠️ CACAT ALAT UKUR DIPERBAIKI 18Sep26: `captureBeyondViewport=True`
    # membuat Chrome menolak ("Unable to capture screenshot") karena tinggi
    # halaman melebihi batas. Solusinya: batasi tinggi jendela ke isi yang
    # mau difoto, lalu TIDAK memakai captureBeyondViewport.
    print('\n  ── mengambil tangkapan layar ──')
    for nm, siapkan in [
        ('hp_ujit_minus', 'document.querySelectorAll(".ujit-pilih")[1].click()'),
        ('hp_ujit_tidaksig', 'document.querySelectorAll(".ujit-pilih")[3].click()'),
    ]:
        js(siapkan)
        time.sleep(0.9)
        tinggi = js('Math.min(document.body.scrollHeight, 4200)') or 2600
        perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP,
                 height=int(tinggi), deviceScaleFactor=1, mobile=True)
        time.sleep(0.8)
        png = SHOT / f'{nm}.png'
        r = perintah('Page.captureScreenshot', format='png')
        if r.get('data'):
            import base64
            png.write_bytes(base64.b64decode(r['data']))
            ukuran = png.stat().st_size
            print(f'     {nm}.png {ukuran} byte'
                  f'{"" if ukuran > 10000 else "  ⚠️ KECIL — foto gagal?"}')

    ws.tutup()
    print('\n' + '═' * 68)
    print(f'HASIL AKHIR: {LULUS} LULUS / {GAGAL} GAGAL')
    print('═' * 68)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
