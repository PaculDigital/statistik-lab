"""Uji MEJA KERJA kualitatif (branch meja-kerja-baru) — cari bug nyata.

Fokus: alur baru "AI per kartu kutipan" memakai fungsi BARU `mintaTeksAI`
yang TIDAK memakai jalur `saranAI` yang sudah diperbaiki.

Yang diperiksa:
  B. Bug: mintaTeksAI tidak menangani balasan HTML (Cloudflare 502) ->
     pesan galat jadi "HTTP 502" polos, persis keluhan Bos sebelumnya.
  C. Bug: mintaTeksAI tidak mengirim `bentuk` -> system prompt tidak
     dapat susunan wajib, AI bebas menulis Markdown/penjelasan.
  D. Robust: format KODE:/TEMA: benar-benar terbaca?
  E. Robust: AI menulis Markdown (tebal/tanda kutip) -> masih terbaca?
"""
import json, re, sys
import urllib.request as u

LULUS = GAGAL = 0
def cek(nama, ok, info=''):
    global LULUS, GAGAL
    if ok: LULUS += 1; print('  LULUS ' + nama)
    else: GAGAL += 1; print('  GAGAL ' + nama + (f'  -> {info}' if info else ''))

BASE = 'http://127.0.0.1:8000'
KONTEKS = ('KONTEKS PENELITIAN (jadikan acuan utama, jangan mengarang di luar ini):\n'
           '- Judul: Makna Ulasan TikTok dalam Keputusan Pembelian Skintific '
           'di Kalangan Mahasiswa\n'
           '- Fokus penelitian: pengalaman mencari informasi, pertimbangan '
           'sebelum membeli\n'
           '- Objek/usaha: produk skincare Skintific, informan mahasiswa\n')

#  Prompt PERSIS seperti bantuKodeAI() menyusunnya.
def prompt_kartu(teks_kutipan, informan, temas=None):
    temas = temas or ['Sumber informasi', 'Keraguan awal']
    return (KONTEKS +
            '\nKamu membantu mahasiswa memberi KODE dan TEMA pada SATU kutipan '
            'hasil wawancara. Kode = nama pendek 2-4 kata. Tema = kelompok yang '
            'lebih besar dari kode.'
            '\nTema yang SUDAH dipakai di penelitian ini: ' + ', '.join(temas) +
            '. Pakai salah satu tema itu bila cocok, jangan membuat tema baru '
            'yang mirip.'
            '\n\nKutipan dari ' + informan + ':\n"' + teks_kutipan + '"'
            '\n\nBalas PERSIS dalam format 2 baris ini, tanpa penjelasan lain:\n'
            'KODE: <kode usulan>\nTEMA: <tema usulan>')


def panggil(prompt, bentuk=None):
    d = {'prompt': prompt}
    if bentuk is not None:
        d['bentuk'] = bentuk
    req = u.Request(BASE + '/api/kualitatif/saran',
                    data=json.dumps(d).encode(),
                    headers={'Content-Type': 'application/json'})
    r = u.urlopen(req, timeout=240)
    return r.status, json.loads(r.read().decode())


print('╔══════════════════════════════════════════════════════════════╗')
print('║  B. GALAT HTML (Cloudflare 502) — dibaca sebagai SEBAB?      ║')
print('╚══════════════════════════════════════════════════════════════╝')
layar = open('/app/app/templates/kualitatif.html').read()
#  Tiru logika mintaTeksAI persis: r.json() dulu, tanpa cek content-type.
minta = layar[layar.find('async function mintaTeksAI'):]
minta = minta[:minta.find('\nasync function bantuKodeAI')]
#  ⚠️ JEBAKAN (kena 21Okt26): jangan cari kata 'content-type' — itu ADA
#  di header PERMINTAAN, bukan pemeriksaan BALASAN. Yang benar: cari
#  pembacaan header BALASAN (r.headers.get).
cek('B1 mintaTeksAI memeriksa jenis BALASAN (bukan header kiriman)',
    "r.headers.get('content-type')" in minta,
    'masih r.json() buta')
cek('B2 ada cadangan r.text() saat balasan bukan JSON',
    'r.text()' in minta, 'tidak ada cadangan')
cek('B3 ada kalimat sebab khusus 502/503/504',
    ("r.status === 502" in minta and "r.status === 504" in minta),
    'tidak ada sebab khusus')
cek('B4 TIDAK lagi memakai sebab polos',
    "d.sebab || ('HTTP ' + r.status)" not in minta,
    'masih polos')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  C. BENTUK tidak dikirim — AI bebas Markdown?                ║')
print('╚══════════════════════════════════════════════════════════════╝')
cek('C1 mintaTeksAI mengirim bentuk ke server',
    "bentuk: bentuk || ''" in minta, 'masih tidak mengirim')
cek('C2 bantuKodeAI memakai bentuk kartu',
    "'kartu'" in layar, "bentuk 'kartu' tidak dipakai")

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  D. FORMAT KODE:/TEMA: benar-benar terbaca?                  ║')
print('╚══════════════════════════════════════════════════════════════╝')
p = prompt_kartu('Awalnya ragu sih, takut nggak cocok di kulit saya.',
                 'Informan 1')
st, d = panggil(p, 'kartu')
teks = (d.get('saran') or '')
print('--- balasan AI ---')
print(teks[:300])
print()
mk = re.search(r'KODE\s*:\s*(.+)', teks, re.I)
mt = re.search(r'TEMA\s*:\s*(.+)', teks, re.I)
cek('D1 ada baris KODE:', bool(mk), teks[:100])
cek('D2 ada baris TEMA:', bool(mt), teks[:100])
if mk: print('     kode =', repr(mk.group(1).strip()[:40]))
if mt: print('     tema =', repr(mt.group(1).strip()[:40]))
#  Apakah kode masuk akal (2-4 kata)?
if mk:
    kode = mk.group(1).strip()
    cek('D3 kode 2-4 kata', 1 <= len(kode.split()) <= 5, f'{len(kode.split())} kata: {kode}')
#  Apakah tema memakai tema yang sudah ada?
if mt:
    tema = mt.group(1).strip()
    cek('D4 tema memakai tema yang sudah ada',
        any(t.lower() in tema.lower() or tema.lower() in t.lower()
            for t in ['Sumber informasi', 'Keraguan awal']),
        f'tema baru: {tema}')
#  Apakah ada Markdown nyasar?
cek('D5 tanpa Markdown', not re.search(r'^#{1,6}\s|\*\*', teks, re.M), 'ADA Markdown')
cek('D6 tepat 2 baris (tanpa pengantar/penutup)',
    len([x for x in teks.strip().splitlines() if x.strip()]) == 2,
    f'{len([x for x in teks.strip().splitlines() if x.strip()])} baris')

print()
print('╔══════════════════════════════════════════════════════════════╗')
print('║  E. AI menulis Markdown — parser masih terbaca?              ║')
print('╚══════════════════════════════════════════════════════════════╝')
#  Tiru parser bantuKodeAI pada masukan yang SUDAH dibungkus model.
for contoh in [
    'KODE: keraguan kulit sensitif\nTEMA: Keraguan awal',
    '**KODE:** keraguan kulit sensitif\n**TEMA:** Keraguan awal',
    'KODE: "keraguan kulit sensitif"\nTEMA: "Keraguan awal"',
    'Berikut analisisnya:\nKODE: keraguan kulit sensitif\nTEMA: Keraguan awal\n\nSemoga membantu.',
]:
    mk2 = re.search(r'KODE\s*:\s*(.+)', contoh, re.I)
    mt2 = re.search(r'TEMA\s*:\s*(.+)', contoh, re.I)
    kode = mk2.group(1).strip().replace('*', '') if mk2 else None
    cek(f'E terbaca: {contoh[:38]!r}', bool(kode), 'GAGAL baca')

print()
print(f'RINGKAS: {LULUS} LULUS / {GAGAL} GAGAL')
sys.exit(1 if GAGAL else 0)
