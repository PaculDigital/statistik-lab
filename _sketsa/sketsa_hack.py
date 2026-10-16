#!/usr/bin/env python3
"""SKETSA — KARTU "5 CARA HACK" (revisi Bos 18Sep26: judul + lebih eye-catching).

PERMINTAAN BOS (verbatim):
"Pada 5 Cara yang kamu hindari ganti menjadi 5 Cara Hack, yang harus dihindari.
 Buat kartu lebih eyechating atau beda background kartu"

MENGAPA 3 VARIASI (bukan 1):
Tema aplikasi = TERANG-WARM (kertas hangat, tinta coklat). Kartu yang terlalu
menyala (merah terang) akan TABRAK dengan tema dan terlihat seperti pesan galat.
Jadi Wulan membuat 3 pilihan dengan tingkat "menonjol" berbeda, lalu Bos pilih:

  V1 TINTA GELAP   — latar coklat-tua, tulisan kertas. Kontras kuat tapi tetap
                     satu keluarga dengan tema. (paling elegan)
  V2 MERAH LEMBUT  — latar merah-muda hangat + garis merah. Lebih mendesak
                     tapi tetap lembut. (paling "mengingatkan")
  V3 STRIP GELAP   — kartu tetap terang, tapi KEPALA kartu gelap + pita "HACK".
                     Paling ringan, tidak mengubah irama halaman.

CARA JALAN: .venv/bin/python _sketsa/sketsa_hack.py
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
        --hijau:#3C7A5A;--hijau-muda:#EAF3EE;--tinta-gelap:#332C24;
        --kertas-gelap:#4A4038;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--kertas);color:var(--tinta);
       font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;
       padding:24px 16px;font-size:14.5px;line-height:1.55}
  .bungkus{max-width:640px;margin:0 auto}
  h2{font-size:16.5px;margin:0}
  .judul-bagian{font-size:12px;font-weight:700;letter-spacing:.09em;
                text-transform:uppercase;color:var(--teal);margin:22px 0 8px}
  .papan{background:#fff;border:1px solid var(--garis);border-radius:14px;
         padding:18px}
  /* ── V1 : TINTA GELAP ───────────────────────────────────────────── */
  .v1{background:var(--tinta-gelap);border:0;color:#F2EDE4;
      box-shadow:0 6px 22px rgba(43,39,34,.18)}
  .v1 h2{color:#FBF8F3}
  .v1 .ket{color:#C9BEB1;font-size:12.5px;margin:4px 0 14px}
  .v1 .item{display:flex;gap:11px;align-items:flex-start;padding:11px 13px;
            background:rgba(255,255,255,.06);border-radius:10px;margin-bottom:8px;
            border-left:3px solid #C4716B}
  .v1 .n{flex:0 0 auto;width:23px;height:23px;border-radius:50%;
         background:#C4716B;color:#fff;font-size:12px;font-weight:700;
         display:flex;align-items:center;justify-content:center}
  .v1 .item b{color:#FBF8F3;display:block;font-size:13.5px}
  .v1 .item span{color:#C9BEB1;font-size:12.5px}
  .v1 .kaki{margin-top:13px;background:rgba(255,255,255,.07);border-radius:10px;
            padding:12px 13px;font-size:13px;color:#E5DED4}
  /* ── V2 : MERAH LEMBUT ─────────────────────────────────────────── */
  .v2{background:#FBF0EC;border:1.5px solid #E8C4BC}
  .v2 .ket{color:#8A6259;font-size:12.5px;margin:4px 0 14px}
  .v2 .item{display:flex;gap:11px;align-items:flex-start;padding:11px 13px;
            background:#fff;border-radius:10px;margin-bottom:8px;
            border-left:3px solid var(--merah)}
  .v2 .n{flex:0 0 auto;width:23px;height:23px;border-radius:50%;
         background:var(--merah);color:#fff;font-size:12px;font-weight:700;
         display:flex;align-items:center;justify-content:center}
  .v2 .item b{display:block;font-size:13.5px}
  .v2 .item span{color:var(--lembut);font-size:12.5px}
  .v2 .kaki{margin-top:13px;background:#fff;border-radius:10px;padding:12px 13px;
            font-size:13px;border:1px solid #E8C4BC}
  /* ── V3 : STRIP GELAP ──────────────────────────────────────────── */
  .v3{padding:0;overflow:hidden}
  .v3 .kepala{background:var(--tinta-gelap);color:#FBF8F3;padding:14px 18px;
              display:flex;justify-content:space-between;align-items:center;gap:10px}
  .v3 .kepala h2{color:#FBF8F3;font-size:15.5px}
  .v3 .hack{background:#C4716B;color:#fff;font-size:10.5px;font-weight:800;
            letter-spacing:.1em;padding:4px 10px;border-radius:999px}
  .v3 .badan{padding:16px 18px}
  .v3 .ket{color:var(--lembut);font-size:12.5px;margin:0 0 12px}
  .v3 .item{display:flex;gap:11px;align-items:flex-start;padding:10px 12px;
            background:#F6F3EC;border-radius:10px;margin-bottom:7px}
  .v3 .n{flex:0 0 auto;width:22px;height:22px;border-radius:50%;
         background:#fff;border:1px solid var(--garis);font-size:11.5px;
         font-weight:700;display:flex;align-items:center;justify-content:center}
  .v3 .item b{display:block;font-size:13.5px}
  .v3 .item span{color:var(--lembut);font-size:12.5px}
  .v3 .kaki{margin-top:12px;background:var(--hijau-muda);border-radius:10px;
            padding:12px 13px;font-size:13px}
</style>
"""

CARA = [
    ('p-hacking', 'Membuang data atau mengubah cara hitung sampai Sig. &lt; 0,05'),
    ('Menggeser batas α', 'α diubah 0,05 → 0,10 <b>setelah</b> melihat hasil'),
    ('Fishing', 'Mencoba banyak model, hanya yang lolos dilaporkan'),
    ('HARKing', 'Hipotesis diubah <b>setelah</b> tahu hasilnya'),
    ('Buang pencilan tanpa dasar', 'Membuang responden "aneh" hanya karena '
                                   'mengganggu hasil'),
]

KAKI = ('<b>Kuncinya cuma satu: urutan.</b> Rencanakan dulu di BAB III, '
        'baru lihat hasil. Kalau <b>hasil dilihat dulu, baru aturan '
        'diubah</b> — itulah masalahnya.')


def items(kelas: str) -> str:
    out = ''
    for i, (nama, bentuk) in enumerate(CARA, 1):
        out += (f'<div class="item"><span class="n">{i}</span>'
                f'<div><b>{nama}</b><span>{bentuk}</span></div></div>')
    return out


def v1() -> str:
    return f"""
<div class="papan v1">
  <h2>5 Cara Hack yang Harus Dihindari</h2>
  <p class="ket">Bukan karena penguji melarang — tapi karena hasilnya jadi
     tidak bisa dipercaya, termasuk oleh dirimu sendiri.</p>
  {items('v1')}
  <div class="kaki">{KAKI}</div>
</div>"""


def v2() -> str:
    return f"""
<div class="papan v2">
  <h2>5 Cara Hack yang Harus Dihindari</h2>
  <p class="ket">Bukan karena penguji melarang — tapi karena hasilnya jadi
     tidak bisa dipercaya, termasuk oleh dirimu sendiri.</p>
  {items('v2')}
  <div class="kaki">{KAKI}</div>
</div>"""


def v3() -> str:
    return f"""
<div class="papan v3">
  <div class="kepala"><h2>5 Cara Hack yang Harus Dihindari</h2>
    <span class="hack">HACK</span></div>
  <div class="badan">
    <p class="ket">Bukan karena penguji melarang — tapi karena hasilnya jadi
       tidak bisa dipercaya, termasuk oleh dirimu sendiri.</p>
    {items('v3')}
    <div class="kaki">{KAKI}</div>
  </div>
</div>"""


def halaman(isi: str, nama: str) -> str:
    return f"""
<div class="bungkus">
  <div class="judul-bagian">Pembanding — versi {nama}</div>
  {isi}
  <div class="judul-bagian" style="margin-top:26px">Kartu lain di halaman
    (untuk melihat kontrasnya)</div>
  <div class="papan">
    <h2 style="margin-bottom:6px">Hasilmu yang mana?</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:9px">
      <div style="border:1px solid var(--garis);border-radius:11px;padding:11px 12px;
                  font-size:13px">Sig. 0,003 · B −0,412</div>
      <div style="border:1px solid var(--garis);border-radius:11px;padding:11px 12px;
                  font-size:13px">Sig. 0,142 · B +0,204</div>
    </div>
    <p style="font-size:12.5px;color:#6B6259;margin:10px 0 0">
      Kartu lain tetap putih kertas — supaya kartu hack ini benar-benar
      terasa berbeda.</p>
  </div>
</div>"""


def render(nama: str, isi: str) -> pathlib.Path:
    html = (f'<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{GAYA}</head><body>{isi}</body></html>')
    f_html = OUT / f'hack_{nama}.html'
    f_html.write_text(html)
    f_png = OUT / f'hack_{nama}.png'
    subprocess.run([CH, '--headless=new', '--no-sandbox', '--disable-gpu',
                    '--hide-scrollbars', '--window-size=820,1100',
                    f'--screenshot={f_png}', f'file://{f_html}'],
                   capture_output=True, timeout=150)
    assert f_png.exists() and f_png.stat().st_size > 20000, f'{nama} gagal'
    return f_png


if __name__ == '__main__':
    for nm, fn in [('v1_gelap', v1), ('v2_merah', v2), ('v3_strip', v3)]:
        p = render(nm, halaman(fn(), nm))
        print(f'OK {nm}: {p.stat().st_size} byte')
