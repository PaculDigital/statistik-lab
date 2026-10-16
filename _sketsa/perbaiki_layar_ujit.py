#!/usr/bin/env python3
"""Perbaiki TATA LETAK kartu Uji t supaya "punya halaman sendiri" seperti tab lain.

⚠️ PERMINTAAN BOS (verbatim, 19Sep26):
   "Uji t itu punya halaman sendiri, dan ketika di klik muncul. Dah seperti itu
    aja. Sederhana kan, seperti tab tab yang lain punya halaman sendiri sendiri,
    begitu di klik tab nya halamannya muncul."
   "kenapa di klik uji t, malah pindah ke bawah."

AKAR (terukur dari CSS + HTML):
   .kamus-kisi = GRID 2 KOLOM  (gaya.css baris 388)
       grid-template-columns: 218px 1fr
   Susunan anaknya:
       [0] .kamus-daftar  (pita tombol, 218px)
       [1] .papan         (ISI kamus, kolom 1fr)
       [2] <section kartu-ujit>   ← otomatis MENDARAT DI BARIS KE-2 KOLOM 218px
   ⇒ kartu Uji t TURUN KE BAWAH (di desktop: baris baru kolom sempit;
     di HP 1 kolom: setelah .papan) = persis keluhan Bos "malah pindah ke bawah".

OBAT (dua bagian, keduanya wajib):
   A. CSS: .kartu-ujit { grid-column: 2; grid-row: 1; }  → kartu MENEMPATI
      kolom isi pada baris yang SAMA dengan .papan (menggantikan posisinya).
      Di HP (1 kolom) aturan ini tidak merusak: grid-column:2 tak berlaku,
      otomatis jatuh ke 1 kolom.
   B. JS: saat "ujit" dipilih → sembunyikan .papan (bukan seluruh .kamus-kisi,
      karena pita tombol ada di dalam .kamus-kisi dan harus TETAP terlihat),
      lalu tampilkan kartu. Saat istilah lain dipilih → kebalikannya.

CATATAN: .papan punya `grid-column` bawaan? → TIDAK (hanya 816 & 944 milik
   aturan lain). Jadi menambah grid-column pada .kartu-ujit aman.
"""
import pathlib
import re

CSS = pathlib.Path('/opt/data/services/statistik-lab/app/static/gaya.css')
HTML = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CAD_CSS = pathlib.Path('/tmp/gaya_cadangan_layar_ujit.css')
CAD_HTML = pathlib.Path('/tmp/belajar_cadangan7.html')


def perbaiki_css():
    s = CSS.read_text(encoding='utf-8')
    CAD_CSS.write_text(s, encoding='utf-8')
    print(f'cadangan CSS → {CAD_CSS} ({len(s)} byte)')

    lama = '.kartu-ujit { margin-top: 4px; }'
    if lama not in s:
        print('❌ baris .kartu-ujit tidak ketemu — BATAL')
        return False
    baru = """/* ⚠️ AKAR (19Sep26) — Bos: "klik uji t malah pindah ke bawah. Dia itu posisinya
   sama seperti tab tab disampingnya."
   .kamus-kisi adalah GRID `218px 1fr`. Tanpa aturan di bawah ini, <section
   kartu-ujit> otomatis MENDARAT KE BARIS KE-2 (di bawah .papan) = TURUN.
   Dengan menempatkannya di grid-column 2 / grid-row 1, kartu MENEMPATI KOLOM ISI
   pada baris yang SAMA — jadi terlihat "punya halaman sendiri", menggantikan
   panel kamus di tempat yang sama. Di HP (1 kolom) aturan ini netral. */
.kartu-ujit { margin-top: 4px; grid-column: 2; grid-row: 1; }
@media (max-width: 820px) { .kartu-ujit { grid-column: auto; grid-row: auto; } }"""
    s2 = s.replace(lama, baru)

    # verifikasi kurung tetap seimbang
    buka, tutup = s2.count('{'), s2.count('}')
    print(f'  kurung: {{={buka} }}={tutup} (harus sama & tetap {s.count("{")})')
    if buka != tutup:
        print('❌ kurung tidak seimbang — BATAL')
        return False
    CSS.write_text(s2, encoding='utf-8')
    print(f'  ✅ CSS ditulis ({len(s2)} byte, +{len(s2)-len(s)})')
    return True


def perbaiki_html():
    s = HTML.read_text(encoding='utf-8')
    CAD_HTML.write_text(s, encoding='utf-8')
    print(f'cadangan HTML → {CAD_HTML} ({len(s)} byte)')

    # Ganti blok if (k === 'ujit') supaya menyembunyikan .papan (BUKAN .kamus-kisi)
    lama = """  const kartu = document.getElementById('kartu-ujit');
  const panelKamus = document.querySelector('.kamus-kisi');
  if (k === 'ujit') {
    if (panelKamus) panelKamus.hidden = true;
    if (kartu) kartu.hidden = false;
    document.querySelectorAll('.kamus-tombol').forEach(b =>
      b.classList.toggle('aktif', b.dataset.k === k));
    return;
  }
  if (panelKamus) panelKamus.hidden = false;
  if (kartu) kartu.hidden = true;"""
    if lama not in s:
        print('❌ blok pilih() tidak ketemu PERSIS — BATAL')
        return False
    baru = """  const kartu = document.getElementById('kartu-ujit');
  // ⚠️ AKAR (19Sep26) — yang disembunyikan WAJIB `.papan` (panel ISI), BUKAN
  // `.kamus-kisi`, karena pita tombol istilah ada DI DALAM .kamus-kisi. Kalau
  // seluruh .kamus-kisi disembunyikan, tombolnya ikut hilang → user tidak bisa
  // pindah ke istilah lain lagi. Bos minta: "seperti tab tab yang lain" — pita
  // tetap ada, hanya ISI-nya yang berganti.
  const panelKamus = document.querySelector('#tab-1 .papan');
  if (k === 'ujit') {
    if (panelKamus) panelKamus.hidden = true;
    if (kartu) kartu.hidden = false;
    document.querySelectorAll('.kamus-tombol').forEach(b =>
      b.classList.toggle('aktif', b.dataset.k === k));
    return;
  }
  if (panelKamus) panelKamus.hidden = false;
  if (kartu) kartu.hidden = true;"""
    s2 = s.replace(lama, baru)

    # Hapus fungsi bawaKeAtas (sisa) — tidak dipakai lagi
    s2 = re.sub(r"/\* ⚠️ AKAR YANG DITUTUP \(19Sep26, TERUKUR — keluhan Bos:.*?\n\}\n",
                """/* ⚠️ CATATAN (19Sep26): fungsi bawaKeAtas() DIHAPUS — itu tambalan yang
   salah. Wulan sempat menyelesaikan gejala "kartu tidak terlihat" dengan
   MENGGULIR OTOMATIS, padahal Bos minta kartunya "punya halaman sendiri"
   (isi berganti DI TEMPAT, seperti tab lain). Akar sebenarnya = tata letak
   grid: kartu duduk di baris ke-2. Obatnya di CSS (.kartu-ujit grid-column:2)
   + menyembunyikan .papan yang benar, BUKAN menggulir. */
""", s2, flags=re.DOTALL)

    HTML.write_text(s2, encoding='utf-8')

    print('\n── VERIFIKASI ──')
    print(f'  ukuran: {len(s)} → {len(s2)} byte')
    print(f'  <script> {s2.count("<script>")} / </script> {s2.count("</script>")}')
    print(f'  <section {s2.count("<section")} / </section> {s2.count("</section>")}')
    print(f'  {{% block {s2.count("{% block")} / {{% endblock {s2.count("{% endblock")}')
    print(f'  bawaKeAtas: {s2.count("bawaKeAtas")} (harus 0)')
    print(f'  #tab-1 .papan dipakai: {"#tab-1 .papan" in s2}')
    print(f'  .kamus-kisi TIDAK disembunyikan: '
          f'{"panelKamus.hidden = true" in s2 and "querySelector(\'.kamus-kisi\')" not in s2}')
    return True


if __name__ == '__main__':
    ok_css = perbaiki_css()
    print()
    ok_html = perbaiki_html()
    print(f'\nHASIL: CSS {"OK" if ok_css else "GAGAL"} · HTML {"OK" if ok_html else "GAGAL"}')
