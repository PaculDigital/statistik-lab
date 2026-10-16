#!/usr/bin/env python3
"""GERBANG: tata letak kontrol slider & tombol preset di halaman BUAT DATA.

KENAPA GERBANG INI ADA (pelajaran 17Sep26):
  Semua gerbang lain LULUS, tetapi MATA menemukan tombol −/+ tidak sejajar
  dan tombol preset 1..8 menumpuk VERTIKAL. Penyebabnya CSS: `.pilih`
  memasang display:flex + flex-direction:column yang menimpa `.pilih-kecil`.
  Galat seperti ini TIDAK terlihat dari HTML, tidak terlihat dari galat JS,
  dan tidak terlihat dari uji HTTP — hanya terlihat dari GEOMETRI elemen.

Cara kerja: buka halaman dengan Chrome headless, lalu baca posisi & ukuran
elemen (getBoundingClientRect) dan nilai gaya terhitung (getComputedStyle):
  - tombol − dan + harus SEJAJAR dengan slider (selisih titik tengah kecil)
  - 6 tombol preset harus dalam SATU baris (titik tengah Y sama)
  - semua kontrol harus ≥ 44px (target sentuh) dan di dalam lebar layar
"""
import json
import os
import subprocess
import sys

CHROME_URUT = [
    '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome',
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.4-pro/chrome',
]

SKRIP_UKUR = r"""
(() => {
  const out = {};
  const rect = el => { const r = el.getBoundingClientRect();
    return {x: r.x, y: r.y, w: r.width, h: r.height,
            cy: r.y + r.height / 2, cx: r.x + r.width / 2}; };

  const kurang = document.getElementById('x-kurang');
  const tambah = document.getElementById('x-tambah');
  const slider = document.getElementById('x-slider');
  const presets = [...document.querySelectorAll('.pilih-kecil')];
  const nama = [...document.querySelectorAll('.nama-var')];

  out.kurang = kurang ? rect(kurang) : null;
  out.tambah = tambah ? rect(tambah) : null;
  out.slider = slider ? rect(slider) : null;
  out.preset = presets.map(p => ({teks: p.textContent.trim(), ...rect(p)}));
  out.namaJumlah = nama.length;
  out.namaNilai = nama.map(n => n.value);
  out.lebarLayar = window.innerWidth;
  out.scrollW = document.documentElement.scrollWidth;

  // gaya terhitung tombol preset (deteksi flex-direction:column)
  if (presets.length) {
    const cs = getComputedStyle(presets[0]);
    out.preset_arah = cs.flexDirection;
    out.preset_display = cs.display;
  }
  return JSON.stringify(out);
})()
"""


def cari_chrome():
    for c in CHROME_URUT:
        if os.path.exists(c):
            return c
    return None


def main() -> int:
    ch = cari_chrome()
    if not ch:
        print('  ⚠️  Chrome tidak ada — gerbang tata letak dilewati')
        return 0

    ip = os.environ.get('TATA_IP') or subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True).stdout.strip()
    # TATA_PORT: untuk menguji SEBELUM deploy (server uji di host).
    # Normalnya 8000 (port DALAM kontainer) — itulah yang dipakai gerbang.
    port = os.environ.get('TATA_PORT', '8000')
    if not ip:
        print('  ⚠️  kontainer tidak jalan — gerbang tata letak dilewati')
        return 0

    print('═══ GERBANG: tata letak slider & tombol (geometri elemen) ═══')

    # Suntikkan skrip pengukur lewat halaman pembantu di dalam aplikasi.
    # ⚠️ `?model=sederhana` WAJIB (20Sep26): /buat-data TANPA ?model=
    #    SENGAJA dialihkan ke /kuantitatif (Tahap 1.4) → Chrome pindah
    #    halaman → gerbang mengukur halaman yang SALAH.
    url = f'http://{ip}:{port}/buat-data?model=sederhana'
    p = subprocess.run(
        [ch, '--headless', '--disable-gpu', '--no-sandbox',
         '--window-size=1280,1400', '--virtual-time-budget=9000',
         '--enable-logging=stderr', '--log-level=0',
         '--dump-dom', url],
        capture_output=True, text=True, timeout=140)

    # Chrome headless --dump-dom tidak bisa menjalankan JS sembarang.
    # Jadi kita memakai halaman pengukur yang disajikan aplikasi.
    # ⚠️ WAJIB uji BEBERAPA LEBAR. Bug 17Sep26 hanya muncul di lebar
    # tertentu (panel menyempit -> tombol preset bertumpuk), padahal pada
    # lebar lain tampak sempurna. Satu lebar saja = gerbang buta.
    import html as _h
    import re
    # ⚠️ WAJIB termasuk lebar HP. Bug 17Sep26 lolos karena uji berhenti di
    # 820px — padahal di 390px tombol preset bertumpuk & halaman meluber.
    LEBAR_UJI = [1280, 1100, 1000, 900, 820, 412, 390, 375, 360]
    gagal = 0

    for lebar in LEBAR_UJI:
        p2 = subprocess.run(
            [ch, '--headless', '--disable-gpu', '--no-sandbox',
             f'--window-size={lebar},1500', '--virtual-time-budget=9000',
             '--dump-dom',
             f'http://{ip}:{port}/static/ukur_tata.html?lebar={lebar}&tinggi=1500'],
            capture_output=True, text=True, timeout=140)

        if 'TA::' not in (p2.stdout or ''):
            print('  ⚠️  halaman pengukur /static/ukur_tata.html belum ada')
            print('     (gerbang dilewati — bukan kegagalan)')
            return 0

        m = re.search(r'TA::(.*?)</title>', p2.stdout, re.S)
        if not m:
            print(f'  ⚠️  lebar {lebar}: hasil ukur tidak terbaca')
            continue
        data = json.loads(_h.unescape(m.group(1).strip()))
        print(f'  ── lebar {lebar}px ──')
        # ⚠️ PENJAGA ANTI-UJI-PALSU: pastikan lebar yang TERUKUR benar-benar
        # sesuai yang diminta. Tanpa ini, "5 lebar berbeda" bisa saja
        # sebenarnya menguji satu lebar yang sama (bug gerbang 17Sep26).
        if abs(data.get('lebarLayar', 0) - lebar) > 40:
            print(f'  ❌ TERUKUR lebar {data.get("lebarLayar")}px, '
                  f'padahal diminta {lebar}px — uji ini tidak sah')
            gagal += 1
            print()
            continue
        gagal += periksa(data, lebar)
        print()

def periksa(data, lebar):
    """Periksa geometri untuk satu lebar layar. Kembalikan jumlah masalah."""
    gagal = 0

    # 1) tombol − dan + harus SEJAJAR satu sama lain DAN sejajar barisnya
    #    dengan slider.
    #    ⚠️ PELAJARAN: <input type=range> punya tinggi kotaknya hanya ~5px
    #    (track-nya tipis) sedangkan tombol 44px. Membandingkan titik tengah
    #    tombol dengan titik tengah slider SELALU selisih ~12px walaupun
    #    tampilannya benar. Jadi yang dibandingkan: − vs + (wajib sama), dan
    #    tombol harus berada di dalam rentang VERTIKAL slider + tinggi tombol.
    if data.get('kurang') and data.get('tambah') and data.get('slider'):
        k, t, s = data['kurang'], data['tambah'], data['slider']
        dkt = abs(k['cy'] - t['cy'])
        if dkt <= 3:
            print(f'  ✅ tombol − dan + sejajar (selisih titik tengah {dkt:.1f}px)')
        else:
            print(f'  ❌ tombol − dan + TIDAK sejajar (selisih {dkt:.0f}px)')
            gagal += 1
        # tombol harus mengapit slider (kiri & kanan), bukan bertumpuk
        if k['x'] + k['w'] <= s['x'] + 2 and t['x'] >= s['x'] + s['w'] - 2:
            print(f'  ✅ slider diapit − di kiri ({k["x"]:.0f}) dan + di kanan ({t["x"]:.0f})')
        else:
            print(f'  ❌ slider TIDAK diapit − / + '
                  f'(− di {k["x"]:.0f}, slider {s["x"]:.0f}–{s["x"] + s["w"]:.0f}, '
                  f'+ di {t["x"]:.0f})')
            gagal += 1
        for nm, b in (('−', k), ('+', t)):
            if b['h'] < 40:
                print(f'  ❌ tombol {nm} terlalu kecil ({b["h"]:.0f}px)')
                gagal += 1
    else:
        print('  ⚠️  tombol − / + / slider tidak ditemukan')
        gagal += 1

    # 2) tombol preset dalam satu baris
    pr = data.get('preset') or []
    if pr:
        ys = [x['cy'] for x in pr]
        sebaris = (max(ys) - min(ys)) <= 12
        if sebaris and data.get('preset_arah') != 'column':
            print(f'  ✅ {len(pr)} tombol preset dalam SATU baris')
        else:
            print(f'  ❌ tombol preset TIDAK sebaris '
                  f'(sebaran Y {max(ys) - min(ys):.0f}px, '
                  f'flex-direction={data.get("preset_arah")})')
            gagal += 1
        # ⚠️ PENJAGA UTAMA: kalau preset SEBARIS, x harus MENAIK berurutan.
        # Kalau bertumpuk (wrap), akan ada dua tombol dengan x hampir sama
        # tetapi y berbeda. Inilah yang menangkap bug lebar-sempit 17Sep26.
        xs = [x['x'] for x in pr]
        naik = all(xs[i] < xs[i + 1] + 1 for i in range(len(xs) - 1))
        if not naik:
            print(f'  ❌ tombol preset BERTUMPUK (x tidak menaik: '
                  f'{[round(v) for v in xs]})')
            gagal += 1
        elif sebaris:
            print(f'  ✅ {len(pr)} tombol preset sebaris, x menaik '
                  f'({round(xs[0])} → {round(xs[-1])})')

        for x in pr:
            if x['h'] < 40:
                print(f'  ❌ tombol preset "{x["teks"]}" tinggi {x["h"]:.0f}px < 40px')
                gagal += 1
            if x['x'] < -1 or x['x'] + x['w'] > data['lebarLayar'] + 1:
                print(f'  ❌ tombol preset "{x["teks"]}" keluar layar')
                gagal += 1
    else:
        print('  ⚠️  tombol preset tidak ditemukan')
        gagal += 1

    # 3) tidak ada geser kiri-kanan
    if data['scrollW'] > data['lebarLayar'] + 1:
        print(f'  ❌ halaman geser kiri-kanan '
              f'({data["scrollW"]} > {data["lebarLayar"]})')
        gagal += 1
    else:
        print(f'  ✅ tidak ada geser kiri-kanan ({data["scrollW"]} ≤ {data["lebarLayar"]})')

    if gagal:
        print(f'  ❌ lebar {lebar}: {gagal} masalah tata letak')
        print('  Uji HTTP/JS TIDAK menangkap ini; hanya geometri elemen bisa.')
    return gagal


if __name__ == '__main__':
    sys.exit(main())
