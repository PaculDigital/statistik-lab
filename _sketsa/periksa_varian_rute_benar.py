"""Uji 9 varian jalur lewat RUTE YANG BENAR: /api/buat-data/jalur.

Pelajaran (skill): jangan tebak nama rute/parameter — grep dulu, lalu CETAK
bentuk jawabannya sebelum menyimpulkan.
"""
from __future__ import annotations

import json
import subprocess
import urllib.error
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


def main() -> int:
    base = f'http://{ip()}:8000/api/buat-data/jalur'
    print(f'POST {base}\n')

    hidup, mati = [], []
    contoh_bentuk = None

    for v in VARIAN:
        payload = {'model': v, 'n': 150, 'mode': 'presisi', 'seed': 42,
                   'params': {}, 'nama': {}, 'skala': 5, 'alpha': 0.85}
        req = urllib.request.Request(
            base, data=json.dumps(payload).encode(),
            headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as f:
                body = json.loads(f.read().decode())
            kunci = sorted(body.keys())
            galat = body.get('galat_maks')
            hasil = body.get('hasil') or {}
            n_kol = len(body.get('kolom') or [])
            ada = bool(hasil) or n_kol > 0
            (hidup if ada else mati).append(v)
            print(f'  {v:22} OK  | galat_maks={galat} | kolom={n_kol} '
                  f'| kunci={kunci[:6]}')
            if contoh_bentuk is None:
                contoh_bentuk = body
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:200]
            mati.append(v)
            print(f'  {v:22} HTTP {e.code} | {detail}')
        except Exception as e:  # noqa: BLE001
            mati.append(v)
            print(f'  {v:22} GALAT {str(e)[:120]}')

    print(f'\nRINGKAS: hidup={len(hidup)}/9  mati={len(mati)}/9')
    if mati:
        print(f'  mati: {mati}')

    if contoh_bentuk:
        print('\nBENTUK JAWABAN (contoh pertama):')
        for k, v in list(contoh_bentuk.items())[:14]:
            teks = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
            print(f'  {k:16} = {teks[:110]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
