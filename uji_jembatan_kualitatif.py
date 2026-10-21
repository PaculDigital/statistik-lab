# Uji pintu kualitatif jembatan (Fase 4) — AI diganti boneka deterministik.
import os, sys
os.environ['JEMBATAN_KUNCI_LAYANAN'] = 'kunci-uji'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.jembatan import buat_router, hitung_triangulasi, hitung_swot
gagal = []
def cek(nama, kondisi, info=''):
    print(('  ✓ ' if kondisi else '  ✗ GAGAL ') + nama + ((' — ' + str(info)[:130]) if (info and not kondisi) else ''))
    if not kondisi: gagal.append(nama)

def ai_boneka(prompt):
    return ('Berikut usulan: [{"indeks": 0, "kode": "pelayanan lambat", "tema": "Mutu Layanan"},'
            ' {"indeks": 1, "kode": "antrean panjang", "tema": "Mutu Layanan"},'
            ' {"indeks": 2, "kode": "harga naik", "tema": "Tekanan Harga"}] selesai.')
app = FastAPI(); app.include_router(buat_router(lambda b, p: b, lambda h, p: h, ai_boneka))
k = TestClient(app); H = {'X-Kunci-Layanan': 'kunci-uji'}

print('── hitung_triangulasi (port logika peramban) ──')
seg = [
    {'teks': 'pelayanannya lambat', 'informan': 'A', 'teknik': 'wawancara', 'jenis': 'eksternal', 'kode': 'pelayanan lambat', 'tema': 'Mutu Layanan'},
    {'teks': 'antre lama sekali', 'informan': 'B', 'teknik': 'observasi', 'jenis': 'eksternal', 'kode': 'antrean panjang', 'tema': 'Mutu Layanan'},
    {'teks': 'memang kami kekurangan staf', 'informan': 'C', 'teknik': 'wawancara', 'jenis': 'internal', 'kode': 'staf kurang', 'tema': 'Mutu Layanan'},
    {'teks': 'harga naik terus', 'informan': 'A', 'teknik': 'wawancara', 'jenis': 'eksternal', 'kode': 'harga naik', 'tema': 'Tekanan Harga'},
    {'teks': 'tanpa kode', 'informan': 'A', 'teknik': 'wawancara', 'jenis': 'eksternal', 'kode': '', 'tema': ''},
]
tri = hitung_triangulasi(seg)
ml = [x for x in tri['tema'] if x['tema'] == 'Mutu Layanan'][0]
cek('segmen tanpa kode/tema tersisih (4 dari 5)', tri['jumlah_segmen'] == 4)
cek('Mutu Layanan: 3 informan -> kuat', ml['kuat'] is True and ml['jumlah_informan'] == 3)
cek('Mutu Layanan: internal+eksternal -> tertriangulasi', ml['tertriangulasi'] is True)
cek('matriks per informan benar', ml['per_informan'] == {'A': 1, 'B': 1, 'C': 1}, ml['per_informan'])
cek('Tekanan Harga: 1 informan 1 teknik -> perlu diperkuat', [x for x in tri['tema'] if x['tema'] == 'Tekanan Harga'][0]['kuat'] is False)
cek('contoh kutipan = segmen pertama tema', ml['contoh_kutipan']['teks'] == 'pelayanannya lambat')

print('── hitung_swot (port tabelSkor) ──')
fak = [{'kelompok': 'S', 'teks': 'rasa enak', 'bobot': 0.6, 'rating': 4},
       {'kelompok': 'W', 'teks': 'tempat sempit', 'bobot': 0.4, 'rating': 2},
       {'kelompok': 'O', 'teks': 'ojek online', 'bobot': 0.5, 'rating': 3},
       {'kelompok': 'T', 'teks': 'saingan baru', 'bobot': 0.5, 'rating': 2}]
sw = hitung_swot(fak)
cek('IFAS = 0.6*4+0.4*2 = 3.20', sw['ifas']['total_skor'] == 3.2, sw['ifas'])
cek('EFAS = 0.5*3+0.5*2 = 2.50', sw['efas']['total_skor'] == 2.5)
cek('bobot pas satu kedua grup', sw['ifas']['bobot_pas_satu'] and sw['efas']['bobot_pas_satu'])
cek('kuadran: x=+0.70 y=0.00 -> I agresif', sw['kuadran']['kode'] == 'I', sw['kuadran'])
sw2 = hitung_swot([{'kelompok': 'S', 'teks': 'a', 'bobot': 1, 'rating': 1},
                    {'kelompok': 'O', 'teks': 'b', 'bobot': 1, 'rating': 4}])
cek('kuadran II (dalam lemah, luar kuat)', sw2['kuadran']['kode'] == 'II', sw2['kuadran'])
cek('angka rusak -> 0 bukan 500', hitung_swot([{'kelompok': 'S', 'teks': 'x', 'bobot': 'abc', 'rating': None}])['ifas']['total_skor'] == 0)

print('── Rute ──')
r = k.post('/api/jembatan/kualitatif/koding', json={'fokus': 'mutu layanan', 'catatan': [
    {'informan': 'A', 'teks': 'pelayanannya lambat'}, {'informan': 'B', 'teks': 'antre lama'},
    {'informan': 'C', 'teks': 'harga naik'}]}, headers=H)
cek('koding 200 + usulan sejajar catatan', r.status_code == 200 and r.json()['usulan'][0]['kode_usulan'] == 'pelayanan lambat', r.text[:150])
cek('koding tanpa kunci -> 401', k.post('/api/jembatan/kualitatif/koding', json={'catatan': [{'teks': 'x'}]}).status_code == 401)
cek('koding catatan kosong -> 400', k.post('/api/jembatan/kualitatif/koding', json={'catatan': []}, headers=H).status_code == 400)
r = k.post('/api/jembatan/kualitatif/matriks', json={'jenis': 'tematik', 'segmen': seg}, headers=H)
cek('matriks tematik 200', r.status_code == 200 and r.json()['triangulasi']['jumlah_segmen'] == 4)
r = k.post('/api/jembatan/kualitatif/matriks', json={'jenis': 'swot', 'faktor': fak}, headers=H)
cek('matriks swot 200 + kuadran I', r.status_code == 200 and r.json()['swot']['kuadran']['kode'] == 'I')
cek('matriks jenis aneh -> 400', k.post('/api/jembatan/kualitatif/matriks', json={'jenis': 'aneh'}, headers=H).status_code == 400)
print()
print('❌ GAGAL: ' + ', '.join(gagal) if gagal else '✅ SEMUA LULUS — jembatan kualitatif Fase 4')
sys.exit(1 if gagal else 0)
