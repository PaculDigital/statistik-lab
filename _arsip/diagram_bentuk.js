/* ══════════════════════════════════════════════════════════════════════
   PENGGAMBAR DIAGRAM MODEL — 6 bentuk, NOTASI LENGKAP
   ──────────────────────────────────────────────────────────────────────
   Setiap bentuk menggambar:
     · kotak berkode   : X1, X2, M1, M2, Y, Z
     · nama variabel   : kecil di bawah kode
     · label hipotesis : H1, H2, … di atas panah  (NH1 bila tak diuji)
     · koefisien jalur : a, b, c′ pada panah mediasi
   ══════════════════════════════════════════════════════════════════════ */

var DIAGRAM = {
  L: 420,   /* lebar viewBox */
  T: 260    /* tinggi viewBox */
};

/**
 * @param bentuk  'sederhana'|'mediasi'|'moderasi'|'dual-paralel'|'berjenjang'|'modmed'
 * @param v       daftar nama variabel, urut sesuai bentuk
 */
function gambarDiagram(bentuk, v){
  var jid = 'g' + (++_URUT_SVG);
  var s = '<svg viewBox="0 0 ' + DIAGRAM.L + ' ' + DIAGRAM.T + '" class="dugaan" ' +
          'role="img" style="width:100%;height:auto">';
  s += definisiPanah(jid);

  if (bentuk === 'sederhana'){
    /* X1 → Y   (H1) */
    s += kotakVariabel(24, 88, 132, 52, 'X1', v[0], 'x');
    s += kotakVariabel(264, 88, 132, 52, 'Y',  v[1], 'y');
    s += panahLengkap(jid, 156, 114, 260, 114, 'H1', 'tinta');

  } else if (bentuk === 'mediasi'){
    /* X1 → M (a, H1) · M → Y (b, H2) · X1 ⇢ Y (c′, H3) */
    s += kotakVariabel(6, 78, 108, 52, 'X1', v[0], 'x');
    s += kotakVariabel(156, 78, 108, 52, 'M',  v[1], 'm');
    s += kotakVariabel(306, 78, 108, 52, 'Y',  v[2], 'y');
    s += panahLengkap(jid, 114, 96, 152, 96, 'H1', 'tinta');
    s += '<text x="133" y="112" font-size="9" fill="#6B6259" text-anchor="middle" font-weight="700">a</text>';
    s += panahLengkap(jid, 264, 96, 302, 96, 'H2', 'tinta');
    s += '<text x="283" y="112" font-size="9" fill="#6B6259" text-anchor="middle" font-weight="700">b</text>';
    /* jalur langsung: lengkung di BAWAH kotak */
    s += '<path d="M 60 130 C 60 190 150 200 340 200 C 380 200 392 160 392 130" ' +
         'fill="none" stroke="#6B6259" stroke-width="2" stroke-dasharray="6 4" ' +
         'marker-end="url(#mk-' + jid + '-tinta)"/>';
    s += '<rect x="196" y="192" width="64" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="228" y="203" font-size="10" fill="#2B2722" text-anchor="middle" ' +
         'font-weight="800">H3 · c′</text>';

  } else if (bentuk === 'moderasi'){
    /* X1 → Y (H1) · Z ⇢ garis X1→Y (H2) */
    s += kotakVariabel(24, 60, 130, 52, 'X1', v[0], 'x');
    s += kotakVariabel(266, 60, 130, 52, 'Y', v[2], 'y');
    s += kotakVariabel(145, 176, 130, 52, 'Z', v[1], 'z');
    s += panahLengkap(jid, 154, 78, 262, 78, 'H1', 'tinta');
    /* Z masuk ke GARIS (bukan kotak) — aturan moderasi */
    s += '<line x1="210" y1="174" x2="210" y2="120" stroke="#2E7D6F" ' +
         'stroke-width="2.2" stroke-dasharray="5 4" marker-end="url(#mk-' + jid + '-teal)"/>';
    s += '<line x1="210" y1="120" x2="210" y2="54" stroke="#2E7D6F" ' +
         'stroke-width="2.2" marker-end="url(#mk-' + jid + '-teal)"/>';
    s += '<rect x="126" y="96" width="52" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="152" y="107" font-size="10" fill="#1F6357" text-anchor="middle" ' +
         'font-weight="800">H2</text>';

  } else if (bentuk === 'dual-paralel'){
    /* X1 → M1 (H1) · X1 → M2 (H2) · M1 → Y (H3) · M2 → Y (H4) */
    s += kotakVariabel(4, 104, 100, 52, 'X1', v[0], 'x');
    s += kotakVariabel(160, 24, 100, 52, 'M1', v[1], 'm');
    s += kotakVariabel(160, 184, 100, 52, 'M2', v[2], 'm');
    s += kotakVariabel(316, 104, 100, 52, 'Y',  v[3], 'y');
    s += panahLengkap(jid, 106, 120, 156, 62, 'H1', 'tinta');
    s += panahLengkap(jid, 106, 140, 156, 198, 'H2', 'tinta');
    s += panahLengkap(jid, 262, 62, 314, 120, 'H3', 'tinta');
    s += panahLengkap(jid, 262, 198, 314, 140, 'H4', 'tinta');

  } else if (bentuk === 'berjenjang'){
    /* X1 → M1 (H1) · M1 → M2 (H2) · M2 → Y (H3) */
    s += kotakVariabel(2, 96, 92, 52, 'X1', v[0], 'x');
    s += kotakVariabel(116, 96, 92, 52, 'M1', v[1], 'm');
    s += kotakVariabel(230, 96, 92, 52, 'M2', v[2], 'm');
    s += kotakVariabel(330, 178, 88, 52, 'Y',  v[3], 'y');
    s += panahLengkap(jid, 96, 114, 112, 114, 'H1', 'tinta');
    s += panahLengkap(jid, 210, 114, 226, 114, 'H2', 'tinta');
    s += '<path d="M 276 150 L 276 204 L 326 204" fill="none" stroke="#6B6259" ' +
         'stroke-width="2" marker-end="url(#mk-' + jid + '-tinta)"/>';
    s += '<rect x="258" y="164" width="46" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="281" y="175" font-size="10" fill="#2B2722" text-anchor="middle" ' +
         'font-weight="800">H3</text>';

  } else if (bentuk === 'modmed'){
    /* Jalur baku + notasi lengkap (X1, M, Z, Y · H1..H5 · NH1) */
    s += kotakVariabel(6, 34, 104, 52, 'X1', v[0], 'x');
    s += kotakVariabel(158, 34, 104, 52, 'M', v[1], 'm');
    s += kotakVariabel(310, 34, 104, 52, 'Y',  v[3], 'y');
    s += kotakVariabel(158, 186, 104, 52, 'Z', v[2], 'z');
    s += panahLengkap(jid, 112, 60, 154, 60, 'H1', 'tinta');
    s += panahLengkap(jid, 264, 60, 306, 60, 'H2', 'tinta');
    /* X1 → Y langsung: lengkung BAWAH, di bawah kotak Z (y=186..238) */
    s += '<path d="M 34 88 C 34 122 90 254 210 254 C 330 254 386 200 380 92" ' +
         'fill="none" stroke="#B5762A" stroke-width="2" ' +
         'marker-end="url(#mk-' + jid + '-amber)"/>';
    s += '<rect x="168" y="246" width="92" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="214" y="257" font-size="10" fill="#8A5A1C" text-anchor="middle" ' +
         'font-weight="800">H3 · c′</text>';
    /* Z → Y (H4) */
    s += '<path d="M 264 212 L 392 212 L 392 92" fill="none" stroke="#2E7D6F" ' +
         'stroke-width="2" marker-end="url(#mk-' + jid + '-teal)"/>';
    s += '<rect x="300" y="202" width="52" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="326" y="213" font-size="10" fill="#1F6357" text-anchor="middle" ' +
         'font-weight="800">H4</text>';
    /* Moderasi M×Z → garis M→Y (H5) */
    s += '<line x1="210" y1="184" x2="210" y2="148" stroke="#2E7D6F" ' +
         'stroke-width="2.2" stroke-dasharray="5 4" marker-end="url(#mk-' + jid + '-teal)"/>';
    s += '<line x1="210" y1="148" x2="256" y2="148" stroke="#2E7D6F" ' +
         'stroke-width="2.2" marker-end="url(#mk-' + jid + '-teal)"/>';
    s += '<rect x="212" y="132" width="62" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="243" y="143" font-size="10" fill="#1F6357" text-anchor="middle" ' +
         'font-weight="800">H5</text>';
    /* Z ⇢ M — TIDAK dihipotesiskan */
    s += '<line x1="182" y1="184" x2="182" y2="90" stroke="#9A9086" ' +
         'stroke-width="2" stroke-dasharray="2 4" marker-end="url(#mk-' + jid + '-abu)"/>';
    s += '<rect x="186" y="130" width="36" height="14" rx="3" fill="#FBF8F3" opacity="0.92"/>';
    s += '<text x="204" y="141" font-size="9.5" fill="#9A9086" text-anchor="middle" ' +
         'font-weight="800">NH1</text>';
  }

  s += '</svg>';
  return s;
}
