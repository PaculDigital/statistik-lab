#!/usr/bin/env python3
"""SKETSA KARTU UJI t — SUSUNAN 2 TINGKAT (ACC Bos 18Sep26: 1A·2A·3A).

MENGAPA SUSUNANNYA SEPERTI INI (dari diskusi dengan Bos):
Bos bertanya: "sebenarnya apa saja keluaran uji t? Apakah juga bisa tidak
signifikan dan bernilai positif atau negatif juga?" Jawabannya: BISA — ada
4 kemungkinan (Sig. × tanda). Itu memunculkan MISKONSEPSI KEDUA yang tadinya
tidak terpikir: mahasiswa menganggap "tidak signifikan tapi positif" berarti
"berpengaruh positif lemah". Itu SALAH — kalau tidak signifikan, tandanya
tidak boleh ditafsirkan sama sekali.

STRUKTUR YANG DIMINTA BOS:
  TINGKAT 1 — pilih HASIL yang kamu lihat di SPSS (4 kotak: Sig × tanda)
  TINGKAT 2 — keluar ARTINYA + apa yang harus ditulis + jangan bilang apa
  Termasuk 1 keadaan "marginal" (Sig. 0,05–0,10) yang sering bikin debat.

BAHASA (perintah Bos): mudah dipahami, TIDAK menakutkan, dan WAJIB memberi
CONTOH PENULISAN hasil interpretasi yang benar — jadi mahasiswa bisa meniru.

CARA JALAN: .venv/bin/python _sketsa/sketsa_uji_t2.py
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
  .bungkus{max-width:640px;margin:0 auto}
  h1{font-size:21px;margin:0 0 6px}
  h2{font-size:16.5px;margin:0}
  .eyebrow{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.09em;
           text-transform:uppercase;color:var(--teal);margin-bottom:10px}
  .papan{background:#fff;border:1px solid var(--garis);border-radius:14px;
         padding:18px;margin-top:14px}
  .pita{display:inline-block;font-size:11.5px;font-weight:700;padding:3px 9px;
        border-radius:999px;white-space:nowrap}
  .pita-hijau{background:var(--hijau-muda);color:var(--hijau)}
  .pita-merah{background:var(--merah-muda);color:var(--merah)}
  .pita-amber{background:var(--amber-muda);color:var(--amber)}
  .pita-teal{background:var(--teal-muda);color:var(--teal)}
  .pita-abu{background:#EFEBE3;color:var(--lembut)}
  .empat{display:grid;grid-template-columns:1fr 1fr;gap:9px}
  @media(max-width:520px){.empat{grid-template-columns:1fr}}
  .kotak{background:#fff;border:1px solid var(--garis);border-radius:11px;
         padding:12px 13px;text-align:left;font:inherit;color:inherit;cursor:pointer}
  .kotak.aktif{border-color:var(--teal);box-shadow:0 0 0 2px var(--teal-muda)}
  .kotak .kepala{display:flex;justify-content:space-between;gap:8px;
                 align-items:center;margin-bottom:6px}
  .kotak .nilai{font-size:12.5px;font-weight:700;font-variant-numeric:tabular-nums}
  .kotak .nama{font-size:13.5px;font-weight:700;display:block;margin-bottom:3px}
  .kotak .kecil{font-size:12.5px;color:var(--lembut)}
  .catatan{display:flex;gap:10px;align-items:flex-start;border-radius:11px;
           padding:12px 13px;font-size:13.5px;margin-top:12px}
  .catatan svg{flex:0 0 auto;margin-top:2px}
  .c-teal{background:var(--teal-muda)}
  .c-amber{background:var(--amber-muda)}
  .c-merah{background:var(--merah-muda)}
  .c-hijau{background:var(--hijau-muda)}
  .tulis{background:#F6F3EC;border-left:3px solid var(--teal);border-radius:8px;
         padding:12px 14px;margin-top:12px;font-size:13.5px}
  .tulis .lbl{font-size:11px;font-weight:700;letter-spacing:.07em;
              text-transform:uppercase;color:var(--lembut);margin-bottom:7px}
  .tulis p{margin:0 0 8px}
  .salah{color:var(--merah);font-weight:600}
  .benar{color:var(--hijau);font-weight:600}
  .dua{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  @media(max-width:520px){.dua{grid-template-columns:1fr}}
  .langkah{display:flex;gap:9px;align-items:center;color:var(--lembut);
           font-size:12.5px;margin-bottom:10px}
  .langkah b{background:var(--teal-muda);color:var(--teal);width:20px;height:20px;
             border-radius:50%;display:inline-flex;align-items:center;
             justify-content:center;font-size:11.5px;flex:0 0 auto}
</style>
"""

IKON_TAHU = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
             'stroke="#2E7D6F" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
             '<path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/></svg>')
IKON_ALERT = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
              'stroke="#9A7328" stroke-width="2"><path d="M12 9v4M12 17h.01"/>'
              '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3'
              'L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>')


def svg_sebaran(naik: bool) -> str:
    """Sebaran naik (positif) atau menurun (negatif)."""
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


# ── 4 HASIL + 1 MARGINAL ──────────────────────────────────────────────────
HASIL = [
    dict(kunci='sig-plus', nama='Ada pengaruh, searah dugaan',
         nilai='Sig. 0,008 · B +0,368', kelas='pita-hijau', label='DITERIMA',
         naik=True, kabar='Kabar baik — hasilmu sesuai dugaan.',
         arti=('Angka Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>, '
               'bukan kebetulan. Tanda plus artinya arahnya <b>sama</b> '
               'dengan yang kamu duga.'),
         benar=('Promosi berpengaruh positif dan signifikan terhadap kepuasan '
                '(B = 0,368; Sig. = 0,008). Artinya, semakin gencar promosi, '
                'semakin tinggi kepuasan konsumen. Hipotesis diterima.'),
         salah=None),
    dict(kunci='sig-minus', nama='Ada pengaruh, arah berlawanan',
         nilai='Sig. 0,003 · B −0,412', kelas='pita-merah', label='ADA TEMUAN',
         naik=False, kabar='Jangan panik — ini temuan, bukan kesalahan.',
         arti=('Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>. Tanda '
               'minus hanya menunjukkan <b>arahnya berlawanan</b> dengan '
               'dugaanmu. Dua hal ini terpisah: <i>"ada tidaknya"</i> dijawab '
               'Sig., <i>"arahnya"</i> dijawab tanda.'),
         benar=('Harga berpengaruh signifikan negatif terhadap kepuasan '
                '(B = −0,412; Sig. = 0,003). Artinya, semakin tinggi persepsi '
                'harga, semakin rendah kepuasan konsumen. Hasil ini berlawanan '
                'dengan hipotesis awal, dan diduga karena konsumen lebih '
                'peka terhadap harga pada produk sejenis.'),
         salah='Harga tidak berpengaruh terhadap kepuasan.'),
    dict(kunci='marginal', nama='Cenderung berpengaruh (marginal)',
         nilai='Sig. 0,062 · B −0,380', kelas='pita-amber', label='HATI-HATI',
         naik=False, kabar='Hasilnya di batas — perlu dibahas, jangan dipaksa.',
         arti=('Sig. 0,062 berada <b>di atas 0,05</b> tapi belum jauh. '
               'Sebagian dosen menerima sampai 0,10, sebagian tidak. '
               '<b>Jangan menaikkan ambang jadi 0,10 hanya supaya '
               '"jadi signifikan"</b> — itu bisa dianggap mencari-cari.'),
         benar=('Harga berpengaruh negatif terhadap kepuasan, namun belum '
                'mencapai signifikansi pada α = 0,05 (B = −0,380; '
                'Sig. = 0,062). Arah pengaruhnya sejalan dengan dugaan dan '
                'cenderung berpengaruh; disarankan menambah jumlah responden '
                'untuk memastikan.'),
         salah='Harga berpengaruh negatif signifikan terhadap kepuasan.'),
    dict(kunci='tidaksig-plus', nama='Tidak ada pengaruh (tanda plus)',
         nilai='Sig. 0,142 · B +0,204', kelas='pita-abu', label='TIDAK TERBUKTI',
         naik=True, kabar='Tidak apa-apa — bukan berarti gagal.',
         arti=('Sig. di atas 0,05 artinya buktinya <b>belum cukup</b> untuk '
               'bilang ada pengaruh. <b>Penting:</b> kalau tidak signifikan, '
               'tandanya <b>tidak boleh ditafsirkan</b> — angka +0,204 itu '
               'bisa saja kebetulan.'),
         benar=('Kualitas tidak terbukti berpengaruh nyata terhadap kepuasan '
                '(B = 0,204; Sig. = 0,142). Dengan demikian hipotesis tidak '
                'terbukti pada penelitian ini.'),
         salah='Kualitas berpengaruh positif tapi lemah terhadap kepuasan.'),
    dict(kunci='tidaksig-minus', nama='Tidak ada pengaruh (tanda minus)',
         nilai='Sig. 0,310 · B −0,115', kelas='pita-abu', label='TIDAK TERBUKTI',
         naik=False, kabar='Sama seperti di atas — tandanya belum bisa dipakai.',
         arti=('Sig. di atas 0,05 = buktinya belum cukup. Tanda minusnya '
               '<b>juga tidak bisa ditafsirkan</b> — jangan menulis '
               '"cenderung menurunkan" kalau belum signifikan.'),
         benar=('Tidak ada bukti yang cukup bahwa variabel ini berpengaruh '
                'terhadap kepuasan (B = −0,115; Sig. = 0,310). Hipotesis tidak '
                'terbukti pada penelitian ini.'),
         salah='Variabel ini cenderung menurunkan kepuasan.'),
]


def kartu_hasil(k: str) -> str:
    """Kartu TINGKAT 1 — 4 kotak pilih hasil (+ 1 marginal)."""
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
  <div class="langkah"><b>1</b> Lihat tabel Coefficients di SPSS-mu, cari dua angka ini</div>
  <h2 style="margin-bottom:10px">Hasilmu yang mana?</h2>
  <div class="empat">{kotak}</div>
  <p style="font-size:12.5px;color:#6B6259;margin:10px 0 0">
    Yang dipakai cuma dua angka: <b>Sig.</b> (ada pengaruhnya atau tidak)
    dan <b>tanda di B</b> (arahnya). Selebihnya tidak perlu.</p>
</div>
"""


def kartu_arti(h: dict) -> str:
    """Kartu TINGKAT 2 — arti + contoh penulisan."""
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
    <div>
      <div class="catatan {kelas_ikon}" style="margin-top:0">{IKON_TAHU}
        <div>{h['arti']}</div></div>
    </div>
  </div>
  <div class="tulis">
    <div class="lbl">Contoh penulisan di skripsi</div>
    <p><span class="benar">✓ Tulis seperti ini:</span><br>&ldquo;{h['benar']}&rdquo;</p>
    {blok_salah}
  </div>
</div>
"""


def halaman(k: str) -> str:
    h = next(x for x in HASIL if x['kunci'] == k)
    return f"""
<div class="bungkus">
  <span class="eyebrow">📖 BELAJAR</span>
  <h1>Uji t: membaca hasil dengan tenang</h1>
  <p style="color:#6B6259;margin:4px 0 0">
    Pilih hasil yang kamu lihat di SPSS — keluar artinya dan contoh
    penulisannya.</p>
  {kartu_hasil(k)}
  {kartu_arti(h)}
  <div class="papan">
    <div class="catatan c-hijau" style="margin-top:0">{IKON_TAHI if False else IKON_TAHU}
      <div><b>Ingat satu kalimat ini:</b> <i>Sig. menjawab &ldquo;ada
      pengaruhnya atau tidak&rdquo;; tanda di B menjawab &ldquo;arahnya ke
      mana&rdquo;.</i> Dua pertanyaan berbeda — jawabannya boleh tidak
      seasal.</div></div>
    <div class="catatan c-amber">{IKON_ALERT}
      <div><b>Jangan pernah buang data supaya tandanya jadi plus.</b>
      Itu memalsukan hasil. Kalau arahnya berlawanan, laporkan apa adanya
      lalu bahas sebabnya — penguji justru akan menghargai.</div></div>
  </div>
</div>
"""


def render(nama: str, isi: str) -> pathlib.Path:
    html = (f'<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{GAYA}</head><body>{isi}</body></html>')
    f_html = OUT / f'sketsa2_{nama}.html'
    f_html.write_text(html)
    f_png = OUT / f'sketsa2_{nama}.png'
    subprocess.run([CH, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--hide-scrollbars', '--window-size=820,2600',
                    f'--screenshot={f_png}', f'file://{f_html}'],
                   capture_output=True, timeout=150)
    assert f_png.exists() and f_png.stat().st_size > 20000, f'{nama} gagal'
    return f_png


if __name__ == '__main__':
    for kunci in ['sig-minus', 'tidaksig-plus', 'marginal']:
        p = render(kunci, halaman(kunci))
        print(f'OK {kunci}: {p.stat().st_size} byte')
