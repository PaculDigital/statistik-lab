#!/usr/bin/env python3
"""UJI BELAJAR dari TAMPILAN HP (18Sep26) — versi yang BENAR.

═══════════════════════════════════════════════════════════════════════════
MENGAPA BERKAS INI DITULIS ULANG (jangan dianggap "tambalan baru"):
Wulan sempat membuat versi yang memakai IFRAME selebar HP. Versi itu GAGAL
4 kali berturut-turut dengan akar yang SAMA: browser mengunci isi iframe
(contentDocument = null) karena halaman pembungkus bukan sesama-origin.
Wulan sudah mencoba berbagai cara menambal (data: URL → server lokal →
CDP frame) — semuanya JALAN BUNTU.

KEPUTUSAN WULAN: berhenti menambal, GANTI PENDEKATAN. Chrome DevTools
Protocol sudah punya cara RESMI dan jauh lebih sederhana:
    Emulation.setDeviceMetricsOverride(mobile=True, width=390, height=...)
Itu menjadikan tab SUNGGUHAN berukuran HP — tanpa iframe sama sekali.
Cara ini sudah terbukti dipakai Wulan untuk tangkapan layar sebelumnya.
═══════════════════════════════════════════════════════════════════════════

YANG DIUKUR (semuanya GEOMETRI NYATA, bukan klaim):
 1. Gambar tidak melar/terpotong di lebar HP (rasio terjaga)
 2. Semua isi diagram berada di dalam kanvas
 3. VIF: ujung kiri BENAR-BENAR berpisah, ujung kanan BENAR-BENAR menumpuk
 4. p-value: garis batas BERLABEL + penanda yang benar-benar bergerak
 5. Kotak "Kenapa bisa terjadi?" terisi untuk keenam istilah
 6. Tidak ada kode tumpah jadi teks

CARA JALAN:  .venv/bin/python uji_belajar_hp.py
Keluar 0 = lulus.
"""
from __future__ import annotations

import base64
import os
import sys
import time

sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_klik_mulai import tab_baru                    # noqa: E402

HAL = os.environ.get('HAL_UJI', 'https://statistik.bikinaja.id/belajar')
LEBAR_HP = 390

LULUS = 0
GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str = '') -> None:
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' → {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' → {bukti}' if bukti else ''))


def main() -> int:
    print('═' * 66)
    print(f'UJI BELAJAR di LAYAR HP {LEBAR_HP}px → {HAL}')
    print('═' * 66)

    ws, _ = tab_baru('about:blank')
    no = 0

    def perintah(m, **p):
        nonlocal no
        no += 1
        return ws.perintah(no, m, **p)

    def js(ekspresi):
        d = perintah('Runtime.evaluate', expression=ekspresi,
                     returnByValue=True, awaitPromise=True)
        if d.get('result', {}).get('exceptionDetails'):
            return {'__galat__': d['result']['exceptionDetails']
                    .get('exception', {}).get('description', 'galat')}
        return d.get('result', {}).get('result', {}).get('value')

    # ⚠️ INI KUNCINYA: tab dibuat SUNGGUHAN berukuran HP (bukan iframe).
    perintah('Emulation.setDeviceMetricsOverride',
             width=LEBAR_HP, height=900, deviceScaleFactor=2, mobile=True)
    perintah('Page.enable')
    # ⚠️ CACAT ALAT UKUR DIPERBAIKI 18Sep26 (akar, dari pengukuran):
    # Uji ini sempat melaporkan "VIF tidak berubah" dan "hetero masih salah"
    # padahal kode di domain SUDAH baru (terbukti dari curl: `jarakPusat` dan
    # `derau SEMU` ADA di HTML yang terkirim). Penyebabnya: tab CDP menyimpan
    # halaman versi lama (cache HTTP 4 jam — lihat gerbang_cache.py), sehingga
    # yang diukur adalah versi BASI. Ini kelas kesalahan yang sama dengan
    # cacat CSS basi yang pernah menipu Wulan. ATURAN: setiap mengukur halaman
    # yang baru di-deploy, WAJIB matikan cache + muat ulang paksa.
    perintah('Network.enable')
    perintah('Network.setCacheDisabled', cacheDisabled=True)
    perintah('Page.navigate', url=HAL)
    perintah('Page.reload', ignoreCache=True)

    siap = False
    for _ in range(60):
        time.sleep(0.5)
        if js("""(() => {
              if (document.readyState !== 'complete') return false;
              return document.querySelector('svg.grafik') !== null;
            })()"""):
            siap = True
            break
    cek('halaman BELAJAR siap di layar HP', siap)
    if not siap:
        print('\n⛔ Halaman tidak siap — pengukuran dihentikan.')
        print(f'\nHASIL UJI HP: {LULUS} LULUS / {GAGAL} GAGAL')
        ws.tutup()
        return 1

    # ── 1. lebar & rasio gambar ───────────────────────────────────────────
    print('\n[1] Gambar tidak melar / terpotong di lebar HP')
    ukur = js("""(() => {
      const s = document.querySelector('svg.grafik');
      const r = s.getBoundingClientRect();
      return { w: Math.round(r.width), h: Math.round(r.height),
               par: s.getAttribute('preserveAspectRatio'),
               layar: window.innerWidth };
    })()""")
    cek('SVG ada & punya ukuran', isinstance(ukur, dict) and 'w' in ukur,
        str(ukur))
    if isinstance(ukur, dict) and 'w' in ukur:
        cek('lebar SVG tidak melebihi layar HP',
            ukur['w'] <= ukur['layar'] + 1,
            f"{ukur['w']}px di layar {ukur['layar']}px")
        cek('rasio TIDAK melar (preserveAspectRatio bukan "none")',
            ukur['par'] != 'none', str(ukur['par']))
        rasio = ukur['w'] / max(1, ukur['h'])
        cek('rasio gambar wajar (1,6–2,6)', 1.6 <= rasio <= 2.6,
            f"rasio={rasio:.2f} ({ukur['w']}×{ukur['h']})")

    # ── 2. isi diagram di dalam kanvas ────────────────────────────────────
    print('\n[2] Isi diagram tidak keluar kanvas')
    keluar = js("""(() => {
      const s = document.querySelector('svg.grafik');
      const vb = s.viewBox.baseVal;
      const hasil = [];
      for (const e of s.querySelectorAll('text, circle, rect, line, path')) {
        const b = e.getBBox();
        if (b.x < -4 || b.y < -4 ||
            b.x + b.width > vb.width + 4 ||
            b.y + b.height > vb.height + 4) {
          hasil.push((e.tagName + ':' + (e.textContent || '').slice(0, 22)));
        }
      }
      return hasil;
    })()""")
    cek('tidak ada isi keluar kanvas', keluar == [],
        f'{len(keluar)} keluar: {keluar[:3]}' if keluar else 'bersih')

    # ── 3. HETEROSKEDASTISITAS (temuan Bos 18Sep26) ───────────────────────
    print('\n[3] Heteroskedastisitas — ujung "rata" harus BENAR-BENAR rata')
    js("document.querySelector('.kamus-tombol[data-k=\"hetero\"]').click()")

    def ukur_hetero(n):
        js(f"""(() => {{
          const s = document.getElementById('slider');
          s.value = '{n}';
          s.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }})()""")
        time.sleep(0.45)
        return js("""(() => {
          const s = document.querySelector('svg.grafik');
          const t = Array.from(s.querySelectorAll('circle'))
                     .map(e => e.getBoundingClientRect())
                     .sort((a, b) => a.left - b.left);
          if (t.length < 10) return null;
          const n = t.length, bagi = Math.floor(n / 3);
          const kiri = t.slice(0, bagi), kanan = t.slice(-bagi);
          const tinggi = (arr) => {
            const atas = Math.min(...arr.map(r => r.top));
            const bawah = Math.max(...arr.map(r => r.bottom));
            return bawah - atas;
          };
          return { titik: n, kiri: Math.round(tinggi(kiri)),
                   kanan: Math.round(tinggi(kanan)),
                   teks: s.textContent.replace(/\\s+/g, ' ').slice(0, 200) };
        })()""")

    h0 = ukur_hetero(0)
    h100 = ukur_hetero(100)
    if isinstance(h0, dict) and isinstance(h100, dict):
        rasio0 = h0['kanan'] / max(1, h0['kiri'])
        rasio100 = h100['kanan'] / max(1, h100['kiri'])
        cek('ujung "rata": kiri dan kanan SAMA TINGGI (rasio ≤ 1,6)',
            rasio0 <= 1.6,
            f"kiri {h0['kiri']}px vs kanan {h0['kanan']}px → rasio {rasio0:.2f}×")
        cek('ujung "tidak rata": kanan JAUH lebih lebar (rasio ≥ 2,5)',
            rasio100 >= 2.5,
            f"kiri {h100['kiri']}px vs kanan {h100['kanan']}px → rasio {rasio100:.2f}×")
        cek('gambar benar-benar berubah dari ujung ke ujung',
            rasio100 - rasio0 >= 1.5,
            f"rasio {rasio0:.2f}× → {rasio100:.2f}×")
        cek('label keadaan ikut berubah (bukan gambar bisu)',
            isinstance(h0, dict) and isinstance(h100, dict)
            and h0['teks'] != h100['teks'],
            f"v=0: {h0['teks'][-42:]} | v=100: {h100['teks'][-42:]}")
    else:
        cek('geometri hetero terbaca', False, str(h0) + str(h100))

    # titik TIDAK berkedip: dua kali ukur nilai sama → susunan sama
    a1 = js("""(() => { const s = document.getElementById('slider');
      s.value = '50'; s.dispatchEvent(new Event('input', { bubbles: true }));
      return Array.from(document.querySelectorAll('svg.grafik circle'))
        .map(e => e.getAttribute('cy')).join(','); })()""")
    time.sleep(0.4)
    a2 = js("""(() => { const s = document.getElementById('slider');
      s.value = '50'; s.dispatchEvent(new Event('input', { bubbles: true }));
      return Array.from(document.querySelectorAll('svg.grafik circle'))
        .map(e => e.getAttribute('cy')).join(','); })()""")
    cek('titik TIDAK berkedip (gambar sama saat nilai sama)', a1 == a2,
        'sama' if a1 == a2 else 'BERUBAH-UBah')

    # ── 4. VIF ────────────────────────────────────────────────────────────
    print('\n[4] VIF — slider benar-benar mengubah keadaan')

    # ⚠️ CACAT ALAT UKUR DIPERBAIKI 18Sep26 (akar, dari pengukuran langsung):
    # Uji ini sempat melaporkan `istilahAktif: 'hetero'` dan `jmlCircle: 110`
    # walaupun klik VIF sudah dijalankan. Ternyata klik MEMANG bekerja
    # (dibuktikan lewat pemeriksaan manual: aktif='vif', circle=4): yang salah
    # adalah uji TIDAK MENUNGGU penggambaran ulang selesai sebelum mengukur,
    # sehingga masih membaca sisa gambar hetero (110 titik). Sekarang klik
    # ditunggu sampai jumlah lingkaran benar-benar berubah jadi 4.
    js("document.querySelector('.kamus-tombol[data-k=\"vif\"]').click()")
    for _ in range(20):
        time.sleep(0.25)
        n = js("document.querySelectorAll('svg.grafik circle').length")
        if n == 4:
            break
    cek('istilah VIF benar-benar aktif sebelum diukur',
        js("document.querySelector('.kamus-tombol.aktif').dataset.k") == 'vif',
        'aktif = vif')

    def geser(n):
        js(f"""(() => {{
          const s = document.getElementById('slider');
          s.value = '{n}';
          s.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }})()""")
        time.sleep(0.45)

    def pusat(n):
        """Kembalikan jarak pusat dua lingkaran X1 & X2.

        ⚠️ CACAT ALAT UKUR DIPERBAIKI 18Sep26 (akar, dari diagnosa):
        Tiap lingkaran digambar DUA KALI di SVG (isi berwarna + garis tepi),
        jadi ada 4 elemen <circle>, bukan 2. Uji lama membaca circle[0] dan
        circle[1] — padahal itu ISINYA dan TEPINYA lingkaran yang SAMA →
        jarak terbaca 3px (mustahil) dan Wulan hampir "memperbaiki" kode yang
        sudah benar. Sekarang dipilih hanya elemen dengan jari-jari penuh
        (lingkaran besar), lalu diambil dua pusat yang berbeda.
        """
        js(f"""(() => {{
          const s = document.getElementById('slider');
          s.value = '{n}';
          s.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }})()""")
        time.sleep(0.45)
        return js("""(() => {
          const semua = Array.from(document.querySelectorAll('svg.grafik circle'))
            .map(e => e.getBoundingClientRect())
            .filter(r => r.width > 20);            // buang titik/label kecil
          if (semua.length < 2) return null;
          const r0 = semua[0].width;
          // ambil HANYA elemen dengan jari-jari sama (lingkaran penuh,
          // bukan lingkaran kedua yang ukurannya bisa berbeda kalau ada)
          const sama = semua.filter(r => Math.abs(r.width - r0) < 2);
          if (sama.length < 2) return null;
          const xA = sama[0].left + sama[0].width / 2;
          const xB = sama[sama.length - 1].left + sama[sama.length - 1].width / 2;
          return { pusat: Math.round(Math.abs(xB - xA)),
                   R: Math.round(sama[0].width / 2),
                   jml: semua.length };
        })()""")

    kiri = pusat(0)
    kanan = pusat(100)
    if isinstance(kiri, dict) and isinstance(kanan, dict):
        cek('ujung kiri: lingkaran BERPISAH (beda semua)',
            kiri['pusat'] >= 2 * kiri['R'],
            f"jarak pusat {kiri['pusat']}px ≥ 2R {2 * kiri['R']}px")
        cek('ujung kanan: lingkaran MENUMPUK (nyaris kembar)',
            kanan['pusat'] < 2 * kanan['R'],
            f"jarak pusat {kanan['pusat']}px < 2R {2 * kanan['R']}px")
        cek('slider VIF benar-benar berguna (bukan hiasan)',
            kiri['pusat'] >= 2 * kiri['R'] > kanan['pusat'],
            f"pisah {kiri['pusat']}px → menumpuk {kanan['pusat']}px")
    else:
        # ⚠️ Kalau tidak terbaca, JANGAN simpulkan aplikasi rusak — tampilkan
        # APA YANG SEBENARNYA ADA di halaman, supaya akarnya kelihatan.
        rinci = js("""(() => {
          const s = document.querySelector('svg.grafik');
          const c = s ? Array.from(s.querySelectorAll('circle')) : [];
          return { istilahAktif:
                     (document.querySelector('.kamus-tombol.aktif') || {})
                       .getAttribute ? (document.querySelector('.kamus-tombol.aktif')
                       || {}).getAttribute('data-k') : '?',
                   jmlCircle: c.length,
                   ukuran: c.map(e =>
                     Math.round(e.getBoundingClientRect().width)),
                   nilaiSlider: (document.getElementById('slider') || {}).value,
                   adaSvg: !!s };
        })()""")
        cek('geometri VIF terbaca', False, str(rinci))

    # ── 5. p-value ────────────────────────────────────────────────────────
    print('\n[5] p-value — garis batas berlabel & penanda bergerak')
    js("document.querySelector('.kamus-tombol[data-k=\"pvalue\"]').click()")
    geser(10)
    a = js("""(() => {
      const s = document.querySelector('svg.grafik');
      const t = s.textContent;
      const garis = s.querySelectorAll('line');
      // ⚠️ CACAT ALAT UKUR DIPERBAIKI 18Sep26: dulu di sini Wulan membaca
      // `garis[2]`, padahal garis[0]=sumbu bawah, garis[1]=batas kiri,
      // garis[2]=batas KANAN (memang TETAP di 267), dan garis[3]=PENANDA p
      // yang bergerak. Akibatnya Wulan "menemukan cacat" pada kode yang
      // sebenarnya sudah benar, lalu mengubah kode tanpa perlu. Ditemukan
      // lewat diagnosa_slider.py. Sekarang pakai garis[3].
      const xp = garis[3] ? Math.round(garis[3].getBoundingClientRect().left) : -1;
      return { labelBatas: /batas\\s*0,05/.test(t),
               adaP: /p\\s*=/.test(t), xp: xp };
    })()""")
    cek('garis batas berlabel "batas 0,05"',
        isinstance(a, dict) and a.get('labelBatas'), str(a))
    cek('penanda "p = ..." ada di gambar',
        isinstance(a, dict) and a.get('adaP'))
    geser(90)
    b = js("""(() => {
      const s = document.querySelector('svg.grafik');
      const garis = s.querySelectorAll('line');
      return garis[3] ? Math.round(garis[3].getBoundingClientRect().left) : -1;
    })()""")
    cek('penanda p BERGERAK saat slider digeser',
        isinstance(a, dict) and a.get('xp') != b,
        f"x(10)={a.get('xp')} → x(90)={b}")

    # ── 6. kotak "Kenapa bisa terjadi?" ───────────────────────────────────
    print('\n[6] Kotak "Kenapa bisa terjadi?" terisi')
    for k in ['hetero', 'beta', 'pvalue', 'r2', 'vif', 'alpha']:
        js(f"document.querySelector('.kamus-tombol[data-k=\"{k}\"]').click()")
        time.sleep(0.3)
        n = js('document.querySelectorAll(".daftar-kenapa li").length')
        tampil = js('document.getElementById("kenapa-kotak").hidden === false')
        cek(f'{k}: {n} sebab, kotak tampil', (n or 0) >= 3 and tampil,
            f'{n} sebab')

    # ── 7. tidak ada tag mentah ───────────────────────────────────────────
    print('\n[7] Tidak ada kode tumpah jadi teks')
    teks = js('document.body.innerText') or ''
    for tag in ['</text>', '</strong>', 'function()', '</script>']:
        cek(f'tidak ada "{tag}" jadi teks', tag not in teks)

    # ── tangkapan layar untuk Bos ─────────────────────────────────────────
    os.makedirs('/tmp/shot', exist_ok=True)
    js("document.querySelector('.kamus-tombol[data-k=\"vif\"]').click()")
    for nama, nilai in [('vif_beda', 0), ('vif_mirip', 100)]:
        geser(nilai)
        perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP,
                 height=1500, deviceScaleFactor=2, mobile=True)
        time.sleep(0.6)
        d = perintah('Page.captureScreenshot', format='png')
        open(f'/tmp/shot/hp_{nama}.png', 'wb').write(
            base64.b64decode(d['result']['data']))
        perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP,
                 height=900, deviceScaleFactor=2, mobile=True)
    for kunci, nilai in [('hetero', 0), ('hetero', 100), ('r2', 41), ('pvalue', 41)]:
        js(f"document.querySelector('.kamus-tombol[data-k=\"{kunci}\"]').click()")
        geser(nilai)
        nama_file = f'{kunci}_{nilai}' if kunci == 'hetero' else kunci
        perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP,
                 height=1500, deviceScaleFactor=2, mobile=True)
        time.sleep(0.6)
        d = perintah('Page.captureScreenshot', format='png')
        open(f'/tmp/shot/hp_{nama_file}.png', 'wb').write(
            base64.b64decode(d['result']['data']))
        perintah('Emulation.setDeviceMetricsOverride', width=LEBAR_HP,
                 height=900, deviceScaleFactor=2, mobile=True)
    print('\n  📷 /tmp/shot/hp_{vif_beda,vif_mirip,r2,pvalue}.png')

    print('\n' + '=' * 66)
    print(f'HASIL UJI HP: {LULUS} LULUS / {GAGAL} GAGAL')
    print('=' * 66)
    ws.tutup()
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
