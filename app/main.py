"""
Penelitian STATISTIK Lab. — kerangka aplikasi web.

Modul (kerangka, dibangun bertahap):
  📚 BELAJAR   — kamus istilah berslider
  🧪 BUAT DATA — simulator data penelitian
  🩺 DIAGNOSIS DATA — (dulu KLINIK) unggah data SPSS/PLS
  🎓 UJIAN     — (Fase 4)
  🧭 PEMILIH   — (Fase 5)
  ⚙️ PENGATURAN

Aturan induk:
  - Hitungan statistik LOKAL (numpy/scipy) — TANPA AI, gratis, instan.
  - AI hanya untuk interpretasi/soal, WAJIB ada tombol ON/OFF.
  - Jangan tempel teks server ke innerHTML — pakai aman().
"""
from __future__ import annotations

import os
import json
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup

BASE = Path(__file__).resolve().parent
STATIC = BASE / 'static'
_VERSI_ASET = '0'

app = FastAPI(title='Penelitian STATISTIK Lab.', docs_url=None, redoc_url=None)
app.mount('/static', StaticFiles(directory=str(STATIC)), name='static')

templates = Jinja2Templates(directory=str(BASE / 'templates'))


# ═══════════════════════════════════════════════════════════════════════════
# MAKRO IKON LUCIDE (nama divalidasi — cegah penyisipan markup)
# ═══════════════════════════════════════════════════════════════════════════
def _ikon(nama: str, ukuran: int = 16, kelas: str = '') -> Markup:
    import re
    if not re.fullmatch(r'[a-z0-9-]{1,40}', nama or ''):
        return Markup('')
    kls = ('ik ' + kelas).strip()
    return Markup(
        '<svg class="%s" width="%d" height="%d" aria-hidden="true">'
        '<use href="#ik-%s"></use></svg>' % (kls, int(ukuran), int(ukuran), nama))


def _ikon_sprite() -> Markup:
    p = STATIC / 'ikon' / 'lucide.svg'
    try:
        return Markup(p.read_text(encoding='utf-8'))
    except OSError:
        return Markup('')


templates.env.globals['ikon'] = _ikon
templates.env.globals['ikon_sprite'] = _ikon_sprite

# ── Status AI (tombol ON/OFF) — disimpan di berkas kecil, tanpa DB ───────
STATUS_AI = BASE.parent / 'data' / 'ai_aktif.txt'


def ai_aktif() -> bool:
    try:
        return STATUS_AI.read_text(encoding='utf-8').strip() == '1'
    except OSError:
        return False


def set_ai(nilai: bool) -> bool:
    STATUS_AI.parent.mkdir(parents=True, exist_ok=True)
    STATUS_AI.write_text('1' if nilai else '0', encoding='utf-8')
    return nilai


templates.env.globals['ai_aktif'] = ai_aktif


# ═══════════════════════════════════════════════════════════════════════════
# ROUTE
# ═══════════════════════════════════════════════════════════════════════════
MODUL = [
    {'slug': 'mulai', 'nama': 'MULAI', 'ikon': 'play',
     'warna': '#2E7D6F', 'siap': True,
     'ringkas': 'Pilih jenis penelitianmu dulu — jalurnya bercabang dari sini.'},
    {'slug': 'belajar', 'nama': 'BELAJAR', 'ikon': 'book-open',
     'warna': '#2E7D6F', 'siap': True,
     'ringkas': 'Kamus istilah statistik dengan slider — pahami lewat gambar, bukan hafalan.'},
    {'slug': 'buat-data', 'nama': 'BUAT DATA', 'ikon': 'flask-conical',
     'warna': '#B5762A', 'siap': True,
     'ringkas': 'Rancang datamu, lihat hasilnya sebelum diolah di SPSS atau SmartPLS.'},
    {'slug': 'klinik', 'nama': 'DIAGNOSIS DATA', 'ikon': 'microscope',
     'warna': '#A85A5A', 'siap': True,
     'ringkas': 'Unggah data SPSS/SmartPLS (.sav/.csv/.xlsx) — kami periksa '
                'mana yang sudah benar dan mana yang perlu dibetulkan.'},
    {'slug': 'ujian', 'nama': 'UJIAN', 'ikon': 'graduation-cap',
     'warna': '#5A6FA8', 'siap': False,
     'ringkas': 'Latihan soal statistik, individual atau kelompok.'},
    {'slug': 'pemilih', 'nama': 'PEMILIH ALAT', 'ikon': 'compass',
     'warna': '#7A5AA8', 'siap': False,
     'ringkas': 'Bingung mau pakai SPSS atau SmartPLS? Jawab beberapa pertanyaan, dapat rekomendasi.'},
    {'slug': 'pengaturan', 'nama': 'PENGATURAN', 'ikon': 'settings',
     'warna': '#5F6B70', 'siap': True,
     'ringkas': 'Atur saklar AI, tampilan, dan pilihan unduhan data penelitianmu.'},
    {'slug': 'kualitatif', 'nama': 'KUALITATIF', 'ikon': 'file-text',
     'warna': '#7A5AA8', 'siap': True,
     'ringkas': 'Penelitian kata & cerita — panduan wawancara, koding, '
                'triangulasi, sampai SWOT.'},
]


def _konteks(request: Request, aktif: str, judul: str) -> dict:
    # ⚠️ CAP VERSI ASET (akar, 18Sep26) — lihat penjelasan di dasar.html.
    # Diambil dari CAP WAKTU BERKAS CSS, jadi tidak mungkin basi: begitu
    # berkas berubah, versinya otomatis berubah dan cache dianggap baru.
    global _VERSI_ASET
    try:
        cap = (STATIC / 'gaya.css').stat().st_mtime
    except OSError:
        cap = 0
    _VERSI_ASET = str(int(cap))
    # META DESCRIPTION (Wulan, 20Okt26): ambil 'ringkas' modul yang sedang
    # dibuka, supaya deskripsi halaman benar-benar menjelaskan isinya —
    # bukan kalimat baku yang sama di semua halaman. Halaman yang tidak
    # punya modul (beranda, /kuantitatif) → None → template pakai baku.
    ringkas = next((m.get('ringkas') for m in MODUL if m['slug'] == aktif), None)
    return {'request': request, 'aktif': aktif, 'judul': judul, 'modul': MODUL,
            'ai': ai_aktif(), 'versi_aset': _VERSI_ASET, 'ringkas': ringkas}


@app.get('/', response_class=HTMLResponse)
async def beranda(request: Request):
    return templates.TemplateResponse(request, 'beranda.html',
                                      _konteks(request, 'beranda', 'Beranda'))


@app.get('/belajar', response_class=HTMLResponse)
async def belajar(request: Request):
    return templates.TemplateResponse(request, 'belajar.html',
                                      _konteks(request, 'belajar', 'BELAJAR'))


# ── TAHAP 1: pilih JENIS penelitian (ACC Bos 18Sep26) ────────────────────
# MENGAPA ADA: /buat-data dulu langsung meminta angka β → bagi orang awam
# itu seperti mengisi formulir pajak (dia belum tahu mau model apa).
# Halaman ini cuma mengarahkan; TIDAK ada perhitungan di sini.
@app.get('/mulai', response_class=HTMLResponse)
async def mulai(request: Request):
    return templates.TemplateResponse(request, 'mulai.html',
                                      _konteks(request, 'mulai', 'Mulai'))


# ── TAHAP 2: pilih MODEL kuantitatif (ACC Bos 18Sep26) ───────────────────
# Kartu bergambar + bahasa TUJUAN penelitian (bukan nama teknik), supaya
# orang awam paham tanpa harus tahu istilah "mediasi"/"moderasi" dulu.
@app.get('/kuantitatif', response_class=HTMLResponse)
async def kuantitatif(request: Request):
    return templates.TemplateResponse(request, 'kuantitatif.html',
                                      _konteks(request, 'kuantitatif', 'Kuantitatif'))


# ── PERIKSA SYARAT: grafik uji asumsi (ACC Bos 18Sep26, pilihan A) ───────
# MENGAPA ADA: di SPSS grafik ini tersembunyi di Analyze → Regression →
# Plots; mahasiswa sering lupa / tidak tahu cara membacanya. Halaman ini
# memberi gambar + TAFSIR + cara mengeceknya sendiri. Bos minta keterangan
# didetailkan (ACC #3), dan minta tampil DUA-DUANYA (SPSS + khas PLS).
@app.get('/syarat')
async def syarat():
    """DIALIHKAN ke tab "Baca Grafik" di BELAJAR (ACC Bos 19Sep26 langkah 3A).

    ⚠️ MENGAPA DIALIHKAN, BUKAN DIHAPUS (20Sep26):
      (a) 7 kartu bacaannya sudah PINDAH ke BELAJAR tab ke-3 "Baca Grafik" —
          halaman ini jadi isi kembar;
      (b) BANYAK tautan lama menuju ke sini: /belajar, /kuantitatif, /segera,
          dan bookmark mahasiswa. Menghapus rutenya = tautan PATAH (404);
      (c) aturan Bos: "alihkan, jangan matikan".
    ⇒ 308 (PERMANENT REDIRECT): peramban & mesin pencari ikut memindahkan
      alamatnya, jadi tidak ada yang tersesat dan tidak ada isi kembar.

    template 'syarat.html' SENGAJA dibiarkan ada di disk — kalau Bos mau
    menghidupkan halamannya lagi, cukup kembalikan rutenya.
    """
    return RedirectResponse('/belajar#tab-3', status_code=308)


# ── DIAGNOSIS DATA: ALAT unggah + periksa + cara membetulkan ──────────────
# ACC Bos 19Sep26 (verbatim): "Halaman Syarat, jadikan tool / alat saja.
#   Namanya Diagnosis Data SPSS & PLS. Isinya user upload data dari spss
#   atau pls, untuk di diaknosa dan cara tulisnya. Benar katakan benar
#   salah katakan salah dan beri panduan untuk cara membetulkan data."
# Keputusan Bos: 1B (terima .xlsx/.csv/.sav) · 2A (tunjuk kolom manual) ·
#   3A (7 kartu bacaan /syarat dipindah ke BELAJAR — NANTI, Tahap 2).
# MENGAPA pakai menu 'klinik' (yang sudah ADA) dan bukan menu baru:
# menu 'klinik' sudah terdaftar di MODUL dengan ringkas yang HAMPIR SAMA
# ("Unggah data lapangan (.sav/.csv/.xlsx) — periksa & jelaskan cara
# memperbaikinya"). Kalau dibuat menu baru, dua menu saling menimpa dan
# mahasiswa bingung mana yang dipakai. ⇒ ISI menu yang sudah ada.
@app.get('/klinik', response_class=HTMLResponse)
@app.get('/diagnosis', response_class=HTMLResponse)
async def diagnosis(request: Request):
    """DIAGNOSIS DATA SPSS & PLS — alat unggah + diagnosa + cara membetulkan.

    ⚠️ NAMA MENU (keputusan Bos 19Sep26, VERBATIM): "menu KLINIK diganti nama
    jadi 'DIAGNOSIS DATA' + diisi alat unggah". Jadi MENU-nya bernama
    DIAGNOSIS DATA, tapi SLUG/tautannya tetap `klinik` (tautan lama tidak
    patah, dan `_konteks(request,'klinik',...)` menyalakan menu yang benar).
    `/diagnosis` DIPERTAHANKAN sebagai tautan pendek yang enak diketik.
    """
    return templates.TemplateResponse(request, 'diagnosis.html',
                                      _konteks(request, 'klinik', 'Diagnosis Data'))


@app.get('/kualitatif', response_class=HTMLResponse)
async def kualitatif(request: Request):
    k = _konteks(request, 'kualitatif', 'Kualitatif — Penelitian Kata & Cerita')
    return templates.TemplateResponse(request, 'kualitatif.html', k)


@app.get('/buat-data', response_class=HTMLResponse)
async def buat_data(request: Request):
    k = _konteks(request, 'buat-data', 'BUAT DATA')
    # ⚠️ BATAS TOTAL β untuk cara 'berantai' — SATU SUMBER (ACC Bos 18Sep26,
    #    Opsi C). Dikirim dari server supaya JS tidak menyimpan angka
    #    bisnis sendiri (pelajaran EduAi 15Sep26: batas yang ditulis di dua
    #    tempat bikin gerbang tak pernah tersentuh).
    from app.berkas_kerja import BATAS_BETA_RANTAI
    k['batas_beta_rantai'] = BATAS_BETA_RANTAI
    # ⚠️ BATAS BEDA KELOMPOK (MANOVA) — SATU SUMBER (ACC Bos 21Sep26, Opsi A).
    #    Halaman memakai angka ini supaya JS tidak menyimpan angka bisnis
    #    sendiri (pelajaran EduAi: batas di dua tempat → gerbang tak tersentuh).
    from app.hitung.kelompok import BEDA_MAKS, BEDA_MIN
    k['beda_min'] = BEDA_MIN
    k['beda_maks'] = BEDA_MAKS
    # model dari URL (?model=banding-kelompok) → halaman bisa memilih mode
    k['model'] = request.query_params.get('model') or ''
    return templates.TemplateResponse(request, 'buat_data.html', k)


@app.get('/pengaturan', response_class=HTMLResponse)
async def pengaturan(request: Request):
    return templates.TemplateResponse(request, 'pengaturan.html',
                                      _konteks(request, 'pengaturan', 'PENGATURAN'))


@app.get('/segera/{slug}', response_class=HTMLResponse)
async def segera(request: Request, slug: str):
    m = next((x for x in MODUL if x['slug'] == slug), None)
    k = _konteks(request, slug, m['nama'] if m else 'Modul')
    k['m'] = m
    return templates.TemplateResponse(request, 'segera.html', k)


# ═══════════════════════════════════════════════════════════════════════════
# BERKAS UNTUK MESIN PENCARI (Wulan, 20Okt26)
#
# AKAR: /favicon.ico & /sitemap.xml dulu 404, dan beranda tak punya meta
# description — cuplikan di Google jadi kosong. Bukan kerusakan, tapi
# kelengkapan yang nyata kurang.
#
# ⚠️ /robots.txt dulu 200 TANPA rute di kode (dilayani lapisan luar).
#    Sekarang dilayani app supaya ISI-nya ikut terkendali dan menunjuk
#    sitemap. Kalau nanti ada proxy yang menimpanya, uji SEO akan protes.
# ═══════════════════════════════════════════════════════════════════════════
@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    """Favicon. Chrome/Firefox modern menerima SVG; ini menyajikan SVG
    dengan jalur .ico supaya peramban lama & pemindai tetap dapat 200."""
    from fastapi.responses import FileResponse
    return FileResponse(STATIC / 'favicon.svg',
                        media_type='image/svg+xml',
                        headers={'Cache-Control': 'public, max-age=604800'})


@app.get('/sitemap.xml', include_in_schema=False)
async def sitemap_xml(request: Request):
    """Sitemap DIHITUNG dari MODUL — modul baru otomatis ikut, tak bisa basi."""
    from fastapi.responses import Response
    dasar = str(request.base_url).rstrip('/')
    # hanya halaman yang benar-benar ADA (siap=True); /segera/* tidak didaftar
    jalur = ['/'] + [f'/{m["slug"]}' for m in MODUL if m.get('siap')]
    jalur += ['/kuantitatif', '/kualitatif', '/diagnosis']
    # buang duplikat sambil menjaga urutan
    terlihat, unik = set(), []
    for j in jalur:
        if j not in terlihat:
            terlihat.add(j)
            unik.append(j)
    baris = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for j in unik:
        baris.append(f'  <url><loc>{dasar}{j}</loc>'
                     f'<changefreq>weekly</changefreq>'
                     f'<priority>{"1.0" if j == "/" else "0.8"}</priority></url>')
    baris.append('</urlset>')
    return Response('\n'.join(baris), media_type='application/xml')


@app.get('/robots.txt', include_in_schema=False)
async def robots_txt(request: Request):
    """Robots menunjuk sitemap — dulu tidak ada di kode sama sekali."""
    from fastapi.responses import PlainTextResponse
    dasar = str(request.base_url).rstrip('/')
    isi = ('User-agent: *\n'
           'Allow: /\n'
           'Disallow: /api/\n'
           '\n'
           f'Sitemap: {dasar}/sitemap.xml\n')
    return PlainTextResponse(isi)


# ═══════════════════════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════════════════════
@app.get('/api/status')
async def api_status():
    return {'app': 'Penelitian STATISTIK Lab.', 'ai_aktif': ai_aktif(),
            'versi': 'fase1'}


@app.post('/api/ai')
async def api_ai(payload: dict):
    return {'ai_aktif': set_ai(bool(payload.get('aktif')))}


def _teks_dari_balasan(mentah: str) -> str:
    """Ambil isi jawaban dari balasan 9router — TAHAN bentuk aneh.

    ⚠️ KENAPA PERLU (Wulan, 19Okt26 — terukur, bukan tebakan):
      9router membalas satu objek JSON, lalu MENEMPEL `data: [DONE]` di
      ekornya TANPA baris baru:

          {"choices":[{...}]}data: [DONE]

    Parser lama: mentah[find('{'):rfind('}')+1] → karena '}' terakhir ada
    di dalam "[DONE]" hasilnya JSON RUSAK → endpoint balas 200 tapi
    `content` tidak terambil → user melihat kotak KOSONG (bug senyap).
    Bukti: panjang respons 1426 char, jumlah '"content"' = 1, tapi
    teks terambil = 0 char. Jawaban asli memang ada di dalamnya.

    Urutan percobaan:
      1) JSON utuh / objek pertama via raw_decode (paling sering benar)
      2) buang ekor SSE `data: [DONE]` lalu coba lagi
      3) gabungkan delta SSE kalau balasannya memang streaming
    """
    if not mentah or not mentah.strip():
        return ''

    def _dari_objek(o):
        """Tarik teks dari satu objek balasan (utuh, bukan delta)."""
        if not isinstance(o, dict):
            return ''
        for ch in (o.get('choices') or []):
            # bentuk non-stream
            isi = ((ch.get('message') or {}).get('content') or '').strip()
            if isi:
                return isi
        return ''

    def _gabung_delta(teks: str) -> str:
        """Gabungkan delta SSE jadi satu teks utuh."""
        potongan = []
        for baris in teks.splitlines():
            baris = baris.strip()
            if not baris.startswith('data:'):
                continue
            isi_baris = baris[5:].strip()
            if not isi_baris or isi_baris == '[DONE]':
                continue
            try:
                o = json.loads(isi_baris)
            except Exception:
                continue
            for ch in (o.get('choices') or []):
                d = (ch.get('delta') or {}).get('content')
                if d:
                    potongan.append(d)
        return ''.join(potongan).strip()

    # ── (0) STREAMING MURNI: banyak baris "data: {...}" ──────────────────
    # ⚠️ Harus dicek DULU. Kalau tidak, raw_decode berhenti di objek
    #    PERTAMA dan cuma dapat potongan pertama ("Halo", bukan "Halo dunia").
    if mentah.count('data:') >= 2:
        hasil = _gabung_delta(mentah)
        if hasil:
            return hasil

    # ── (1) JSON utuh / (2) objek pertama via raw_decode ─────────────────
    kandidat = [mentah.strip()]
    # buang ekor SSE "data: [DONE]" (bisa nempel tanpa newline)
    bersih = mentah.strip()
    for tanda in ('data:', 'data ', '\ndata'):
        pos = bersih.find(tanda)
        if pos > 0:
            bersih = bersih[:pos].strip()
            break
    if bersih and bersih != kandidat[0]:
        kandidat.append(bersih)

    for teks_uji in kandidat:
        try:
            isi = _dari_objek(json.loads(teks_uji))
            if isi:
                return isi
        except Exception:
            pass
        awal = teks_uji.find('{')
        if awal >= 0:
            try:
                obj, _akhir = json.JSONDecoder().raw_decode(teks_uji[awal:])
                isi = _dari_objek(obj)
                if isi:
                    return isi
            except Exception:
                pass

    # ── (3) sisa: coba gabung delta sekali lagi ──────────────────────────
    return _gabung_delta(mentah)


def _sebab_kosong(mentah: str) -> str:
    """KENAPA jawaban kosong? — dibaca dari balasan, bukan ditebak.

    ⚠️ AKAR "Minta saran AI → HTTP 502" (Wulan, 21Okt26 — terukur):
      Model `cb/deepseek-v4.1-flash` punya `reasoning_content`: dia
      menulis PROSES BERPIKIR dulu, baru `content`. Kalau `max_tokens`
      habis dipakai berpikir, balasannya:

          {"finish_reason":"length","message":{"content":"","reasoning_content":"The user wants..."}}

      Terbukti: max_tokens=200 → content KOSONG; 800/3000 → terisi.
      Balasan tetap HTTP 200, jadi tanpa pemeriksaan ini user hanya
      melihat "AI menjawab tapi isinya kosong" — tanpa tahu sebabnya.

    Kembalian: kalimat SEBAB yang bisa dibaca user (bukan kode galat).
    """
    if not mentah or not mentah.strip():
        return 'AI tidak mengirim apa pun.'
    try:
        awal = mentah.find('{')
        if awal < 0:
            return 'AI mengirim jawaban yang tidak bisa dibaca.'
        obj, _ = json.JSONDecoder().raw_decode(mentah[awal:])
    except Exception:
        return 'AI mengirim jawaban yang tidak bisa dibaca.'

    for ch in (obj.get('choices') or []):
        alasan = str(ch.get('finish_reason') or '')
        pesan = ch.get('message') or {}
        ada_pikir = bool((pesan.get('reasoning_content') or '').strip())
        if alasan == 'length':
            if ada_pikir:
                return ('AI kehabisan jatah token saat menyusun jawaban '
                        '(model ini berpikir dulu sebelum menjawab), jadi '
                        'jawabannya tidak sempat ditulis. Coba lagi — kalau '
                        'terus begini, pakai mode manual.')
            return ('AI kehabisan jatah token sebelum menyelesaikan '
                    'jawaban. Coba lagi dengan permintaan lebih pendek, '
                    'atau pakai mode manual.')
        if alasan == 'content_filter':
            return ('AI menolak menjawab permintaan ini (penyaring isi). '
                    'Ubah sedikit kata kuncinya, atau pakai mode manual.')
    return 'AI menjawab tapi isinya kosong.'


#  BENTUK KELUARAN per jenis permintaan (permintaan Bos 21Okt26).
#  ⚠️ KENAPA PERLU (terukur dari keluhan Bos): hasil "Panduan Wawancara"
#  keluar sebagai Markdown datar — `# Panduan`, `## FOKUS 1:`, `---`,
#  `**INTERNAL**`, `- *Contoh jawaban:*`. Itu terjadi karena system
#  prompt LAMA tidak punya SATU kata pun soal format, jadi AI bebas
#  memakai Markdown. Panduan wawancara juga DIPAKAI DI LAPANGAN, jadi
#  rupanya harus bersih: angka + indentasi + tanda kutip.
#
#  Larangan Markdown GLOBAL (semua bentuk):
LARANGAN_MD = (
    'ATURAN WAJIB: JANGAN pakai Markdown sama sekali. Dilarang menulis '
    'tanda #, ##, ###, **, __, ---, ``` atau bullet dengan - / *. '
    'Jangan menyalin pertanyaan user menjadi judul. Tulis sebagai teks '
    'biasa yang rapi. Untuk penekanan gunakan kata, bukan tanda bintang.'
)

BENTUK = {
    #  Panduan wawancara: dibawa ke lapangan -> angka + indentasi + kutip.
    'panduan': (
        'SUSUNAN WAJIB untuk panduan wawancara (patuhi persis):\n'
        'Baris pertama: "Panduan Wawancara" lalu nama penelitian, satu baris.\n'
        'Baris kedua: satu kalimat pengantar praktis (durasi + suasana).\n'
        'Lalu untuk TIAP fokus penelitian:\n'
        '  "Fokus 1 — <nama fokus>" (tanpa tanda bintang, tanpa pagar)\n'
        '  Untuk informasi tiap kelompok informan, tulis satu baris pembuka '
        'berupa kalimat biasa, contoh: "Untuk informan internal, yang sudah '
        'biasa riset dulu sebelum membeli:"\n'
        '  Lalu pertanyaan bernomor 1, 2, 3 (bukan bullet). Setiap '
        'pertanyaan ditulis sebagai kalimat yang diucapkan apa adanya, '
        'diawali dan diakhiri tanda kutip.\n'
        '  Di bawah pertanyaan, dua baris pendalaman yang diberi indentasi '
        '4 spasi, ditandai "Kalau jawabannya singkat:" dan "Kalau masih '
        'datar:". Pedalaman juga berupa kalimat yang diucapkan, dalam '
        'tanda kutip.\n'
        'Bahasa: bahasa sehari-hari orang ngobrol, bukan bahasa buku. '
        'Sebut "kamu", bukan "Anda". Hindari kata "menggali", "aspek", '
        '"persepsi", "indikator" — ganti dengan kata yang dipakai orang '
        'sebenarnya, misalnya "cari tahu", "yang dilihat", "yang bikin yakin".'
    ),
    #  Koding: user menyalin kode ke kolom -> satu baris satu potongan.
    'koding': (
        'SUSUNAN WAJIB untuk usulan kode (patuhi persis):\n'
        'Satu baris per potongan, bentuknya: "Potongan N: kode"\n'
        'Kode = 2 sampai 4 kata, huruf biasa (bukan huruf besar semua), '
        'menggambarkan ISI potongan, bukan mengulang kalimatnya.\n'
        'JANGAN beri penjelasan, pengantar, atau penutup per potongan. '
        'Setelah daftar kode, boleh satu paragraf pendek (maksimal 3 '
        'kalimat) contoh cara memakai kode itu saat mengisi tabel.'
    ),
    #  Tafsir: contoh paragraf mengalir, bukan butir.
    'tafsir': (
        'SUSUNAN WAJIB untuk contoh tafsir (patuhi persis):\n'
        'Satu tema ditulis sebagai SATU paragraf mengalir 2 sampai 3 '
        'kalimat (bukan butir, bukan bernomor).\n'
        'Awali dengan nama temanya dalam kalimat biasa, lalu lanjutkan '
        'dengan maknanya. Jangan buka dengan kata "Tema:" diikuti titik dua.\n'
        'Bahasa mengalir seperti orang menjelaskan ke teman, bukan laporan.'
    ),
    #  SWOT faktor: tepat 4+4+4+4, satu baris satu faktor.
    'swot_faktor': (
        'SUSUNAN WAJIB untuk usulan faktor SWOT (patuhi persis):\n'
        'Empat blok berurutan dengan penanda huruf di awal baris: '
        '"S: <faktor>" lalu "W: <faktor>" lalu "O: <faktor>" lalu '
        '"T: <faktor>".\n'
        'Tepat 4 baris S, 4 baris W, 4 baris O, 4 baris T. Satu faktor '
        'satu baris, panjangnya maksimal 12 kata, SPESIFIK untuk objek di '
        'konteks (jangan yang berlaku umum untuk semua usaha).\n'
        'Jangan beri penjelasan apa pun di antara baris.'
    ),
    #  SWOT strategi: SO/WO/ST/WT masing-masing satu kalimat.
    'swot_strategi': (
        'SUSUNAN WAJIB untuk usulan strategi SWOT (patuhi persis):\n'
        'Empat baris berurutan: "SO: <satu kalimat strategi>" lalu '
        '"WO: ..." lalu "ST: ..." lalu "WT: ...".\n'
        'Tiap strategi SATU kalimat, maksimal 20 kata, menyebut hal konkret '
        'dari faktor yang sudah ada (jangan mengarang faktor baru).\n'
        'Jangan beri pengantar, penutup, atau penjelasan tambahan.'
    ),
    #  Kartu kutipan (Meja Kerja, 21Okt26): balasan DIBACA MESIN, bukan
    #  mata — aplikasi mengambil dua baris itu lalu mengisi kolom kartu.
    #  Kalau ada kata pengantar, tema jadi ikut kotor.
    'kartu': (
        'SUSUNAN WAJIB untuk satu kartu kutipan (patuhi persis):\n'
        'Balas TEPAT DUA BARIS, tanpa baris kosong, tanpa pengantar, '
        'tanpa penutup, tanpa penomoran, tanpa tanda kutip pembungkus:\n'
        'KODE: <2 sampai 4 kata>\n'
        'TEMA: <nama tema>\n'
        'Kode ditulis huruf biasa (bukan huruf besar semua), menggambarkan '
        'ISI kutipan. Tema WAJIB salah satu dari tema yang sudah dipakai '
        'bila ada yang cocok; hanya buat tema baru kalau benar-benar tidak '
        'ada yang pas.\n'
        'JANGAN menulis kalimat penjelasan apa pun sesudah dua baris itu.'
    ),
}

SYS_DASAR = ('Kamu asisten penelitian kualitatif untuk mahasiswa S1 '
             'Manajemen Indonesia. Jawab Bahasa Indonesia sederhana, '
             'kalimat pendek, SELALU sertai contoh konkret yang mudah '
             'diikuti. Jangan bertele-tele.')


def _system_prompt(bentuk: str) -> str:
    """Rakit system prompt: dasar + larangan Markdown + susunan per bentuk."""
    bagian = [SYS_DASAR, LARANGAN_MD]
    susunan = BENTUK.get((bentuk or '').strip().lower())
    if susunan:
        bagian.append(susunan)
    else:
        #  Tanpa bentuk: tetap larang Markdown, minta teks mengalir.
        bagian.append('Tulis jawaban sebagai teks biasa yang mengalir. '
                      'Kalau perlu daftar, pakai nomor 1, 2, 3, bukan bullet.')
    return '\n\n'.join(bagian)


#  Jatah token untuk saran kualitatif. Model reasoning (mis.
#  cb/deepseek-v4.1-flash) memakai token untuk `reasoning_content` DULU;
#  800 terbukti bisa habis sebelum `content` ditulis → jawaban kosong.
#  2000 memberi ruang berpikir + menjawab (terukur 21Okt26: 2,2 dtk).
SARAN_MAX_TOKEN = int(os.environ.get('SARAN_MAX_TOKEN', '2000'))


@app.post('/api/kualitatif/saran')
async def kualitatif_saran(payload: dict):
    """Proksi saran AI untuk modul kualitatif (Wulan, 19Okt26).

    POLA SAMA DENGAN APLIKASI INI (judul.py / jatah.py):
      · saklar AI dihormati  -> kalau `ai_aktif()` mati, jawab 503 jujur
      · kunci API dari ENV   -> ROUTER9_API_KEY, TIDAK PERNAH ke browser
      · tanpa kunci          -> 503 jujur (mode manual tetap jalan)
      · 9router menolak UA Python-urllib -> pakai UA netral
      · respons 9router berekor SSE ("data: [DONE]") -> dibersihkan dulu

    ⚠️ KENAPA PARSER DIPERBAIKI (Wulan, 19Okt26):
      9router membalas SATU objek JSON lalu menempel `data: [DONE]` di
      ekornya — tanpa baris baru. Parser lama memakai rfind('}') yang
      mengenai penutup "[DONE]" sehingga JSON rusak -> SUKSES tapi isi
      KOSONG (bug senyap: user lihat kotak kosong, bukan pesan galat).
      Sekarang: buang ekor SSE dulu, lalu pakai JSONDecoder.raw_decode
      yang berhenti tepat di akhir objek pertama. Teruji 2.9 detik.
    """
    import json as _json
    import urllib.request as _url

    # ── 1. Hormati saklar AI aplikasi (sama seperti jalur judul) ──────────
    if not ai_aktif():
        return JSONResponse(
            {'boleh': False,
             'sebab': 'AI sedang dimatikan di aplikasi. Nyalakan saklar AI '
                      'dulu, atau pakai mode manual — hasilnya sama baiknya.'},
            status_code=503)

    # ── 2. Kunci dari environment (tidak pernah ke browser) ───────────────
    kunci = os.environ.get('ROUTER9_API_KEY', '').strip()
    if not kunci:
        return JSONResponse(
            {'boleh': False,
             'sebab': 'AI belum disambung (kunci API belum diisi di server). '
                      'Pakai mode manual — hasilnya sama baiknya.'},
            status_code=503)
    dasar = os.environ.get('ROUTER9_BASE',
                           'https://9router.bikinaja.id/v1').rstrip('/')
    model = os.environ.get('ROUTER9_MODEL', 'EduAi')

    prompt = str((payload or {}).get('prompt', ''))[:4000]
    if not prompt.strip():
        return JSONResponse({'boleh': False, 'sebab': 'Prompt kosong.'},
                            status_code=400)
    #  Bentuk keluaran diminta LAYAR (panduan/koding/tafsir/swot_*).
    bentuk = str((payload or {}).get('bentuk', '') or '').strip().lower()
    sys_prompt = _system_prompt(bentuk)

    tubuh = _json.dumps({
        'model': model, 'max_tokens': SARAN_MAX_TOKEN, 'temperature': 0.7,
        #  MATIKAN BERPIKIR (putusan Bos 21Okt26: "reasoning = false aja").
        #  Model reasoning (cb/deepseek-v4.1-flash) memakai token untuk
        #  `reasoning_content` DULU; kalau habis, `content` keluar KOSONG
        #  dengan finish_reason=length -> itulah akar "HTTP 502".
        #  Terukur 21Okt26: tanpa param jawaban bisa kosong, dengan param
        #  jawaban langsung terisi (~2 dtk).
        'enable_thinking': False,
        'messages': [
            {'role': 'system', 'content': sys_prompt},
            {'role': 'user', 'content': prompt},
        ]}).encode()

    def _sekali():
        """Satu panggilan ke 9router -> (teks, mentah). Melempar bila gagal."""
        import http.client as _http
        req = _url.Request(dasar + '/chat/completions', data=tubuh, headers={
            'Authorization': 'Bearer ' + kunci,
            'Content-Type': 'application/json',
            # 9router menolak UA Python-urllib (403) — pakai UA netral
            'User-Agent': 'statistik-lab/1.0'})
        try:
            mentah = _url.urlopen(req, timeout=90).read().decode(
                'utf-8', 'replace')
        except _http.IncompleteRead as _ir:
            # 9router menutup stream SSE lebih awal — pakai yang terbaca
            mentah = _ir.partial.decode('utf-8', 'replace')
        return _teks_dari_balasan(mentah), mentah

    #  Percobaan 1. Kalau kosong karena `finish_reason=length` (model
    #  kehabisan token saat BERPIKIR — terukur 21Okt26), ulangi SEKALI
    #  dengan jatah token dua kali lipat sebelum menyerah. Percobaan
    #  ulang hanya untuk sebab ini, supaya galat jaringan tidak disembuhkan
    #  diam-diam (dan tidak menahan user menunggu sia-sia).
    try:
        teks, mentah = _sekali()
        if not teks:
            sebab = _sebab_kosong(mentah)
            if 'jatah token' in sebab:
                tubuh2 = _json.dumps({
                    'model': model, 'max_tokens': SARAN_MAX_TOKEN * 2,
                    'temperature': 0.7,
                    'enable_thinking': False,
                    'messages': _json.loads(tubuh.decode())['messages'],
                }).encode()
                asli, tubuh = tubuh, tubuh2
                try:
                    teks, mentah = _sekali()
                finally:
                    tubuh = asli
                if teks:
                    return {'boleh': True, 'saran': teks, 'model': model}
            return JSONResponse(
                {'boleh': False, 'sebab': sebab + ' Pakai mode manual kalau '
                                                  'masih gagal.'},
                status_code=502)
        return {'boleh': True, 'saran': teks, 'bentuk': bentuk,
                'model': model}
    except Exception as e:
        return JSONResponse(
            {'boleh': False, 'sebab': f'AI tidak menjawab ({e}). Coba lagi '
                                     'atau pakai mode manual.'},
            status_code=502)


@app.post('/api/kualitatif/ekspor-qdpx')
async def kualitatif_ekspor_qdpx(payload: dict):
    """Ekspor REFI-QDA Project (.qdpx) — dibuka di NVivo/ATLAS.ti/MAXQDA.

    Data koding dikirim dari browser (localStorage); server merakit
    project.qde yang VALID terhadap XSD resmi REFI-QDA 1.0.
    (Wulan, 19Okt26)"""
    from fastapi.responses import Response
    from app.hitung.refi_qda import bangun_proyek
    payload = payload or {}
    try:
        data = bangun_proyek(payload.get('nama_proyek', 'Proyek statistik-lab'),
                             payload.get('segmen', []),
                             payload.get('informan', []))
    except ValueError as e:
        return JSONResponse({'boleh': False, 'sebab': str(e)}, status_code=400)
    except Exception as e:
        # ⚠️ Wulan 19Okt26: payload dari browser (localStorage) bentuknya tak
        #    dijamin. Dulu AttributeError/TypeError lolos jadi HTTP 500 mentah.
        #    Sekarang ditangkap -> 400 ramah, user tahu harus apa.
        return JSONResponse(
            {'boleh': False,
             'sebab': f'Data koding tidak bisa diekspor ({type(e).__name__}: '
                      f'{e}). Periksa kembali segmen & informanmu.'},
            status_code=400)
    nama = 'koding-statistik-lab.qdpx'
    return Response(data, media_type='application/octet-stream',
                    headers={'Content-Disposition':
                             'attachment; filename="%s"' % nama})


@app.post('/api/kualitatif/ekspor-qdc')
async def kualitatif_ekspor_qdc(payload: dict):
    """Ekspor REFI-QDA Codebook (.qdc) — codebook saja. (Wulan, 19Okt26)"""
    from fastapi.responses import Response
    from app.hitung.refi_qda import bangun_codebook
    payload = payload or {}
    try:
        data = bangun_codebook(payload.get('segmen', []))
    except ValueError as e:
        return JSONResponse({'boleh': False, 'sebab': str(e)}, status_code=400)
    return Response(data, media_type='application/xml',
                    headers={'Content-Disposition':
                             'attachment; filename="codebook-statistik-lab.qdc"'})


@app.post('/api/baca-judul')
async def api_baca_judul(payload: dict):
    """LAPIS 1: baca judul → usul model + ALASAN. TANPA AI (Rp 0, instan).

    ⚠️ MENGAPA TANPA AI DULU (ACC Bos 18Sep26, hybrid 3 lapis):
    Uji 42 judul membuktikan Lapis 1 benar 40/42 (95%), 0 salah tebak.
    Jadi 95% judul TIDAK PERLU memanggil AI sama sekali — ini yang menjaga
    token Bos. AI hanya dipanggil kalau Lapis 1 JUJUR bilang ragu.

    ⚠️ JATAH: dihitung per JUDUL BARU per hari (ACC Bos: 20/hari).
    Judul yang sama TIDAK dipotong (jawabannya disimpan di browser user).
    Kalau jatah habis → tetap dijawab Lapis 1, user TIDAK diblokir.

    ⚠️ TIDAK ADA PESAN GALAT di sini. Jatah penuh bukan kesalahan user.
    """
    from app.judul import baca, nama_awam, kode_model
    from app import jatah

    judul = (payload.get('judul') or '').strip()
    if not judul:
        return JSONResponse({'ok': False,
                             'pesan': 'Judulnya masih kosong.', })

    # ── 1. baca dengan kata kunci (selalu jalan, tidak butuh apa pun) ─────
    hasil = baca(judul)

    # ── 2. catat jatah (judul baru dipotong, judul sama tidak) ────────────
    keadaan = jatah.pakai(judul)

    # ── 3. putuskan apakah perlu AI (Lapis 2) ─────────────────────────────
    # Syarat: Lapis 1 ragu DAN jatah belum penuh DAN saklar AI hidup.
    perlu_ai = bool(hasil['butuh_ai']) and not keadaan['penuh'] and ai_aktif()
    if hasil['butuh_ai'] and keadaan['penuh']:
        hasil['alasan'] = (hasil['alasan'] +
                           ' Kamu bisa pilih sendiri di halaman berikutnya — '
                           'itu sama sahnya.')
    if hasil['butuh_ai'] and not ai_aktif():
        hasil['alasan'] = (hasil['alasan'] +
                           ' Pilih sendiri di halaman berikutnya juga tidak '
                           'masalah.')

    return JSONResponse({
        'ok': True,
        'model': hasil['model'],
        'nama': nama_awam(hasil['model']),
        'kode': kode_model(hasil['model']),
        'yakin': hasil['yakin'],
        'alasan': hasil['alasan'],
        'penanda': hasil['penanda'],
        'variabel': hasil['variabel'],
        'perlu_ai': perlu_ai,          # True = lanjut Lapis 2 (belum aktif)
        'jatah': {'terpakai': keadaan['terpakai'],
                  'batas': keadaan['batas'],
                  'sisa': keadaan['sisa']},
        'judul': judul,
    })


@app.get('/api/jatah-judul')
async def api_jatah_judul():
    """Keadaan jatah hari ini (dipakai halaman untuk menampilkan sisa)."""
    from app import jatah
    return JSONResponse(jatah.cek())


@app.post('/api/buat-data')
async def api_buat_data(payload: dict):
    """Bangun data + ukur ulang hasilnya sendiri (lokal, tanpa AI)."""
    from fastapi import HTTPException
    from app.berkas_kerja import buat_data, simpan_terakhir, ke_csv, ke_xlsx
    try:
        d = buat_data(
            n=int(payload.get('n', 150)),
            x=int(payload.get('x', 3)),
            beta=[float(b) for b in payload.get('beta', [0.30, 0.22, 0.15])],
            skala=int(payload.get('skala', 5)),
            alpha=float(payload.get('alpha', 0.85)),
            mode=str(payload.get('mode', 'presisi')),
            nama_x=payload.get('nama_x') or None,
            # cara = cara MENGUJI Y, terpisah dari jumlah X (ACC Bos 18Sep26)
            cara=str(payload.get('cara', 'sederhana')),
        )
    except Exception as e:                       # noqa: BLE001
        raise HTTPException(status_code=400, detail=f'Gagal membuat data: {e}')
    simpan_terakhir(d)
    d_kirim = {k: v for k, v in d.items() if k != 'data'}
    return JSONResponse(d_kirim)


@app.post('/api/buat-data/jalur')
async def api_buat_data_jalur(payload: dict):
    """Bangun data MODEL JALUR (mediasi/moderasi) + ukur hasilnya sendiri.

    (Wulan, 19Okt26 — temuan audit 16Okt26: halaman ?model=mediasi|moderasi
    dulu hanya menampilkan UI regresi biasa. Sekarang membangun & mengukur
    struktur jalurnya sungguhan: kalibrasi_per_jalur + kaitan.py.)
    """
    from fastapi import HTTPException
    from app.berkas_kerja import buat_data_jalur, simpan_terakhir
    try:
        d = buat_data_jalur(
            model=str(payload.get('model', '')),
            n=int(payload.get('n', 150)),
            params=dict(payload.get('params') or {}),
            nama=dict(payload.get('nama') or {}),
            skala=int(payload.get('skala', 5)),
            alpha=float(payload.get('alpha', 0.85)),
            mode=str(payload.get('mode', 'presisi')),
        )
    except Exception as e:                       # noqa: BLE001
        raise HTTPException(status_code=400, detail=f'Gagal membuat data: {e}')
    simpan_terakhir(d)
    d_kirim = {k: v for k, v in d.items() if k != 'data'}
    return JSONResponse(d_kirim)


# ── MANOVA: BANDING KELOMPOK (ACC Bos 21Sep26: "Ok buka untuk manova") ────
# Pola yang sudah jalan sejak awal — MASUK + KELUAR:
#   /api/manova/buat  → mesin MEMBANGUN data berkelompok (+ kunci jawaban)
#   /api/manova/uji   → mesin MENGUJI & MENJELASKAN (Wilks, Pillai, …)
#
# ⚠️ R4 DIPATUHI: kolom kelompok TIDAK ditempelkan ke format data lama
#    yang dipakai 17 grup gerbang. Kelompok dibawa TERPISAH.
#
# ⚠️ PAGAR (Opsi A, ACC Bos): di luar beda 0,30–1,50 mesin TIDAK akurat
#    (terukur: beda 2,50 hanya 76% akurat) → DITOLAK dengan saran angka.
#    Pesan SELALU ramah (tidak pernah traceback).
@app.post('/api/manova/buat')
async def api_manova_buat(payload: dict):
    """Bangun data berkelompok untuk MANOVA + akui akurasinya sendiri."""
    from fastapi import HTTPException
    from app.hitung.kelompok import buat_data_kelompok, ukur_ulang
    try:
        d = buat_data_kelompok(
            n_per_kelompok=payload.get('n_per_kelompok', 60),
            nama_kelompok=payload.get('nama_kelompok') or None,
            nama_y=payload.get('nama_y') or None,
            beda=payload.get('beda') or None,
            skala=int(payload.get('skala', 5)),
            mode=str(payload.get('mode', 'presisi')),
            seed=payload.get('seed'),
            butir=int(payload.get('butir', 2)),
        )
    except ValueError as e:            # pesan pagar → ramah, bukan traceback
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:             # noqa: BLE001
        raise HTTPException(status_code=400,
                            detail=f'Gagal membuat data berkelompok: {e}')

    hasil = ukur_ulang(d)
    from numpy import asarray as _asarray          # impor lokal (main.py tanpa np)
    kirim = {kk: vv for kk, vv in d.items() if kk != 'Y'}
    kirim['kelompok'] = [str(q) for q in d['kelompok']]
    kirim['Y'] = d['Y'].tolist()
    # ⚠️ ndarray TIDAK bisa di-JSON-kan → ubah ke list (terukur: 500 error).
    kirim['beda_dipasang'] = _asarray(d['beda_dipasang']).tolist()
    kirim['beda_terbaca'] = _asarray(d['beda_terbaca']).tolist()
    for nm in ('skor', 'kolom'):
        kirim[nm] = {kk: (_asarray(vv).tolist()
                          if hasattr(vv, 'tolist') else vv)
                     for kk, vv in d[nm].items()}
    kirim['ukur'] = hasil
    return JSONResponse(kirim)


@app.post('/api/manova/uji')
async def api_manova_uji(payload: dict):
    """Uji MANOVA: Wilks/Pillai/Hotelling/Roy + F&p + ANOVA per-Y + asumsi."""
    from fastapi import HTTPException
    from app.hitung.manova import bisa_manova, hitung_manova
    try:
        Y = payload.get('Y')
        kel = payload.get('kelompok')
        nama_y = payload.get('nama_y') or None
        gate = bisa_manova(kel, nama_y or ['Y1', 'Y2'])
        if not gate['bisa']:
            raise HTTPException(status_code=400, detail=gate['sebab'])
        r = hitung_manova(Y, kel, nama_y)
    except HTTPException:
        raise
    except Exception as e:             # noqa: BLE001
        raise HTTPException(status_code=400, detail=f'Uji MANOVA gagal: {e}')
    if not r.get('boleh'):
        raise HTTPException(status_code=400, detail=r.get('sebab'))
    # matriks SSCP besar → tidak perlu dikirim ke halaman
    r.pop('sscp', None)
    return JSONResponse(r)


@app.get('/api/manova/batas')
async def api_manova_batas():
    """Batas beda yang AMAN — satu sumber, dibaca halaman & uji."""
    from app.hitung.kelompok import BEDA_MAKS, BEDA_MIN
    return JSONResponse({'min': BEDA_MIN, 'maks': BEDA_MAKS,
                         'catatan': ('Mesin akurat pada rentang ini. '
                                     'Di luar itu hasilnya meleset.')})


# ── DIAGNOSIS DATA: unggah → periksa → cara membetulkan (ACC Bos 19Sep26) ──
# Inilah ALAT yang Bos minta: user mengunggah data dari SPSS/SmartPLS,
# alat memeriksa syaratnya, bilang BENAR kalau benar dan SALAH kalau salah,
# lalu memberi panduan cara membetulkan.
#
# Pagar yang dipasang di sini:
#   · Ukuran maksimal 10 MB — DIPERIKSA DI SERVER, bukan cuma di JS
#     (pelajaran EduAi 15Sep26: batas yang hanya ada di JS bisa dilewati).
#   · Format diperiksa dari ISI berkas, bukan dari namanya saja.
#   · Pesan galat SELALU ramah (GagalBaca), tidak pernah traceback.
@app.post('/api/diagnosis/unggah')
async def api_diagnosis_unggah(berkas: UploadFile = File(...)):
    """Terima berkas → kembalikan daftar kolom + pratinjau.

    HANYA membaca. Perhitungan dijalankan di /api/diagnosis/periksa supaya
    user bisa MENUNJUK KOLOM dulu (keputusan Bos 2A), bukan ditebak mesin.
    """
    from fastapi import HTTPException
    from app.diagnosis import baca_berkas, GagalBaca, MAX_BYTE
    import pandas as pd

    isi = await berkas.read()
    if len(isi) > MAX_BYTE:
        raise HTTPException(status_code=413, detail=(
            f'Berkasnya {len(isi)/1_048_576:.1f} MB — melebihi batas '
            f'{MAX_BYTE/1_048_576:.0f} MB. Coba simpan sebagian data dulu ya.'))
    try:
        df, ket = baca_berkas(berkas.filename or 'data.csv', isi)
    except GagalBaca as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Simpan sementara supaya tidak perlu unggah dua kali. Kunci dari nama
    # berkas + ukuran — cukup untuk satu sesi pemakaian, tanpa basis data.
    from app.diagnosis import simpan_sementara
    kunci = simpan_sementara(df)

    kolom = [{'nama': str(c), 'kosong': int(df[c].isna().sum()),
              'jenis': ('angka' if pd.api.types.is_numeric_dtype(df[c])
                        else 'teks')} for c in df.columns]
    return JSONResponse({
        'kunci': kunci,
        'nama_berkas': berkas.filename,
        'n_baris': int(len(df)),
        'n_kolom': int(len(df.columns)),
        'kolom': kolom,
        'keterangan': ket,
        'pratinjau': df.head(5).astype(str).values.tolist(),
    })


@app.post('/api/diagnosis/periksa-peran')
async def api_diagnosis_periksa_peran(payload: dict):
    """PERIKSA PERAN KOLOM sebelum diproses (ACC Bos 21Sep26).

    ARAH BOS: "Sebelum proses tampilkan kondisi yang telah di parsing benar
    atau tidak? Kalau tidak minta beberapa hal untuk mhs verifikasi."

    payload:
      kunci : kunci dari /unggah
      peran : {'nama kolom': 'X1' | 'M1' | 'Z1' | 'Y1' | …}

    Kembalikan hasil periksa_peran() apa adanya — masalah (harus diperbaiki),
    tanya (boleh lanjut tapi dicek dulu), kelompok, ringkas.
    ⚠️ Fungsi ini TIDAK menghitung apa pun. Murni memeriksa.
    """
    from fastapi import HTTPException
    from app.diagnosis import ambil_sementara, periksa_peran

    df = ambil_sementara(payload.get('kunci', ''))
    if df is None:
        raise HTTPException(status_code=400, detail=(
            'Datanya sudah tidak ada di server (mungkin sesi terlalu lama). '
            'Coba unggah ulang ya — sekali klik saja.'))

    peran = payload.get('peran') or {}
    if not isinstance(peran, dict):
        raise HTTPException(status_code=400,
                            detail='Bentuk penandaan peran tidak dikenali.')
    return periksa_peran(list(df.columns), peran)


def _gabung_peran(df, payload: dict):
    """Terapkan PERAN: gabung kolom seperan jadi satu skor (ACC Bos 21Sep26).

    Mahasiswa menandai beberapa kolom sebagai peran SAMA (mis. X1 = 3
    pertanyaan). Kalau kolom itu dihitung satu per satu, mesin melihat
    'X1' sebagai 3 variabel terpisah — SALAH secara statistik.

    Dipakai untuk SPSS (peran X*→kolom_x, M*→kolom_m, Y*→kolom_y) dan PLS
    (peran X1/M1/Y1 → konstruk bernama peran). PLS tetap didahulukan lewat
    `konstruk` kalau halaman sudah mengirimnya — di sini hanya jalur PERAN.

    Kembalikan (df_baru, payload_baru). Kalau tidak ada peran, kembalikan
    apa adanya (halaman lama tetap jalan).
    """
    peran = payload.get('peran') or {}
    if not isinstance(peran, dict) or not peran:
        return df, payload

    from app.diagnosis import skor_konstruk

    tabel, _ = skor_konstruk(df, peran)
    if tabel.shape[1] == 0:
        return df, payload

    baru = dict(payload)
    peta_peran = sorted(tabel.columns)

    if str(payload.get('mode', 'spss')) == 'pls':
        # Nama konstruk = nama PERAN (X1, M1, Y1…), butirnya kolom asli
        # supaya α/AVE/CR tetap dihitung dari butir (bukan dari skor).
        peta_butir: dict[str, list[str]] = {}
        for kolom in df.columns:
            p = peran.get(kolom)
            if p:
                peta_butir.setdefault(p, []).append(kolom)
        baru['konstruk'] = peta_butir
        y_awal = str(payload.get('kolom_y_konstruk') or '')
        if y_awal in peta_butir:
            baru['kolom_y_konstruk'] = y_awal
        else:                       # kalau tidak cocok, ambil Y pertama
            y_peran = [p for p in peta_peran if p.startswith('Y')]
            if y_peran:
                baru['kolom_y_konstruk'] = y_peran[-1]
        return tabel, baru

    baru['kolom_x'] = [p for p in peta_peran if p.startswith('X')]
    baru['kolom_m'] = [p for p in peta_peran if p.startswith('M')]
    # ⚠️ Z (penguat) — DITAMBAHKAN 21Sep26. Sebelumnya baris ini HANYA
    # meneruskan X, M, Y → PERAN Z yang ditandai mahasiswa DIBUANG TOTAL
    # (terukur: halaman kirim Z1, hasil mesin hanya X1). Akibatnya kartu
    # "Moderasi" tidak memberi hasil moderasi apa pun. Ditemukan lewat uji
    # pintu produksi (unggah → Hasil), lihat TEMUAN_MEDIASI_MODERASI_21SEP2026.md.
    baru['kolom_z'] = [p for p in peta_peran if p.startswith('Z')]
    y_peran = [p for p in peta_peran if p.startswith('Y')]
    if y_peran:
        baru['kolom_y'] = y_peran[-1]
    return tabel, baru


def _hias_hasil(r: dict, mode: str) -> dict:
    """Tempelkan nasihat perbaikan + penanda mode ke hasil mesin.

    Dipakai BERSAMA oleh rute lama /api/diagnosis/periksa dan pintu
    jembatan /api/jembatan/hitung — satu sumber, supaya hasil kedua
    pintu untuk data yang sama tidak mungkin berbeda.
    """
    from app import nasihat

    # Tempelkan nasihat "cara membetulkan" untuk tiap masalah yang muncul.
    # WAJIB dari server: kalau ditaruh di JS, teksnya harus dijaga di dua
    # tempat (pelajaran EduAi 15Sep26 — batas/teks yang ditulis dua kali
    # membuat yang satu tak pernah tersentuh).
    kode_masalah = []
    if mode == 'pls':
        # ⚠️ KUNCI yang BENAR (dibaca dari mesin 19Sep26, bukan tebakan):
        #    per konstruk → 'lulus_muat' (bukan lulus_cl) · 'ave' · 'cr'
        #    tidak ada 'vif_inner_maks' → dihitung dari daftar 'vif_inner'
        #    'fornell' BELUM ADA di mesin → tidak bisa dinilai (jujur).
        for h in r.get('konstruk', []):
            if h.get('lulus_muat') is False:  kode_masalah.append('outer_loading')
            if h.get('lulus_ave') is False:   kode_masalah.append('ave')
            if h.get('lulus_cr') is False:    kode_masalah.append('cr')
        vif_i = [float(v['vif']) for v in (r.get('vif_inner') or [])
                 if isinstance(v.get('vif'), (int, float))]
        r['vif_inner_maks'] = max(vif_i) if vif_i else None
        if r['vif_inner_maks'] and r['vif_inner_maks'] > 5:
            kode_masalah.append('vif_inner')
        # Fornell-Larcker + HTMT — DIHITUNG 20Sep26 (dulu sengaja dikosongkan).
        # Mesin sudah mengirim `fornell` & `htmt` dari app/diagnosis.py.
        f_list = r.get('fornell') or []
        r['fornell'] = f_list
        r['fornell_ada_masalah'] = any(x.get('lulus') is False for x in f_list)
        if r['fornell_ada_masalah']:
            kode_masalah.append('fornell')

        h_list = r.get('htmt') or []
        r['htmt'] = h_list
        r['htmt_ada_masalah'] = any(
            x.get('lulus_ketat') is False for x in h_list)
        if r['htmt_ada_masalah']:
            kode_masalah.append('htmt')

        # Jujur: hanya yang BENAR-BENAR belum dihitung yang ditulis di sini.
        r['catatan_belum'] = []
    else:
        if r.get('normalitas', {}).get('lulus') is False:  kode_masalah.append('normalitas')
        if r.get('hetero', {}).get('lulus') is False:      kode_masalah.append('hetero')
        if r.get('vif_maks') and r['vif_maks'] > 10:       kode_masalah.append('vif')
        if r.get('linearitas', {}).get('lulus') is False:  kode_masalah.append('linearitas')
        if r.get('outlier', {}).get('n_y', 0) >= 3:        kode_masalah.append('outlier')
        if r.get('dw') is not None and not (1.5 <= r['dw'] <= 2.5):
            kode_masalah.append('dw')
    r['masalah'] = [{'kode': k, 'nasihat': nasihat.ambil(k, mode)}
                    for k in dict.fromkeys(kode_masalah)]
    r['nasihat_semua'] = {k: nasihat.ambil(k, mode)
                          for k in nasihat.daftar_kode(mode)}
    r['mode'] = mode
    return r


@app.post('/api/diagnosis/periksa')
async def api_diagnosis_periksa(payload: dict):
    """Hitung syarat dari data yang sudah diunggah.

    payload:
      kunci     : kunci dari /unggah
      mode      : 'spss' | 'pls'
      kolom_x   : [nama kolom X…]     (SPSS)
      kolom_y   : nama kolom Y        (SPSS)
      kolom_m   : [nama kolom M…]     (SPSS, opsional)
      konstruk  : {nama: [butir…]}    (PLS)
      kolom_y_konstruk : nama konstruk endogen (PLS)
      missing   : 'buang' | 'rata'    cara menangani sel kosong
    """
    from fastapi import HTTPException
    from app.diagnosis import ambil_sementara, periksa_spss, periksa_pls, GagalBaca
    from app import nasihat

    df = ambil_sementara(payload.get('kunci', ''))
    if df is None:
        raise HTTPException(status_code=400, detail=(
            'Datanya sudah tidak ada di server (mungkin sesi terlalu lama). '
            'Coba unggah ulang ya — sekali klik saja.'))

    mode = str(payload.get('mode', 'spss'))

    # ── PERAN → SKOR KONSTRUK (ACC Bos 21Sep26) ──────────────────────────
    # Beberapa kolom bisa satu peran (X1 = 3 pertanyaan). Digabung jadi SATU
    # skor sebelum dihitung — kalau tidak, mesin melihat 3 variabel, padahal
    # statistiknya satu. Aturan jawaban kosong = Opsi B (rata-rata terjawab
    # × jumlah item) — lihat app/diagnosis.py skor_konstruk().
    df, payload = _gabung_peran(df, payload)

    # ⚠️ AKAR 19Sep26: `buang_kosong` menerima 'baris'/'rata', BUKAN
    # 'buang'/'rata'. Wulan mula-mula MENEBAK nama parameter dan nilainya
    # tanpa membaca tanda tangan fungsinya → HTTP 500 (TypeError). Penerjemahan
    # dari bahasa tampilan → bahasa mesin dilakukan DI SINI, satu tempat.
    # ATURAN: sebelum memanggil fungsi, BACA tanda tangannya (grep "^def").
    missing = str(payload.get('missing', 'buang'))
    buang_kosong = 'rata' if missing == 'rata' else 'baris'
    try:
        if mode == 'pls':
            # ⚠️ periksa_pls TIDAK punya parameter buang_kosong — jangan kirim.
            r = periksa_pls(df, payload.get('konstruk') or {},
                            str(payload.get('kolom_y_konstruk') or ''))
        else:
            r = periksa_spss(df, payload.get('kolom_x') or [],
                             str(payload.get('kolom_y') or ''),
                             kolom_m=payload.get('kolom_m') or [],
                             kolom_z=payload.get('kolom_z') or [],
                             bentuk_mediasi=payload.get('bentuk_mediasi'),
                             buang_kosong=buang_kosong)
    except GagalBaca as e:
        raise HTTPException(status_code=400, detail=str(e))

    r = _hias_hasil(r, mode)

    return JSONResponse(r)


@app.get('/api/unduh')
async def api_unduh(bentuk: str = 'csv', untuk: str = 'spss',
                    pemisah: str = ','):
    """Unduh data siap impor.

    untuk   : 'spss' → nama PANJANG ('Kualitas_Produk_1')  ← bawaan, aman
              'pls'  → kode PENDEK  ('KP1')                ← konvensi SmartPLS
    pemisah : ',' atau ';' (Excel Indonesia sering perlu ';')

    ⚠️ BAWAAN 'spss' SENGAJA dipilih supaya tautan lama tidak berubah
    perilaku — mahasiswa yang sudah menyimpan tautan tidak kaget.
    """
    from fastapi import HTTPException
    from fastapi.responses import Response
    from app.berkas_kerja import ambil_terakhir, ke_csv, ke_xlsx
    d = ambil_terakhir()
    if not d:
        raise HTTPException(status_code=404, detail='Belum ada data. Buat dulu.')

    # Pagar nilai — jangan percaya masukan dari alamat URL.
    untuk = untuk if untuk in ('spss', 'pls') else 'spss'
    pemisah = pemisah if pemisah in (',', ';') else ','
    tanda = 'pls' if untuk == 'pls' else 'spss'

    if bentuk == 'xlsx':
        isi = ke_xlsx(d, untuk=untuk)
        return Response(
            isi, media_type=(
                'application/vnd.openxmlformats-officedocument.'
                'spreadsheetml.sheet'),
            headers={'Content-Disposition':
                     f'attachment; filename="data_{tanda}.xlsx"'})
    isi = ke_csv(d, untuk=untuk, pemisah=pemisah)
    return Response(isi, media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition':
                             f'attachment; filename="data_{tanda}.csv"'})


# ── JEMBATAN EduAi (pintu tanpa sesi, Opsi B) — app/jembatan.py ──
from app.jembatan import buat_router as _buat_router_jembatan
app.include_router(_buat_router_jembatan(_gabung_peran, _hias_hasil))


@app.get('/health')
async def health():
    return {'status': 'ok', 'ai_aktif': ai_aktif()}
