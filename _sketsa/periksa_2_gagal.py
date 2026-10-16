"""Periksa: 2 kegagalan verifikasi Tahap 2 — cacat app atau cacat uji?"""
import re
import subprocess


def baca(jalur, kode_ekstra=''):
    kode = (
        "import urllib.request\n"
        f"r=urllib.request.urlopen('http://127.0.0.1:8000{jalur}',timeout=8)\n"
        "print(r.status)\n"
        "print('__BATAS__')\n"
        "print(r.read().decode('utf-8','replace'))\n"
        + kode_ekstra
    )
    p = subprocess.run(['docker', 'exec', 'simulasi-olah-data', 'python', '-c', kode],
                       capture_output=True, text=True, timeout=40)
    return p.stdout


out = baca('/syarat')
print('════════ 1. APAKAH /syarat DIALIHKAN? ════════')
print('  (urllib OTOMATIS mengikuti pengalihan → akan tampak 200 walau asli 308)')
baris = out.split('__BATAS__')
print(f'  status yang dilihat urllib: {baris[0].strip()}')
print(f'  isi halaman memuat "Baca Grafik"? {"Baca Grafik" in (baris[1] if len(baris)>1 else "")}')
print()
print('  ➜ PERIKSA pengalihan TANPA mengikuti (class NoRedirect):')
kode2 = (
    "import urllib.request\n"
    "class T(urllib.request.HTTPRedirectHandler):\n"
    "    def redirect_request(self,*a,**k): return None\n"
    "op=urllib.request.build_opener(T)\n"
    "try:\n"
    "    r=op.open('http://127.0.0.1:8000/syarat',timeout=8)\n"
    "    print('STATUS', r.status)\n"
    "except urllib.error.HTTPError as e:\n"
    "    print('STATUS', e.code)\n"
    "    print('LOKASI', e.headers.get('Location'))\n"
)
p = subprocess.run(['docker', 'exec', 'simulasi-olah-data', 'python', '-c', kode2],
                   capture_output=True, text=True, timeout=40)
print('  ' + p.stdout.strip().replace('\n', '\n  '))

print()
print('════════ 2. APAKAH TOMBOL CONTOH ADA DI /klinik? ════════')
st, html = None, None
kode3 = (
    "import urllib.request\n"
    "h=urllib.request.urlopen('http://127.0.0.1:8000/klinik',timeout=8).read().decode('utf-8','replace')\n"
    "print(len(h))\n"
    "for k in ['Contoh sehat','Contoh bermasalah','pakaiContoh','contoh-sehat','contoh-sakit','Contoh']:\n"
    "    print(k, '->', h.count(k))\n"
)
p = subprocess.run(['docker', 'exec', 'simulasi-olah-data', 'python', '-c', kode3],
                   capture_output=True, text=True, timeout=40)
print('  ' + p.stdout.strip().replace('\n', '\n  '))
