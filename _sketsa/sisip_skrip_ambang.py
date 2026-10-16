#!/usr/bin/env python3
"""Sisip SKRIP slider ambang Sig. + KETERANGAN di dalam <script> belajar.html.

⚠️ JEBAKAN URUTAN PEMUATAN (pelajaran mahal, jangan ulang):
   Di berkas ini, `pilih('hetero')` HARUS dipanggil PALING BAWAH karena `let`
   di bawah tidak boleh dipakai di atas. Skrip baru ini TIDAK memakai variabel
   `ujit*` maupun `kunci`, jadi aman — TAPI tetap diletakkan di paling bawah,
   tepat SEBELUM `</script>`, supaya urutannya tidak bisa mengejutkan.

⚠️ DILARANG menulis `</script>` (walau di dalam komentar) — gerbang
   gerbang_tag_skrip.py akan menandainya sebagai penutup tag. Kalau perlu
   menyebutnya, tulis "tag penutup skrip".

CARA KERJA SLIDER (ACC Bos):
   rentang 0,000–0,50 (OPSI A) — batas 0,05 diberi garis tegak, semua angka
   bisa digeser. Kotak isian & slider saling mengikuti.
   Ambang 3 jawaban: <0,05 SIGNIFIKAN (hijau) · 0,05–0,10 MARGINAL (amber)
   · >0,10 TIDAK SIGNIFIKAN (abu).
"""
import pathlib

HTML = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CAD = pathlib.Path('/tmp/belajar_cadangan9.html')

BLOK = '''
/* ══════════════════════════════════════════════════════════════════════════
   KETERANGAN AMBANG SIG. (19Sep26, ACC Bos) — slider pembanding.
   Tujuan: mahasiswa LEMAH membandingkan angka. Mereka tidak yakin apakah hasil
   0,008 itu lebih kecil atau lebih besar dari 0,05 → signifikan atau tidak.
   Slider ini menunjukkan POSISI angka hasil temuan terhadap garis batas 0,05.
   Rentang 0,000–0,50 (OPSI A) — batas 0,05 tetap bergaris, semua bisa digeser.
   ══════════════════════════════════════════════════════════════════════════ */
function ambGambar(v) {
  v = Math.max(0, Math.min(0.50, v));
  const persen = (v / 0.50) * 100;
  const teks = v.toFixed(3).replace('.', ',');

  const pin = document.getElementById('amb-pin');
  const nilai = document.getElementById('amb-nilai');
  const jawab = document.getElementById('amb-jawab');
  if (pin) pin.style.left = persen + '%';
  if (nilai) nilai.textContent = teks;
  if (!jawab) return;

  let besar, ket, kelas;
  if (v < 0.05) {
    besar = 'Sig. ' + teks + ' → SIGNIFIKAN';
    ket = teks + ' <strong>lebih kecil</strong> dari batas 0,05 → pengaruhnya ' +
          'nyata, bukan kebetulan.' +
          (v > 0 && v < 0.01 ? ' Angka sekecil ini biasanya ditulis p &lt; 0,001.' : '');
    kelas = ' hijau';
  } else if (v <= 0.10) {
    besar = 'Sig. ' + teks + ' → MARGINAL';
    ket = 'Hasilnya <strong>di batas</strong> (0,05–0,10). Perlu dibahas ' +
          'hati-hati — jangan dipaksa jadi signifikan.';
    kelas = ' kuning';
  } else {
    besar = 'Sig. ' + teks + ' → TIDAK SIGNIFIKAN';
    ket = teks + ' <strong>lebih besar</strong> dari batas 0,05 → belum cukup ' +
          'bukti. Tandanya juga belum bisa dipakai.';
    kelas = ' abu';
  }
  jawab.className = 'catatan amb-jawab-' + kelas.trim();
  jawab.innerHTML = '<div class="amb-besar">' + besar + '</div>' +
                    '<div class="amb-ket">' + ket + '</div>';
}

(function ambPasang() {
  const inp = document.getElementById('amb-sig');
  const ges = document.getElementById('amb-geser');
  if (!inp || !ges) return;

  ges.addEventListener('input', function () {
    const v = parseInt(this.value, 10) / 1000;
    inp.value = v.toFixed(3).replace('.', ',');
    ambGambar(v);
  });

  function dariKotak() {
    // terima "0,008" maupun "0.008"; juga "0,00 8" dan spasi lain
    const v = parseFloat(String(inp.value).replace(',', '.').replace(/[^0-9.]/g, ''));
    if (isNaN(v)) return;
    ges.value = Math.round(Math.max(0, Math.min(0.50, v)) * 1000);
    ambGambar(Math.max(0, Math.min(0.50, v)));
  }
  inp.addEventListener('input', dariKotak);
  inp.addEventListener('change', dariKotak);
  // kalau user tekan Enter, hilangkan fokus supaya papan angka HP menutup
  inp.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { e.preventDefault(); this.blur(); dariKotak(); }
  });

  ambGambar(0.008);
})();
'''

PENANDA = "ujitLot();\nujitIsi();\npilih('hetero');\n"
PENGGANTI = ("ujitLot();\nujitIsi();\npilih('hetero');\n" + BLOK)


def utama():
    s = HTML.read_text(encoding='utf-8')
    CAD.write_text(s, encoding='utf-8')
    print(f'cadangan → {CAD} ({len(s)} byte)')

    if 'function ambGambar' in s:
        print('⚠️ skrip ambGambar SUDAH ADA — batal')
        return

    if PENANDA not in s:
        print('❌ penanda ekor skrip tidak ketemu PERSIS — BATAL')
        return
    hasil = s.replace(PENANDA, PENGGANTI, 1)

    HTML.write_text(hasil, encoding='utf-8')

    print(f'ukuran: {len(s)} → {len(hasil)} byte (+{len(hasil)-len(s)})')
    print('\n── VERIFIKASI ──')
    print(f'  <script> {hasil.count("<script>")} / </script> {hasil.count("</script>")}'
          ' <- harus 1 & 1')
    n = hasil.count('</scr' + 'ipt>')
    print(f'  tag penutup skrip di dalam JS: {hasil.count(PENANDA)-1} '
          f'(di luar tag asli)')
    print(f'  jinja: {hasil.count("{% block")} / {hasil.count("{% endblock")}')
    print(f'  <div {hasil.count("<div")} / </div> {hasil.count("</div>")}')
    for k in ['function ambGambar', 'ambPasang', "getElementById('amb-sig')",
              "getElementById('amb-geser')", "getElementById('amb-jawab')"]:
        print(f'  {"✅" if k in hasil else "❌"} {k}')
    # urutan: ambGambar HARUS sebelum panggilan ambPasang & sesudah semua fungsi ujit
    a = hasil.find('function ambGambar')
    b = hasil.find('let ujitAktif')
    c = hasil.find('</script>')
    print(f'  posisi: ambGambar={a} · ujitAktif={b} · tutupSkrip={c}')
    print(f'  {"✅" if b < a < c else "❌"} ambGambar SESUDAH ujitAktif & SEBELUM '
          f'tag penutup (urutan aman)')


if __name__ == '__main__':
    utama()
