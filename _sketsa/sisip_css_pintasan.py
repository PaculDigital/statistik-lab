#!/usr/bin/env python3
"""SISIP CSS tombol pintasan ke gaya.css (20Sep26).

GREP DULU (aturan Bos): sebelum menulis kelas, pastikan namanya BELUM ADA.
Terukur lewat _sketsa/grep_nama_baru.sh:
    .pintasan-baris  → 0  (belum ada → boleh dibuat)
    .pintasan        → 0  (belum ada → boleh dibuat)
    .pintasan.nyala  → 0  (belum ada → boleh dibuat)
    --teal, --teal-terang, --garis, --kertas-2 → SEMUA ADA (dipakai, bukan dikarang)

Pakai: .venv/bin/python _sketsa/sisip_css_pintasan.py
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BERKAS = BASE / 'app' / 'static' / 'gaya.css'
CADANGAN = BASE / 'app' / 'static' / 'gaya.css.cadangan_pintasan'

teks = BERKAS.read_text(encoding='utf-8')

# ── 1. PASTIKAN KELAS BELUM ADA (jangan menimpa yang sudah jalan) ─────────
for kelas in ['.pintasan-baris', '.pintasan ']:
    if kelas in teks:
        print(f'❌ BATAL — kelas `{kelas}` ternyata SUDAH ADA di gaya.css')
        sys.exit(1)
print('✅ kelas belum ada — aman dibuat')

# ── 2. PASTIKAN VARIABEL YANG DIPAKAI BENAR-BENAR ADA ────────────────────
for var in ['--teal:', '--teal-terang:', '--garis:', '--kertas-2:']:
    if var not in teks:
        print(f'❌ BATAL — variabel `{var}` tidak ada di gaya.css (jangan mengarang nama)')
        sys.exit(1)
print('✅ semua variabel CSS yang dipakai benar-benar ada')

# ── 3. UKUR KURUNG SEIMBANG SEBELUM ──────────────────────────────────────
buka, tutup = teks.count('{'), teks.count('}')
print(f'   kurung sebelum: {buka} buka / {tutup} tutup', '✅' if buka == tutup else '❌')
if buka != tutup:
    sys.exit(1)

shutil.copy2(BERKAS, CADANGAN)
print(f'\n✅ cadangan: {CADANGAN.name}')

# ── 4. BLOK CSS BARU ─────────────────────────────────────────────────────
BLOK = '''
/* ══════════════════════════════════════════════════════════════════════════
   TOMBOL PINTASAN SEHAT/SAKIT — kartu Heteroskedastisitas (20Sep26, ACC Bos)
   ──────────────────────────────────────────────────────────────────────────
   MENGAPA ADA: slider memaksa mahasiswa menghayal dulu ("yang sehat itu
   bagaimana ya?"). Dua tombol ini membuat keadaan sehat & sakit bisa DILIHAT
   LANGSUNG dan dibandingkan dalam satu klik. Slider tetap ada (keputusan Bos:
   variasi B) supaya user masih bisa menjelajah di antaranya.

   ⚠️ TOMBOL INI HANYA UNTUK HETERO. Saat istilah lain dipilih, JS
   menyembunyikan wadahnya (pilih() menyetel `hidden`) — JANGAN menampilkan
   tombol yang tidak berfungsi.
   ══════════════════════════════════════════════════════════════════════════ */
.pintasan-baris {
  display: flex;
  gap: 8px;
  background: var(--kertas-2);
  border: 1.5px solid var(--garis);
  border-radius: 9px;
  padding: 5px;
  margin-bottom: 13px;
}
.pintasan-baris[hidden] { display: none; }

.pintasan {
  flex: 1;
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  padding: 9px 6px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--tinta-2);
  cursor: pointer;
}
.pintasan:hover { background: #fff; }
.pintasan.nyala {
  background: var(--teal);
  color: #fff;
  box-shadow: 0 2px 6px rgba(15, 115, 103, .28);
}
'''
teks_baru = teks.rstrip() + '\n' + BLOK
BERKAS.write_text(teks_baru, encoding='utf-8')

# ── 5. VERIFIKASI KURUNG SETELAH ─────────────────────────────────────────
akhir = BERKAS.read_text(encoding='utf-8')
b2, t2 = akhir.count('{'), akhir.count('}')
print(f'\n✅ BERKAS DITULIS: {len(teks)} → {len(akhir)} byte ({len(akhir)-len(teks):+d})')
print(f'   kurung sesudah: {b2} buka / {t2} tutup', '✅' if b2 == t2 else '❌ TIDAK SEIMBANG')
if b2 != t2:
    sys.exit(1)
print(f'   .pintasan-baris: {"ADA" if ".pintasan-baris" in akhir else "TIDAK"}')
