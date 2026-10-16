/* ══════════════════════════════════════════════════════════════════════
   DIAGRAM MODEL PENELITIAN — notasi lengkap
   ──────────────────────────────────────────────────────────────────────
   AKAR MASALAH YANG DITUTUP (18Sep26):
   Versi lama menggambar kotak berisi NAMA saja, tanpa kode variabel,
   tanpa label hipotesis, dan MATA PANAH hilang (marker id bentrok karena
   <defs> ditulis ulang tiap kali fungsi dipanggil → browser ambil marker
   pertama yang sudah hilang → garis tampil tanpa ujung).

   ATURAN YANG DIPAKAI SEKARANG:
   1. Setiap kotak WAJIB punya KODE (X1/X2/M/Y/Z) — besar & tebal.
      Nama variabel jadi keterangan di bawah kode.
   2. Setiap panah WAJIB punya LABEL HIPOTESIS (H1, H2, …) di atas garisnya,
      ATAU "NH1" kalau tidak dihipotesiskan.
   3. Panah wajib punya MATA PANAH (marker) — id marker UNIK per gambar
      (ditambah penanda) supaya tidak bentrok.
   4. Jalur mediasi wajib punya label a / b / c′.
   ══════════════════════════════════════════════════════════════════════ */

/* ── Gaya kotak per peran ───────────────────────────────────────────── */
var GAYA_KOTAK = {
  x: { isi:'#FBF8F3', garis:'#E0D8C8', tinta:'#2B2722' },  /* Variabel bebas  */
  m: { isi:'#FBEFDC', garis:'#B5762A', tinta:'#8A5A1C' },  /* Mediasi         */
  y: { isi:'#F5F0E6', garis:'#2B2722', tinta:'#2B2722' },  /* Variabel terikat*/
  z: { isi:'#E4F0EC', garis:'#2E7D6F', tinta:'#1F6357' }   /* Moderasi        */
};

/* ── Bikin id unik supaya marker tidak bentrok antar-gambar ─────────── */
var _URUT_SVG = 0;

function _esc(t){
  return String(t === null || t === undefined ? '' : t)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Gambar kotak variabel.
 * @param kode  'X1' | 'M' | 'Y' | 'Z'  → tampil BESAR
 * @param nama  'Kepemimpinan'          → tampil kecil di bawah kode
 */
function kotakVariabel(x, y, w, h, kode, nama, peran){
  var g = GAYA_KOTAK[peran] || GAYA_KOTAK.x;
  var kodeUkuran = 15;
  var namaUkuran = 9.5;

  /* Kalau nama panjang, perkecil font nama (JANGAN dipotong) */
  var n = (nama || '').length;
  if (n > 16) namaUkuran = 8.5;
  if (n > 22) namaUkuran = 7.5;
  if (n > 28) namaUkuran = 6.8;

  var s = '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h +
    '" rx="8" fill="' + g.isi + '" stroke="' + g.garis + '" stroke-width="1.8"/>';

  /* Kode variabel — besar, tebal, di tengah-atas kotak */
  var adaNama = !!(nama && nama.length);
  var yKode = adaNama ? y + h / 2 - 2 : y + h / 2 + 5;
  s += '<text x="' + (x + w / 2) + '" y="' + yKode + '" font-size="' + kodeUkuran +
    '" fill="' + g.tinta + '" text-anchor="middle" font-weight="800" ' +
    'letter-spacing="0.3">' + _esc(kode) + '</text>';

  /* Nama variabel — kecil, di bawah kode */
  if (adaNama){
    s += '<text x="' + (x + w / 2) + '" y="' + (y + h / 2 + 11) +
      '" font-size="' + namaUkuran + '" fill="#6B6259" text-anchor="middle" ' +
      'font-weight="500">' + _esc(nama) + '</text>';
  }
  return s;
}

/**
 * Gambar panah + LABEL HIPOTESIS.
 * @param jid    penanda unik gambar (supaya marker tidak bentrok)
 * @param label  'H1' | 'NH1' | 'a' | 'b' | "c'" | null
 * @param warna  'tinta' | 'teal' | 'amber' | 'abu'
 */
function panahLengkap(jid, x1, y1, x2, y2, label, warna, putus){
  var peta = {
    tinta: { garis:'#6B6259', teks:'#2B2722' },
    teal:  { garis:'#2E7D6F', teks:'#1F6357' },
    amber: { garis:'#B5762A', teks:'#8A5A1C' },
    abu:   { garis:'#9A9086', teks:'#9A9086' }
  };
  var w = peta[warna] || peta.tinta;
  var putusAtur = (putus === 'mod') ? ' stroke-dasharray="5 4"' :
                  (putus === 'nh'  ? ' stroke-dasharray="2 4"' :
                  (putus ? ' stroke-dasharray="6 4"' : ''));
  var tebal = (warna === 'teal' && putus === 'mod') ? 2.2 : 2;

  var s = '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 +
    '" stroke="' + w.garis + '" stroke-width="' + tebal + '"' + putusAtur +
    ' marker-end="url(#mk-' + jid + '-' + warna + ')"/>';

  /* LABEL HIPOTESIS — wajib terlihat, ada latar putih supaya tidak
     tertabrak garis (dulu hilang total → model tidak terbaca) */
  if (label){
    var lx = (x1 + x2) / 2;
    var ly = (y1 + y2) / 2 - 7;
    var lebar = label.length * 6.2 + 8;
    s += '<rect x="' + (lx - lebar / 2) + '" y="' + (ly - 10) + '" width="' +
      lebar + '" height="13" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="' + lx + '" y="' + (ly) + '" font-size="10" ' +
      'fill="' + w.teks + '" text-anchor="middle" font-weight="800">' +
      _esc(label) + '</text>';
  }
  return s;
}

/** Definisi mata panah — id UNIK per gambar. WAJIB dipanggil sekali. */
function definisiPanah(jid){
  var s = '<defs>';
  [['tinta','#6B6259'], ['teal','#2E7D6F'], ['amber','#B5762A'], ['abu','#9A9086']]
    .forEach(function(p){
      s += '<marker id="mk-' + jid + '-' + p[0] + '" markerWidth="10" markerHeight="10" ' +
        'refX="9" refY="5" orient="auto" markerUnits="strokeWidth">' +
        '<path d="M0,0 L10,5 L0,10 z" fill="' + p[1] + '"/></marker>';
    });
  s += '</defs>';
  return s;
}
