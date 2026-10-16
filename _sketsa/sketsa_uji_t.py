#!/usr/bin/env python3
"""SKETSA KARTU UJI t — dua pilihan desain (ACC Bos: kartu khusus di BELAJAR).

MENGAPA SKETSA DULU (kebiasaan kerja dengan Bos):
Bos selalu minta melihat bentuknya dulu sebelum Wulan menulis kode sungguhan.
Di sini Wulan menggambar DUA bentuk alternatif, merender keduanya, lalu
mengirim tangkapan layarnya supaya Bos memilih.

RANCANGAN YANG DIUJI (dari diskusi 18Sep26):
"1 kartu khusus untuk simulasi menjelaskan uji t yang sering dialami mahasiswa
 dan mereka bingung, signifikan kok hasilnya negatif; disertai penjelasan dan
 buat interaktif agar menarik; dilengkapi beberapa skenario uji t."

DESAIN A — "PILIH SKENARIO": kartu berisi daftar 5 skenario (kartu kecil yang
           bisa diklik), lalu di bawahnya satu panel hasil yang berubah sesuai
           skenario terpilih.
DESAIN B — "SATU KARTU, DUA KOTAK SEJAJAR": sebelah kiri gambar sebaran, sebelah
           kanan kalimat penjelasan; skenario dipilih lewat tombol kecil di atas.

Keduanya dijalankan TANPA browser (murni HTML statis) supaya cepat dan tidak
kena masalah cache.
"""
from __future__ import annotations

import pathlib
import subprocess

OUT = pathlib.Path('/tmp/shot')
OUT.mkdir(parents=True, exist_ok=True)
CH = '/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome'

GAYA = """
<style>
  :root{--kertas:#FBF8F3;--tinta:#2B2722;--lembut:#6B6259;--garis:#E0D8C8;
        --teal:#2E7D6F;--teal-muda:#E8F1EE;--merah:#A85A5A;--merah-muda:#F7ECEC;
        --hijau:#3C7A5A;--hijau-muda:#EAF3EE;--amber:#9A7328;--amber-muda:#FBF3E2;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--kertas);color:var(--tinta);
       font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
       padding:26px 16px;font-size:14.5px;line-height:1.55}
  .bungkus{max-width:620px;margin:0 auto}
  h1{font-size:21px;margin:0 0 6px}
  h2{font-size:17px;margin:0}
  .eyebrow{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.09em;
           text-transform:uppercase;color:var(--teal);margin-bottom:10px}
  .papan{background:#fff;border:1px solid var(--garis);border-radius:14px;
         padding:18px;margin-top:14px}
  .pita{display:inline-block;font-size:11.5px;font-weight:700;padding:3px 9px;
        border-radius:999px}
  .pita-merah{background:var(--merah-muda);color:var(--merah)}
  .pita-hijau{background:var(--hijau-muda);color:var(--hijau)}
  .pita-teal{background:var(--teal-muda);color:var(--teal)}
  .catatan{display:flex;gap:10px;align-items:flex-start;border-radius:11px;
           padding:12px 13px;font-size:13.5px;margin-top:12px}
  .catatan svg{flex:0 0 auto;margin-top:2px}
  .c-teal{background:var(--teal-muda)}
  .c-amber{background:var(--amber-muda)}
  /* DESAIN A */
  .skenario{display:grid;gap:8px;margin-top:12px}
  .sk{display:flex;gap:11px;align-items:flex-start;background:#fff;
      border:1px solid var(--garis);border-radius:11px;padding:11px 13px;
      cursor:pointer;text-align:left;font:inherit;color:inherit;width:100%}
  .sk.aktif{border-color:var(--teal);box-shadow:0 0 0 2px var(--teal-muda)}
  .sk .no{flex:0 0 auto;width:22px;height:22px;border-radius:50%;
          background:var(--teal-muda);color:var(--teal);font-size:12px;
          font-weight:700;display:flex;align-items:center;justify-content:center}
  .sk b{display:block;font-size:13.5px}
  .sk span{font-size:12.5px;color:var(--lembut)}
  /* DESAIN B */
  .dua{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:12px}
  @media(max-width:520px){.dua{grid-template-columns:1fr}}
  .angka-besar{font-size:34px;font-weight:800;letter-spacing:-.02em}
  .baris-t{display:grid;grid-template-columns:auto 1fr auto;gap:10px;
           align-items:center;font-size:13.5px;padding:7px 0;
           border-bottom:1px solid var(--garis)}
  .baris-t:last-child{border-bottom:0}
  .mono{font-variant-numeric:tabular-nums;font-weight:700}
  table{border-collapse:collapse;width:100%;font-size:13px}
  th,td{padding:7px 8px;border-bottom:1px solid var(--garis);text-align:left}
  th{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--lembut)}
</style>
"""

SEBARAN = """
<svg viewBox="0 0 320 150" style="width:100%;height:auto;display:block">
  <line x1="26" y1="128" x2="308" y2="128" stroke="#E0D8C8" stroke-width="1.5"/>
  <text x="167" y="145" text-anchor="middle" font-size="10.5" fill="#6B6259">Harga (X)</text>
  <line x1="26" y1="20" x2="26" y2="128" stroke="#E0D8C8" stroke-width="1.5"/>
  <text x="12" y="74" text-anchor="middle" font-size="10.5" fill="#6B6259"
        transform="rotate(-90 12 74)">Kepuasan (Y)</text>
  <line x1="40" y1="34" x2="298" y2="118" stroke="#A85A5A" stroke-width="2.2"/>
  <text x="250" y="52" font-size="11" font-weight="700" fill="#A85A5A">garis menurun</text>
  <circle cx="62" cy="46" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="88" cy="38" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="112" cy="58" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="140" cy="62" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="168" cy="76" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="196" cy="84" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="224" cy="96" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="252" cy="102" r="3" fill="#2E7D6F" opacity=".55"/>
  <circle cx="280" cy="114" r="3" fill="#2E7D6F" opacity=".55"/>
</svg>
"""

IKON_ALERT = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
              'stroke="#9A7328" stroke-width="2"><path d="M12 9v4M12 17h.01"/>'
              '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3'
              'L13.7 3.9a2 2 0 0 0-3.4 0Z"/></svg>')
IKON_TAHU = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
             'stroke="#2E7D6F" stroke-width="2"><circle cx="12" cy="12" r="10"/>'
             '<path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/></svg>')

SEKENARIO = [
    ('Hipotesis berlawanan', 'Diduga positif, hasilnya negatif. Artinya apa?',
     'Ada pengaruh nyata, tapi arahnya berlawanan dengan dugaan.'),
    ('Skala kuisioner terbalik', 'Item "harga mahal" diskor 5 = sangat setuju',
     'Tanda negatif itu BENAR — yang salah hanya penamaannya. Pakai reverse coding.'),
    ('Multikolinearitas', 'Dua X saling berkaitan erat (VIF tinggi)',
     'Tanda β tidak bisa dipercaya — X2 mencuri pengaruh X1.'),
    ('Ada pencilan (outlier)', 'Beberapa data ekstrem',
     'Beberapa titik bisa membalik tanda seluruh model.'),
    ('Konsep memang kebalikan', 'Variabel "Biaya" atau "Risiko"',
     'Makin besar biaya, makin rendah kepuasan. Negatif itu wajar.'),
]

TABEL_SPSS = """
<table>
  <tr><th>Model</th><th>B</th><th>Sig.</th><th>Cara baca</th></tr>
  <tr><td>Harga → Kepuasan</td><td class="mono">−0,412</td><td class="mono">0,003</td>
      <td>Nyata, arah berlawanan</td></tr>
  <tr><td>Promosi → Kepuasan</td><td class="mono">+0,368</td><td class="mono">0,008</td>
      <td>Nyata, searah dugaan</td></tr>
  <tr><td>Kualitas → Kepuasan</td><td class="mono">+0,204</td><td class="mono">0,142</td>
      <td>Tidak nyata</td></tr>
</table>
"""


def desain_a() -> str:
    kartu = ''
    for i, (nama, tanya, arti) in enumerate(SEKENARIO, 1):
        aktif = ' aktif' if i == 1 else ''
        kartu += (f'<button class="sk{aktif}"><span class="no">{i}</span>'
                  f'<span><b>{nama}</b><span>{tanya}</span></span></button>')
    return f"""
<div class="bungkus">
  <span class="eyebrow">📖 BELAJAR</span>
  <h1>Uji t: signifikan kok negatif?</h1>
  <p style="color:#6B6259;margin-top:4px">
    Klik satu skenario — lihat apa yang sebenarnya terjadi.</p>

  <div class="papan">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
      <h2>Pilih skenario yang kamu alami</h2>
      <span class="pita pita-teal">5 skenario</span>
    </div>
    <div class="skenario">{kartu}</div>
  </div>

  <div class="papan">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
      <h2>Hasil: Hipotesis berlawanan</h2>
      <span class="pita pita-merah">perlu dibahas</span>
    </div>
    <div class="dua">
      <div>{SEBARAN}</div>
      <div>
        <div class="baris-t"><span>Koefisien (B)</span>
          <span></span><span class="mono" style="color:#A85A5A">−0,412</span></div>
        <div class="baris-t"><span>Nilai peluang (Sig.)</span>
          <span></span><span class="mono" style="color:#A85A5A">0,003</span></div>
        <div class="baris-t"><span>Kesimpulan</span>
          <span></span><span class="pita pita-merah">SIGNIFIKAN</span></div>
      </div>
    </div>
    <div class="catatan c-teal">{IKON_TAHU}<div>
      <b>Signifikan &ne; positif.</b> Dua pertanyaan yang berbeda:<br>
      &bull; <i>Ada pengaruhnya, bukan kebetulan?</i> &rarr; dijawab <b>Sig.</b><br>
      &bull; <i>Arahnya ke mana?</i> &rarr; dijawab <b>tanda pada B</b><br>
      Jadi &minus;0,412 dengan Sig. 0,003 = <b>ada pengaruh yang nyata, DAN
      arahnya berlawanan</b>. Itu <b>temuan</b>, bukan kesalahan.</div></div>
  </div>

  <div class="papan">
    <h2 style="margin-bottom:8px">Contoh keluaran SPSS</h2>
    {TABEL_SPSS}
    <div class="catatan c-amber">{IKON_ALERT}<div>
      <b>Jangan buang data supaya tandanya jadi positif.</b> Itu memalsukan
      hasil. Laporkan apa adanya, lalu bahas kenapa arahnya berlawanan.</div></div>
  </div>
</div>
"""


def desain_b() -> str:
    tombol = ''.join(
        f'<button class="sk" style="padding:8px 11px">'
        f'<span class="no">{i}</span><span><b>{n}</b></span></button>'
        for i, (n, _, _) in enumerate(SEKENARIO, 1))
    return f"""
<div class="bungkus">
  <span class="eyebrow">📖 BELAJAR</span>
  <h1>Uji t: signifikan kok negatif?</h1>

  <div class="papan">
    <h2 style="margin-bottom:10px">Skenario</h2>
    <div class="skenario" style="grid-template-columns:1fr 1fr">{tombol}</div>
  </div>

  <div class="papan">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px">
      <h2>Skala kuisioner terbalik</h2>
      <span class="pita pita-merah">paling sering</span>
    </div>
    <p style="margin:9px 0 0;font-size:13.5px;color:#6B6259">
      Item: <i>"Harga produk ini mahal"</i> &mdash; 1 sangat tidak setuju,
      5 sangat setuju.</p>
    <div class="dua">
      <div>
        <div style="background:#FBF3E2;border-radius:10px;padding:11px">
          <div style="font-size:12px;color:#6B6259;margin-bottom:6px">
            Responden setuju "mahal" (skor 5)</div>
          <div style="font-size:13.5px">Sebenarnya kepuasannya
            <b style="color:#A85A5A">RENDAH</b></div>
        </div>
        <div style="margin-top:10px;background:#EAF3EE;border-radius:10px;padding:11px">
          <div style="font-size:12px;color:#6B6259;margin-bottom:6px">
            Sesudah reverse coding (5→1)</div>
          <div style="font-size:13.5px">Tanda berubah jadi
            <b style="color:#3C7A5A">POSITIF</b></div>
        </div>
      </div>
      <div>{SEBARAN}</div>
    </div>
    <div class="catatan c-teal">{IKON_TAHU}<div>
      <b>Tanda negatif itu BENAR</b> — yang salah cuma penamaannya. Cek tiap
      item: kalau kalimatnya bernada negatif ("mahal", "lambat", "sulit"),
      di situ jebakannya.</div></div>
  </div>
</div>
"""


def render(nama: str, isi: str, tinggi: int) -> pathlib.Path:
    html = (f'<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{GAYA}</head><body>{isi}</body></html>')
    f_html = OUT / f'sketsa_{nama}.html'
    f_html.write_text(html)
    f_png = OUT / f'sketsa_{nama}.png'
    subprocess.run([CH, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--hide-scrollbars', f'--window-size=430,{tinggi}',
                    f'--screenshot={f_png}', f'file://{f_html}'],
                   capture_output=True, timeout=120)
    assert f_png.exists() and f_png.stat().st_size > 20000, f'{nama} gagal'
    return f_png


if __name__ == '__main__':
    a = render('uji_t_A', desain_a(), 1500)
    b = render('uji_t_B', desain_b(), 1150)
    print(f'OK {a} {a.stat().st_size}')
    print(f'OK {b} {b.stat().st_size}')
