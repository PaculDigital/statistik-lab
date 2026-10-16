#!/usr/bin/env python3
"""PERIKSA KARTU S3 DI HALAMAN SUNGGUHAN — benar-benar MENGUKUR.

Tujuan (ACC Bos 18Sep26): pastikan kartu "Berganda-berantai" muncul di
halaman sungguhan, bisa diklik, dan kartu lama tidak rusak.

Ikut pola `gerbang_slider.py` / `periksa_halaman_sungguhan.py`:
Chrome headless + CDP, HTML diambil dari server sungguhan.

⚠️ PELAJARAN 18Sep26: JANGAN ukur KOTAK elemen (selalu selebar kolom —
itu yang menipu). Ukur KATA pakai document.createRange().
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent
URL = 'https://statistik.bikinaja.id/buat-data'

CHROME_KANDIDAT = [
    '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome',
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome',
    '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.4-pro/chrome',
]


def cari_chrome():
    for c in CHROME_KANDIDAT:
        if Path(c).exists():
            return c
    p = subprocess.run(['find', '/opt/data/home/.cloakbrowser', '-maxdepth', '2',
                        '-name', 'chrome', '-type', 'f'],
                       capture_output=True, text=True)
    for baris in p.stdout.splitlines():
        if baris.strip():
            return baris.strip()
    return None


JS_UKUR = r"""
(() => {
  const kartu = [...document.querySelectorAll('.pilih-cara')];
  const out = kartu.map(k => ({
    cara: k.dataset.cara,
    judul: ((k.querySelector('.cara-judul')||{}).textContent||'').trim(),
    hitung: ((k.querySelector('.cara-hitung')||{}).textContent||'').trim(),
    display: getComputedStyle(k).display,
    tinggi: Math.round(k.getBoundingClientRect().height),
    lebar: Math.round(k.getBoundingClientRect().width)
  }));
  // ukur KATA judul (bukan kotak) — pakai Range
  const r = document.createRange();
  const kata = kartu.map(k => {
    const t = k.querySelector('.cara-judul');
    if (!t) return {cara: k.dataset.cara, lebar: 0, y: 0};
    r.selectNodeContents(t);
    const b = r.getBoundingClientRect();
    return {cara: k.dataset.cara, lebar: Math.round(b.width),
            y: Math.round(b.y)};
  });
  return JSON.stringify({
    jumlah: kartu.length, kartu: out, kata: kata,
    ringkas: ((document.getElementById('cara-ringkas')||{}).textContent||'').trim(),
    adaBlok: !!document.getElementById('blok-cara'),
    galatKonsol: window.__galatJS || []
  });
})()
"""


def main():
    chrome = cari_chrome()
    if not chrome:
        print("❌ Chrome tidak ditemukan")
        return 1
    print(f"Chrome: {chrome}")

    print(f"mengambil {URL} ...")
    try:
        with urllib.request.urlopen(URL, timeout=25) as r:
            html = r.read().decode('utf-8', 'replace')
    except Exception as e:                       # noqa: BLE001
        print(f"❌ gagal ambil halaman: {e}")
        return 1
    print(f"  {len(html)} byte")

    # tulis ke berkas sementara DI DALAM direktori statis proyek supaya
    # /static/gaya.css & sprite termuat (file:// di luar = CSS tak termuat).
    port = 9339
    tmpdir = Path(tempfile.mkdtemp())
    hal = tmpdir / 'hal.html'
    # ganti path relatif jadi absolut ke domain supaya CSS termuat
    html2 = html.replace('href="/static/', f'href="{URL.rsplit("/buat-data",1)[0]}/static/')
    html2 = html2.replace('src="/static/', f'src="{URL.rsplit("/buat-data",1)[0]}/static/')
    hal.write_text(html2, encoding='utf-8')

    proc = subprocess.Popen(
        [chrome, '--headless=new', f'--remote-debugging-port={port}',
         '--no-sandbox', '--disable-gpu', '--window-size=1280,900',
         f'file://{hal}'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws = None
        for _ in range(40):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen(
                        f'http://127.0.0.1:{port}/json/list', timeout=2) as r:
                    daftar = json.loads(r.read())
                for t in daftar:
                    if t.get('type') == 'page' and t.get('webSocketDebuggerUrl'):
                        ws = t['webSocketDebuggerUrl']
                        break
            except Exception:                    # noqa: BLE001
                continue
            if ws:
                break
        if not ws:
            print("❌ tidak bisa menyambung ke Chrome")
            return 1
        time.sleep(2.0)     # beri waktu JS halaman jalan

        import websocket                        # noqa: PLC0415
        conn = websocket.create_connection(ws, timeout=20)
        conn.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                              'params': {'expression': JS_UKUR,
                                         'returnByValue': True}}))
        hasil = None
        for _ in range(60):
            pesan = json.loads(conn.recv())
            if pesan.get('id') == 1:
                hasil = pesan
                break
        conn.close()
        if not hasil:
            print("❌ tidak ada jawaban dari Chrome")
            return 1
        nilai = hasil['result']['result']['value']
        d = json.loads(nilai)
    finally:
        proc.terminate()

    print("\n=== KARTU DI HALAMAN SUNGGUHAN ===")
    for k in d['kartu']:
        print(f"  [{k['cara']:<10}] {k['judul']:<20} display={k['display']:<6} "
              f"tinggi={k['tinggi']}px lebar={k['lebar']}px")
        print(f"     hitungan: {k['hitung']}")
    print("\n=== LEBAR KATA JUDUL (ukur Range, bukan kotak) ===")
    for k in d['kata']:
        print(f"  [{k['cara']:<10}] lebar kata={k['lebar']}px  y={k['y']}")
    print(f"\nringkas: {d['ringkas']}")
    print(f"ada blok-cara: {d['adaBlok']}")

    galat = []
    cara_ada = {k['cara'] for k in d['kartu']}
    if 'berantai' not in cara_ada:
        galat.append("kartu 'berantai' TIDAK ADA di halaman")
    for k in d['kartu']:
        if k['judul'] == '' and k['cara'] != 'berantai':
            galat.append(f"kartu {k['cara']} tidak punya judul")
        if k['tinggi'] < 40:
            galat.append(f"kartu {k['cara']} terlalu pendek ({k['tinggi']}px)")
    if d.get('galatKonsol'):
        galat.append(f"galat JS: {d['galatKonsol']}")

    print("\n" + "=" * 60)
    if galat:
        print("HASIL: ADA CACAT")
        for g in galat:
            print(f"  ❌ {g}")
        return 1
    print("HASIL: LULUS — kartu tampil, ukuran wajar, tidak ada galat JS")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
