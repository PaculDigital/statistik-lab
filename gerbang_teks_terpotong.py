#!/usr/bin/env python3
"""GERBANG TEKS TERPOTONG — cari teks yang TERPOTONG DI TENGAH KATA.

KENAPA GERBANG INI ADA (pelajaran 18Sep26):
  Bos mengotaki merah bagian "Tampilkan dua-duanya di hasil" di HP-nya.
  Yang tampil di layar: "Tampilk an" / "dua- duanya" / "di hasil".
  Akarnya: elemen `display:flex` yang teksnya tersebar sebagai ANAK
  LANGSUNG (`Tampilkan <strong>dua-duanya</strong> di hasil`) → browser
  memperlakukan tiap potongan sebagai flex-item sendiri → memotong paksa
  di tengah kata saat ruangnya sempit.

  KEJADIAN KEDUA (18Sep26, Bos melingkari "1  8"): `.skala-slider` pakai
  flex + space-between dengan 2 angka. Di HP ruangnya sempit (diapit tombol
  − dan +) → flexbox memindahkan angka ke baris berikutnya → keduanya
  tampak melayang di tengah, bukan di ujung.

CARA UKUR YANG SAH:
  🚨 Jangan pakai iframe `file://` — dokumennya jadi origin lain dan
     `contentDocument` bisa null (Wulan pernah terjebak: "TXT::[]").
  ✅ Pakai PEMBUNGKUS `<div>` selebar HP di dalam jendela 700px. Chrome
     headless menolak `--window-size` < ~500px (merender 500px), jadi lebar
     HP TIDAK bisa diminta langsung — pembungkus adalah cara yang sah.
  Ukur: `scrollWidth` (lebar yang dibutuhkan isi) vs `clientWidth`
  (lebar yang tersedia). Kalau isi lebih lebar → TERPOTONG.

Jalankan: .venv/bin/python gerbang_teks_terpotong.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
CHROME = Path('/opt/data/home/.cloakbrowser/'
              'chromium-146.0.7680.177.5/chrome')
LEBAR_HP = [412, 390, 375, 360]
HALAMAN = ['buat_data.html', 'belajar.html']


def baca_css() -> str:
    return (BASE / 'app' / 'static' / 'gaya.css').read_text(encoding='utf-8')


def rakit(nama: str, lebar: int) -> str:
    """Gabungkan template + gaya.css + pembungkus selebar HP.

    ⚠️ PENTING (pelajaran 18Sep26): berkas di app/templates/ adalah POTONGAN
    Jinja yang memakai {% extends %} — jadi TIDAK punya <html>, <body>,
    maupun </body>. Versi pertama gerbang ini menempelkan skrip ke '</body>'
    dan karena tag itu tidak ada, skripnya TIDAK PERNAH masuk → penanda
    hasil tidak muncul ("tidak terbaca"). Solusinya: BANGUN kerangka HTML
    sendiri di sini.
    """
    html = (BASE / 'app' / 'templates' / nama).read_text(encoding='utf-8')

    # buang tag template Jinja (isi dinamis diisi JS halaman saat dimuat)
    html = re.sub(r'\{%.*?%\}', '', html, flags=re.S)
    html = re.sub(r'\{\{\s*ikon\([^}]*\)\s*\}\}', '', html)
    html = re.sub(r'\{\{.*?\}\}', '', html, flags=re.S)

    css = baca_css()
    css += f"""
    /* ── pembungkus uji: meniru lebar layar HP ───────────────────────── */
    html, body {{ margin: 0; background: #fff; }}
    #bukus-uji {{ width: {lebar}px; overflow-x: hidden; }}
    """

    skrip_penutup = f"""
<script>
window.addEventListener('load', () => {{
  let out = [];
  try {{ out = {SKRIP_UKUR}; }}
  catch (e) {{ out = [{{jenis: 'GALAT_UKUR', teks: String(e.message)}}]; }}
  window.__hasil = out;
  document.title = 'HASIL::' + JSON.stringify(out) + '::END';
}});
</script>
"""
    # ⚠️ Kerangka dibangun SENDIRI — template tidak punya <body>/</body>.
    return f"""<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<style>{css}</style></head>
<body><div id="bukus-uji">
{html}
</div>{skrip_penutup}</body></html>"""


SKRIP_UKUR = r"""
(() => {
  const out = [];
  const akar = document.getElementById('bukus-uji') || document.body;
  for (const e of akar.querySelectorAll('*')) {
    let teks = '';
    for (const n of e.childNodes) {
      if (n.nodeType === 3) teks += n.textContent;
    }
    teks = teks.trim();
    if (!teks || teks.length < 2) continue;

    const cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (parseFloat(cs.opacity) === 0) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 5 || r.height < 5) continue;

    const perlu = e.scrollWidth, ada = e.clientWidth;

    // (a) overflow tersembunyi tapi isi lebih lebar → TERPOTONG
    if ((cs.overflow === 'hidden' || cs.overflowX === 'hidden')
        && perlu > ada + 2 && ada > 10) {
      out.push({jenis: 'overflow-hidden', tag: e.tagName.toLowerCase(),
                kelas: String(e.className || '').slice(0, 40),
                teks: teks.slice(0, 60), perlu, ada, selisih: perlu - ada});
      continue;
    }
    // (b) nowrap + isi lebih lebar dari kotak → TERPOTONG
    if (cs.whiteSpace === 'nowrap' && perlu > ada + 2 && ada > 10) {
      out.push({jenis: 'nowrap-sempit', tag: e.tagName.toLowerCase(),
                kelas: String(e.className || '').slice(0, 40),
                teks: teks.slice(0, 60), perlu, ada, selisih: perlu - ada});
    }
  }

  // (c) anak flex yang isinya CAMPURAN teks + elemen DAN ISINYA TERPOTONG.
  //
  // ⚠️ PELAJARAN (18Sep26): versi pertama gerbang ini menandai SEMUA anak
  // flex yang berisi campuran teks + <strong>. Itu SALAH — memakai <strong>
  // di dalam teks itu NORMAL dan aman selama isinya masih muat di kotaknya.
  // Yang berbahaya hanya kalau isinya LEBIH LEBAR dari ruang yang tersedia
  // (di situlah browser memotong paksa di tengah kata).
  //
  // CARA UKUR YANG BENAR: paksa elemen mengukur lebar ISI-nya dengan
  // `white-space:nowrap` sementara, bandingkan dengan lebar kotaknya.
  // Kalau `scrollWidth > clientWidth` → memang terpotong.
  for (const e of akar.querySelectorAll('*')) {
    const cs = getComputedStyle(e);
    const disp = cs.display || '';
    if (!disp.includes('flex')) continue;
    for (const anak of e.children) {
      let adaTeks = false, adaElemen = false;
      for (const n of anak.childNodes) {
        if (n.nodeType === 3 && n.textContent.trim()) adaTeks = true;
        if (n.nodeType === 1) adaElemen = true;
      }
      if (!adaTeks || !adaElemen) continue;
      if (getComputedStyle(anak).whiteSpace === 'nowrap') continue;

      const ar = anak.getBoundingClientRect();
      if (ar.width < 5 || ar.height < 5) continue;

      // ukur lebar ISI sebenarnya (tanpa mengubah tampilan permanen)
      const nowrapAsli = anak.style.whiteSpace;
      anak.style.whiteSpace = 'nowrap';
      const lebarIsi = anak.scrollWidth;
      const lebarKotak = anak.clientWidth || ar.width;
      anak.style.whiteSpace = nowrapAsli;

      // toleransi 4px supaya pembulatan piksel tidak jadi temuan palsu
      if (lebarIsi > lebarKotak + 4) {
        out.push({jenis: 'flex-teks-terpotong',
                  tag: anak.tagName.toLowerCase(),
                  kelas: String(anak.className || '').slice(0, 40),
                  teks: (anak.textContent || '').trim().slice(0, 60),
                  perlu: Math.round(lebarIsi),
                  ada: Math.round(lebarKotak),
                  selisih: Math.round(lebarIsi - lebarKotak)});
      }
    }
  }

  // (d) label ujung slider: pastikan angka #1 benar-benar di KIRI kotak dan
  // angka terakhir benar-benar di KANAN kotak.
  //
  // ⚠️ PELAJARAN (18Sep26): versi pertama gerbang ini mengukur "jarak antara
  // kedua angka" dan menandai kalau jaraknya kecil. Itu SALAH — kalau kedua
  // angka ada di ujung BERLAWANAN (x=0 dan x=390), jarak antar-teks memang
  // 0 px, dan itu justru KEADAAN YANG BENAR. Yang harus diperiksa adalah:
  //   (i)  apakah keduanya di BARIS yang sama?
  //   (ii) apakah angka #1 menempel ke tepi KIRI kotaknya?
  //   (iii) apakah angka terakhir menempel ke tepi KANAN kotaknya?
  // Kalau salah satu tidak, berarti labelnya "melayang di tengah" seperti
  // yang Bos lihat ("1  8" pindah ke bawah).
  for (const sk of akar.querySelectorAll('.skala-slider')) {
    const k = sk.children;
    if (k.length < 2) continue;
    const kotakR = sk.getBoundingClientRect();
    const kotak = kotakR.width;
    if (kotak < 60) continue;

    const a = k[0].getBoundingClientRect();
    const b = k[k.length - 1].getBoundingClientRect();

    // (i) jatuh ke baris berbeda → pasti salah
    if (Math.abs(a.top - b.top) > 4) {
      out.push({jenis: 'skala-jatuh-baris', tag: 'div',
                kelas: 'skala-slider',
                teks: `${k[0].textContent} / ${k[k.length - 1].textContent}`,
                perlu: Math.round(a.left), ada: Math.round(kotak),
                selisih: -1});
      continue;
    }
    // (ii) angka kiri TIDAK menempel tepi kiri (toleransi 12px)
    const geserKiri = a.left - kotakR.left;
    // (iii) angka kanan TIDAK menempel tepi kanan
    const geserKanan = kotakR.right - b.right;
    if (geserKiri > 12 || geserKanan > 12) {
      out.push({jenis: 'skala-melayang-tengah', tag: 'div',
                kelas: 'skala-slider',
                teks: `${k[0].textContent} / ${k[k.length - 1].textContent}`,
                perlu: Math.round(geserKiri), ada: Math.round(geserKanan),
                selisih: Math.round(Math.max(geserKiri, geserKanan))});
    }
  }

  // (e) radio tersembunyi TIDAK dihitung sebagai masalah tata letak.
  //     (Kartu cara sengaja menyembunyikan radio: 1×1px + opacity 0.
  //      Versi lama gerbang menandainya "radio di atas kartu" — PALSU.)
  return out;
})()
"""


def render(nama: str, lebar: int) -> dict:
    """Render + ukur. Penanda hasil ditulis ke <title> supaya mudah dibaca."""
    isi = rakit(nama, lebar)      # sudah memuat pembungkus + skrip pengukur

    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False,
                                     encoding='utf-8') as f:
        f.write(isi)
        tmp = f.name

    perintah = [
        str(CHROME), '--headless=new', '--no-sandbox', '--disable-gpu',
        '--disable-dev-shm-usage', '--hide-scrollbars',
        '--virtual-time-budget=5000',
        '--window-size=700,2400',
        f'--user-data-dir={tempfile.mkdtemp()}',
        '--dump-dom', f'file://{tmp}',
    ]
    try:
        p = subprocess.run(perintah, capture_output=True, text=True,
                           timeout=120)
        dom = p.stdout or ''
    except subprocess.TimeoutExpired:
        Path(tmp).unlink(missing_ok=True)
        return {'galat': 'timeout', 'potong': []}
    finally:
        Path(tmp).unlink(missing_ok=True)

    m = re.search(r'HASIL::(.*?)::END', dom, re.S)
    if not m:
        return {'galat': 'tidak terbaca (penanda tidak ada)', 'potong': []}
    try:
        return {'galat': '', 'potong': json.loads(m.group(1))}
    except Exception as e:                       # noqa: BLE001
        return {'galat': f'json: {e}', 'potong': []}


def main() -> int:
    print('═══ GERBANG: teks terpotong / anak flex campur (HP) ═══')
    masalah = []
    for nama in HALAMAN:
        for lebar in LEBAR_HP:
            h = render(nama, lebar)
            if h['galat']:
                masalah.append((nama, lebar, f'UKUR GAGAL — {h["galat"]}'))
                continue
            for p in h['potong']:
                if p.get('jenis') == 'GALAT_UKUR':
                    masalah.append((nama, lebar, p.get('teks', 'galat')))
                    continue
                masalah.append(
                    (nama, lebar,
                     f'{p["jenis"]} <{p["tag"]} class="{p["kelas"]}"> '
                     f'"{p["teks"]}" (butuh {p["perlu"]}px, ada {p["ada"]}px)'))

    if masalah:
        print(f'\n  ❌ {len(masalah)} masalah:')
        for nama, lebar, ket in masalah[:24]:
            print(f'     {nama} @{lebar}px — {ket}')
        print('\n  CARA BENAR:')
        print('   • flex — bungkus SEMUA teks dalam SATU <span>; jangan biarkan')
        print('     teks + <strong> jadi bersaudara di dalam elemen flex.')
        print('   • label ujung slider — pakai grid 2 kolom + text-align kiri/kanan;')
        print('     JANGAN flex space-between (angka loncat saat ruang sempit).')
        return 1

    print(f'  ✅ tidak ada teks terpotong '
          f'({len(HALAMAN)} halaman × {len(LEBAR_HP)} lebar HP = '
          f'{len(HALAMAN) * len(LEBAR_HP)} pengukuran)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
