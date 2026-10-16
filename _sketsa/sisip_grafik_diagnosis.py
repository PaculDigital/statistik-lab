"""Sisip GRAFIK HIDUP ke kartu Normalitas + Hetero di diagnosis.html.

⚠️ ATURAN SISIP (pelajaran 20Sep26, jangan ulang):
  · Baca berkas UTUH, hitung penanda DULU.
  · Penanda WAJIB memuat PEMBUKA + PENUTUP blok — jangan potong separuh.
  · Bikin cadangan `*.cadangan_grafik` sebelum menulis.
  · Sesudah menulis: buktikan dengan grep + UKURAN berkas (sed bisa gagal senyap).
"""
from pathlib import Path
import shutil

F = Path('app/templates/diagnosis.html')
asli = F.read_text(encoding='utf-8')
shutil.copy(F, F.with_suffix('.html.cadangan_grafik'))
sebelum = len(asli)

# ── Penanda 1: kartu NORMALITAS (utuh sampai penutupnya) ───────────────────
LAMA_N = """    /* ① Normalitas */
    const n = d.normalitas || {};
    h += kartuUji('Normalitas sisa', n.lulus,
      '<p style="margin:0;color:#6B6259">Tiga uji sekaligus, supaya kesimpulannya kokoh.<\\/p>' +
      tabelBaris(['Uji', 'Nilai p'],
        [['Kolmogorov-Smirnov', angka(n.ks_p)],
         ['Shapiro-Wilk', angka(n.shapiro_p)],
         ["D'Agostino", angka(n.dagostino_p)]]) +
      '<p style="margin:9px 0 0;font-size:.92rem">Kemiringan (skewness) = ' + angka(n.skew) +
      ' · Keruncingan = ' + angka(n.kurtosis) + '. ' +
      'Nilai p di atas 0,05 artinya sisa menyebar normal.<\\/p>');"""

BARU_N = """    /* ① Normalitas */
    const n = d.normalitas || {};
    h += kartuUji('Normalitas sisa', n.lulus,
      '<p style="margin:0;color:#6B6259">Tiga uji sekaligus, supaya kesimpulannya kokoh.<\\/p>' +
      tabelBaris(['Uji', 'Nilai p'],
        [['Kolmogorov-Smirnov', angka(n.ks_p)],
         ['Shapiro-Wilk', angka(n.shapiro_p)],
         ["D'Agostino", angka(n.dagostino_p)]]) +
      /* ── GRAFIK HIDUP (Tahap 2, ACC Bos 20Sep26) ──────────────────────
         Gambar dari DATA YANG DIUNGGAH — bukan contoh tetap. Fungsi gambar
         ada di /static/grafik_hidup.js (satu berkas untuk semua halaman). */
      kotakGrafik(svgPP(d.titik, n.lulus),
        (n.lulus
          ? 'Titik-titik mengikuti garis miring — sisa menyebar normal.'
          : 'Titik membelok menjauh dari garis, terutama di ujung — sisa belum normal.'),
        'pp') +
      '<p style="margin:6px 0 0;font-size:12.5px;color:#6B6259">' +
        '<strong>Cara membacanya:</strong> titik harus <strong>menempel</strong> ' +
        'pada garis miring. Kalau ujungnya membelok menjauh, bentuknya seperti S — ' +
        'itu tanda sisa belum menyebar normal.<\\/p>' +
      '<p style="margin:7px 0 0;font-size:.92rem">Kemiringan (skewness) = ' + angka(n.skew) +
      ' · Keruncingan = ' + angka(n.kurtosis) + '. ' +
      'Nilai p di atas 0,05 artinya sisa menyebar normal.<\\/p>' +
      catatanTitik(d.n ? d.n.length : 0));"""

# ── Penanda 2: kartu HETEROSKEDASTISITAS ───────────────────────────────────
LAMA_H = """    /* ② Heteroskedastisitas */
    const het = d.hetero || {};
    h += kartuUji('Heteroskedastisitas (Glejser)', het.lulus,
      '<p style="margin:0;color:#6B6259">Seberapa tidak rata sebaran sisanya.<\\/p>' +
      tabelBaris(['Nilai p terkecil'], [[angka(het.glejser_p)]]) +
      '<p style="margin:9px 0 0;font-size:.92rem">' +
      'Nilai p di bawah 0,05 artinya sebaran sisa tidak rata — ada yang perlu diperiksa.<\\/p>');"""

BARU_H = """    /* ② Heteroskedastisitas */
    const het = d.hetero || {};
    h += kartuUji('Heteroskedastisitas (Glejser)', het.lulus,
      '<p style="margin:0;color:#6B6259">Seberapa tidak rata sebaran sisanya.<\\/p>' +
      tabelBaris(['Nilai p terkecil'], [[angka(het.glejser_p)]]) +
      kotakGrafik(svgHetero(d.titik, het.lulus),
        (het.lulus
          ? 'Sebaran sisanya rata dari kiri ke kanan — tidak ada corong.'
          : 'Sebaran makin melebar ke kanan seperti corong — sisa tidak rata.'),
        'hetero') +
      '<p style="margin:6px 0 0;font-size:12.5px;color:#6B6259">' +
        '<strong>Cara membacanya:</strong> lihat lebarnya sebaran titik dari kiri ' +
        'ke kanan. Lebar yang <strong>tetap</strong> = aman. Kalau makin ke kanan ' +
        'makin melebar seperti corong, itu heteroskedastisitas.<\\/p>' +
      '<p style="margin:7px 0 0;font-size:.92rem">' +
      'Nilai p di bawah 0,05 artinya sebaran sisa tidak rata — ada yang perlu diperiksa.<\\/p>' +
      catatanTitik(d.n ? d.n.length : 0));"""

# ── Penanda 3: kartu LINEARITAS — tambahkan scatter X x Y ─────────────────
LAMA_L = """      h += kartuUji('Linearitas', lin.lulus,
        '<p style="margin:0;color:#6B6259">Apakah hubungan X dan Y berbentuk garis lurus.<\\/p>' +
        (lin.p === null || lin.p === undefined ? '' :
          tabelBaris(['Nilai p'], [[angka(lin.p)]])));"""

BARU_L = """      h += kartuUji('Linearitas', lin.lulus,
        '<p style="margin:0;color:#6B6259">Apakah hubungan X dan Y berbentuk garis lurus.<\\/p>' +
        (lin.p === null || lin.p === undefined ? '' :
          tabelBaris(['Nilai p'], [[angka(lin.p)]])) +
        kotakGrafik(svgLinear(d.titik, d.prediktor_grafik, d.y, lin.lulus),
          (lin.lulus
            ? 'Titik-titik memanjang mengikuti satu arah — hubungannya lurus.'
            : 'Titik melengkung atau menyebar tak berarah — hubungannya belum lurus.'),
          'linear') +
        '<p style="margin:6px 0 0;font-size:12.5px;color:#6B6259">' +
          '<strong>Cara membacanya:</strong> titik sebaiknya memanjang mengikuti ' +
          'satu arah seperti garis. Kalau membentuk lengkungan (U atau busur), ' +
          'hubungannya tidak lurus.<\\/p>');"""

for lama, baru, nama in ((LAMA_N, BARU_N, 'normalitas'),
                         (LAMA_H, BARU_H, 'hetero'),
                         (LAMA_L, BARU_L, 'linearitas')):
    jml = asli.count(lama)
    if jml != 1:
        raise SystemExit(f'  ❌ penanda {nama}: ketemu {jml}× (harus TEPAT 1) — DIBATALKAN')
    asli = asli.replace(lama, baru, 1)
    print(f'  ✅ {nama}: penanda ketemu 1×, disisip')

F.write_text(asli, encoding='utf-8')
print(f'  berkas: {sebelum} → {len(asli)} karakter (+{len(asli) - sebelum})')
