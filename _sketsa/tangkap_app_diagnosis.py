#!/usr/bin/env python3
"""Render HASIL app /diagnosis — pakai Tab PROVEN dari uji_jalur_tampilan.py
(bukan class baru, bukan websockets). Buka app, unggah contoh, isi kolom,
klik periksa, tangkap hasil.

⚠️ Aturan Bos 19Sep26: JANGAN buat script baru — pakai yang SUDAH ADA.
   Wulan TIDAK membuat class sendiri; Wulan IMPOR `Tab` dari uji_jalur_tampilan.
   Alur ini BUKAN class baru, hanya penggunaan alat (Tab) yang ada + navigasi.

App berjalan di 127.0.0.1:8135 (sudah dinyalakan). CDP di 9333 (Tab proven
memakai 9333 — lihat uji_jalur_tampilan.py CDP='http://127.0.0.1:9333').
"""
import base64
import json
import os
import sys
import time
import urllib.request
from urllib.error import HTTPError

sys.path.insert(0, '/opt/data/services/statistik-lab')
from uji_jalur_tampilan import Tab  # noqa: E402  — PROVEN, sudah ada

CDP = 'http://127.0.0.1:9333'
APP = 'http://127.0.0.1:8135'


def post_file(url, nama, isi, tipe='text/csv'):
    batas = '----WulanTipis'
    b = (f'--{batas}\r\n'
         f'Content-Disposition: form-data; name="berkas"; filename="{nama}"\r\n'
         f'Content-Type: {tipe}\r\n\r\n').encode() + isi + f'\r\n--{batas}--\r\n'.encode()
    r = urllib.request.Request(url, data=b,
                               headers={'Content-Type': f'multipart/form-data; boundary={batas}'})
    try:
        with urllib.request.urlopen(r, timeout=25) as f:
            return json.loads(f.read())
    except HTTPError as e:
        return {'galat': e.read().decode()[:200]}


def ev(t, expr):
    """Runtime.evaluate + ambil value (pola proven dari uji_jalur_tampilan)."""
    r = t.kirim('Runtime.evaluate', {'expression': expr, 'returnByValue': True})
    return (r.get('result') or {}).get('result', {}).get('value')


def tangkap(t, path):
    """Screenshot — pola proven: captureBeyondViewport OFF (gagal halaman tinggi)."""
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': True})
    time.sleep(0.6)
    s = t.kirim('Page.captureScreenshot', {'format': 'png'})
    data = (s.get('result') or {}).get('data')
    if not data:
        print(f'  GAGAL tangkap: {str(s)[:150]}')
        return False
    with open(path, 'wb') as f:
        f.write(base64.b64decode(data))
    print(f'  OK {path} ({os.path.getsize(path)//1024} KB)')
    return True


def utama() -> int:
    # 0. unggah data contoh lewat API (sungguhan)
    data_csv = ('Harga,Promosi,Kepuasan\n' +
                '\n'.join(f'{round(1+((i*7)%5),2)},{round(1+((i*3)%5),2)},'
                          f'{round(1+((i*11)%5)+0.2,2)}' for i in range(1, 41)))
    d = post_file(APP + '/api/diagnosis/unggah', 'contoh.csv', data_csv.encode())
    if 'galat' in d or 'kunci' not in d:
        print('UNGGAH GAGAL:', d); return 1
    print(f"unggah OK: kunci={d['kunci'][:8]}… n={d['n_baris']}")

    # 1. buka tab page yang ada + navigasi ke /diagnosis
    with urllib.request.urlopen(f'{CDP}/json/list', timeout=10) as r:
        daftar = json.load(r)
    hal = [x for x in daftar if x.get('type') == 'page']
    if not hal:
        print('tidak ada tab'); return 1
    t = Tab(hal[0]['webSocketDebuggerUrl'])
    t.kirim('Page.enable'); t.kirim('Runtime.enable')
    t.kirim('Emulation.setDeviceMetricsOverride',
            {'width': 390, 'height': 900, 'deviceScaleFactor': 1, 'mobile': True})
    t.kirim('Page.navigate', {'url': APP + '/diagnosis'})
    time.sleep(2.5)

    print('path:', ev(t, 'location.pathname'), '| judul:', ev(t, 'document.title'))

    # 2. isi state JS (KUNCI + KOLOM) + buka panel kolom
    t.kirim('Runtime.evaluate', {'expression':
        f'KUNCI={json.dumps(d["kunci"])}; KOLOM={json.dumps(d["kolom"])}; nX=0;'})
    ev(t, """(() => {
      document.getElementById('ringkas-berkas').hidden = false;
      document.getElementById('kartu-kolom').hidden = false;
      document.getElementById('baris-x').innerHTML = '';
      tambahX(); tambahX();
      const s = document.querySelectorAll('#baris-x .pilih-kolom');
      if (s[0]) s[0].value = 'Harga';
      if (s[1]) s[1].value = 'Promosi';
      document.getElementById('kolom-y').value = 'Kepuasan';
      return 'ok';
    })()""")
    time.sleep(0.5)
    tangkap(t, '/tmp/diag_app_kolom.png')

    # 3. klik periksa + tunggu hasil
    ev(t, 'periksa();')
    tampil = False
    for _ in range(40):
        v = ev(t, "document.getElementById('kartu-hasil').hidden === false")
        if v is True:
            tampil = True
            break
        time.sleep(0.4)
    print('kartu hasil tampil?', tampil)
    if tampil:
        teks = ev(t, "document.getElementById('kartu-hasil').innerText.slice(0,500)")
        print('--- teks hasil ---'); print(teks)
        tangkap(t, '/tmp/diag_app_hasil.png')
    else:
        # tangkap pesan / error untuk dipahami
        pesan = ev(t,
            "document.getElementById('pesan-periksa') "
            "? document.getElementById('pesan-periksa').innerText : '(no-el)'")
        print('pesan-periksa:', pesan)

    try:
        t.s.close()
    except Exception:
        pass
    return 0 if tampil else 1


if __name__ == '__main__':
    sys.exit(utama())
