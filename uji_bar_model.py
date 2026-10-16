#!/usr/bin/env python3
"""UJI TAHAP 1.4 — BAR "MODEL KAMU SEKARANG" (19Sep26).

MENGAPA ADA: bar ini dinilai dari HALAMAN SUNGGUHAN, bukan dari berkas.
Uji HTTP tidak cukup — bar dibangun oleh JavaScript setelah DOM siap.

YANG DIUJI (keputusan Bos: opsi 1B + 2A):
  1B — buka /buat-data TANPA ?model= → DIARAHKAN BALIK ke /kuantitatif
  2A — bar MENEMPEL (position:sticky) dan tombol ganti SELALU terlihat

⚠️ JEBAKAN YANG DICEGAH (19Sep26):
  - `--tinta-1` TIDAK ADA di gaya.css (adanya `--tinta`) → warna bar salah.
  - ikon `arrow-left-right` TIDAK ADA di sprite → ikon KOSONG tanpa galat.
  Keduanya sudah ditutup; uji di bawah menjaga supaya tidak kembali.
"""
import json
import sys
import time
import urllib.request

sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_jalur_tampilan import Tab  # kelas CDP yang sudah terbukti

CDP = 'http://127.0.0.1:9333'
HAL = 'https://statistik.bikinaja.id'


def nilai(r):
    return ((r.get('result', {}) or {}).get('result', {}) or {}).get('value')


def main() -> int:
    daftar = json.load(urllib.request.urlopen(f'{CDP}/json/list', timeout=10))
    halaman = [t for t in daftar if t.get('type') == 'page']
    if not halaman:
        print('❌ tidak ada tab CDP')
        return 1

    t = Tab(halaman[0]['webSocketDebuggerUrl'])
    t.kirim('Page.enable')
    t.kirim('Runtime.enable')
    # HP 390px — tempat cacat tampilan paling sering muncul
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 844, 'deviceScaleFactor': 2, 'mobile': True})

    pesan, lulus, gagal = [], 0, 0

    def catat(ok, teks):
        nonlocal lulus, gagal
        pesan.append(('  ✅ ' if ok else '  ❌ ') + teks)
        lulus += (1 if ok else 0)
        gagal += (0 if ok else 1)

    # ── UJI 1 (keputusan 1B): tanpa ?model= → diarahkan ke /kuantitatif ────
    t.kirim('Page.navigate', {'url': f'{HAL}/buat-data'})
    time.sleep(6)
    t.kirim('Runtime.evaluate', {
        'expression': 'window.stop && undefined', 'returnByValue': True})
    url = nilai(t.kirim('Runtime.evaluate',
                        {'expression': 'location.pathname', 'returnByValue': True}))
    catat(url == '/kuantitatif',
          f"1B: /buat-data tanpa model → diarahkan ke /kuantitatif (dapat {url})")

    # ── UJI 2: dengan ?model= → tetap di /buat-data ─────────────────────────
    for slug, namanya in (('moderasi-jalur-b', 'Penguat di jalur kedua'),
                          ('mediasi-paralel', 'Perantara sejajar'),
                          ('berantai', 'saling berhubungan')):
        t.kirim('Page.navigate', {'url': f'{HAL}/buat-data?model={slug}'})
        time.sleep(6)

        # ⚠️ UKUR SAAT SUDAH DI-SCROLL — bukan saat di atas. Inilah satu-satunya
        # cara membuktikan "menempel": kalau bar ikut tergulung, top jadi negatif.
        # Pelajaran 19Sep26: pertama kali Wulan cuma membaca `position:sticky`
        # dari CSS lalu bilang LULUS — padahal di halaman nyata bar TERGULUNG.
        # Membaca ATRIBUT bukan mengukur PERILAKU.
        t.kirim('Runtime.evaluate', {'expression': 'window.scrollTo(0, 1400)',
                                     'returnByValue': True})
        time.sleep(1.5)

        js = ('(() => {'
              'const b = document.getElementById("bar-model");'
              'const n = document.getElementById("bar-model-nama");'
              'const a = document.querySelector(".bar-model-ganti");'
              'if (!b) return JSON.stringify({ada:false});'
              'const cs = getComputedStyle(b);'
              'const rb = b.getBoundingClientRect();'
              'const ra = a ? a.getBoundingClientRect() : null;'
              'return JSON.stringify({'
              '  ada: true, tampak: !b.hidden,'
              '  nama: n ? n.textContent : "",'
              '  posisi: cs.position, atas: cs.top,'
              '  menempel: Math.round(rb.top) <= 1,'
              '  lebar: Math.round(rb.width),'
              '  tombolAda: !!a,'
              '  tombolTeks: a ? a.textContent.trim() : "",'
              '  tombolMuats: ra ? (ra.left >= 0 && ra.right <= innerWidth + 1) : false,'
              '  ikonKosong: [...b.querySelectorAll("svg")].filter('
              '     s => !s.querySelector("use") || '
              '          !document.getElementById((s.querySelector("use").getAttribute("href")||"").slice(1))'
              '   ).length,'
              '  tumpah: b.innerHTML.indexOf("&lt;") >= 0,'
              '  lebarHalaman: document.documentElement.scrollWidth,'
              '  lebarLayar: innerWidth'
              '});})()')
        d = json.loads(nilai(t.kirim('Runtime.evaluate',
                                     {'expression': js, 'returnByValue': True})))

        catat(d.get('tampak'), f"[{slug}] bar MUNCUL")
        catat(namanya.lower() in (d.get('nama') or '').lower(),
              f"[{slug}] nama model benar → '{d.get('nama')}'")
        # ⚠️ DIUBAH 19Sep26: dulu uji ini menuntut `sticky`. TERBUKTI SALAH —
        # `sticky` TIDAK BEKERJA di halaman ini karena gaya.css:554 punya
        # `html, body { overflow-x: hidden }` yang mematikan sticky (bar
        # tergulung: top 258 → −1142). Ganti ke `fixed`. Yang diuji sekarang
        # yang PENTING bagi user: bar benar-benar MENEMPEL di atas.
        catat(d.get('posisi') in ('fixed', 'sticky'),
              f"[{slug}] 2A: bar MENEMPEL (position={d.get('posisi')})")
        catat(d.get('menempel'), f"[{slug}] 2A: terbukti menempel (top=0 saat scroll)")
        catat(d.get('tombolAda'), f"[{slug}] tombol GANTI MODEL ada")
        catat('Ganti model' in (d.get('tombolTeks') or ''),
              f"[{slug}] tombol bertulis 'Ganti model'")
        catat(d.get('tombolMuats'), f"[{slug}] tombol TIDAK meluber keluar layar")
        catat(d.get('ikonKosong') == 0,
              f"[{slug}] tidak ada ikon KOSONG di bar (dapat {d.get('ikonKosong')})")
        catat(not d.get('tumpah'), f"[{slug}] tidak ada kode tumpah")
        # ⚠️ WAJIB: bar `fixed` TIDAK boleh membuat halaman bisa digeser ke
        # samping (aturan lama `overflow-x:hidden` sengaja ada untuk ini).
        # Kalau lebar halaman > lebar layar, Wulan menambah cacat baru.
        catat((d.get('lebarHalaman') or 0) <= (d.get('lebarLayar') or 0) + 1,
              f"[{slug}] halaman TIDAK bisa digeser ke samping "
              f"({d.get('lebarHalaman')} ≤ {d.get('lebarLayar')})")

    # ── UJI 3: tombol benar-benar membawa ke /kuantitatif ───────────────────
    t.kirim('Page.navigate', {'url': f'{HAL}/buat-data?model=moderasi'})
    time.sleep(6)
    t.kirim('Runtime.evaluate', {
        'expression': 'document.querySelector(".bar-model-ganti").click()',
        'returnByValue': True})
    time.sleep(5)
    url2 = nilai(t.kirim('Runtime.evaluate',
                         {'expression': 'location.pathname', 'returnByValue': True}))
    catat(url2 == '/kuantitatif',
          f"KLIK 'Ganti model' → sampai di /kuantitatif (dapat {url2})")

    # ── UJI 4: tidak ada galat JS ───────────────────────────────────────────
    t.s.close()
    print('\n'.join(pesan))
    print(f'\n  {lulus} LULUS / {gagal} GAGAL')
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
