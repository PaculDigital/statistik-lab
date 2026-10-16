"""Tambah TAB KE-3 "Baca Grafik" di BELAJAR — pindahkan 7 kartu dari /syarat.

KEPUTUSAN BOS (20Sep26): nama tab = "Baca Grafik"; /syarat DIALIHKAN
(bukan dihapus) supaya tautan lama dari /belajar, /kuantitatif, /segera
tetap hidup.

⚠️ ATURAN SISIP (pelajaran 20Sep26, WAJIB):
  · baca berkas UTUH, hitung penanda DULU (harus tepat 1×)
  · cadangan dulu (berkas .cadangan_tab3)
  · JANGAN menulis tanda kurung Jinja di dalam komentar JS
     → Jinja tetap membacanya sebagai perintah (halaman MATI, 19Sep26)
  · JANGAN menulis tag penutup HTML berkurung siku di dalam komentar JS
     → gerbang_tag_skrip.py membacanya sebagai kode tumpah (19Sep26)
  · setelah selesai: buktikan dengan grep + jalankan gerbang

ISI YANG DIPINDAH (dari syarat.html, teks APA ADANYA):
  A. Dipakai di SPSS dan SmartPLS  — 4 kartu
     ① Sisa tersebar rata?      (heteroskedastisitas)
     ② Sisa menyebar normal?    (normalitas)
     ③ Bentuknya garis lurus?   (linearitas)
     ④ Antar variabel tidak mirip? (multikolinearitas / VIF)
  B. Khas SmartPLS — 3 kartu
     ⑤ Bobot item cukup kuat?   (outer loading)
     ⑥ Rata-rata item mewakili? (AVE)
     ⑦ Jawaban konsisten?       (composite reliability)
  ⇒ Total 7 kartu, ke-7 masih memakai grafik CONTOH TETAP (statis).
     Grafik HIDUP (dari data user) ada di /klinik — itu pembagian perannya.

⚠️ Yang SENGAJA TIDAK diubah: grafik di dalam kartu tetap contoh tetap.
   Alasannya: halaman BELAJAR = tempat MEMBACA bentuk; kalau grafiknya
   berubah-ubah mengikuti data terakhir, mahasiswa yang belum paham jadi
   bingung. Grafik hidup ada di /klinik (ALAT), di mana mahasiswa SUDAH
   membawa datanya sendiri.
"""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
F_BELAJAR = ROOT / 'app' / 'templates' / 'belajar.html'
F_SYARAT = ROOT / 'app' / 'templates' / 'syarat.html'

t = F_BELAJAR.read_text(encoding='utf-8')
s = F_SYARAT.read_text(encoding='utf-8')
shutil.copy(F_BELAJAR, F_BELAJAR.with_name('belajar.html.cadangan_tab3'))
sebelum = len(t)

# ══ 1. AMBIL isi kartu dari syarat.html (dari <h2>A...</h2> sampai sebelum
#      blok penutup "Masih disiapkan" + catatan kaki)
A = s.find('<h2 style="font-size:17px;margin:0 0 4px">A. Dipakai di SPSS')
if A == -1:
    raise SystemExit('  ❌ tidak menemukan bagian A di syarat.html')
# akhir: <div class="kartu" style="margin-top:26px"> (kotak catatan kaki)
Z = s.find('<div class="kartu" style="margin-top:26px">', A)
if Z == -1:
    raise SystemExit('  ❌ tidak menemukan penutup bagian di syarat.html')
ISI_KARTU = s[A:Z].rstrip()

# HITUNG kartu — 7 kartu BACAAN (ke-8 = "Masih disiapkan", itu PENANDA
# pekerjaan belum selesai, bukan kartu bacaan — dibuang, di tab baru sudah
# ada kotak "coba dengan datamu" sebagai gantinya).
n_semua = ISI_KARTU.count('class="kartu-syarat"')
print(f'  isi kartu diambil: {len(ISI_KARTU)} karakter, {n_semua} kartu')
if n_semua != 8:
    raise SystemExit(f'  ❌ kartu ketemu {n_semua} (harus 8 termasuk penanda) — DIBATALKAN')

# buang kartu ke-8 "Masih disiapkan" — dari komentarnya sampai penutupnya
LAMA_K8 = """  {# ── 8. PENANDA PEKERJAAN BERIKUTNYA ── #}"""
K8 = ISI_KARTU.find('Masih disiapkan')
if K8 == -1:
    raise SystemExit('  ❌ kartu "Masih disiapkan" tidak ketemu — DIBATALKAN')
# mundur ke awal <div class="kartu-syarat"> terakhir
awal_k8 = ISI_KARTU.rfind('<div class="kartu-syarat"', 0, K8)
if awal_k8 == -1:
    raise SystemExit('  ❌ awal kartu ke-8 tidak ketemu — DIBATALKAN')
ISI_KARTU = ISI_KARTU[:awal_k8].rstrip()
n_kartu = ISI_KARTU.count('class="kartu-syarat"')
print(f'  → dibuang kartu "Masih disiapkan"; sisa {n_kartu} kartu bacaan')
if n_kartu != 7:
    raise SystemExit(f'  ❌ sisa kartu {n_kartu} (harus 7) — DIBATALKAN')

# buang penanda "masih disiapkan" yang sudah tidak relevan (kartu ke-7)
ISI_KARTU = ISI_KARTU.replace(
    ' style="border-style:dashed;opacity:.85"', '')

# ══ 2. PITA TAB: tambah tombol ke-3 ═══════════════════════════════════════
LAMA_PITA = """  <a href="#tab-2" id="pa-2" role="tab" onclick="bukaTab(2);return false">
    {{ ikon('flask-conical', 15) }} Ruang Uji <span class="biji">2</span>"""
BARU_PITA = """  <a href="#tab-2" id="pa-2" role="tab" onclick="bukaTab(2);return false">
    {{ ikon('flask-conical', 15) }} Ruang Uji <span class="biji">2</span>
  </a>
  <a href="#tab-3" id="pa-3" role="tab" onclick="bukaTab(3);return false">
    {{ ikon('line-chart', 15) }} Baca Grafik <span class="biji">7</span>"""
c = t.count(LAMA_PITA)
if c != 1:
    raise SystemExit(f'  ❌ penanda pita ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_PITA, BARU_PITA, 1)

# ══ 3. bukaTab: [1,2] → [1,2,3] dan regex hash ════════════════════════════
LAMA_FN = """  [1, 2].forEach(function (i) {"""
BARU_FN = """  [1, 2, 3].forEach(function (i) {"""
c = t.count(LAMA_FN)
if c != 1:
    raise SystemExit(f'  ❌ penanda bukaTab ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_FN, BARU_FN, 1)

LAMA_HASH = """  const m = (location.hash || '').match(/tab-([12])/);"""
BARU_HASH = """  const m = (location.hash || '').match(/tab-([123])/);"""
c = t.count(LAMA_HASH)
if c != 1:
    raise SystemExit(f'  ❌ penanda hash ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_HASH, BARU_HASH, 1)

# ══ 4. PANEL tab-3 — sisip setelah penutup tab-2 ═══════════════════════════
LAMA_PANEL = """</div><!-- /tab-2 -->"""
BARU_PANEL = """</div><!-- /tab-2 -->

{# ═══ TAB 3 — BACA GRAFIK (Tahap 2, ACC Bos 20Sep26) ═══════════════════
   Isinya dipindah UTUH dari halaman Periksa Syarat: 7 kartu cara MEMBACA
   bentuk grafik. Halaman Periksa Syarat dialihkan ke sini (tidak dihapus)
   supaya tautan lama tetap hidup.

   ⚠️ Kenapa grafiknya tetap CONTOH TETAP (bukan grafik hidup seperti di
   KLINIK): halaman ini tempat MEMBACA bentuk — kalau grafiknya berubah
   mengikuti data terakhir yang diunggah, mahasiswa yang belum paham justru
   bingung. Grafik hidup ada di DIAGNOSIS DATA, di mana mahasiswa sudah
   membawa datanya sendiri. Satu tempat, satu pertanyaan. #}
<div id="tab-3" role="tabpanel" hidden>
  <h1 style="margin:0 0 8px">Baca Grafik</h1>
  <p class="samar" style="font-size:14px;margin:0 0 20px">
    Tujuh gambar di bawah ini adalah bentuk yang kamu temui di SPSS dan
    SmartPLS. Kenali <strong>bentuknya</strong> dulu — nanti di halaman
    {{ '' }}<a href="/klinik">Diagnosis Data</a>, grafik yang sama digambar
    dari <strong>datamu sendiri</strong>.
  </p>

  <div class="kartu" style="margin:0 0 26px;border-left:3px solid var(--amber)">
    <p style="margin:0;font-size:13.5px;line-height:1.65">
      <strong>Contoh di halaman ini sengaja dipilih yang sehat.</strong>
      Kalau kamu ingin melihat data yang <strong>bermasalah</strong>,
      buka <a href="/klinik">Diagnosis Data</a> lalu tekan tombol
      &ldquo;Lihat contoh data bermasalah&rdquo; — di sana grafiknya
      digambar dari data, jadi corongnya benar-benar kelihatan.
    </p>
  </div>

""" + ISI_KARTU + """

  <div class="kartu" style="margin-top:26px">
    <h3 style="margin:0 0 6px">{{ ikon('settings', 15) }} Sudah tahu bentuknya? Coba dengan datamu</h3>
    <p style="margin:0 0 12px;color:#6B6259">
      Bawa berkasmu ke halaman Diagnosis Data — di sana grafik yang sama
      digambar dari datamu, lengkap dengan angka dan jalan keluarnya
      kalau ada yang bermasalah.
    </p>
    <a href="/klinik" class="tb tb-utama">{{ ikon('stethoscope', 15) }} Periksa dataku</a>
  </div>
</div><!-- /tab-3 -->"""
c = t.count(LAMA_PANEL)
if c != 1:
    raise SystemExit(f'  ❌ penanda panel ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_PANEL, BARU_PANEL, 1)

# ══ 5. PERIKSA AKHIR sebelum menulis ══════════════════════════════════════
# (a) tanda kurung Jinja di dalam komentar JS? — 19Sep26 pernah mematikan halaman
blok_skrip = t[t.find('{% block skrip %}'):]
pola_jinja_di_komentar = re.findall(r'/\*[^*]*\{%', blok_skrip)
if pola_jinja_di_komentar:
    raise SystemExit('  ❌ ada {% di dalam komentar JS — DIBATALKAN (halaman bisa mati)')

F_BELAJAR.write_text(t, encoding='utf-8')
print(f'  ✅ belajar.html: {sebelum} → {len(t)} karakter (+{len(t) - sebelum})')
print(f'  ✅ tab ke-3 "Baca Grafik" ditambah · {n_kartu} kartu dipindah')
print('  ✅ bukaTab jadi [1,2,3] · hash jadi /tab-([123])/')
print()
print('  ⚠️ BELUM: mengalihkan /syarat — itu langkah berikutnya (berkas lain).')
