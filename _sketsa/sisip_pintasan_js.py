#!/usr/bin/env python3
"""SISIP JS tombol pintasan + kalimat penegas (20Sep26).

APA YANG DITAMBAH:
  1. Daftar tombol pintasan dipasang event-nya (sehat → geser ke 0,
     sakit → geser ke 100) + tombol MENYALA mengikuti posisi slider.
  2. `pesan-isi` (kalimat di kotak info) DIPERKAYA untuk tiga keadaan,
     memuat kalimat kunci Bos: "tidak ada corong — justru ini yang bagus".

KENAPA TIDAK MENGUBAH `tafsir` SAJA:
  `tafsir` hanya satu kalimat pendek untuk pita. Yang Bos minta adalah
  kalimat PENEGAS yang menjelaskan kenapa keadaan rapi itu menjawab
  pertanyaan "kok tidak ada apa-apa". Jadi kalimat detailnya ditaruh di
  fungsi terpisah (`kalimatTafsir`), supaya `tafsir` lama tetap utuh dan
  istilah lain tidak ikut berubah.

Pakai: .venv/bin/python _sketsa/sisip_pintasan_js.py
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BERKAS = BASE / 'app' / 'templates' / 'belajar.html'
CADANGAN = BASE / 'app' / 'templates' / 'belajar.html.cadangan_pintasan'

teks = BERKAS.read_text(encoding='utf-8')

# ── PENANDA ───────────────────────────────────────────────────────────────
P = {
    'baris pesan-isi': "  el('pesan-isi').innerHTML = pesan;",
    'listener slider': "el('slider').addEventListener('input', gambar);",
}
for nama, pola in P.items():
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
# 1. gambar() — pakai kalimatTafsir kalau ada
# ══════════════════════════════════════════════════════════════════════════
baru = baru.replace(
    "  el('pesan-isi').innerHTML = pesan;",
    """  // ⚠️ KALIMAT PENEGAS (20Sep26, permintaan Bos): "tidak ada corong berarti
  // bagus/sehat". `tafsir` tetap dipakai untuk pita & istilah lain; kalimat
  // panjangnya diambil dari kalimatTafsir bila entri punya. Entri lama TIDAK
  // punya → otomatis pakai `pesan` seperti sebelumnya (tidak ada yang rusak).
  el('pesan-isi').innerHTML =
    (typeof kalimatTafsir === 'function')
      ? kalimatTafsir(kunci, v, pesan) : pesan;""", 1)
print('✅ 1. gambar() pakai kalimatTafsir')

# ══════════════════════════════════════════════════════════════════════════
# 2. Fungsi kalimatTafsir + tombol pintasan — ditaruh SEBELUM listener slider
# ══════════════════════════════════════════════════════════════════════════
BLOK = '''/* ══════════════════════════════════════════════════════════════════════════
   KALIMAT PENEGAS + TOMBOL PINTASAN (20Sep26, ACC Bos)

   MENGAPA ADA — temuan Bos saat memeriksa grafik heteroskedastisitas:
     "Heteroskedastisitas kenapa di gambar contoh saya atau SPSS tidak ada
      corongnya?"
   Jawabannya: TIDAK ADA CORONG = DATA SEHAT. Corong itu nama PENYAKITNYA.
   Masalahnya, mahasiswa membaca "tidak ada apa-apa" sebagai "tidak ada hasil"
   — padahal justru itu kabar baiknya. Kalimat ini yang menutup salah paham
   itu, dan hanya muncul saat memang sedang sehat (di pita lain diganti
   kalimat yang sesuai).

   TOMBOL PINTASAN — kenapa tombol, padahal slider sudah ada:
     Slider memaksa user MENGHAYAL dulu ("yang sehat itu bagaimana ya?").
     Dua tombol ini membuatkeadaan sehat & sakit bisa DILIHAT LANGSUNG,
     membandingkan keduanya dalam satu klik. Slider tetap ada supaya user
     masih bisa menjelajah di antaranya (keputusan Bos: variasi B).
   ══════════════════════════════════════════════════════════════════════════ */
function kalimatTafsir(k, v, pesanBawaan) {
  // Hanya hetero & normalitas yang punya penegas. Istilah lain apa adanya.
  if (k === 'hetero') {
    if (v < 18) {
      return '<strong>Tidak ada corong — justru ini yang bagus.</strong> '
        + 'Sebarannya rata dari kiri ke kanan, jadi syarat ini <strong>terpenuhi</strong>. '
        + 'Data seperti ini sudah boleh lanjut ke pengujian hipotesis.';
    }
    if (v < 45) {
      return '<strong>Sebarannya mulai melebar.</strong> Belum pasti bermasalah, '
        + 'tapi jangan langsung diabaikan. Periksa dengan <strong>uji Glejser</strong>: '
        + 'kalau Sig. di atas 0,05, sebaran ini masih boleh dipakai.';
    }
    return '<strong>Ini contoh yang bermasalah.</strong> Sebarannya melebar ke kanan. '
      + 'Tapi ingat: <strong>melebar bukan cuma bentuk corong</strong> — bisa juga '
      + 'mekar ke arah sebaliknya, atau melengkung di ujung. Dua jalan keluar: '
      + 'pakai <em>robust standard error</em>, atau ubah data dengan logaritma.';
  }
  if (k === 'normalitas') {
    if (Math.abs(v) < 18) {
      return '<strong>Tidak ada kemiringan — justru ini yang bagus.</strong> '
        + 'Bentuknya lonceng yang simetris, jadi syarat normalitas <strong>terpenuhi</strong>. '
        + 'Uji hipotesis sudah boleh dilanjutkan.';
    }
    if (Math.abs(v) < 45) {
      return '<strong>Mulai condong ke satu sisi.</strong> Belum tentu mengganggu — '
        + 'cek angka <strong>Sig. Kolmogorov-Smirnov</strong> di SPSS. Kalau masih '
        + 'di atas 0,05, kemiringan ini belum menjadi masalah.';
    }
    const arah = v > 0 ? 'kanan (miring positif)' : 'kiri (miring negatif)';
    return '<strong>Jauh dari bentuk lonceng</strong> — ekornya memanjang ke ' + arah + '. '
      + 'Jalan keluarnya: periksa dulu apakah ada pencilan yang memang terbukti '
      + 'menyimpang, atau pakai uji statistik yang tidak menuntut normalitas.';
  }
  return pesanBawaan;
}

/* ── Tombol pintasan sehat/sakit (khusus hetero) ──────────────────────────
   Menyetel slider lalu memanggil gambar(). Tombol MENYALA mengikuti posisi
   slider, jadi saat user menggeser slider sendiri, nyala tombolnya ikut
   pindah — tidak pernah menunjuk keadaan yang tidak sesuai. */
function pintasanPasang() {
  const sehat = document.getElementById('pintasan-sehat');
  const sakit = document.getElementById('pintasan-sakit');
  if (!sehat || !sakit) return;
  const ke = (nilai) => {
    const s = el('slider');
    if (!s) return;
    s.value = nilai;
    gambar();
    pintasanNyalakan();
  };
  sehat.addEventListener('click', () => ke(0));
  sakit.addEventListener('click', () => ke(100));
  el('slider').addEventListener('input', pintasanNyalakan);
}
function pintasanNyalakan() {
  const s = el('slider');
  const sehat = document.getElementById('pintasan-sehat');
  const sakit = document.getElementById('pintasan-sakit');
  if (!s || !sehat || !sakit) return;
  const nilai = parseInt(s.value, 10);
  const bawah = parseInt(s.min, 10);
  const atas = parseInt(s.max, 10);
  // "mentok" dihitung dari rentang SEKARANG, bukan angka mati — supaya tetap
  // benar kalau rentang slider berbeda (normalitas −100…+100).
  sehat.classList.toggle('nyala', nilai <= bawah + 2);
  sakit.classList.toggle('nyala', nilai >= atas - 2);
}

el('slider').addEventListener('input', gambar);
pintasanPasang();
'''
baru = baru.replace(P['listener slider'], BLOK, 1)
print('✅ 2. kalimatTafsir + tombol pintasan dipasang')

BERKAS.write_text(baru, encoding='utf-8')
akhir = BERKAS.read_text(encoding='utf-8')

print(f'\n✅ BERKAS DITULIS: {len(teks)} → {len(akhir)} byte ({len(akhir)-len(teks):+d})')
print(f'   <script  : {len(re.findall(r"<script", akhir))} (harus 3)')
print(f'   </script>: {len(re.findall(r"</script>", akhir))} (harus 1)')
print(f'   kalimatTafsir: {"ADA" if "function kalimatTafsir" in akhir else "TIDAK"}')
print(f'   pintasanPasang: {"ADA" if "function pintasanPasang" in akhir else "TIDAK"}')
