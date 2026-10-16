#!/usr/bin/env python3
"""SISIP entri NORMALITAS ke KAMUS + batas slider per-istilah (20Sep26).

AKAR YANG DITUTUP DI SINI:
  Slider #slider sekarang dipakai BERSAMA semua entri kamus dengan batas
  `min=0 max=100`. Normalitas butuh rentang −100…+100 supaya bisa miring
  KIRI dan KANAN (dua keadaan yang beda artinya). Kalau batas itu diubah
  langsung di HTML, SEMUA istilah lain (beta, pvalue, r2, vif, alpha) ikut
  rusak — nilai defaultnya di tengah, bukan di ujung.

  PERBAIKAN DI AKAR (bukan tambal):
    · Tiap entri KAMUS boleh punya `min`, `maks`, `bawaan` sendiri.
    · Fungsi `pilih()` MENYETEL batas slider dari entri yang dipilih.
    · Entri lama TIDAK diubah — tanpa `min`, otomatis 0…100 (seperti sekarang).
    · `gambar()` memakai `k.format(v)` seperti biasa — format normalitas
      memakai Math.abs karena yang dibaca "seberapa jauh dari lonceng".

Pakai: .venv/bin/python _sketsa/sisip_kamus_normalitas.py
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BERKAS = BASE / 'app' / 'templates' / 'belajar.html'
CADANGAN = BASE / 'app' / 'templates' / 'belajar.html.cadangan_kamus'

teks = BERKAS.read_text(encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════════
# PENANDA — harus tepat 1×, kalau tidak BATAL
# ══════════════════════════════════════════════════════════════════════════
P_AKHIR_KAMUS = "  },\n  beta: {\n"
P_GAMBAR_FN = """function gambar() {
  const k = KAMUS[kunci];
  const v = parseInt(el('slider').value, 10);"""
P_PILIH_FN = """  el('judul').textContent = kk.judul;
  el('arti').innerHTML = kk.arti;
  el('label-slider').textContent = kk.tanya;"""

for nama, pola in [('akhir KAMUS hetero', P_AKHIR_KAMUS),
                   ('fungsi gambar()', P_GAMBAR_FN),
                   ('fungsi pilih()', P_PILIH_FN)]:
    n = teks.count(pola)
    print(f'  penanda {nama:20} {n}×', end='  ')
    if n != 1:
        print('❌ BATAL')
        sys.exit(1)
    print('✅')

shutil.copy2(BERKAS, CADANGAN)
print(f'\n✅ cadangan: {CADANGAN.name}')

baru = teks

# ══════════════════════════════════════════════════════════════════════════
# 1. ENTRI KAMUS: normalitas (ditaruh SETELAH hetero, sebelum beta)
# ══════════════════════════════════════════════════════════════════════════
ENTRI = '''  normalitas: {
    judul: 'Normalitas',
    arti: 'Syarat regresi: sisa (residu) harus <strong>menyebar normal</strong> — bentuknya seperti lonceng yang simetris, bukan miring ke satu sisi. Ini diperiksa dari BENTUK sebarannya, bukan dari lebarnya.',
    tanya: 'Sebesar apa kemiringannya?',
    kiri: 'Miring kiri', kanan: 'Miring kanan',
    // ⚠️ ENTRI INI PUNYA RENTANG SENDIRI (−100…+100), beda dari istilah lain.
    // Tengah (0) = lonceng sempurna. Inilah sebabnya `pilih()` perlu menyetel
    // batas slider dari entri yang dipilih — lihat catatan akar di bawah.
    min: -100, maks: 100, bawaan: 0,
    satuan: '', ambang: null,
    // Yang dibaca user = "seberapa jauh dari lonceng", jadi pakai Math.abs.
    ukur: v => Math.abs(v) / 100,
    format: v => (v === 0 ? 'lonceng' : Math.abs(v / 100).toFixed(3)),
    // Ambang 0,18 & 0,45 — SAMA dengan hetero supaya bahasa "kapan dianggap
    // aman" seragam di seluruh kamus (pelajaran 18Sep26: ambang harus
    // bercerita sama dengan gambarnya).
    tafsir: v => Math.abs(v) < 18
      ? ['pita-hijau', 'Normal', 'Bentuknya lonceng simetris. Syarat normalitas terpenuhi — uji hipotesis boleh dilanjutkan.']
      : Math.abs(v) < 45
      ? ['pita-amber', 'Mulai miring', 'Sebarannya mulai condong ke satu sisi. Cek Sig. Kolmogorov-Smirnov di SPSS: kalau masih di atas 0,05, kemiringan ini belum mengganggu.']
      : ['pita-merah', 'Jauh dari normal', 'Ekornya memanjang ke satu sisi. Jalan keluar: buang pencilan yang memang terbukti menyimpang, atau pakai uji yang tidak menuntut normalitas.'],
    spss: 'Analyze → Descriptive Statistics → Explore → tombol Plots → centang Histogram dan Normality plots with tests. Lihat Sig. Kolmogorov-Smirnov dan Sig. Saphiro-Wilk — di atas 0,05 berarti sebarannya normal.',
    kenapa: [
      'Ada beberapa jawaban yang jauh berbeda dari yang lain (pencilan).',
      'Jumlah responden sedikit, sehingga bentuk sebarannya belum stabil.',
      'Pertanyaannya terlalu mudah atau terlalu sulit, jadi jawabannya menumpuk di satu sisi.',
      'Skala yang dipakai tidak menampung variasi jawaban yang sebenarnya.'
    ],
    /*
      GAMBAR NORMALITAS — HISTOGRAM (BARU 20Sep26, ACC Bos).

      INI MENJAWAB PERTANYAAN BOS yang paling penting:
        "Kenapa di gambar contoh saya atau SPSS tidak ada corongnya?"
      Jawabannya: TIDAK ADA CORONG = DATA SEHAT. Corong itu nama
      PENYAKITNYA (heteroskedastisitas), bukan tanda keberhasilan uji.
      Karena itu gambar contoh yang rapi TIDAK boleh dibaca "tidak ada hasil".

      BEDA DENGAN HETERO (penting, jangan disamakan):
        · Hetero  = BENTUK titik (scatter ZPRED×ZRESID) → dilihat dari SAMPING.
        · Normali = BENTUK batang (histogram)          → dilihat dari DEPAN.
      Keduanya diperiksa dari benda yang SAMA (sisa/residu), tapi
      pertanyaannya beda. Itu yang membuat keduanya perlu kartu tersendiri.

      CARA MENGGAMBAR: lonceng dasar (fungsi Gauss) di puncak yang digeser
      oleh kemiringan, lalu ekor di sisi kemiringan DITARIK MEMANJANG.
      Derau semu ber-seed supaya batangnya tidak berkedip saat digeser —
      akar yang sama dengan perbaikan hetero 18Sep26.
    */
    gambar: (v, c) => {
      const t = v / 100;                       // −1 … +1
      const x0 = 34, x1 = 366, ym = 150, tinggi = 118;
      const acak = (i) => {
        const s = Math.sin(i * 27.3119) * 9137.1357;
        return s - Math.floor(s);
      };
      const batang = [];
      const N = 26;
      for (let i = 0; i < N; i++) {
        const per = i / (N - 1);
        // puncak bergeser mengikuti arah kemiringan
        const puncak = 0.5 + t * 0.30;
        let g = Math.exp(-Math.pow((per - puncak) / (0.19 + Math.abs(t) * 0.07), 2));
        // ekor memanjang ke SISI kemiringan
        if (t > 0 && per > puncak) {
          g += t * 0.55 * Math.pow(per - puncak, 1.1) * 3.2;
        }
        if (t < 0 && per < puncak) {
          g += Math.abs(t) * 0.55 * Math.pow(puncak - per, 1.1) * 3.2;
        }
        g = Math.max(0, Math.min(1, g + (acak(i) - 0.5) * 0.07));
        const leb = (x1 - x0) / N - 2.5;
        const x = x0 + per * (x1 - x0) - leb / 2;
        const h = g * tinggi;
        if (h > 1.5) {
          batang.push(`<rect x="${x.toFixed(1)}" y="${(ym - h).toFixed(1)}" `
            + `width="${leb.toFixed(1)}" height="${h.toFixed(1)}" rx="2" `
            + `fill="${c}" opacity="0.72"/>`);
        }
      }
      const label = Math.abs(t) < 0.06 ? 'bentuk lonceng — normal'
                  : (t > 0 ? 'ekor memanjang ke kanan (miring positif)'
                           : 'ekor memanjang ke kiri (miring negatif)');
      return `<line x1="24" y1="${ym}" x2="376" y2="${ym}"
                    stroke="#E0D8C8" stroke-width="1.5"/>
        ${batang.join('')}
        <line x1="200" y1="20" x2="200" y2="${ym}" stroke="#D8CDBC"
              stroke-width="1" stroke-dasharray="4 4"/>
        <text x="200" y="164" text-anchor="middle" font-size="10.5"
              fill="#6B6259">${label}<\\/text>`;
    }
  },
  beta: {
'''
baru = baru.replace(P_AKHIR_KAMUS, ENTRI, 1)
print('✅ 1. entri KAMUS `normalitas` disisipkan')

# ══════════════════════════════════════════════════════════════════════════
# 2. gambar() — pakai format entri apa adanya (tidak diubah, hanya dipastikan)
#    Ternyata sudah OK. Yang perlu: pilih() menyetel batas slider.
# ══════════════════════════════════════════════════════════════════════════
GANTI_PILIH = """  el('judul').textContent = kk.judul;
  el('arti').innerHTML = kk.arti;
  el('label-slider').textContent = kk.tanya;
  // ⚠️ AKAR (20Sep26) — BATAS SLIDER DISETEL DARI ENTRI, bukan dipaku 0…100.
  // Normalitas butuh −100…+100 (bisa miring dua arah); istilah lain tetap
  // 0…100 karena tidak punya `min`/`maks`. Tanpa ini, salah satu istilah
  // pasti rusak: normalitas kehilangan sisi kiri, ATAU istilah lain
  // kehilangan separuh rentangnya.
  el('slider').min = (kk.min !== undefined) ? kk.min : 0;
  el('slider').maks = undefined;                       // jaga-jaga: properti tak dikenal
  el('slider').max = (kk.maks !== undefined) ? kk.maks : 100;
  el('slider').value = (kk.bawaan !== undefined) ? kk.bawaan : 35;
  // Tombol pintasan hanya masuk akal untuk hetero (yang punya keadaan
  // "sehat/sakit" satu arah). Istilah lain disembunyikan — JANGAN
  // menampilkan tombol yang tidak berfungsi.
  const barisPintasan = document.getElementById('pintasan-baris');
  if (barisPintasan) barisPintasan.hidden = (k !== 'hetero');"""
baru = baru.replace(P_PILIH_FN, GANTI_PILIH, 1)
print('✅ 2. pilih() menyetel batas slider dari entri (akar ditutup)')

BERKAS.write_text(baru, encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════════
# VERIFIKASI
# ══════════════════════════════════════════════════════════════════════════
akhir = BERKAS.read_text(encoding='utf-8')
print(f'\n✅ BERKAS DITULIS: {len(teks)} → {len(akhir)} byte ({len(akhir)-len(teks):+d})')
print(f'   <script  : {len(re.findall(r"<script", akhir))} (harus 3)')
print(f'   </script>: {len(re.findall(r"</script>", akhir))} (harus 1)')
print(f'   entri normalitas: {"ADA" if "  normalitas: {" in akhir else "TIDAK ADA"}')
print(f'   tombol pintasan di pilih(): {"ADA" if "barisPintasan" in akhir else "TIDAK ADA"}')
