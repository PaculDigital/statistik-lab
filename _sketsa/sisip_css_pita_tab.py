#!/usr/bin/env python3
"""Sisipkan CSS PITA TAB ke app/static/gaya.css.

⚠️ ATURAN (pelajaran 19Sep26): JANGAN patch buta. Pakai skrip + cadangan +
   verifikasi kurung CSS SEIMBANG setelah sisip.

Kelas yang ditambah:
  .pita-tab          — pita tab (variasi dari .pilih yang sudah ada)
  .pita-tab a        — tombol tab
  .pita-tab a.aktif  — tab yang sedang dibuka
  .pita-tab .biji    — angka kecil (jumlah isi tab)
  .kartu-alat        — kartu besar di Ruang Uji (ikon + isi + panah)

Rujukan sketsa: _sketsa/belajar_tab_sketsa.html baris 19-38.
Variabel CSS sudah DICEK ADA: --tinta-2 --garis --kertas-3 --teal-terang --teal.
"""
import pathlib
import shutil

BERKAS = pathlib.Path('/opt/data/services/statistik-lab/app/static/gaya.css')
CADANGAN = pathlib.Path('/tmp/gaya_css_cadangan.txt')

TANDA = '/* ══════ PITA TAB (19Sep26) ══════ */'

CSS = TANDA + """
/* ⚠️ Pita tab di halaman BELAJAR (Materi & Kamus | Ruang Uji).
   Dirancang 19Sep26 dari sketsa _sketsa/belajar_tab_sketsa.html.
   Variasi dari .pilih yang SUDAH ADA — tidak bikin bahasa gaya baru.
   margin-bottom:-1.5px pada <a> supaya garis tab MENEMPEL garis bawah pita
   (kalau tidak, ada celah 1,5px yang terlihat seperti garis putus). */
.pita-tab {
  display: flex; gap: 6px; flex-wrap: wrap;
  border-bottom: 1.5px solid var(--garis); margin: 18px 0 22px;
}
.pita-tab a {
  display: flex; align-items: center; gap: 8px;
  padding: 11px 16px 12px; font-size: 14px; font-weight: 650;
  color: var(--tinta-2); text-decoration: none;
  border-bottom: 2.5px solid transparent; margin-bottom: -1.5px;
}
.pita-tab a:hover { color: var(--teal); }
.pita-tab a.aktif { color: var(--teal); border-bottom-color: var(--teal); }
.pita-tab .biji {
  font-size: 11px; background: var(--kertas-3); color: var(--tinta-2);
  border-radius: 20px; padding: 2px 8px; font-weight: 700;
}
.pita-tab a.aktif .biji { background: var(--teal-terang); color: var(--teal); }

/* ⚠️ ISI: cegah kartu meluber di dalam tab (pola sama seperti .kartu lain).
   Kartu alat di Ruang Uji: ikon kiri · isi tengah · panah kanan. */
.kartu-alat {
  display: flex; align-items: center; gap: 14px;
  background: #fff; border: 1px solid var(--garis); border-radius: 14px;
  padding: 16px 18px; margin: 0 0 12px; text-decoration: none;
  color: var(--tinta); transition: border-color .15s, background .15s;
  overflow-wrap: break-word;
}
.kartu-alat:hover { border-color: var(--teal); background: var(--teal-terang); }
.kartu-alat .ikon-alat { font-size: 26px; flex: 0 0 auto; line-height: 1; }
.kartu-alat .isi-alat { min-width: 0; flex: 1 1 auto; }
.kartu-alat .isi-alat b { display: block; font-size: 15px; margin-bottom: 2px; }
.kartu-alat .isi-alat span { font-size: 13px; color: var(--tinta-2); }
.kartu-alat .panah { font-size: 22px; color: var(--tinta-2); flex: 0 0 auto; }

/* Kartu "belum jadi" di dalam Ruang Uji — jujur tapi tidak menghalangi. */
.kartu-alat.segera { opacity: .75; }
.kartu-alat.segera:hover { border-color: var(--garis); background: #fff; }

/* ⚠️ DI HP 390px: pita tab harus tetap bisa dibaca. Tab memakai flex-wrap
   sehingga turun baris sendiri kalau tidak muat — JANGAN dipaksa 1 baris. */
@media (max-width: 430px) {
  .pita-tab a { padding: 10px 12px 11px; font-size: 13.5px; gap: 6px; }
  .pita-tab .biji { font-size: 10.5px; padding: 2px 7px; }
}
"""


def utama():
    s = BERKAS.read_text(encoding='utf-8')
    asli = len(s)
    CADANGAN.write_text(s, encoding='utf-8')
    print(f'cadangan → {CADANGAN} ({asli} byte)')

    if TANDA in s:
        print('⚠️  SUDAH ADA — tidak menyisipkan ulang (mencegah dobel)')
        return

    s2 = s.rstrip('\n') + '\n\n' + CSS
    BERKAS.write_text(s2, encoding='utf-8')

    buka, tutup = s2.count('{'), s2.count('}')
    print(f'kurung: {buka} buka / {tutup} tutup → '
          + ('SEIMBANG ✅' if buka == tutup else '❌ TIDAK SEIMBANG — PULIHKAN!'))
    print(f'ukuran: {asli} → {len(s2)} byte')

    # verifikasi kelas benar-benar ada
    for k in ['.pita-tab {', '.pita-tab a.aktif', '.biji', '.kartu-alat {',
              '.kartu-alat.segera', '@media (max-width: 430px)']:
        print(f'  {"✅" if k in s2 else "❌"} {k}')


if __name__ == '__main__':
    utama()
