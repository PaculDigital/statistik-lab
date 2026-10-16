#!/usr/bin/env python3
"""Tambah CSS untuk bagian KETERANGAN AMBANG SIG. (kelas berawalan `amb-`).

⚠️ ATURAN YANG DIPATUHI (dari memory, pelajaran mahal):
   SEBELUM memakai NAMA variabel CSS — GREP dulu buktikan ADA.
   Terukur 19Sep26: `--hijau-bg`, `--kuning`, `--kuning-bg`, `--merah-bg`,
   `--abu-bg` TIDAK ADA di gaya.css. Yang ADA: `--hijau-terang`,
   `--merah-terang`, `--amber`, `--amber-terang`, `--kertas-3`.
   Memakai nama palsu = warna mati tanpa galat apa pun (kelas ikon kosong versi CSS).

⚠️ 2 CACAT SKETSA yang diperbaiki di sini (temuan vision 19sep26):
   (a) penanda angka MENIMPA label "batas 0,05" saat berdekatan
       → label batas ditaruh DI ATAS jalur, penanda angka DI BAWAH jalur
         (dua jalur terpisah, tidak bisa bertabrakan)
   (b) teks tabel kepotong → kolom pendek, `overflow-wrap: break-word`
"""
import pathlib

CSS = pathlib.Path('/opt/data/services/statistik-lab/app/static/gaya.css')
CAD = pathlib.Path('/tmp/gaya_cadangan_amb.css')

BLOK = '''

/* ══════════════════════════════════════════════════════════════════════════
   KETERANGAN AMBANG SIG. — slider pembanding hasil temuan vs batas 0,05
   (19Sep26, ACC Bos). Dipakai di kartu Uji t halaman /belajar.
   Semua kelas berawalan `amb-` supaya tidak bentrok dengan kelas lama.
   Warna memakai variabel yang SUDAH TERBUKTI ADA (grep): --hijau-terang,
   --merah-terang, --amber, --amber-terang, --kertas-3.
   ══════════════════════════════════════════════════════════════════════════ */
.amb-masuk {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  background: var(--kertas-2); border: 1.5px solid var(--garis);
  border-radius: var(--r-s); padding: 10px 12px; margin-bottom: 18px;
}
.amb-masuk label { font-size: 13.5px; font-weight: 600; }
.amb-masuk input {
  width: 100px; padding: 7px 9px; text-align: center;
  font: inherit; font-size: 17px; font-weight: 800; color: var(--teal);
  border: 1.5px solid var(--teal); border-radius: 8px; background: #fff;
}
.amb-masuk .samar { margin-left: auto; font-size: 11.5px; color: var(--tinta-3); }

/* ── garis bilangan: jalur + label batas (ATAS) + penanda angka (BAWAH) ── */
.amb-garis { position: relative; height: 86px; margin: 4px 0 2px; }
.amb-jalur {
  position: absolute; top: 30px; left: 0; right: 0; height: 9px;
  border-radius: 6px;
  background: linear-gradient(90deg,
    var(--hijau-terang) 0%, var(--hijau-terang) 9.9%,
    var(--amber-terang) 10%, var(--amber-terang) 19.9%,
    var(--kertas-3) 20%, var(--kertas-3) 100%);
}
.amb-batas {
  position: absolute; top: 20px; width: 3px; height: 30px;
  background: var(--teal); border-radius: 2px;
}
.amb-batas-lbl {
  position: absolute; top: -20px; left: 50%; transform: translateX(-50%);
  font-size: 11px; font-weight: 800; color: var(--teal);
  background: var(--teal-terang); padding: 1px 6px; border-radius: 5px;
  white-space: nowrap;
}
.amb-tanda {
  position: absolute; top: 42px; transform: translateX(-50%);
  font-size: 10px; color: var(--tinta-3);
}
.amb-tanda:first-of-type { transform: none; }

/* penanda angka user — DI BAWAH jalur, jadi tidak bisa menimpa label batas */
.amb-pin {
  position: absolute; top: 44px; transform: translateX(-50%);
  text-align: center; transition: left .12s ease-out;
}
.amb-tangkai {
  width: 2px; height: 18px; background: var(--tinta);
  margin: 0 auto 2px; position: relative; top: -20px;
}
.amb-nilai {
  font-size: 12.5px; font-weight: 800; background: var(--tinta); color: #fff;
  padding: 2px 8px; border-radius: 6px; white-space: nowrap;
  display: inline-block;
}

/* ── kotak jawaban otomatis ── */
.catatan.amb-jawab-hijau {
  border-left-color: var(--hijau); background: var(--hijau-terang);
}
.catatan.amb-jawab-kuning {
  border-left-color: var(--amber); background: var(--amber-terang);
}
.catatan.amb-jawab-abu {
  border-left-color: var(--tinta-3); background: var(--kertas-3);
}
.catatan .amb-besar { font-size: 14.5px; font-weight: 800; }
.catatan .amb-ket { font-size: 12.5px; color: var(--tinta-2); margin-top: 4px; }

/* ── tabel ── */
.amb-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.amb-tbl th, .amb-tbl td {
  border: 1px solid var(--garis); padding: 7px 9px;
  text-align: left; vertical-align: top; overflow-wrap: break-word;
}
.amb-tbl th { background: var(--kertas-2); font-size: 11.5px; }
.amb-merah { color: var(--merah); }
.amb-hijau { color: var(--hijau); }

/* ── 3 contoh angka minus ── */
.amb-tiga { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
.amb-contoh {
  border: 1px solid var(--garis); border-radius: var(--r-s);
  padding: 9px 6px; text-align: center; background: var(--kertas);
}
.amb-angka { font-size: 13.5px; font-weight: 800; }
.amb-lbl {
  font-size: 10px; margin-top: 4px; padding: 2px 6px;
  border-radius: 10px; display: inline-block; line-height: 1.5;
}
.amb-lbl-hijau { color: var(--hijau); background: var(--hijau-terang); }
.amb-lbl-kuning { color: var(--amber); background: var(--amber-terang); }
.amb-lbl-abu { color: var(--tinta-2); background: var(--kertas-3); }

/* ── teori ── */
.amb-teori {
  border: 1px solid var(--garis); border-radius: var(--r-s);
  padding: 12px; margin-bottom: 10px; background: var(--kertas-2);
}
.amb-teori h3 { margin: 0 0 6px; font-size: 13.5px; color: var(--teal); }
.amb-teori p { margin: 0; font-size: 12.5px; color: var(--tinta-2); line-height: 1.6; }
.amb-teori blockquote {
  margin: 8px 0 0; padding-left: 10px; border-left: 2px solid var(--teal);
  font-style: italic; color: var(--tinta); font-size: 12.5px; line-height: 1.55;
}
.amb-kutip-siapa {
  font-style: normal; font-size: 11px; color: var(--tinta-3);
}

@media (max-width: 430px) {
  .amb-masuk input { width: 88px; font-size: 16px; }
  .amb-nilai { font-size: 11.5px; padding: 2px 6px; }
  .amb-angka { font-size: 12.5px; }
  .amb-lbl { font-size: 9.5px; }
}
'''


def utama():
    s = CSS.read_text(encoding='utf-8')
    CAD.write_text(s, encoding='utf-8')
    print(f'cadangan → {CAD} ({len(s)} byte)')

    if '.amb-masuk' in s:
        print('⚠️ CSS amb-* SUDAH ADA — batal (jangan tambah dua kali)')
        return

    kurung_awal = (s.count('{'), s.count('}'))
    hasil = s.rstrip() + '\n' + BLOK
    kurung_akhir = (hasil.count('{'), hasil.count('}'))
    print(f'kode kurung: {kurung_awal} → {kurung_akhir}')
    if kurung_akhir[0] != kurung_akhir[1]:
        print('❌ KURUNG TIDAK SEIMBANG — BATAL (tidak ditulis)')
        return
    if kurung_akhir[0] - kurung_awal[0] != len(
            [1 for b in BLOK.split('{') if True]) - 1:
        print('⚠️ jumlah buka bertambah, cek manual')

    CSS.write_text(hasil, encoding='utf-8')
    print(f'✅ CSS ditulis: {len(s)} → {len(hasil)} byte (+{len(hasil)-len(s)})')

    print('\n── VERIFIKASI ──')
    for k in ['.amb-masuk', '.amb-garis', '.amb-jalur', '.amb-batas', '.amb-pin',
              '.amb-nilai', '.amb-tbl', '.amb-tiga', '.amb-teori', '.amb-jawab-hijau']:
        print(f'  {"✅" if k in hasil else "❌"} {k}')
    # pastikan TIDAK memakai variabel yang tidak ada
    for v in ['--hijau-bg', '--kuning', '--kuning-bg', '--merah-bg', '--abu-bg']:
        n = hasil.count(v)
        print(f'  {"❌ MASIH DIPAKAI" if n else "✅ tidak dipakai"}: {v}')


if __name__ == '__main__':
    utama()
