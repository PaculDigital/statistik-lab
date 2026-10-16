#!/usr/bin/env python3
"""Sisipkan fungsi gambarHasil() ke diagnosis.html — dengan verifikasi.

⚠️ PELAJARAN 19Sep26: Wulan 3× merusak main.py dengan `patch` karena teks
   penandanya tidak unik. ATURAN: sisipkan lewat PENANDA + PARSE ULANG.
   (Berkas .html tidak bisa di-ast.parse → verifikasi: penanda unik,
    panjang bertambah, dan fungsi benar-benar ada setelah ditulis.)
"""
import re
import sys
from pathlib import Path

BERKAS = Path('/opt/data/services/statistik-lab/app/templates/diagnosis.html')

JS = '''
/* ── GAMBAR HASIL ───────────────────────────────────────────────────────
   Semua angka datang dari server. Fungsi ini hanya MENYUSUN tampilan.
   ⚠️ Nasihat "cara membetulkan" juga dari server (d.nasihat_semua) —
   sengaja TIDAK ditulis di sini supaya hanya ada SATU sumber teks.
   ───────────────────────────────────────────────────────────────────── */
function angka(n, desimal) {
  if (n === null || n === undefined || n === '') return '—';
  if (typeof n !== 'number') return String(n);
  return n.toFixed(desimal === undefined ? 3 : desimal).replace('.', ',');
}

function lambang(lulus) {
  if (lulus === true)  return '<span class="pita pita-hijau">Sudah benar</span>';
  if (lulus === false) return '<span class="pita pita-merah">Perlu dibetulkan</span>';
  return '<span class="pita pita-kuning">Belum bisa dinilai</span>';
}

function kartuUji(nama, lulus, isi) {
  return '<div class="kartu" style="margin-bottom:13px">' +
    '<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:7px">' +
      '<h3 style="margin:0;font-size:1rem">' + nama + '</h3>' + lambang(lulus) +
    '</div>' + isi + '</div>';
}

function tabelBaris(judul, baris) {
  return '<table class="data" style="margin-top:8px">' +
    '<thead><tr>' + judul.map(h => '<th style="text-align:left">' + h + '</th>').join('') + '</tr></thead>' +
    '<tbody>' + baris.map(r => '<tr>' + r.map((c, i) =>
      '<td' + (i ? ' style="text-align:right"' : '') + '>' + c + '</td>').join('') + '</tr>').join('') +
    '</tbody></table>';
}

/* Kotak nasihat — SATU nasihat lengkap (arti, kenapa, langkah, jangan) */
function kotakNasihat(n, nomor) {
  if (!n) return '';
  const langkah = n.langkah.map((l, i) =>
    '<li style="margin-bottom:10px"><strong>' + l[0] + '</strong><br>' +
    '<span style="color:#6B6259">' + l[1] + '</span></li>').join('');
  return '<div class="kartu" style="margin-top:12px;border-left:4px solid #B5762A">' +
    '<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">' +
      '<span class="langkah-nomor">' + nomor + '</span>' +
      '<h3 style="margin:0;font-size:1rem">' + n.judul + '</h3>' +
    '</div>' +
    '<p style="margin:6px 0"><strong>Apa artinya:</strong> ' + n.arti + '</p>' +
    '<p style="margin:6px 0"><strong>Kenapa penting:</strong> ' + n.kenapa + '</p>' +
    '<p style="margin:10px 0 6px"><strong>Cara membetulkan:</strong></p>' +
    '<ol style="margin:0 0 10px 18px;padding:0">' + langkah + '</ol>' +
    '<div class="catatan" style="background:#F3F8F5;border-color:#CDE3D5;margin-bottom:9px">' +
      '<strong>Kapan masih aman:</strong> ' + n.boleh_abaikan + '</div>' +
    '<div class="catatan" style="background:#FBEFEF;border-color:#E8C9C9">' +
      '<strong>Yang sebaiknya tidak dilakukan:</strong> ' + n.jangan + '</div>' +
    '</div>';
}

function gambarHasil(d) {
  const wadah = document.getElementById('kartu-hasil');
  let h = '';

  /* ── RINGKASAN di atas: berapa masalah, berapa aman ── */
  const nMasalah = (d.masalah || []).length;
  const judulAlat = d.mode === 'pls' ? 'SmartPLS' : 'SPSS';
  h += '<div class="kartu" style="margin-bottom:18px;border-left:4px solid ' +
       (nMasalah ? '#B5762A' : '#4E8A5A') + '">' +
    '<span class="eyebrow">Hasil pemeriksaan ' + judulAlat + '</span>' +
    '<h2 style="margin:6px 0 8px">' +
      (nMasalah
        ? 'Ada ' + nMasalah + ' hal yang perlu kamu lihat'
        : 'Semua syarat sudah terpenuhi') + '</h2>' +
    '<p style="margin:0;color:#6B6259">' +
      d.n_baris + ' responden diperiksa · ' + (d.n_kolom || '') +
      (nMasalah
        ? '. Tidak semua harus dibetulkan — lihat penjelasan tiap bagian.'
        : '. Datamu siap diolah lebih lanjut.') +
    '</p></div>';

  /* ══════════ MODE SPSS ══════════ */
  if (d.mode !== 'pls') {
    /* Model ringkas */
    if (d.koef && d.koef.length) {
      h += kartuUji('Model yang diperiksa', true,
        '<p style="margin:0 0 4px;color:#6B6259">' +
        'Prediktor: ' + (d.prediktor || []).join(', ') + ' · Y: ' + d.kolom_y + '</p>' +
        tabelBaris(['Prediktor', 'B', 't', 'p'],
          d.koef.map(k => [k.nama, angka(k.b), angka(k.t), angka(k.p)])) +
        '<p style="margin:9px 0 0;font-size:.92rem">' +
        '<strong>R² = ' + angka(d.r2) + '</strong> (R² terkoreksi ' + angka(d.r2_adj) + ') — ' +
        'artinya ' + angka(d.r2 * 100, 1) + '% keragaman Y bisa dijelaskan model. ' +
        '<strong>' + (d.prediktor || []).length + '</strong> responden dianalisis: ' + d.n_baris + '.</p>');
    }

    /* ① Normalitas */
    const n = d.normalitas || {};
    h += kartuUji('Normalitas sisa', n.lulus,
      '<p style="margin:0;color:#6B6259">Tiga uji sekaligus, supaya kesimpulannya kokoh.</p>' +
      tabelBaris(['Uji', 'Nilai p'],
        [['Kolmogorov-Smirnov', angka(n.ks_p)],
         ['Shapiro-Wilk', angka(n.shapiro_p)],
         ["D'Agostino", angka(n.dagostino_p)]]) +
      '<p style="margin:9px 0 0;font-size:.92rem">Kemiringan (skewness) = ' + angka(n.skew) +
      ' · Keruncingan = ' + angka(n.kurtosis) + '. ' +
      'Nilai p di atas 0,05 artinya sisa menyebar normal.</p>');

    /* ② Heteroskedastisitas */
    const het = d.hetero || {};
    h += kartuUji('Heteroskedastisitas (Glejser)', het.lulus,
      '<p style="margin:0;color:#6B6259">Seberapa tidak rata sebaran sisanya.</p>' +
      tabelBaris(['Nilai p terkecil'], [[angka(het.glejser_p)]]) +
      '<p style="margin:9px 0 0;font-size:.92rem">' +
      'Nilai p di bawah 0,05 artinya sebaran sisa tidak rata — ada yang perlu diperiksa.</p>');

    /* ③ Multikolinearitas */
    const vif = d.vif || [];
    const vifMaks = d.vif_maks || 0;
    h += kartuUji('Multikolinearitas (VIF)', vifMaks <= 10,
      '<p style="margin:0;color:#6B6259">Apakah X saling kembar.</p>' +
      (vif.length ? tabelBaris(['Prediktor', 'VIF'],
        vif.map(v => [v.nama, angka(v.vif, 2)])) : '') +
      '<p style="margin:9px 0 0;font-size:.92rem">VIF di bawah 5 umumnya aman; di atas 10 perlu ditangani.</p>');

    /* ④ Linearitas */
    if (d.linearitas) {
      const lin = d.linearitas;
      h += kartuUji('Linearitas', lin.lulus,
        '<p style="margin:0;color:#6B6259">Apakah hubungan X dan Y berbentuk garis lurus.</p>' +
        (lin.p === null || lin.p === undefined ? '' :
          tabelBaris(['Nilai p'], [[angka(lin.p)]])));
    }

    /* ⑤ Outlier */
    const out = d.outlier || {};
    h += kartuUji('Data menyimpang jauh', (out.n_y || 0) < 3,
      '<p style="margin:0;color:#6B6259">Responden yang jawabannya jauh berbeda dari yang lain.</p>' +
      tabelBaris(['Yang ditemukan', 'Jumlah'],
        [['Menyimpang di Y', (out.n_y || 0) + ' titik'],
         ['Menyimpang di X', (out.n_x || 0) + ' titik']]) +
      '<p style="margin:9px 0 0;font-size:.92rem">' +
      (out.batas_atas !== undefined
        ? 'Batas wajar Y: ' + angka(out.batas_bawah, 2) + ' sampai ' + angka(out.batas_atas, 2) + '.'
        : '') + '</p>');

    /* ⑥ Durbin-Watson */
    if (d.dw !== null && d.dw !== undefined) {
      h += kartuUji('Autokorelasi (Durbin-Watson)', d.dw >= 1.5 && d.dw <= 2.5,
        '<p style="margin:0;color:#6B6259">Apakah sisa berhubungan dengan urutan responden.</p>' +
        tabelBaris(['Durbin-Watson'], [[angka(d.dw, 3)]]) +
        '<p style="margin:9px 0 0;font-size:.92rem">Nilai sehat mendekati 2.</p>');
    }
  } else {
    /* ══════════ MODE SmartPLS ══════════ */
    (d.konstruk || []).forEach(function (k) {
      h += kartuUji('Variabel: ' + k.nama,
        k.lulus_cl && k.lulus_ave && k.lulus_cr,
        tabelBaris(['Ukuran', 'Nilai', 'Ambang'],
          [['Outer loading terendah', angka(k.loading_min) + ' (' + (k.butir_lemah || '—') + ')', '≥ 0,70'],
           ['AVE', angka(k.ave), '≥ 0,50'],
           ['Composite Reliability', angka(k.cr), '≥ 0,70']]) +
        (k.pesan ? '<p style="margin:9px 0 0;font-size:.92rem">' + k.pesan + '</p>' : ''));
    });

    if (d.vif_inner && d.vif_inner.length) {
      h += kartuUji('VIF antar-variabel', (d.vif_inner_maks || 0) <= 5,
        tabelBaris(['Variabel', 'VIF'],
          d.vif_inner.map(v => [v.nama, angka(v.vif, 2)])));
    }

    if (d.fornell && d.fornell.length) {
      h += kartuUji('Fornell-Larcker', !d.fornell_ada_masalah,
        '<p style="margin:0;color:#6B6259">Apakah tiap variabel lebih erat dengan ' +
        'butirnya sendiri daripada dengan variabel lain.</p>' +
        tabelBaris(['Pasangan', 'Korelasi', 'Batas'],
          d.fornell.map(f => [f.pasangan, angka(f.korelasi, 3), angka(f.batas, 3)])) +
        '<p style="margin:9px 0 0;font-size:.92rem">Lulus kalau korelasi ' +
        'tidak melebihi akar AVE masing-masing variabel.</p>');
    }
  }

  /* ══════════ NASIHAT — datang dari server ══════════ */
  const masalah = d.masalah || [];
  if (masalah.length) {
    h += '<h2 style="margin:26px 0 4px">Cara membetulkannya</h2>' +
         '<p style="margin:0 0 14px;color:#6B6259">Satu per satu, mulai dari yang paling perlu.</p>';
    masalah.forEach(function (m, i) { h += kotakNasihat(m.nasihat, i + 1); });
  } else {
    h += '<div class="kartu" style="margin-top:20px;border-left:4px solid #4E8A5A">' +
      '<h3 style="margin:0 0 6px">{{ ikon("check-circle-2", 16) }} Tidak ada yang perlu dibetulkan</h3>' +
      '<p style="margin:0;color:#6B6259">Datamu sudah memenuhi syarat yang diperiksa. ' +
      'Lanjutkan ke analisis di ' + (d.mode === 'pls' ? 'SmartPLS' : 'SPSS') + ' ya. ' +
      'Kalau nanti hasilnya berbeda dari harapan, unggah lagi ke sini.</p></div>';
  }

  wadah.innerHTML = h;
  wadah.hidden = false;
  wadah.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
'''


def utama() -> int:
    asli = BERKAS.read_text()
    cadangan = Path('/tmp/diagnosis.html.bak')
    cadangan.write_text(asli)
    print(f'cadangan: {cadangan} ({len(asli)} byte)')

    # Penanda: komentar terakhir di blok skrip.
    penanda = '/* ── PERIKSA ────────────────────────────────────────────────────────── */'
    n = asli.count(penanda)
    print(f'penanda ditemukan {n}×')
    if n != 1:
        print('GAGAL: penanda tidak unik.'); return 1

    baru = asli.replace(penanda, JS.strip('\n') + '\n\n' + penanda, 1)

    # Verifikasi: penanda JS lama harus masih ada + fungsi baru ada + ukuran naik.
    for wajib in ('function gambarHasil', 'function kotakNasihat',
                  'async function periksa', 'function pilihAlat'):
        if wajib not in baru:
            print(f'GAGAL: "{wajib}" tidak ada setelah sisip.'); return 1
    if len(baru) <= len(asli):
        print('GAGAL: ukuran tidak bertambah.'); return 1
    # Pastikan kurung kurawal JS seimbang (tidak ada blok terpotong).
    if baru.count('{') != baru.count('}'):
        print(f'GAGAL: kurung tidak seimbang {{={baru.count("{")} }}={baru.count("}")}')
        return 1

    BERKAS.write_text(baru)
    print(f'berhasil. {len(asli)} → {len(baru)} byte (+{len(baru)-len(asli)})')
    print('verifikasi: gambarHasil ✓  kotakNasihat ✓  periksa ✓  pilihAlat ✓')
    print(f'kurung seimbang: {{={baru.count("{")} }}={baru.count("}")}')
    return 0


if __name__ == '__main__':
    sys.exit(utama())
