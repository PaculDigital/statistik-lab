"""Uji BENTUK keluaran saran AI — apakah Markdown benar-benar hilang?

Latar: hasil "Panduan Wawancara" keluar `# Panduan`, `## FOKUS 1:`, `---`,
`**INTERNAL**`, `- *Contoh jawaban:*` karena system prompt lama tidak
punya aturan format sama sekali.

Uji ini memanggil RUTE HIDUP dengan 5 bentuk, lalu memeriksa:
  M. Tidak ada tanda Markdown (paling penting)
  B. Bentuk sesuai jenisnya (panduan=bernomor+kutip, koding=satu baris, dst)
"""
import json, re, sys, os
import urllib.request as u

LULUS = GAGAL = 0
def cek(nama, ok, info=''):
    global LULUS, GAGAL
    if ok:
        LULUS += 1; print('  LULUS ' + nama)
    else:
        GAGAL += 1; print('  GAGAL ' + nama + (f'  -> {info}' if info else ''))

KONTEKS = ('KONTEKS PENELITIAN (jadikan acuan utama, jangan mengarang di luar ini):\n'
           '- Judul: Makna Ulasan TikTok dalam Keputusan Pembelian Skintific '
           'di Kalangan Mahasiswa\n'
           '- Fokus penelitian: pengalaman mencari informasi, pertimbangan '
           'sebelum membeli\n'
           '- Objek/usaha: produk skincare Skintific, informan mahasiswa\n')


def panggil(prompt, bentuk):
    req = u.Request('http://127.0.0.1:8000/api/kualitatif/saran',
                    data=json.dumps({'prompt': prompt, 'bentuk': bentuk}).encode(),
                    headers={'Content-Type': 'application/json'})
    r = u.urlopen(req, timeout=240)
    return r.status, json.loads(r.read().decode())


def ada_markdown(t):
    """Cari tanda Markdown yang dilarang. Kembalian: daftar temuan."""
    temuan = []
    if re.search(r'^#{1,6}\s', t, re.M):        temuan.append('#judul')
    if '**' in t:                                temuan.append('**tebal')
    if '__' in t:                                temuan.append('__tebal')
    if re.search(r'^\s*-{3,}\s*$', t, re.M):     temuan.append('---pagar')
    if '```' in t:                               temuan.append('```blok')
    if re.search(r'^\s*[-*]\s+\S', t, re.M):     temuan.append('-bullet')
    if re.search(r'\*[^*\n]+\*', t):             temuan.append('*miring*')
    return temuan


print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK 1 — PANDUAN WAWANCARA (keluhan asli Bos)             ║')
print('╚══════════════════════════════════════════════════════════════╝')
p_panduan = (KONTEKS +
             '\nBuatkan panduan wawancara semi-terstruktur. Untuk tiap fokus '
             'penelitian beri 1 pertanyaan pembuka + 2 probing, plus contoh '
             'jawabannya. Bedakan untuk informan internal dan eksternal: untuk '
             'INTERNAL (pelaku di dalam) gali pengalaman & proses; untuk '
             'EKSTERNAL (pelanggan/pengamat luar) gali penilaian & persepsi.')
st, d = panggil(p_panduan, 'panduan')
print('HTTP', st, '| bentuk:', d.get('bentuk'))
teks = (d.get('saran') or '')
print('--- HASIL (300 char pertama) ---')
print(teks[:300])
print('...')
print()
#  Baris awal tampilkan bersih (bukan repr) supaya mata bisa menilai.
md = ada_markdown(teks)
cek('P1 tidak ada tanda Markdown', not md, f'ketemu: {md}')
cek('P2 ada kata "Panduan Wawancara"', 'Panduan Wawancara' in teks, teks[:80])
cek('P3 ada "Fokus 1"', bool(re.search(r'Fokus\s*1', teks)), 'tidak ada')
cek('P4 pertanyaan bernomor (1. / 2.)', bool(re.search(r'^\s*1[.)]\s', teks, re.M)), 'tidak bernomor')
cek('P5 pertanyaan pakai tanda kutip', '"' in teks or '“' in teks, 'tanpa kutip')
cek('P6 tanpa huruf besar semua (INTERNAL/EKSTERNAL)', 'INTERNAL' not in teks and 'EKSTERNAL' not in teks, 'masih kapital')
cek('P7 tidak menyebut "Anda"', 'Anda' not in teks, 'pakai Anda')
cek('P8 ada pendalaman (kalau/singkat/datar)', ('kalau' in teks.lower()), 'tanpa pendalaman')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK 2 — KODING                                          ║')
print('╚══════════════════════════════════════════════════════════════╝')
p_koding = (KONTEKS + '\nBerikan USULAN KODE (nama pendek, 2-4 kata) untuk tiap '
            'potongan berikut, SESUAI fokus penelitian di konteks. Format: '
            '"Potongan N: kode". Jangan menjelaskan panjang-panjang.\n'
            'Potongan 1 (I1): Pelayanan cepat dan ramah, staf responsif\n'
            'Potongan 2 (I2): Fasilitas ruang tunggu kurang memadai\n'
            'Potongan 3 (I3): Harga terjangkau tetapi porsi sedikit')
st, d = panggil(p_koding, 'koding')
teks = (d.get('saran') or '')
print('--- HASIL ---'); print(teks[:250]); print()
cek('K1 tidak ada Markdown', not ada_markdown(teks), ada_markdown(teks))
cek('K2 ada "Potongan 1:"', 'Potongan 1' in teks, teks[:80])
cek('K3 tidak huruf besar semua', bool(re.search(r'[a-z]', teks)), 'kapital semua')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK 3 — TAFSIR (paragraf mengalir)                       ║')
print('╚══════════════════════════════════════════════════════════════╝')
p_tafsir = (KONTEKS + '\nBerikan CONTOH tafsir 2-3 kalimat untuk tiap tema berikut, '
            'bahasa mahasiswa, kaitkan dengan judul penelitian:\n'
            '1. Responsivitas layanan\n2. Ketersediaan fasilitas')
st, d = panggil(p_tafsir, 'tafsir')
teks = (d.get('saran') or '')
print('--- HASIL ---'); print(teks[:280]); print()
cek('T1 tidak ada Markdown', not ada_markdown(teks), ada_markdown(teks))
cek('T2 bukan butir bernomor tiap baris', not re.search(r'^\s*\d[.)]\s', teks, re.M), 'masih bernomor')
cek('T3 tidak dibuka "Tema:"', not teks.strip().startswith('Tema:'), teks[:40])

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK 4 — SWOT FAKTOR (4+4+4+4)                            ║')
print('╚══════════════════════════════════════════════════════════════╝')
p_swot = (KONTEKS + '\nUsulkan 4 Strength, 4 Weakness, 4 Opportunity, 4 Threat '
          'yang SPESIFIK untuk objek di konteks (jangan yang generik). '
          'Format: "S: ...". Satu baris satu faktor, pendek saja.')
st, d = panggil(p_swot, 'swot_faktor')
teks = (d.get('saran') or '')
print('--- HASIL ---'); print(teks[:300]); print()
cek('S1 tidak ada Markdown', not ada_markdown(teks), ada_markdown(teks))
n_s = len(re.findall(r'^S:\s*\S', teks, re.M))
n_w = len(re.findall(r'^W:\s*\S', teks, re.M))
n_o = len(re.findall(r'^O:\s*\S', teks, re.M))
n_t = len(re.findall(r'^T:\s*\S', teks, re.M))
cek('S2 tepat 4 faktor S', n_s == 4, f'S={n_s}')
cek('S3 tepat 4 faktor W', n_w == 4, f'W={n_w}')
cek('S4 tepat 4 faktor O', n_o == 4, f'O={n_o}')
cek('S5 tepat 4 faktor T', n_t == 4, f'T={n_t}')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK 5 — SWOT STRATEGI (SO/WO/ST/WT)                      ║')
print('╚══════════════════════════════════════════════════════════════╝')
p_strat = (KONTEKS + '\nBerdasarkan faktor SWOT berikut, usulkan SATU strategi untuk '
           'tiap pasangan SO, WO, ST, WT (satu kalimat tiap strategi, spesifik '
           'untuk objek di konteks).\nS: review TikTok relevan\nW: stok sering kosong\n'
           'O: tren skincare lokal\nT: kompetitor harga murah')
st, d = panggil(p_strat, 'swot_strategi')
teks = (d.get('saran') or '')
print('--- HASIL ---'); print(teks[:280]); print()
cek('G1 tidak ada Markdown', not ada_markdown(teks), ada_markdown(teks))
for k in ('SO', 'WO', 'ST', 'WT'):
    cek(f'G2 ada strategi {k}', bool(re.search(rf'^{k}\s*:', teks, re.M)), 'tidak ada')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  BENTUK KOSONG — tetap dilarang Markdown                     ║')
print('╚══════════════════════════════════════════════════════════════╝')
st, d = panggil('Sebutkan 3 hal yang perlu disiapkan sebelum wawancara.', '')
teks = (d.get('saran') or '')
print(teks[:200]); print()
cek('X1 tanpa bentuk pun tidak ada Markdown', not ada_markdown(teks), ada_markdown(teks))

print()
print(f'RINGKAS: {LULUS} LULUS / {GAGAL} GAGAL')
sys.exit(1 if GAGAL else 0)
