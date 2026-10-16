"""UKUR: berkas uji yang TIDAK masuk gerbang — masih jalan atau sudah rusak?

Kenapa ini perlu: `uji_tombol_contoh.py` ternyata SUDAH GAGAL berhari-hari
tapi tidak ketahuan karena TIDAK masuk gerbang. Uji yang tidak dijalankan
siapa pun = uji mati (atau jebakan). Sebelum memutuskan mau diapakan,
UKUR DULU: jalan / lewat-prasarana / rusak.

Dijalankan satu per satu dengan batas waktu, TANPA mengubah apa pun.
"""
import subprocess
import sys
from pathlib import Path

AKAR = Path(__file__).resolve().parent.parent
PY = str(AKAR / '.venv' / 'bin' / 'python')
BATAS = 120          # detik per berkas

# Yang TIDAK dipakai skrip lain (dipakai-oleh = 0) DAN tidak masuk gerbang
KANDIDAT = [
    'uji_bar_model.py', 'uji_belajar_hp.py', 'uji_efek_tidak_langsung.py',
    'uji_final.py', 'uji_halaman.py', 'uji_jalur_model.py',
    'uji_kalibrasi.py', 'uji_kartu_ujit.py', 'uji_klinik_lapangan.py',
    'uji_mesin.py', 'uji_mesin_s3.py', 'uji_mesin_s3_kalibrasi.py',
    'uji_mockup_konfirmasi.py', 'uji_model.py', 'uji_pita_tab.py',
    'uji_resep3.py', 'uji_setel.py', 'uji_spss_sav.py', 'uji_struktural.py',
    'uji_tuntas_kemampuan.py', 'uji_v3.py', 'uji_web_data.py',
    'uji_web_s3.py',
]

hasil = []
for nama in KANDIDAT:
    f = AKAR / nama
    if not f.exists():
        hasil.append((nama, 'HILANG', ''))
        continue
    try:
        p = subprocess.run([PY, str(f)], cwd=str(AKAR), timeout=BATAS,
                           capture_output=True, text=True)
        keluaran = (p.stdout or '') + (p.stderr or '')
        baris = [b for b in keluaran.splitlines()
                 if 'LULUS' in b.upper() or 'GAGAL' in b.upper()]
        ringkas = baris[-1].strip()[:58] if baris else ''
        if p.returncode == 0:
            status = 'JALAN'
        elif p.returncode == 77:
            status = 'LEWAT'
        else:
            status = f'RUSAK({p.returncode})'
        hasil.append((nama, status, ringkas))
    except subprocess.TimeoutExpired:
        hasil.append((nama, 'TIMEOUT', f'>{BATAS} dtk'))
    except Exception as e:                                    # noqa: BLE001
        hasil.append((nama, 'GALAT', str(e)[:50]))

print('=' * 78)
print(' UKUR: berkas uji yang TIDAK MASUK GERBANG')
print('=' * 78)
print(f'{"berkas":<32} {"status":<12} ringkas')
print('-' * 78)
for nama, status, ringkas in hasil:
    print(f'{nama:<32} {status:<12} {ringkas}')

print('\n' + '=' * 78)
print(' RINGKASAN')
print('=' * 78)
for status in ('JALAN', 'LEWAT', 'TIMEOUT'):
    n = sum(1 for _, s, _ in hasil if s == status)
    if n:
        print(f'  {status:<10} {n}')
rusak = [(n, r) for n, s, r in hasil if s.startswith('RUSAK') or s == 'GALAT']
print(f'  RUSAK      {len(rusak)}')
for n, r in rusak:
    print(f'      · {n}  →  {r}')

sys.exit(0)
