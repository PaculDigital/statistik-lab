#!/usr/bin/env python3
"""UKUR KARTU CARA — ambil dari HALAMAN SUNGGUHAN, bukan halaman uji.

KENAPA BERKAS INI ADA (pelajaran 18Sep26 — Wulan SALAH UKUR 2×):
  Wulan mengukur `.skala-slider` di halaman UJI kecil buatan sendiri, dan
  CSS-nya tampak benar. Tapi di HALAMAN SUNGGUHAN (dari kontainer, ada
  `.papan`, `.kartu`, `.medan` yang membungkus) hasilnya BEDA — angka tetap
  melayang. Pelajarannya:  UKUR DARI HALAMAN SUNGGUHAN.

CARA: ambil HTML dari kontainer lewat HTTP, lalu periksa di Chrome:
  • posisi KATA (bukan kotak elemen — kotak selalu penuh, itu yang menipu)
  • radio button: di mana sebenarnya ia berada
  • tinggi kartu (boros atau tidak)
  • apakah teks di kartu terpusat atau rata kiri

Jalankan: .venv/bin/python periksa_halaman_sungguhan.py
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
CH = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'
URL = 'http://127.0.0.1:8120/buat-data'


def _url_halaman() -> str:
    """Ambil URL halaman yang BISA dijangkau dari tempat skrip ini jalan.

    ⚠️ JEBAKAN (18Sep26): `127.0.0.1:8120` HANYA jalan kalau skrip dijalankan
    dari HOST. Dari dalam container/sesi lain, itu loopback yang salah →
    "Connection refused". Jadi kami cari IP container dulu, baru jatuh ke
    localhost.
    """
    import subprocess as sp
    try:
        nama = 'simulasi-olah-data'
        ip = sp.run(['docker', 'inspect', '-f',
                     '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                     nama], capture_output=True, text=True, timeout=15)
        ip = (ip.stdout or '').strip()
        if ip:
            return f'http://{ip}:8000/buat-data'
    except Exception:                            # noqa: BLE001
        pass
    return URL

JS = r"""
window.addEventListener('load', () => {
  // posisi KATA sebenarnya (kotak span itu MENIPU — selalu penuh)
  const kataKotak = (el) => {
    if (!el || !el.firstChild) return null;
    const rg = document.createRange();
    rg.selectNodeContents(el);
    const r = rg.getBoundingClientRect();
    return {kiri: Math.round(r.left), kanan: Math.round(r.right),
            atas: Math.round(r.top), tengahX: Math.round((r.left + r.right) / 2)};
  };
  const out = {};

  // ── label slider ──
  const sk = document.querySelector('.skala-slider');
  if (sk) {
    const kotak = sk.getBoundingClientRect();
    const a = kataKotak(sk.children[0]);
    const b = kataKotak(sk.children[sk.children.length - 1]);
    out.skala = {
      kotakKiri: Math.round(kotak.left), kotakKanan: Math.round(kotak.right),
      kata1: a, kataAkhir: b,
      geserKiri: a ? a.kiri - Math.round(kotak.left) : null,
      geserKanan: b ? Math.round(kotak.right) - b.kanan : null,
      sebaris: (a && b) ? Math.abs(a.atas - b.atas) < 4 : null,
      teks: (sk.textContent || '').trim()
    };
  }

  // ── kartu cara ──
  const kartu = document.querySelectorAll('.pilih-cara');
  out.kartu = [];
  kartu.forEach(k => {
    const r = k.getBoundingClientRect();
    const radio = k.querySelector('input[type=radio]');
    const rr = radio ? radio.getBoundingClientRect() : null;
    const judul = k.querySelector('.cara-judul');
    const jr = judul ? judul.getBoundingClientRect() : null;
    const cs = getComputedStyle(k);

    // SIAPA yang menang? tanya CSSOM langsung — jangan menebak.
    let menang = [];
    try {
      for (const r2 of document.styleSheets) {
        let aturan;
        try { aturan = r2.cssRules; } catch (e) { continue; }
        for (const c of aturan) {
          const cek = (sel, isi) => {
            try {
              if (k.matches(sel) && isi.includes('display'))
                menang.push(sel + ' → ' + isi.slice(0, 60));
            } catch (e) { /* selektor aneh */ }
          };
          if (c.selectorText) {
            cek(c.selectorText, c.style ? c.style.cssText : '');
          } else if (c.cssRules) {          // @media
            for (const c2 of c.cssRules) {
              if (c2.selectorText && k.matches(c2.selectorText)) {
                const isi = c2.style ? c2.style.cssText : '';
                if (isi.includes('display') || isi.includes('min-height'))
                  menang.push('@media ' + c.conditionText + ' · ' +
                              c2.selectorText + ' → ' + isi.slice(0, 50));
              }
            }
          }
        }
      }
    } catch (e) { menang.push('gagal baca CSSOM: ' + e.message); }

    out.kartu.push({
      display: cs.display,
      flexDirection: cs.flexDirection,
      alignItems: cs.alignItems,
      minHeight: cs.minHeight,
      textAlign: cs.textAlign,
      tinggi: Math.round(r.height),
      lebar: Math.round(r.width),
      radioX: rr ? Math.round(rr.left - r.left) : null,
      radioY: rr ? Math.round(rr.top - r.top) : null,
      radioAda: !!radio,
      radioLebar: rr ? Math.round(rr.width) : null,
      judulTengahX: jr ? Math.round((jr.left + jr.right) / 2 - r.left) : null,
      temaKartu: Math.round(r.width / 2),
      aturanDisplay: menang.slice(0, 6)
    });
  });

  // ── semua input range: labelnya di mana? ──
  out.sliderSemua = [];
  document.querySelectorAll('input[type=range]').forEach(inp => {
    const medan = inp.closest('.medan') || inp.parentElement;
    const skala = medan ? medan.querySelector('.skala-slider') : null;
    if (!skala) { out.sliderSemua.push({ada: false, id: inp.id}); return; }
    const a = kataKotak(skala.children[0]);
    const kotak = skala.getBoundingClientRect();
    out.sliderSemua.push({
      id: inp.id || '(tanpa id)',
      teks: (skala.textContent || '').trim(),
      geserKiri: a ? a.kiri - Math.round(kotak.left) : null,
      lebar: Math.round(kotak.width)
    });
  });

  document.title = 'HS::' + JSON.stringify(out) + '::E';
});
"""


def ambil_halaman() -> str:
    url = _url_halaman()
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def ambil_css_dari_kontainer() -> str:
    """Ambil gaya.css dari kontainer (agar ukuran sama dengan LIVE)."""
    import subprocess as sp
    try:
        ip = sp.run(['docker', 'inspect', '-f',
                     '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                     'simulasi-olah-data'], capture_output=True, text=True,
                    timeout=15).stdout.strip()
        if ip:
            with urllib.request.urlopen(f'http://{ip}:8000/static/gaya.css',
                                        timeout=30) as r:
                return r.read().decode('utf-8', 'replace')
    except Exception:                            # noqa: BLE001
        pass
    return (BASE / 'app' / 'static' / 'gaya.css').read_text(encoding='utf-8')


def main() -> int:
    url = _url_halaman()
    print(f'═══ PERIKSA HALAMAN SUNGGUHAN: {url} ═══')
    try:
        html = ambil_halaman()
    except Exception as e:                       # noqa: BLE001
        print(f'  ❌ tidak bisa ambil halaman: {e}')
        return 1

    # ⚠️ WAJIB (pelajaran 18Sep26 — pengukuran Wulan sempat PALSU):
    # halaman memakai <link href="/static/gaya.css">. Kalau halaman dibuka
    # dengan file://, tautan itu jadi file:///static/gaya.css → TIDAK ADA →
    # CSS tidak termuat → semua elemen tampak "display:inline" dan temuan
    # jadi palsu. Jadi CSS-nya DISUNTIK LANGSUNG ke dalam halaman.
    css = ambil_css_dari_kontainer()
    html = re.sub(r'<link[^>]*gaya\.css[^>]*>', '', html)
    html = html.replace('</head>', f'<style>{css}</style></head>', 1)
    print(f'  CSS disuntik: {len(css)} karakter (dari kontainer)')
    print(f'  halaman terambil: {len(html)} karakter')

    # jalankan skrip pengukur di halaman sungguhan
    if '</body>' in html:
        html = html.replace('</body>', f'<script>{JS}</script></body>', 1)
    else:
        html += f'<script>{JS}</script>'

    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False,
                                     encoding='utf-8') as f:
        f.write(html)
        tmp = f.name
    try:
        p = subprocess.run([CH, '--headless=new', '--no-sandbox',
                            '--disable-gpu', '--hide-scrollbars',
                            f'--user-data-dir={tempfile.mkdtemp()}',
                            '--window-size=500,3000',
                            '--virtual-time-budget=5000',
                            '--dump-dom', f'file://{tmp}'],
                           capture_output=True, text=True, timeout=120)
        dom = p.stdout or ''
    finally:
        Path(tmp).unlink(missing_ok=True)

    m = re.search(r'HS::(.*?)::E', dom, re.S)
    if not m:
        print('  ❌ penanda tidak terbaca (halaman mungkin butuh login?)')
        return 1
    d = json.loads(m.group(1))

    gagal = 0
    print()
    print('  ── LABEL SLIDER ──')
    sk = d.get('skala')
    if sk:
        print(f'     teks        : "{sk["teks"]}"')
        print(f'     kotak       : {sk["kotakKiri"]} … {sk["kotakKanan"]}')
        print(f'     kata "1"    : kiri={sk["kata1"]["kiri"]} '
              f'tengahX={sk["kata1"]["tengahX"]}')
        print(f'     kata terakhir: kiri={sk["kataAkhir"]["kiri"]} '
              f'tengahX={sk["kataAkhir"]["tengahX"]}')
        print(f'     geser kiri={sk["geserKiri"]}px  kanan={sk["geserKanan"]}px  '
              f'sebaris={sk["sebaris"]}')
        if sk['geserKiri'] > 12 or sk['geserKanan'] > 12:
            print('     ❌ MASIH MELAYANG — label tidak menempel tepi')
            gagal += 1
        else:
            print('     ✅ menempel tepi kiri & kanan')
    print()
    print('  ── SLIDER LAIN ──')
    for s in d.get('sliderSemua', []):
        if not s.get('ada', True) and 'teks' not in s:
            print(f'     {s.get("id")}: tidak punya .skala-slider')
            continue
        tanda = '✅' if (s.get('geserKiri') or 0) <= 12 else '❌'
        print(f'     {tanda} {s.get("id")}: "{s.get("teks")}" '
              f'geserKiri={s.get("geserKiri")}px lebar={s.get("lebar")}')
        if (s.get('geserKiri') or 0) > 12:
            gagal += 1
    print()
    print('  ── KARTU CARA ──')
    for i, k in enumerate(d.get('kartu', []), 1):
        print(f'     kartu {i}: display={k["display"]} '
              f'flexDir={k.get("flexDirection")} align={k.get("alignItems")}')
        print(f'        textAlign={k["textAlign"]} minHeight={k.get("minHeight")}')
        print(f'        tinggi={k["tinggi"]}px lebar={k["lebar"]}px')
        print(f'        radio: ada={k["radioAda"]} posisi x={k["radioX"]} '
              f'y={k["radioY"]} lebar={k["radioLebar"]}px')
        print(f'        judul tengahX={k["judulTengahX"]} '
              f'(tengah kartu={k["temaKartu"]}) → '
              f'{"TERPUSAT" if abs(k["judulTengahX"] - k["temaKartu"]) < 6 else "RATA KIRI"}')
        print('        aturan yang menyentuh display:')
        for a in k.get('aturanDisplay', []):
            print(f'           • {a}')

        # ⚠️ Radio yang DISEMBUNYIKAN (1×1px) bukan masalah — itu memang
        #    cara kami: seluruh kartu diketuk (permintaan Bos 18Sep26).
        radioTersembunyi = (k['radioLebar'] is not None
                            and k['radioLebar'] <= 2)
        if radioTersembunyi:
            print('        ✅ radio disembunyikan — seluruh kartu bisa diketuk')
        if k['display'] not in ('flex', 'block', 'grid'):
            print(f'        ❌ display tidak wajar: {k["display"]}')
            gagal += 1
        if k.get('flexDirection') == 'column':
            print('        ❌ kartu menyusun ke BAWAH (boros)')
            gagal += 1
        if abs(k['judulTengahX'] - k['temaKartu']) < 6:
            print('        ❌ teks kartu TERPUSAT (mestinya rata kiri)')
            gagal += 1
        elif not radioTersembunyi and k['radioY'] is not None \
                and k['radioY'] < k['tinggi'] * 0.25:
            print('        ⚠️ radio ada di ATAS kartu (boros)')
            gagal += 1

    print()
    if gagal:
        print(f'  ❌ {gagal} temuan perlu diperbaiki')
        return 1
    print('  ✅ semua rapi')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
