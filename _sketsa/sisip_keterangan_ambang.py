#!/usr/bin/env python3
"""Sisip bagian KETERANGAN AMBANG SIG. (slider) di PALING ATAS kartu Uji t.

PERMINTAAN BOS (verbatim, 19Sep26):
  "saya mau tambahkan di paling atas keterangan. Beri keterangan dari teori bahwa
   signifikan itu 0,05. Jadi kadang mahasiswa bingung 0.0008 itu masuk signifikan
   atau tidak dan besar mana 0,5 dengan 0,05 kadang bingung apalagi hasilnya negatif."
  "kamu buat sebuah slider untuk visualisasinya. Dan tambahkan teori dari mana
   datangnya 0,05 itu teori siapa, dan ada juga yang mengatakan ambang tidak 0,05
   tapi 0,07 dll."
  ACC: 1=A (slider + kotak isian) · 2=(i) paling atas · 3=rentang 0,000–0,50 (OPSI A)

RANCANGAN (ACC lewat sketsa _sketsa/sketsa_ambang_sig.html):
  TIGA bagian di dalam SATU panel baru, ditaruh SEBELUM "Langkah 1 Buka tabel":
    ① SLIDER: kotak isian angka Sig. + garis bilangan 0–0,50 + batas 0,05 bergaris
       + kotak jawaban otomatis (SIGNIFIKAN / MARGINAL / TIDAK SIGNIFIKAN)
    ② TANDA MINUS: tabel Sig. vs B + 2 tombol tanda + 3 contoh angka minus
    ③ TEORI: Fisher 1925 + Amrhein dkk. 2019 + ambang ikut bidang (3 baris tabel)

⚠️ 2 CACAT SKETSA YANG WAJIB DIPERBAIKI (ditemukan lewat vision 19Sep26):
   (a) penanda angka menimpa label "batas 0,05" kalau posisinya berdekatan
       → label batas ditaruh DI ATAS, penanda angka DI BAWAH garis (dua jalur beda)
   (b) teks tabel kepotong → kolom "Bisa minus?" dipendekkan isinya

CARA SISIP: cari penanda teks PERSIS di berkas, potong balik ke batas baris,
sisipkan blok baru sebelum baris itu. Semua nama kelas CSS yang dipakai sudah
DIPERIKSA ADA (grep): .papan, .baris-antara, .pita, .samar, .medan, .catatan.
Kelas BARU yang dibuat di sini semua berawalan `amb-` supaya tidak bentrok.
"""
import pathlib

HTML = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CAD = pathlib.Path('/tmp/belajar_cadangan8.html')

# ─────────────────────────────────────────────────────────────
# BLOK HTML — bagian keterangan (ditaruh sebelum "Langkah 1")
# ─────────────────────────────────────────────────────────────
BLOK = '''  {# ══════════════════════════════════════════════════════════════════════════
     KETERANGAN AMBANG SIG. (19Sep26, ACC Bos) — ditaruh di PALING ATAS kartu
     Uji t supaya mahasiswa paham batas 0,05 SEBELUM membaca hasil apa pun.
     Tiga bagian: ① slider+penerjemah  ② tanda minus  ③ teori asal-usul 0,05.
     Alasan: mahasiswa lemah membandingkan angka (0,1 vs 0,05) dan bingung
     apakah hasil negatif berarti tidak signifikan.
     Sketsa yang di-ACC: _sketsa/sketsa_ambang_sig.html
     ══════════════════════════════════════════════════════════════════════ #}
  <div class="papan" id="amb-panel">
    <span class="pita">baca ini dulu</span>
    <h2 style="margin:8px 0 4px;font-size:17px">Sebelum membaca hasilmu</h2>
    <p style="font-size:12.5px;color:var(--tinta-2);margin:0 0 14px;line-height:1.6">
      <strong>Patokan baku: Sig. &lt; 0,05 = signifikan.</strong>
      Angka Sig. makin <strong>kecil</strong>, buktinya makin <strong>kuat</strong>.
      Masukkan angka Sig. dari SPSS-mu — lihat sendiri dia jatuh di kiri atau kanan
      batas.</p>

    <!-- ① kotak isian -->
    <div class="amb-masuk">
      <label for="amb-sig">Angka Sig. hasilmu</label>
      <input id="amb-sig" type="text" inputmode="decimal" value="0,008"
             autocomplete="off" aria-label="Angka Sig hasil penelitian">
      <span class="samar">ketik · atau geser di bawah</span>
    </div>

    <!-- ① garis bilangan -->
    <div class="amb-garis">
      <div class="amb-jalur"></div>
      <div class="amb-batas" style="left:10%">
        <span class="amb-batas-lbl">batas 0,05</span>
      </div>
      <div class="amb-tanda" style="left:0%">0</div>
      <div class="amb-tanda" style="left:10%">0,05</div>
      <div class="amb-tanda" style="left:20%">0,10</div>
      <div class="amb-tanda" style="left:50%">0,25</div>
      <div class="amb-tanda" style="left:100%">0,50</div>
      <div class="amb-pin" id="amb-pin" style="left:1.6%">
        <div class="amb-tangkai"></div>
        <div class="amb-nilai" id="amb-nilai">0,008</div>
      </div>
    </div>

    <div class="medan" style="margin:12px 0 0">
      <input type="range" id="amb-geser" min="0" max="500" value="8"
             aria-label="Geser angka Sig">
      <div class="baris-antara" style="margin-top:2px">
        <span class="samar">0,000 — bukti kuat</span>
        <span class="samar">0,50 — bukti lemah</span>
      </div>
    </div>

    <div class="catatan" id="amb-jawab" style="margin-top:14px"></div>

    <p style="font-size:12px;color:var(--tinta-3);margin:12px 0 0;line-height:1.55">
      ⚠️ Dua hal yang paling sering ketuker: <strong>0,5</strong> itu 10×
      <strong>lebih besar</strong> dari 0,05 — jadi 0,5 jauh di kanan batas.
      Dan angka Sig. <strong>tidak pernah minus</strong> (selalu 0 sampai 1).</p>
  </div>

  {# ── ② TANDA MINUS — dipisah supaya tidak tercampur dengan Sig. ── #}
  <div class="papan">
    <h2 style="margin:0 0 4px;font-size:17px">Tanda B ( − ) itu bukan tanda gagal</h2>
    <p style="font-size:12.5px;color:var(--tinta-2);margin:0 0 10px;line-height:1.6">
      Di tabel SPSS ada <strong>dua kolom berbeda</strong> pada baris yang sama.
      Jangan dibaca jadi satu:</p>

    <table class="amb-tbl">
      <tr><th>Kolom</th><th>Bisa minus?</th><th>Artinya</th></tr>
      <tr>
        <td><strong>Sig.</strong></td>
        <td class="amb-merah">Tidak (0–1)</td>
        <td>Peluang kebetulan → <strong>penentu signifikan</strong></td>
      </tr>
      <tr>
        <td><strong>B</strong></td>
        <td class="amb-hijau">Bisa (− / +)</td>
        <td><strong>Arah</strong> pengaruh (naik / turun) — <strong>bukan</strong> penentu signifikan</td>
      </tr>
    </table>

    <p style="font-size:12.5px;color:var(--tinta-2);margin:12px 0 6px;line-height:1.6">
      Tiga angka di bawah ini <strong>minus semua</strong> — tapi nasibnya beda.
      Yang menentukan <strong>Sig.</strong>, bukan tandanya:</p>

    <div class="amb-tiga">
      <div class="amb-contoh">
        <div class="amb-angka">−0,368</div>
        <div class="amb-lbl amb-lbl-hijau">Sig 0,008 · SAH</div>
      </div>
      <div class="amb-contoh">
        <div class="amb-angka">−0,380</div>
        <div class="amb-lbl amb-lbl-kuning">Sig 0,062 · di batas</div>
      </div>
      <div class="amb-contoh">
        <div class="amb-angka">−0,115</div>
        <div class="amb-lbl amb-lbl-abu">Sig 0,310 · tidak</div>
      </div>
    </div>

    <div class="catatan" style="margin-top:12px">
      Jadi: <strong>−0,368 dengan Sig. 0,008 tetap SIGNIFIKAN</strong> — minusnya cuma
      berarti arahnya turun (makin tinggi X, makin turun Y).</div>
  </div>

  {# ── ③ TEORI — dari mana angka 0,05 ── #}
  <div class="papan">
    <h2 style="margin:0 0 10px;font-size:17px">Kenapa 0,05? Dari mana angka itu?</h2>

    <div class="amb-teori">
      <h3>① R. A. Fisher (1925) — asal angkanya</h3>
      <p>Dalam <em>Statistical Methods for Research Workers</em>, Fisher mengusulkan
        patokan <strong>“1 dari 20” (0,05)</strong> sebagai alat bantu kerja supaya
        peneliti tidak bingung menentukan batas.</p>
      <blockquote>“Batas 0,05 itu hanya kebiasaan — tidak ada dasar ilmiah untuk
        memilih 0,05 dibanding 0,06.”<br>
        <span class="amb-kutip-siapa">— R. A. Fisher</span></blockquote>
    </div>

    <div class="amb-teori">
      <h3>② Amrhein, Greenland &amp; McShane (2019, <em>Nature</em>) — cara pakainya</h3>
      <p>Ditandatangani 800+ ilmuwan: <strong>0,05 bukan tembok “ada / tidak ada
        pengaruh”.</strong> Angka 0,049 dan 0,051 hampir sama saja — satu tidak
        otomatis “berhasil” dan yang lain “gagal”. Nilai p juga <strong>tidak
        mengukur seberapa besar</strong> pengaruhnya, hanya seberapa kuat buktinya.</p>
    </div>

    <p style="font-size:12.5px;color:var(--tinta-2);margin:14px 0 6px;line-height:1.6">
      <strong>Karena itu: ambang ikut bidang penelitian.</strong></p>
    <table class="amb-tbl">
      <tr><th>Bidang</th><th>Ambang lazim</th></tr>
      <tr><td>Ekonomi, sosial, pendidikan (skripsi/tesis)</td><td><strong>0,05</strong></td></tr>
      <tr><td>Kedokteran / uji klinis</td><td><strong>0,01</strong></td></tr>
      <tr><td>Eksplorasi / uji pendahuluan</td><td><strong>0,10</strong></td></tr>
    </table>
    <p style="font-size:12px;color:var(--tinta-3);margin:10px 0 0;line-height:1.6">
      <strong>0,05 itu kesepakatan lapangan, bukan angka dari langit.</strong>
      Yang salah bukan angkanya — yang salah kalau ambangnya digeser
      <strong>supaya hasilmu kelihatan signifikan</strong>.</p>
  </div>

'''


def utama():
    s = HTML.read_text(encoding='utf-8')
    CAD.write_text(s, encoding='utf-8')
    print(f'cadangan → {CAD} ({len(s)} byte)')

    if 'id="amb-panel"' in s:
        print('⚠️ bagian ini SUDAH ADA — batal (jangan sisip dua kali)')
        return

    # ── cari titik sisip: tepat SEBELUM <div class="ujit-langkah"> ──
    penanda = '<div class="ujit-langkah">'
    i = s.find(penanda)
    if i < 0:
        print('❌ penanda ujit-langkah tidak ketemu — BATAL')
        return
    # mundur ke awal baris (termasuk indentasi)
    awal_baris = s.rfind('\n', 0, i) + 1
    print(f'titik sisip: byte {awal_baris} (baris ke-{s[:awal_baris].count(chr(10))+1})')

    hasil = s[:awal_baris] + BLOK + s[awal_baris:]
    HTML.write_text(hasil, encoding='utf-8')

    # ── VERIFIKASI ──
    print('\n── VERIFIKASI HTML ──')
    print(f'  ukuran: {len(s)} → {len(hasil)} byte (+{len(hasil)-len(s)})')
    print(f'  <script> {hasil.count("<script>")} / </script> {hasil.count("</script>")}'
          ' <- harus 1 & 1')
    print(f'  blok jinja: {hasil.count("{% block")} / {hasil.count("{% endblock")}'
          ' <- harus 2 & 2')
    print(f'  <div> {hasil.count("<div")} / </div> {hasil.count("</div>")}'
          ' ← harus seimbang')
    print(f'  <section {hasil.count("<section")} / </section> {hasil.count("</section>")}')
    print(f'  id="amb-panel" : {hasil.count(chr(34)+"amb-panel"+chr(34))}×')
    for k in ['amb-sig', 'amb-geser', 'amb-pin', 'amb-jawab', 'amb-nilai']:
        print(f'  {"✅" if k in hasil else "❌"} id {k}')
    # urutan: amb-panel HARUS sebelum ujit-langkah
    a = hasil.find('id="amb-panel"')
    b = hasil.find('ujit-langkah')
    print(f'  {"✅" if 0 < a < b else "❌"} amb-panel ({a}) DI ATAS ujit-langkah ({b})')


if __name__ == '__main__':
    utama()
