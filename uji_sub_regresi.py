#!/usr/bin/env python3
"""UJI SUB-PILIHAN REGRESI di halaman /kuantitatif (TAHAP 1.3, 19Sep26).

MENGAPA ADA: uji HTTP hanya membuktikan kode TERKIRIM. Ia tidak membuktikan
klik kartu induk benar-benar MEMUNCULKAN sub-pilihan, dan tidak membuktikan
tidak ada galat JS. Ini menjalankan Chrome nyata (CDP 9333, HP 390px) + baca DOM.

Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations
import json, sys, time, urllib.request
sys.path.insert(0, '.')
from uji_jalur_tampilan import Tab  # pakai ULANG kelas yang sudah terbukti

CDP = 'http://127.0.0.1:9333'
URL = 'https://statistik.bikinaja.id/kuantitatif'

lulus = 0; gagal = 0; pesan: list[str] = []

def catat(ok: bool, teks: str) -> None:
    global lulus, gagal
    if ok:
        lulus += 1; pesan.append(f'  ✅ {teks}')
    else:
        gagal += 1; pesan.append(f'  ❌ {teks}')

def nilai(r: dict):
    return (r.get('result', {}).get('result', {}) or {}).get('value')

def main() -> int:
    # ⚠️ AKAR DITUTUP 21Sep26: uji ini dulu memakai `hal[0]` — tab MILIK UJI
    #    LAIN — dan GAGAL (`❌ tidak ada tab`) begitu tab itu tidak ada.
    #    Gerbang jadi bergantung pada urutan/keberadaan tab pihak lain.
    #    FIX: SIAPKAN TAB SENDIRI (pola sama dengan uji_tombol_contoh.py),
    #    lalu tutup lagi di akhir — jangan tinggalkan tab yatim.
    tab_id = None
    # Prasarana: Chrome mati = LEWAT (77), bukan GAGAL — mesin tidak salah.
    from prasarana_uji import pastikan_chrome, KODE_LEWAT
    kode_prasarana = pastikan_chrome(9333)
    if kode_prasarana is not None:
        return kode_prasarana
    try:
        with urllib.request.urlopen(f'{CDP}/json/list', timeout=10) as r:
            daftar = json.load(r)
    except Exception as e:
        print(f'  ❌ CDP tak terjangkau: {e}'); return 1

    hal = [t for t in daftar if t.get('type') == 'page']
    if hal and len(hal) >= 8:
        # banyak tab nyangkut = lingkungan tidak sehat; jangan menebak tab
        print(f'  ❌ terlalu banyak tab nyangkut ({len(hal)}) — bersihkan dulu')
        return 1

    try:
        with urllib.request.urlopen(urllib.request.Request(
                f'{CDP}/json/new?about:blank', method='PUT'), timeout=20) as r:
            baru = json.load(r)
        tab_id = baru['id']
        t = Tab(baru['webSocketDebuggerUrl'])
    except Exception as e:
        print(f'  ❌ gagal menyiapkan tab sendiri: {e}'); return 1
    t.kirim('Page.enable')
    t.kirim('Runtime.enable')
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 844, 'deviceScaleFactor': 2, 'mobile': True})
    t.kirim('Page.navigate', {'url': URL})
    time.sleep(6)

    # ── 1. SEBELUM klik: 4 kartu induk terlihat, sub-pilihan TERSEMBUNYI ──
    # ⚠️ KOREKSI UJI 19Sep26: kartu INDUK yang aktif ada 4, TAPI di DOM juga
    # ada kartu ke-5 "Susun sendiri (expert)" yang SENGAJA TERKUNCI
    # (keputusan Bos: dibahas belakangan). Jadi hitung yang BUKAN .kartu-kunci
    # — kalau menghitung semua, uji menyalahkan aplikasi padahal aplikasinya benar.
    js1 = ('(() => {'
           'const grid = document.querySelector(".grid-model-kartu");'
           'const semua = [...document.querySelectorAll(".grid-model-kartu .kartu-pilih")];'
           'const kartu = semua.filter(k => !k.classList.contains("kartu-kunci"));'
           'const sub = document.getElementById("sub-regresi");'
           'const judul = kartu.map(k => (k.querySelector(".kartu-judul")||{}).textContent||"");'
           'const teknis = kartu.map(k => (k.querySelector(".kartu-teknis")||{}).textContent||"");'
           'return JSON.stringify({'
           '  jml: kartu.length, jmlSemua: semua.length, judul, teknis,'
           '  gridTampak: grid ? !grid.hidden : null,'
           '  subAda: !!sub, subTersembunyi: sub ? sub.hidden : null,'
           '  jmlSub: sub ? sub.querySelectorAll(".kartu-pilih").length : 0'
           '});})()')
    d = json.loads(nilai(t.kirim('Runtime.evaluate', {'expression': js1, 'returnByValue': True})))

    catat(d['jml'] == 4, f"4 kartu INDUK aktif (dapat {d['jml']}, total DOM {d.get('jmlSemua')})")
    catat('Regresi' in d['judul'], f"kartu 'Regresi' ada → {d['judul']}")
    catat(d['subAda'], 'panel #sub-regresi ADA di halaman')
    catat(d['subTersembunyi'] is True, f"sub-pilihan TERSEMBUNYI dulu (hidden={d['subTersembunyi']})")
    catat(d['jmlSub'] == 2, f"sub-pilihan berisi 2 kartu (dapat {d['jmlSub']})")
    catat(d['gridTampak'] is True, 'grid induk TERLIHAT di awal')

    # ── 2. KLIK kartu induk Regresi ──
    t.kirim('Runtime.evaluate', {
        'expression': 'document.querySelector(\'[data-induk="regresi"]\').click()',
        'returnByValue': True})
    time.sleep(1.5)

    # Hindari escape berlapis: pola dibangun lewat variabel Python.
    SLASH2 = chr(92) * 2
    jarum_js = json.dumps(SLASH2 + '/')
    js2 = ('(() => {'
           'const sub = document.getElementById("sub-regresi");'
           'const grid = document.querySelector(".grid-model-kartu");'
           'const kartu = [...sub.querySelectorAll(".kartu-pilih")];'
           'const jarum = ' + jarum_js + ';'
           'return JSON.stringify({'
           '  subTampak: !sub.hidden,'
           '  gridTersembunyi: grid.hidden,'
           '  judul: kartu.map(k => (k.querySelector(".kartu-judul")||{}).textContent||""),'
           '  teknis: kartu.map(k => ((k.querySelector(".kartu-teknis")||{}).textContent||"")'
           '    + " | " + ((k.querySelector(".kartu-judul")||{}).textContent||"")),'
           '  href: kartu.map(k => k.getAttribute("href")),'
           '  yatim: sub.innerHTML.indexOf(jarum) >= 0'
           '});})()')
    d2 = json.loads(nilai(t.kirim('Runtime.evaluate', {'expression': js2, 'returnByValue': True})))

    catat(d2['subTampak'], 'KLIK → sub-pilihan MUNCUL')
    catat(d2['gridTersembunyi'], 'kartu induk disembunyikan (user fokus)')
    catat(len(d2['judul']) == 2, f"2 judul sub terbaca → {d2['judul']}")
    catat('Parsial' in ' '.join(d2['judul']), "sub 'Parsial' ada")
    catat('Berganda' in ' '.join(d2['judul']), "sub 'Berganda' ada")
    # ⚠️ KEPUTUSAN BOS 21Sep26 (N1 + R1) + penegasan Bos: kartu
    #    "Berganda-berantai" SUDAH TIDAK ADA di pintu. Jangan dituntut lagi.
    #    Yang menjaga kode mesinnya tetap terarsip = sot.py::_periksa_kartu_regresi()
    #    + uji_web_pintu.py — JANGAN diduplikasi di sini.
    catat('Simultan' in ' '.join(d2['judul']),
          f"istilah SIMULTAN tertulis (kartu ②) → {d2['judul']}")
    catat(all('/buat-data?model=' in h for h in d2['href']), f"tiap sub punya tautan → {d2['href']}")
    catat('sederhana' in ' '.join(d2['href']) and 'berganda' in ' '.join(d2['href']),
          'tautan mencakup sederhana+berganda')
    # ⚠️ KEPUTUSAN BOS 21Sep26 (N1): nama kartu ① = "PARSIAL (Sederhana)" ·
    #    ② = "Berganda (Parsial + Simultan)". Jadi istilah BAKU yang wajib
    #    tertulis sekarang: "Parsial" (kartu ①) & "Regresi linear berganda".
    catat('Parsial' in d2['teknis'][0] and 'Regresi linear berganda' in d2['teknis'][1],
          f"istilah BAKU tertulis (Parsial · Regresi linear berganda) → {d2['teknis']}")
    catat(not d2['yatim'], 'TIDAK ada tag escape yatim (kode tumpah)')

    # ── 3. Galat JS selama klik ──
    ge = nilai(t.kirim('Runtime.evaluate', {
        'expression': 'window.__galatJS ? window.__galatJS.length : 0',
        'returnByValue': True}))
    catat(ge in (0, None), f'tidak ada galat JS tercatat (dapat {ge})')

    # ── 4. TUTUP sub → kartu induk kembali ──
    t.kirim('Runtime.evaluate', {
        'expression': 'tutupSub()', 'returnByValue': True})
    time.sleep(1.2)
    js3 = ('(() => {'
           'const sub = document.getElementById("sub-regresi");'
           'const grid = document.querySelector(".grid-model-kartu");'
           'const vid = [...document.querySelectorAll(".kartu-pilih")].filter(k => {'
           '  const r = k.getBoundingClientRect();'
           '  return r.width > 0 && r.height > 0;'
           '});'
           'return JSON.stringify({subTersembunyi: sub.hidden, gridTampak: !grid.hidden,'
           '  jmlTerlihat: vid.length});})()')
    d3 = json.loads(nilai(t.kirim('Runtime.evaluate', {'expression': js3, 'returnByValue': True})))
    catat(d3['subTersembunyi'], 'TOMBOL KEMBALI → sub-pilihan tersembunyi lagi')
    catat(d3['gridTampak'], 'kartu induk kembali terlihat')

    # ═══ PANEL MEDIASI (LANGKAH B, 19Sep26) ═══
    t.kirim('Page.navigate', {'url': URL})
    time.sleep(5)
    t.kirim('Runtime.evaluate', {
        'expression': 'document.querySelector(\'[data-induk="mediasi"]\').click()',
        'returnByValue': True})
    time.sleep(1.5)

    jsM = ('(() => {'
           'const sub = document.getElementById("sub-mediasi");'
           'const grid = document.querySelector(".grid-model-kartu");'
           'if (!sub) return JSON.stringify({ada:false});'
           'const kartu = [...sub.querySelectorAll(".kartu-pilih")];'
           'return JSON.stringify({'
           '  ada: true, subTampak: !sub.hidden, gridTersembunyi: grid.hidden,'
           '  jml: kartu.length,'
           '  judul: kartu.map(k => (k.querySelector(".kartu-judul")||{}).textContent||""),'
           '  teknis: kartu.map(k => (k.querySelector(".kartu-teknis")||{}).textContent||""),'
           '  href: kartu.map(k => k.getAttribute("href")),'
           '  tumpah: sub.innerHTML.indexOf("&lt;") >= 0'
           '});})()')
    dm = json.loads(nilai(t.kirim('Runtime.evaluate', {'expression': jsM, 'returnByValue': True})))

    catat(dm.get('ada'), 'panel #sub-mediasi ADA')
    catat(dm.get('subTampak'), 'KLIK Mediasi → sub-pilihan MUNCUL')
    catat(dm.get('gridTersembunyi'), 'kartu induk disembunyikan')
    catat(dm.get('jml') == 4, f"4 sub-pilihan Mediasi (dapat {dm.get('jml')})")
    for nm in ('Tunggal', 'Paralel', 'Berjenjang', 'Campuran'):
        catat(any(nm in j for j in dm.get('judul', [])), f"sub '{nm}' ada")
    catat(all('/buat-data?model=' in h for h in dm.get('href', [])),
          f"tiap sub punya tautan → {dm.get('href')}")
    catat(all('Mediasi' in s for s in dm.get('teknis', [])),
          f"istilah BAKU tertulis → {dm.get('teknis')}")
    catat(not dm.get('tumpah'), 'TIDAK ada kode tumpah di panel Mediasi')

    # ═══ PANEL MODERASI (LANGKAH C, 19Sep26) ═══
    t.kirim('Page.navigate', {'url': URL})
    time.sleep(5)
    t.kirim('Runtime.evaluate', {
        'expression': 'document.querySelector(\'[data-induk="moderasi"]\').click()',
        'returnByValue': True})
    time.sleep(1.5)

    jsMo = ('(() => {'
            'const sub = document.getElementById("sub-moderasi");'
            'const grid = document.querySelector(".grid-model-kartu");'
            'if (!sub) return JSON.stringify({ada:false});'
            'const kartu = [...sub.querySelectorAll(".kartu-pilih")];'
            'const r = kartu.map(k => { const b = k.getBoundingClientRect();'
            '  return {w: Math.round(b.width), h: Math.round(b.height), top: Math.round(b.top)}; });'
            'return JSON.stringify({'
            '  ada: true, subTampak: !sub.hidden, gridTersembunyi: grid.hidden,'
            '  jml: kartu.length,'
            '  judul: kartu.map(k => (k.querySelector(".kartu-judul")||{}).textContent||""),'
            '  teknis: kartu.map(k => (k.querySelector(".kartu-teknis")||{}).textContent||""),'
            '  href: kartu.map(k => k.getAttribute("href")),'
            '  ukuran: r,'
            '  tumpah: sub.innerHTML.indexOf("&lt;") >= 0'
            '});})()')
    dmo = json.loads(nilai(t.kirim('Runtime.evaluate', {'expression': jsMo, 'returnByValue': True})))

    catat(dmo.get('ada'), 'panel #sub-moderasi ADA')
    catat(dmo.get('subTampak'), 'KLIK Moderasi → sub-pilihan MUNCUL')
    catat(dmo.get('gridTersembunyi'), 'kartu induk disembunyikan')
    catat(dmo.get('jml') == 6, f"6 sub-pilihan Moderasi (dapat {dmo.get('jml')})")
    for nm in ('Tunggal', 'Dual', 'Jalur A', 'Jalur B', 'Keduanya', 'Tiga jalur'):
        catat(any(nm == j or nm in j for j in dmo.get('judul', [])), f"sub '{nm}' ada")
    catat(all('/buat-data?model=' in h for h in dmo.get('href', [])),
          f"tiap sub punya tautan → {dmo.get('href')}")
    catat(all('Moderasi' in s or 'moderasi' in s.lower() for s in dmo.get('teknis', [])),
          f"istilah BAKU tertulis → {dmo.get('teknis')}")
    catat(not dmo.get('tumpah'), 'TIDAK ada kode tumpah di panel Moderasi')
    # Geometri: semua kartu harus punya lebar & tinggi wajar (>120px, >60px) di HP 390
    uk = dmo.get('ukuran', [])
    catat(all(u['w'] > 120 for u in uk), f"semua kartu CUKUP LEBAR di HP 390 → {[u['w'] for u in uk]}")
    catat(all(u['h'] > 60 for u in uk), f"semua kartu CUKUP TINGGI → {[u['h'] for u in uk]}")

    print('\n'.join(pesan))
    print(f'\n  {lulus} LULUS / {gagal} GAGAL')
    # tutup tab yang kita buat sendiri — jangan tinggalkan tab yatim
    if tab_id:
        try:
            urllib.request.urlopen(
                f'{CDP}/json/close/{tab_id}', timeout=10).read()
        except Exception:
            pass
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
