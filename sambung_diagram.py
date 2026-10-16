#!/usr/bin/env python3
"""Sambungkan diagram notasi-lengkap ke mockup_konfirmasi_model.html.

Mengganti:
  · blok <script> lama          → modul diagram_model.js + diagram_bentuk.js
  · fungsi gambarModel()        → gambarDiagram() baru
  · data CONTOH + tabel panah   → tambah KODE variabel (X1/X2/M/Y/Z)
"""
from __future__ import annotations

import re
from pathlib import Path

DIR = Path('/opt/data/services/statistik-lab/_arsip')
HAL = DIR / 'mockup_konfirmasi_model.html'
ISI = HAL.read_text(encoding='utf-8')

# ── 1. Data CONTOH: tambah kode variabel + label hipotesis & koefisien ──
CONTOH_BARU = '''var CONTOH = [
  {
    kode:'C1', ikon:'\\u2192',
    judul:'Dua hal yang saling berhubungan',
    ket:'Satu memengaruhi satu. Paling dasar \\u2014 awal yang baik.',
    rumus:'X1 \\u2192 Y',
    varian:['Kualitas Layanan','Kepuasan Pelanggan'],
    kodeVar:['X1','Y'],
    panah:[
      {d:'X1', dn:'Kualitas Layanan', k:'Y', kn:'Kepuasan Pelanggan',
       b:'0,45', kf:'\\u03b2', ket:'pengaruh utama', h:'H1'}
    ],
    gambar:'sederhana', legenda:true
  },
  {
    kode:'C2', ikon:'\\u21e2',
    judul:'Lewat satu perantara',
    ket:'X memengaruhi Y, tapi lewat satu hal di tengah.',
    rumus:'X1 \\u2192 M \\u2192 Y',
    varian:['Motivasi Belajar','Cara Mengajar','Prestasi'],
    kodeVar:['X1','M','Y'],
    panah:[
      {d:'X1', dn:'Motivasi Belajar', k:'M', kn:'Cara Mengajar',
       b:'0,50', kf:'a', ket:'X ke perantara', h:'H1'},
      {d:'M', dn:'Cara Mengajar', k:'Y', kn:'Prestasi',
       b:'0,38', kf:'b', ket:'perantara ke Y', h:'H2'},
      {d:'X1', dn:'Motivasi Belajar', k:'Y', kn:'Prestasi',
       b:'0,08', kf:"c\\u2032", ket:'langsung (kecil)', h:'H3'}
    ],
    gambar:'mediasi'
  },
  {
    kode:'C3', ikon:'\\u2929',
    judul:'Ada yang menguatkan',
    ket:'Pengaruh X ke Y berbeda tergantung kondisi lain.',
    rumus:'X1 \\u00d7 Z \\u2192 Y',
    varian:['Beban Kerja','Dukungan Atasan','Kelelahan'],
    kodeVar:['X1','Z','Y'],
    panah:[
      {d:'X1', dn:'Beban Kerja', k:'Y', kn:'Kelelahan',
       b:'0,35', kf:'\\u03b2', ket:'pengaruh utama', h:'H1'},
      {d:'X1 \\u00d7 Z', dn:'Beban Kerja \\u00d7 Dukungan Atasan', k:'Y', kn:'Kelelahan',
       b:'0,18', kf:'\\u03b2', ket:'penguatan', h:'H2', jenis:'mod'}
    ],
    gambar:'moderasi'
  },
  {
    kode:'C4', ikon:'\\u21e2\\u21e2',
    judul:'Dua perantara sejajar',
    ket:'Dua hal di tengah, jalan masing-masing \\u2014 tidak berurutan.',
    rumus:'X1 \\u2192 M1 \\u2192 Y  \\u00b7  X1 \\u2192 M2 \\u2192 Y',
    varian:['Pelatihan','Kepercayaan','Keterampilan','Kinerja'],
    kodeVar:['X1','M1','M2','Y'],
    panah:[
      {d:'X1', dn:'Pelatihan', k:'M1', kn:'Kepercayaan',
       b:'0,42', kf:'a1', ket:'X ke perantara 1', h:'H1'},
      {d:'X1', dn:'Pelatihan', k:'M2', kn:'Keterampilan',
       b:'0,46', kf:'a2', ket:'X ke perantara 2', h:'H2'},
      {d:'M1', dn:'Kepercayaan', k:'Y', kn:'Kinerja',
       b:'0,30', kf:'b1', ket:'perantara 1 ke Y', h:'H3'},
      {d:'M2', dn:'Keterampilan', k:'Y', kn:'Kinerja',
       b:'0,33', kf:'b2', ket:'perantara 2 ke Y', h:'H4'}
    ],
    gambar:'dual-paralel'
  },
  {
    kode:'C5', ikon:'\\u21e2\\u203a',
    judul:'Perantara berurutan',
    ket:'Yang satu menuju yang lain: X1 \\u2192 M1 \\u2192 M2 \\u2192 Y.',
    rumus:'X1 \\u2192 M1 \\u2192 M2 \\u2192 Y',
    varian:['Gaya Kepemimpinan','Iklim Kerja','Komitmen','Kinerja'],
    kodeVar:['X1','M1','M2','Y'],
    panah:[
      {d:'X1', dn:'Gaya Kepemimpinan', k:'M1', kn:'Iklim Kerja',
       b:'0,48', kf:'a1', ket:'X ke perantara 1', h:'H1'},
      {d:'M1', dn:'Iklim Kerja', k:'M2', kn:'Komitmen',
       b:'0,40', kf:'d', ket:'perantara 1 ke 2', h:'H2'},
      {d:'M2', dn:'Komitmen', k:'Y', kn:'Kinerja',
       b:'0,36', kf:'b', ket:'perantara 2 ke Y', h:'H3'}
    ],
    gambar:'berjenjang'
  },
  {
    kode:'C6', ikon:'\\u21e2\\u2929',
    judul:'Perantara yang dikuatkan',
    ket:'Lewat perantara, DAN kekuatan jalur itu tergantung kondisi lain.',
    rumus:'X1 \\u2192 M \\u2192 Y, dengan M \\u00d7 Z',
    varian:['Kepemimpinan','Motivasi','Budaya Kerja','Kinerja'],
    kodeVar:['X1','M','Z','Y'],
    panah:[
      {d:'X1', dn:'Kepemimpinan', k:'M', kn:'Motivasi',
       b:'0,44', kf:'a', ket:'X ke perantara', h:'H1'},
      {d:'M', dn:'Motivasi', k:'Y', kn:'Kinerja',
       b:'0,32', kf:'b', ket:'perantara ke Y', h:'H2'},
      {d:'X1', dn:'Kepemimpinan', k:'Y', kn:'Kinerja',
       b:'0,10', kf:"c\\u2032", ket:'langsung (kecil)', h:'H3'},
      {d:'Z', dn:'Budaya Kerja', k:'Y', kn:'Kinerja',
       b:'0,15', kf:'\\u03b2', ket:'pengaruh sendiri', h:'H4'},
      {d:'M \\u00d7 Z', dn:'Motivasi \\u00d7 Budaya Kerja', k:'Y', kn:'Kinerja',
       b:'0,14', kf:'\\u03b2', ket:'penguatan jalur', h:'H5', jenis:'mod'},
      {d:'Z', dn:'Budaya Kerja', k:'M', kn:'Motivasi',
       b:'\\u2014', kf:'', ket:'tidak dihipotesiskan', h:'NH1', jenis:'nh'}
    ],
    gambar:'modmed'
  }
];'''

# ganti seluruh blok var CONTOH = [...] (dari 'var CONTOH' sampai '];' terakhir blok)
pola = re.compile(r"var CONTOH = \[.*?\n\];", re.DOTALL)
if not pola.search(ISI):
    raise SystemExit('GAGAL: blok var CONTOH tidak ketemu')
ISI = pola.sub(lambda m: CONTOH_BARU, ISI, count=1)

# ── 2. Tabel panah: tampilkan KODE (besar) + NAMA (kecil) + H + kf ──
TABEL_BARU = '''function gambarTabelPanah(idTabel, panah){
  var h = '<table class="tabel-hp"><thead><tr>' +
    '<th style="width:44px">No</th>' +
    '<th>Panah (arah dugaan)</th>' +
    '<th style="width:70px">Kode</th>' +
    '<th style="width:70px">Besar</th>' +
    '<th style="width:74px">Hipotesis</th>' +
    '<th style="width:120px">Perannya</th></tr></thead><tbody>';
  panah.forEach(function(p, i){
    var isNH = (p.jenis === 'nh');
    var isMod = (p.jenis === 'mod');
    var tanda = isNH ? '\\u21e2' : (isMod ? '\\u2929' : '\\u2192');
    h += '<tr class="' + kelasBaris(p) + '">' +
      '<td data-label="No"><span class="samar">' + (i + 1) + '</span></td>' +
      '<td data-label="Panah (arah dugaan)">' +
        '<span class="panah-sel ' + (isMod ? 'panah-mod' : (isNH ? 'panah-nh' : '')) + '">' +
          tanda + ' <b>' + p.d + '</b> ' + tanda + ' <b>' + p.k + '</b>' +
        '</span>' +
        '<br><span class="samar" style="font-size:11.5px">' + p.dn + ' \\u2192 ' + p.kn + '</span>' +
      '</td>' +
      '<td data-label="Kode"><span class="pita pita-teal">' + (p.kf || '\\u2014') + '</span></td>' +
      '<td data-label="Besar">' + (p.b === '\\u2014' ? '<span class="samar">\\u2014</span>' : '<b>' + p.b + '</b>') + '</td>' +
      '<td data-label="Hipotesis"><span class="pita ' + (isNH ? 'pita-abu' : 'pita-hijau') + '">' + p.h + '</span></td>' +
      '<td data-label="Perannya"><span class="samar" style="font-size:11.5px">' + p.ket + '</span></td>' +
    '</tr>';
  });
  h += '</tbody></table>';
  document.getElementById(idTabel).innerHTML = h;
}'''

pola2 = re.compile(r"function gambarTabelPanah\(idTabel, panah\)\{.*?\n\}", re.DOTALL)
if not pola2.search(ISI):
    raise SystemExit('GAGAL: fungsi gambarTabelPanah tidak ketemu')
ISI = pola2.sub(lambda m: TABEL_BARU, ISI, count=1)

# ── 3. Ganti pemanggilan gambarModel → gambarDiagram ──
ISI = ISI.replace(
    "gambarModel('kanvas-contoh', CONTOH_DIPILIH.gambar, CONTOH_DIPILIH.varian);",
    "document.getElementById('kanvas-contoh').innerHTML =\n"
    "        gambarDiagram(CONTOH_DIPILIH.gambar, CONTOH_DIPILIH.varian);\n"
    "      document.getElementById('legenda-contoh').style.display =\n"
    "        CONTOH_DIPILIH.legenda ? 'block' : 'none';")

# ── 4. Buang fungsi gambarModel() lama (sudah diganti modul baru) ──
pola3 = re.compile(r"/\* ── DIAGRAM ─+ \*/\nfunction gambarModel\(.*?\n\}\n", re.DOTALL)
if pola3.search(ISI):
    ISI = pola3.sub('/* ── DIAGRAM dipindah ke diagram_model.js + diagram_bentuk.js ── */\n', ISI, count=1)
else:
    print('CATATAN: blok gambarModel() lama tidak ketemu (mungkin sudah bersih)')

# ── 5. Sisipkan 2 berkas modul sebelum </script> ──
MODUL = ('<script src="diagram_model.js"></script>\n'
         '<script src="diagram_bentuk.js"></script>\n')
if 'diagram_model.js' not in ISI:
    ISI = ISI.replace('</body>', MODUL + '</body>', 1)

HAL.write_text(ISI, encoding='utf-8')
print('OK: mockup disambungkan ke diagram notasi-lengkap')
print('   blok CONTOH  :', 'kodeVar' in ISI)
print('   tabel berkode:', 'Hipotesis' in ISI)
print('   modul diagram:', 'diagram_model.js' in ISI)
print('   gambarModel  :', 'function gambarModel' in ISI, '(harus False)')
