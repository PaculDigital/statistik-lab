#!/usr/bin/env python3
"""SKETSA KARTU UJI t — 3 LAPIS (ACC Bos 18Sep26 malam: 1A · 2A · 3A).

MENGAPA BENTUKNYA SEPERTI INI (dari pertanyaan Bos):
Bos bertanya: "bisakah juga memberikan kemungkinan APA YANG TERJADI sehingga
hasilnya seperti ini, dan BAGAIMANA CARA MEMPERBAIKINYA (apakah ini cara
curang)?" — pertanyaan itu memunculkan LAPIS 3.

TIGA LAPIS:
  ① "Ini hasil saya"          → 5 kotak (4 kuadran Sig×tanda + 1 marginal)
  ② "Artinya apa"             → penjelasan tenang + contoh ✓ menulis / ✗ jangan
  ③ "Kenapa & boleh diperbaiki?" → sebab-sebab + cara memperbaiki dengan label
        ✅ SAH / ⚠️ HATI-HATI / ❌ CURANG  + daftar periksa 5 langkah

PRINSIP PEMISAH (harus tampil di kartu, ini inti pelajarannya):
  ✅ MEMPERBAIKI  = membetulkan yang memang salah (salah SEBELUM lihat hasil)
  ❌ MENCARI-CARI = mengubah cara analisis SUPAYA hasilnya berubah
  Uji lakmus: "Saya ubah ini karena datanya sudah begini, atau karena saya
  tidak suka hasilnya?" → kalau yang kedua, itu curang.

BAHASA (perintah Bos): mudah dipahami, TIDAK menakutkan (jangan pakai kata
"FATAL/BODOH/DOSA"), beri jalan keluar, dan selalu sertakan contoh penulisan.

CARA JALAN: .venv/bin/python _sketsa/sketsa_uji_t3.py
"""
from __future__ import annotations

import pathlib
import subprocess

OUT = pathlib.Path('/tmp/shot')
CH = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'

GAYA = """
<style>
  :root{--kertas:#FBF8F3;--tinta:#2B2722;--lembut:#6B6259;--garis:#E0D8C8;
        --teal:#2E7D6F;--teal-muda:#E8F1EE;--merah:#A85A5A;--merah-muda:#F7ECEC;
        --hijau:#3C7A5A;--hijau-muda:#EAF3EE;--amber:#9A7328;--amber-muda:#FBF3E2;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--kertas);color:var(--tinta);
       font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
       padding:26px 16px;font-size:14.5px;line-height:1.58}
  .bungkus{max-width:660px;margin:0 auto}
  h1{font-size:21px;margin:0 0 6px}
  h2{font-size:16.5px;margin:0}
  h3{font-size:14px;margin:0 0 8px}
  .eyebrow{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.09em;
           text-transform:uppercase;color:var(--teal);margin-bottom:10px}
  .papan{background:#fff;border:1px solid var(--garis);border-radius:14px;
         padding:18px;margin-top:13px}
  .pita{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;
        border-radius:999px;white-space:nowrap}
  .pita-hijau{background:var(--hijau-muda);color:var(--hijau)}
  .pita-merah{background:var(--merah-muda);color:var(--merah)}
  .pita-amber{background:var(--amber-muda);color:var(--amber)}
  .pita-teal{background:var(--teal-muda);color:var(--teal)}
  .pita-abu{background:#EFEBE3;color:var(--lembut)}
  .langkah{display:flex;gap:9px;align-items:center;color:var(--lembut);
           font-size:12.5px;margin-bottom:11px}
  .langkah b{background:var(--teal-muda);color:var(--teal);width:21px;height:21px;
             border-radius:50%;display:inline-flex;align-items:center;
             justify-content:center;font-size:11.5px;flex:0 0 auto}
  .empat{display:grid;grid-template-columns:1fr 1fr;gap:9px}
  .dua{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media(max-width:540px){.empat,.dua{grid-template-columns:1fr}}
  .kotak{background:#fff;border:1px solid var(--garis);border-radius:11px;
         padding:11px 12px;text-align:left;font:inherit;color:inherit;cursor:pointer}
  .kotak.aktif{border-color:var(--teal);box-shadow:0 0 0 2px var(--teal-muda)}
  .kotak .kepala{display:flex;justify-content:space-between;gap:7px;
                 align-items:center;margin-bottom:5px}
  .kotak .nilai{font-size:12px;font-weight:700;font-variant-numeric:tabular-nums}
  .kotak .nama{font-size:13px;font-weight:700;display:block;margin-bottom:2px}
  .kotak .kecil{font-size:12px;color:var(--lembut)}
  .catatan{display:flex;gap:10px;align-items:flex-start;border-radius:11px;
           padding:12px 13px;font-size:13.5px}
  .catatan svg{flex:0 0 auto;margin-top:2px}
  .c-teal{background:var(--teal-muda)}
  .c-amber{background:var(--amber-muda)}
  .c-merah{background:var(--merah-muda)}
  .c-hijau{background:var(--hijau-muda)}
  .tulis{background:#F6F3EC;border-left:3px solid var(--teal);border-radius:8px;
         padding:12px 14px;margin-top:12px;font-size:13.5px}
  .tulis .lbl{font-size:10.5px;font-weight:700;letter-spacing:.07em;
              text-transform:uppercase;color:var(--lembut);margin-bottom:7px}
  .tulis p{margin:0 0 8px}
  .salah{color:var(--merah);font-weight:600}
  .benar{color:var(--hijau);font-weight:600}
  table{border-collapse:collapse;width:100%;font-size:13px}
  th,td{padding:9px 8px;border-bottom:1px solid var(--garis);text-align:left;
        vertical-align:top}
  th{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;
     color:var(--lembut);font-weight:700}
  tr:last-child td{border-bottom:0}
  .tag{font-size:10.5px;font-weight:700;padding:3px 8px;border-radius:999px;
       white-space:nowrap;display:inline-block}
  .tag-sah{background:var(--hijau-muda);color:var(--hijau)}
  .tag-hati{background:var(--amber-muda);color:var(--amber)}
  .tag-curang{background:var(--merah-muda);color:var(--merah)}
  .cek{display:grid;gap:8px;margin-top:4px}
  .cek-item{display:flex;gap:10px;align-items:flex-start;background:#F6F3EC;
            border-radius:9px;padding:10px 12px;font-size:13px}
  .cek-item .n{background:#fff;border:1px solid var(--garis);width:22px;height:22px;
               border-radius:50%;display:inline-flex;align-items:center;
               justify-content:center;font-size:11.5px;font-weight:700;
               flex:0 0 auto}
  .tombol-cek{display:inline-flex;gap:9px;align-items:center;background:var(--teal);
              color:#fff;border:0;border-radius:11px;padding:12px 16px;
              font:inherit;font-size:13.5px;font-weight:700;cursor:pointer;margin-top:4px}
</style>
"""

IKON_TAHU = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
             'stroke="#2E7D6F" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
             '<path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/></svg>')
IKON_ALERT = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
              'stroke="#9A7328" stroke-width="2"><path d="M12 9v4M12 17h.01"/>'
              '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3'
              'L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>')
IKON_SEARCH = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
               'stroke="#fff" stroke-width="2"><circle cx="11" cy="11" r="8"/>'
               '<path d="m21 21-4.3-4.3"/></svg>')


def svg_sebaran(naik: bool) -> str:
    titik = [(62, 108), (88, 100), (112, 92), (140, 86), (168, 74),
             (196, 66), (224, 58), (252, 48), (280, 40)]
    if not naik:
        titik = [(x, 150 - y + 12) for x, y in titik]
    g = ''.join(f'<circle cx="{x}" cy="{y}" r="3" fill="#2E7D6F" opacity=".55"/>'
                for x, y in titik)
    warna = '#3C7A5A' if naik else '#A85A5A'
    x1, y1, x2, y2 = (40, 112, 298, 32) if naik else (40, 38, 298, 118)
    return f"""<svg viewBox="0 0 320 150" style="width:100%;height:auto;display:block">
  <line x1="26" y1="128" x2="308" y2="128" stroke="#E0D8C8" stroke-width="1.5"/>
  <line x1="26" y1="20" x2="26" y2="128" stroke="#E0D8C8" stroke-width="1.5"/>
  <text x="167" y="145" text-anchor="middle" font-size="10.5" fill="#6B6259">X</text>
  <text x="12" y="74" text-anchor="middle" font-size="10.5" fill="#6B6259"
        transform="rotate(-90 12 74)">Y</text>
  {g}
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{warna}" stroke-width="2.2"/>
</svg>"""


HASIL = [
    dict(kunci='sig-plus', nama='Ada pengaruh, searah dugaan',
         nilai='Sig. 0,008 · B +0,368', kelas='pita-hijau', label='DITERIMA',
         naik=True, kabar='Hasilmu sesuai dugaan.',
         arti=('Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>, bukan '
               'kebetulan. Tanda plus artinya arahnya <b>sama</b> dengan '
               'yang kamu duga.'),
         benar=('Promosi berpengaruh positif dan signifikan terhadap kepuasan '
                '(B = 0,368; Sig. = 0,008). Semakin gencar promosi, semakin '
                'tinggi kepuasan konsumen. Hipotesis diterima.'),
         salah=None,
         sebab=[('Hasilnya memang seperti dugaan', 'Tidak ada yang perlu '
                 'diperbaiki — lanjutkan ke pembahasan.')],
         cek=['Baca ulang salah satu item kuisioner — kalimatnya sudah '
              'bernada sesuai nama variabelnya?',
              'Nilai Alpha Cronbach sudah di atas 0,70?',
              'Jumlah responden sudah memenuhi rumus sampel?']),
    dict(kunci='sig-minus', nama='Ada pengaruh, arah berlawanan',
         nilai='Sig. 0,003 · B −0,412', kelas='pita-merah', label='ADA TEMUAN',
         naik=False, kabar='Jangan panik — ini temuan, bukan kesalahan.',
         arti=('Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>. Tanda '
               'minus hanya menunjukkan <b>arahnya berlawanan</b>. Dua hal '
               'terpisah: <i>"ada tidaknya"</i> dijawab Sig., <i>"arahnya"</i> '
               'dijawab tanda.'),
         benar=('Harga berpengaruh signifikan negatif terhadap kepuasan '
                '(B = −0,412; Sig. = 0,003). Semakin tinggi persepsi harga, '
                'semakin rendah kepuasan konsumen. Hasil ini berlawanan dengan '
                'hipotesis awal, diduga karena konsumen lebih peka terhadap '
                'harga pada produk sejenis.'),
         salah='Harga tidak berpengaruh terhadap kepuasan.',
         sebab=[
             ('Skala kuisioner terbalik',
              'Item <i>"harga produk ini mahal"</i> diskor 5 = sangat setuju. '
              'Skor tinggi berarti kepuasan RENDAH.',
              'Reverse coding (5→1, 4→2, 3→3), lalu hitung ulang. <b>Memang '
              'salah sejak awal</b>, bukan mengubah hasil.', 'sah'),
             ('Salah menentukan Y',
              'Memakai <i>"Ketidakpuasan"</i> padahal seharusnya '
              '<i>"Kepuasan"</i>.',
              'Perbaiki nama &amp; konsep variabel sesuai teori aslinya.',
              'sah'),
             ('Multikolinearitas (VIF &gt; 10)',
              'Dua X saling berkaitan sangat erat, sehingga X2 "mencuri" '
              'pengaruh X1 dan tandanya berputar.',
              'Gabung atau sisihkan salah satu X — <b>dengan alasan teori '
              'yang ditulis di skripsi</b>, bukan karena hasilnya.', 'hati'),
             ('Ada pencilan (data ekstrem)',
              'Beberapa responden dengan pola jawaban jauh berbeda.',
              'Buang <b>hanya kalau terbukti salah input atau jawaban asal</b> '
              '(lihat Box-Plot). Membuang yang wajar hanya supaya tanda jadi '
              'plus = curang.', 'hati'),
             ('Hipotesisnya memang berlawanan',
              'Hubungan yang sebenarnya memang berkebalikan, dan itu wajar.',
              '<b>Tidak perlu diperbaiki.</b> Laporkan apa adanya lalu bahas '
              'sebabnya — penguji menghargai ini.', 'sah'),
         ],
         cek=['Baca ulang <b>kalimat setiap item</b> — ada yang bernada negatif '
              '("mahal", "lambat", "sulit")?',
              'Cek <b>VIF</b> di tabel Coefficients — kalau di atas 10, tanda '
              'tidak bisa ditafsirkan dulu.',
              'Buat <b>Box-Plot</b> — ada data ekstrem yang bukan wajar?',
              'Cek apakah Y sudah yang benar (bukan kebalikannya).',
              'Diskusikan dengan pembimbing sebelum mengubah apa pun.']),
    dict(kunci='marginal', nama='Cenderung berpengaruh (marginal)',
         nilai='Sig. 0,062 · B −0,380', kelas='pita-amber', label='HATI-HATI',
         naik=False, kabar='Di batas — perlu dibahas, jangan dipaksa.',
         arti=('Sig. 0,062 berada <b>di atas 0,05</b> tapi belum jauh. '
               'Sebagian dosen menerima sampai 0,10, sebagian tidak. '
               '<b>Jangan menaikkan ambang jadi 0,10 hanya supaya "jadi '
               'signifikan".</b>'),
         benar=('Harga berpengaruh negatif terhadap kepuasan, namun belum '
                'mencapai signifikansi pada α = 0,05 (B = −0,380; '
                'Sig. = 0,062). Arahnya sejalan dengan dugaan dan cenderung '
                'berpengaruh; disarankan menambah jumlah responden untuk '
                'memastikan.'),
         salah='Harga berpengaruh negatif signifikan terhadap kepuasan.',
         sebab=[
             ('Responden kurang',
              'Dengan bukti yang sedikit, pengaruh yang sebenarnya ada pun '
              'bisa tampak tidak meyakinkan.',
              'Tambah responden mengikuti <b>rumus sampel</b> yang sudah kamu '
              'tetapkan di BAB III.', 'sah'),
             ('Alat ukur kurang tajam',
              'Nilai Alpha Cronbach rendah → jawaban beragam tidak '
              'menggambarkan satu hal.',
              'Rapikan kalimat item (susun ulang kuisioner), ambil ulang data.',
              'sah'),
             ('Pengaruhnya memang kecil',
              'Hubungannya lemah di dunia nyata, bukan soal jumlah data.',
              '<b>Terima hasilnya.</b> Tulis apa adanya — itu jujur dan tetap '
              'dihargai.', 'sah'),
             ('Menaikkan α jadi 0,10 setelah melihat hasil',
              'Menggeser batas <b>sesudah tahu hasilnya</b>.',
              '<b>Jangan.</b> Batas harus ditetapkan di BAB III sebelum data '
              'dikumpulkan.', 'curang'),
         ],
         cek=['Berapa <b>jumlah responden</b>mu, dan sudah memenuhi rumus '
              'sampel?',
              'Berapa <b>Alpha Cronbach</b> tiap variabel?',
              'Apakah <b>α = 0,05</b> sudah kamu tulis di BAB III <b>sebelum</i> '
              'mengumpulkan data?',
              'Apakah kamu mengambil ulang data, atau hanya menggeser batas?',
              'Sudah minta pendapat pembimbing?']),
    dict(kunci='tidaksig-plus', nama='Tidak ada pengaruh (tanda plus)',
         nilai='Sig. 0,142 · B +0,204', kelas='pita-abu', label='TIDAK TERBUKTI',
         naik=True, kabar='Tidak apa-apa — bukan berarti gagal.',
         arti=('Sig. di atas 0,05 artinya buktinya <b>belum cukup</b>. '
               '<b>Penting:</b> kalau tidak signifikan, tandanya <b>tidak boleh '
               'ditafsirkan</b> — angka +0,204 bisa saja kebetulan.'),
         benar=('Kualitas tidak terbukti berpengaruh nyata terhadap kepuasan '
                '(B = 0,204; Sig. = 0,142). Dengan demikian hipotesis tidak '
                'terbukti pada penelitian ini.'),
         salah='Kualitas berpengaruh positif tapi lemah terhadap kepuasan.',
         sebab=[
             ('Responden kurang',
              'Bukti yang terkumpul belum cukup kuat untuk menyimpulkan ada '
              'pengaruh.',
              'Tambah responden sesuai <b>rumus sampel</b>, dikumpulkan '
              'berdasarkan sasaran yang sudah direncanakan.', 'sah'),
             ('Pertanyaannya kurang menggigit',
              'Item kuisioner terlalu umum, sehingga jawaban tidak menangkap '
              'pengaruh yang sebenarnya.',
              'Perbaiki kalimat item, lalu ambil ulang data.', 'sah'),
             ('Variabelnya memang tidak berpengaruh',
              'Bisa jadi di objek penelitianmu, variabel itu memang bukan '
              'penentu.',
              '<b>Laporkan apa adanya.</b> Ini tetap temuan yang sah dan bisa '
              'jadi bahan pembahasan.', 'sah'),
             ('Menghapus data sampai Sig. &lt; 0,05',
              'Membuang responden atau mengubah cara hitung berkali-kali '
              'sampai hasilnya lolos.',
              '<b>Jangan.</b> Ini yang dalam penelitian disebut '
              '<i>p-hacking</i> — hasilnya tidak bisa dipercaya.', 'curang'),
             ('Mencoba banyak model, melaporkan yang lolos saja',
              'Ganti-ganti susunan X sampai ada yang signifikan, lalu hanya '
              'yang lolos ditulis.',
              '<b>Jangan.</b> Model harus ditentukan dari teori di BAB II, '
              'bukan dari hasil.', 'curang'),
         ],
         cek=['Jumlah responden sudah memenuhi rumus sampel?',
              'Alpha Cronbach tiap variabel di atas 0,70?',
              'Susunan X dan Y mengikuti teori di BAB II, atau diubah setelah '
              'melihat hasil?',
              'Anda mengambil <b>data baru</b>, atau hanya menyortir data lama '
              'berulang kali?',
              'Sudah dibahas dengan pembimbing?']),
    dict(kunci='tidaksig-minus', nama='Tidak ada pengaruh (tanda minus)',
         nilai='Sig. 0,310 · B −0,115', kelas='pita-abu', label='TIDAK TERBUKTI',
         naik=False, kabar='Tandanya belum bisa dipakai juga.',
         arti=('Sig. di atas 0,05 = buktinya belum cukup. Tanda minusnya '
               '<b>juga tidak bisa ditafsirkan</b> — jangan menulis '
               '"cenderung menurunkan" kalau belum signifikan.'),
         benar=('Tidak ada bukti yang cukup bahwa variabel ini berpengaruh '
                'terhadap kepuasan (B = −0,115; Sig. = 0,310). Hipotesis tidak '
                'terbukti pada penelitian ini.'),
         salah='Variabel ini cenderung menurunkan kepuasan.',
         sebab=[
             ('Responden kurang', 'Bukti belum cukup kuat.',
              'Tambah responden sesuai rumus sampel.', 'sah'),
             ('Tidak ada pengaruh nyata', 'Memang tidak berpengaruh di objek ini.',
              'Laporkan apa adanya dan bahas di pembahasan.', 'sah'),
             ('Menyortir data sampai tandanya berubah',
              'Mengubah data supaya arahnya sesuai dugaan.',
              '<b>Jangan.</b> Tanda tidak boleh "dibuat" — hanya boleh '
              'dilaporkan.', 'curang'),
         ],
         cek=['Jumlah responden memenuhi rumus sampel?',
              'Alpha Cronbach di atas 0,70?',
              'Tidak ada data yang diubah/dibuang setelah melihat hasil?',
              'Sudah dibahas dengan pembimbing?']),
]

CARA_CURANG = [
    ('p-hacking', 'Membuang data atau mengubah cara hitung sampai Sig. < 0,05'),
    ('Menggeser batas α', 'α diubah 0,05 → 0,10 <b>setelah</b> melihat hasil'),
    ('Fishing', 'Mencoba banyak model, hanya yang lolos dilaporkan'),
    ('HARKing', 'Hipotesis diubah <b>setelah</b> tahu hasilnya'),
    ('Buang pencilan tanpa dasar', 'Membuang responden "aneh" hanya karena '
                                   'mengganggu hasil'),
]


def kartu_hasil(k: str) -> str:
    kotak = ''
    for i, h in enumerate(HASIL, 1):
        aktif = ' aktif' if h['kunci'] == k else ''
        kotak += (f'<button class="kotak{aktif}">'
                  f'<span class="kepala"><span class="nilai">{h["nilai"]}</span>'
                  f'<span class="pita {h["kelas"]}">{h["label"]}</span></span>'
                  f'<span class="nama">{i}. {h["nama"]}</span>'
                  f'<span class="kecil">{h["kabar"]}</span></button>')
    return f"""
<div class="papan">
  <div class="langkah"><b>1</b> Buka tabel Coefficients di SPSS-mu</div>
  <h2 style="margin-bottom:10px">Hasilmu yang mana?</h2>
  <div class="empat">{kotak}</div>
  <p style="font-size:12.5px;color:#6B6259;margin:10px 0 0">
    Hanya dua angka yang dipakai: <b>Sig.</b> (ada pengaruhnya atau tidak)
    dan <b>tanda di B</b> (arahnya).</p>
</div>
"""


def kartu_arti(h: dict) -> str:
    kelas_ikon = 'c-teal' if h['label'] in ('DITERIMA', 'ADA TEMUAN') else 'c-amber'
    blok_salah = ''
    if h['salah']:
        blok_salah = (f'<p><span class="salah">✗ Jangan menulis:</span><br>'
                      f'&ldquo;{h["salah"]}&rdquo;</p>')
    return f"""
<div class="papan">
  <div class="langkah"><b>2</b> Baca artinya &amp; contoh penulisannya</div>
  <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
    <h2>{h['nama']}</h2>
    <span class="pita {h['kelas']}">{h['label']}</span>
  </div>
  <div class="dua" style="margin-top:12px">
    <div>{svg_sebaran(h['naik'])}</div>
    <div class="catatan {kelas_ikon}">{IKON_TAHU}<div>{h['arti']}</div></div>
  </div>
  <div class="tulis">
    <div class="lbl">Contoh penulisan di skripsi</div>
    <p><span class="benar">✓ Tulis seperti ini:</span><br>&ldquo;{h['benar']}&rdquo;</p>
    {blok_salah}
  </div>
</div>
"""


def kartu_sebab(h: dict) -> str:
    baris = ''
    for sebab, kenapa, cara, tag in h['sebab']:
        kelas = {'sah': 'tag-sah', 'hati': 'tag-hati',
                 'curang': 'tag-curang'}[tag]
        teks = {'sah': '✅ SAH', 'hati': '⚠️ HATI-HATI',
                'curang': '❌ CURANG'}[tag]
        baris += (f'<tr><td><b>{sebab}</b><div style="font-size:12.5px;'
                  f'color:#6B6259;margin-top:3px">{kenapa}</div></td>'
                  f'<td style="font-size:13px">{cara}</td>'
                  f'<td><span class="tag {kelas}">{teks}</span></td></tr>')
    return f"""
<div class="papan">
  <div class="langkah"><b>3</b> Kenapa bisa begitu &amp; boleh diperbaiki?</div>
  <h2 style="margin-bottom:4px">Kemungkinan sebabnya</h2>
  <p style="font-size:12.5px;color:#6B6259;margin:0 0 10px">
    Tidak semua perlu diperbaiki. Lihat labelnya dulu sebelum mengubah
    apa pun.</p>
  <table>
    <tr><th>Kemungkinan sebab</th><th>Cara memperbaiki</th>
        <th>Boleh?</th></tr>
    {baris}
  </table>
  <div class="catatan c-merah" style="margin-top:14px">{IKON_ALERT}
    <div><b>Uji lakmus — satu kalimat:</b><br>
    <i>&ldquo;Saya mengubah ini karena datanya memang sudah begini,
    atau karena saya tidak suka hasilnya?&rdquo;</i><br>
    Kalau jawabannya yang <b>kedua</b> — itu bukan memperbaiki, itu mencari-cari.</div>
  </div>
</div>
"""


def kartu_curang() -> str:
    baris = ''
    for i, (nama, bentuk) in enumerate(CARA_CURANG, 1):
        baris += (f'<div class="cek-item"><span class="n">{i}</span>'
                  f'<div><b>{nama}</b><br>'
                  f'<span style="color:#6B6259">{bentuk}</span></div></div>')
    return f"""
<div class="papan">
  <h2 style="margin-bottom:4px">5 cara yang harus kamu hindari</h2>
  <p style="font-size:12.5px;color:#6B6259;margin:0 0 10px">
    Bukan karena penguji melarang, tapi karena hasilnya jadi tidak bisa
    dipercaya — termasuk oleh dirimu sendiri.</p>
  <div class="cek">{baris}</div>
  <div class="catatan c-hijau" style="margin-top:14px">{IKON_TAHU}
    <div><b>Kuncinya cuma satu: urutan.</b> Rencanakan dulu (di BAB III),
    baru lihat hasil. Kalau <b>hasil dilihat dulu, baru aturan diubah</b> —
    itulah masalahnya.</div></div>
</div>
"""


def kartu_cek(h: dict) -> str:
    butir = ''.join(
        f'<div class="cek-item"><span class="n">{i}</span><div>{t}</div></div>'
        for i, t in enumerate(h['cek'], 1))
    return f"""
<div class="papan">
  <h2 style="margin-bottom:4px">Belum yakin datanya benar?</h2>
  <p style="font-size:13px;color:#6B6259;margin:0 0 10px">
    Tidak perlu takut bertanya. Periksa dulu lima hal ini — semuanya cara
    yang sah, dan justru itu yang dilakukan peneliti yang baik.</p>
  <button class="tombol-cek">{IKON_SEARCH} Tampilkan daftar periksa</button>
  <div class="cek" style="margin-top:12px">{butir}</div>
</div>
"""


def halaman(k: str) -> str:
    h = next(x for x in HASIL if x['kunci'] == k)
    return f"""
<div class="bungkus">
  <span class="eyebrow">📖 BELAJAR</span>
  <h1>Uji t: membaca hasil dengan tenang</h1>
  <p style="color:#6B6259;margin:4px 0 0">
    Pilih hasil yang kamu lihat di SPSS — keluar artinya, contoh
    penulisannya, dan apa yang boleh kamu perbaiki.</p>
  {kartu_hasil(k)}
  {kartu_arti(h)}
  {kartu_sebab(h)}
  {kartu_curang()}
  {kartu_cek(h)}
</div>
"""


def render(nama: str, isi: str) -> pathlib.Path:
    html = (f'<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{GAYA}</head><body>{isi}</body></html>')
    f_html = OUT / f'sketsa3_{nama}.html'
    f_html.write_text(html)
    f_png = OUT / f'sketsa3_{nama}.png'
    subprocess.run([CH, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--hide-scrollbars', '--window-size=820,4200',
                    f'--screenshot={f_png}', f'file://{f_html}'],
                   capture_output=True, timeout=180)
    assert f_png.exists() and f_png.stat().st_size > 20000, f'{nama} gagal'
    return f_png


if __name__ == '__main__':
    for kunci in ['sig-minus', 'tidaksig-plus']:
        p = render(kunci, halaman(kunci))
        print(f'OK {kunci}: {p.stat().st_size} byte')
