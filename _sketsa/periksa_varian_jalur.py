"""Periksa: apakah 9 varian jalur BENAR-BENAR berfungsi atau masih 'segera'?

Ukur halaman SUNGGUHAN + coba hitung lewat API. Bukan grep berkas.
Nilai LULUS/GAGAL dari EXIT CODE.
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request

VARIAN = [
    'mediasi-paralel', 'mediasi-berjenjang', 'moderasi-jalur-a',
    'moderasi-jalur-b', 'moderasi-keduanya', 'moderasi-dual',
    'moderasi-3jalur', 'mediasi-campuran', 'gabungan',
]


def ip() -> str:
    r = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
         'simulasi-olah-data'], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=40) as f:
            return f.status, f.read().decode('utf-8', 'replace')
    except Exception as e:  # noqa: BLE001
        return 0, f'GALAT {e}'


def main() -> int:
    base = f'http://{ip()}:8000'
    print(f'BASE = {base}\n')

    print('═══ A. APAKAH /buat-data?model=<varian> MENAMPILKAN FORM? ═══')
    hasil = {}
    for v in VARIAN:
        kode, html = get(f'{base}/buat-data?model={v}')
        segera = 'sedang disiapkan' in html or 'Modul belum' in html
        # tanda form hidup: ada tombol Bangun / slider beta / panel model
        ada_form = ('Bangun' in html or 'beta' in html.lower()) and not segera
        di_alihkan = 'kuantitatif' in html and 'kartu-pilih' in html
        hasil[v] = {'kode': kode, 'segera': segera, 'form': ada_form,
                    'alih': di_alihkan}
        print(f'  {v:22} HTTP {kode} | segera={segera} | form={ada_form} '
              f'| dialihkan={di_alihkan}')

    print('\n═══ B. APAKAH API /api/buat-data MENERIMA VARIAN ITU? ═══')
    for v in VARIAN:
        payload = {
            'model': v.replace('-', '_'),
            'n_resp': 100,
            'seed': 42,
            'beta': {'X1': 0.35},
        }
        req = urllib.request.Request(
            f'{base}/api/buat-data',
            data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=60) as f:
                body = json.loads(f.read().decode())
            ok = bool(body.get('kolom') or body.get('data') or body.get('hasil'))
            kunci = ','.join(list(body.keys())[:6])
            print(f'  {v:22} HTTP 200 | ada_data={ok} | kunci=[{kunci}]')
        except Exception as e:  # noqa: BLE001
            pesan = str(e)[:90]
            print(f'  {v:22} DITOLAK/GALAT: {pesan}')

    print('\n═══ C. RINGKAS HALAMAN ═══')
    hidup = [v for v, d in hasil.items() if d['form'] and not d['segera']]
    mati = [v for v, d in hasil.items() if d['segera']]
    alih = [v for v, d in hasil.items() if d['alih']]
    print(f'  form hidup  ({len(hidup)}): {hidup}')
    print(f'  "segera"    ({len(mati)}): {mati}')
    print(f'  dialihkan   ({len(alih)}): {alih}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
