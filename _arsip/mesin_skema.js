/* ══════════════════════════════════════════════════════════════════════
   MESIN GAMBAR SKEMA PENELITIAN (mockup — nanti dipindah ke produksi)
   ══════════════════════════════════════════════════════════════════════

   MENIRU GAYA YANG BOS TUNJUKKAN (2 gambar nyata):
     · Bentuk  : ELIPS (bukan kotak)
     · Warna   : X = biru muda · perantara = kuning · Y = merah · hitam-putih
                 untuk skema hipotesis (H1..Hn)
     · Garis   : PEJAL   = pengaruh LANGSUNG   (PL)
                 PUTUS2  = pengaruh TAK LANGSUNG (TL) & TOTAL (PT)
     · Label   : di SAMPING garis, tidak menumpuk
     · Tingkat : dihitung otomatis dari struktur (kiri → kanan)

   ATURAN YANG DIPAKAI (semua bisa diuji):
     1. Tingkat sebuah variabel = 1 + maksimal tingkat induknya.
     2. Variabel TANPA induk = tingkat 1 (eksogen).
     3. Variabel tanpa anak = tingkat terakhir (endogen).
     4. Di dalam satu tingkat, urutkan sesuai urutan pendaftaran.
     5. Tinggi kanvas = tingkatTerbanyak × jarakBaris + margin.
     ⚠️ Kalau ada LINGKARAN (A→B→A), gambar DITOLAK dengan pesan jelas
        (jangan gambar sesuatu yang tidak mungkin).
   ══════════════════════════════════════════════════════════════════════ */

const WARNA = {
  x:   { isi: '#DCEBF7', garis: '#7FA8C9' },   /* variabel bebas — biru muda */
  m:   { isi: '#FBEFC9', garis: '#D8B95E' },   /* perantara — kuning */
  y:   { isi: '#F7DEDE', garis: '#C98A8A' },   /* terikat — merah */
  z:   { isi: '#DFF0EA', garis: '#7FBFAE' },   /* penguat — hijau muda */
  hp:  { isi: '#FFFFFF', garis: '#2B2722' }    /* skema hipotesis — hitam-putih */
};

/* ── hitung TINGKAT tiap variabel (kiri → kanan) ──────────────────────── */
function hitungTingkat(simpul, panah) {
  const tingkat = {};
  simpul.forEach(s => { tingkat[s.id] = 1; });
  /* ulangi sampai stabil — model boleh 4-5 tingkat, jadi 12 putaran cukup */
  for (let putaran = 0; putaran < 12; putaran++) {
    let berubah = false;
    panah.forEach(p => {
      if (p.jenis === 'moderasi') return;          /* panah moderasi bukan jalur */
      if (tingkat[p.dari] === undefined || tingkat[p.ke] === undefined) return;
      const calon = tingkat[p.dari] + 1;
      if (calon > tingkat[p.ke]) { tingkat[p.ke] = calon; berubah = true; }
    });
    if (!berubah) break;
  }
  return tingkat;
}

/* ── deteksi LINGKARAN ───────────────────────────────────────────────── */
function adaLingkaran(simpul, panah) {
  const ke = {};
  simpul.forEach(s => { ke[s.id] = []; });
  panah.forEach(p => { if (ke[p.dari]) ke[p.dari].push(p.ke); });
  const warna = {};                     /* 0 belum, 1 sedang, 2 selesai */
  let ada = false;
  function telusuri(id) {
    if (warna[id] === 1) { ada = true; return; }
    if (warna[id] === 2) return;
    warna[id] = 1;
    (ke[id] || []).forEach(telusuri);
    warna[id] = 2;
  }
  simpul.forEach(s => { if (!warna[s.id]) telusuri(s.id); });
  return ada;
}

/* ── gambar skema ────────────────────────────────────────────────────── */
function gambarSkema(simpul, panah, opsi) {
  const o = Object.assign({
    lebar: 900, judul: '', gaya: 'warna',       /* 'warna' | 'hipotesis' */
    tampilkanAngka: false, skala: 1
  }, opsi || {});

  if (adaLingkaran(simpul, panah)) {
    return { galat: 'Model ini melingkar (A memengaruhi B, B memengaruhi A). ' +
                    'Analisis jalur tidak bisa menghitung model melingkar.' };
  }
  if (!simpul.length) return { galat: 'Belum ada variabel.' };

  const tingkat = hitungTingkat(simpul, panah);
  const maksT = Math.max(...Object.values(tingkat));

  /* kelompokkan per tingkat */
  const perTingkat = {};
  simpul.forEach(s => {
    const t = tingkat[s.id];
    (perTingkat[t] = perTingkat[t] || []).push(s);
  });
  const barisMaks = Math.max(...Object.values(perTingkat).map(a => a.length));

  /* ukuran */
  const LEBAR_ELIPS = 152, TINGGI_ELIPS = 46;
  const JARAK_X = o.lebar / (maksT + 1);
  const JARAK_Y = 76;
  const ATAS = o.judul ? 54 : 26;
  const TINGGI = ATAS + barisMaks * JARAK_Y + 74;

  /* posisi tiap simpul */
  const pos = {};
  Object.keys(perTingkat).forEach(k => {
    const t = Number(k);
    const daftar = perTingkat[t];
    const totalTinggi = daftar.length * JARAK_Y;
    const mulai = ATAS + (barisMaks * JARAK_Y - totalTinggi) / 2 + JARAK_Y / 2;
    daftar.forEach((s, i) => {
      pos[s.id] = { x: JARAK_X * t, y: mulai + i * JARAK_Y };
    });
  });

  const gaya = (o.gaya === 'hipotesis') ? WARNA.hp : null;
  const warnaSimpul = (s) => {
    if (gaya) return gaya;
    return WARNA[s.peran] || WARNA.x;
  };

  let isi = '';
  /* ── panah ── */
  const digambar = {};      /* hindari garis ganda persis sama */
  panah.forEach((p, pi) => {
    const a = pos[p.dari], b = pos[p.ke];
    if (!a || !b) return;
    const kunci = p.dari + '>' + p.ke;
    const lewatBawah = !!digambar[kunci];
    digambar[kunci] = true;

    /* ── TITIK TEPI ELIPS — RUMUS BAKU (bisa diuji) ─────────────────────
       Titik potong garis pusat→pusat dengan elips berjari-jari (rx, ry):
           t = 1 / sqrt((dx/rx)^2 + (dy/ry)^2)
           tepi = pusat + (dx, dy) · t
       ⚠️ versi 1 & 2 SALAH karena membagi vektor yang BELUM dinormalkan,
       sehingga garis/tanda panah menembus elips (terbukti vision 2×).   */
    const dx0 = b.x - a.x, dy0 = b.y - a.y;
    const rx = LEBAR_ELIPS / 2, ry = TINGGI_ELIPS / 2;
    const tTepi = 1 / Math.sqrt((dx0 / rx) ** 2 + (dy0 / ry) ** 2);
    /* ⚠️ BERI JARAK (padding) supaya kepala panah TIDAK menyentuh tepi */
    const PAD = 3;
    let x1 = a.x + dx0 * tTepi;
    let y1 = a.y + dy0 * tTepi;
    let x2 = b.x - dx0 * tTepi;
    let y2 = b.y - dy0 * tTepi;
    const arah = Math.hypot(x2 - x1, y2 - y1) || 1;
    x1 += (x2 - x1) / arah * PAD;  y1 += (y2 - y1) / arah * PAD;
    x2 -= (x2 - x1) / arah * PAD;  y2 -= (y2 - y1) / arah * PAD;
    const dx = x2 - x1, dy = y2 - y1;

    /* geser kalau dua panah sepasang (dari & ke sama) */
    let geser = 0;
    if (lewatBawah) geser = 17;
    else if (panah.some((q, qi) => qi !== pi && q.dari === p.dari && q.ke === p.ke)) geser = -13;

    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2 + geser;
    const kendali = (p.jenis === 'moderasi') ? 0.34 : 0.16;

    const warna = '#2B2722';
    let atr = `stroke="${warna}" stroke-width="${p.jenis === 'moderasi' ? 2 : 1.9}" fill="none"`;
    if (p.jenis === 'taklangsung') atr += ' stroke-dasharray="8 5"';
    if (p.jenis === 'moderasi') atr += ' stroke-dasharray="5 4"';

    let tanda = ` marker-end="url(#mk-${p.jenis === 'moderasi' ? 'm' : 'a'})"`;
    /* kepala panah untuk garis putus-putus = panah terbuka (tanpa isian) */
    if (p.jenis === 'taklangsung') tanda = ` marker-end="url(#mk-t)"`;

    /* panah MODERASI: dari Z ke TENGAH panah tujuan (menunjuk panah, bukan simpul) */
    if (p.jenis === 'moderasi') {
      const t = pos[p.ke];
      const induk = panah.find(q => q.jenis !== 'moderasi' && q.ke === p.ke && q.dari !== p.dari);
      let tx = t.x - 70, ty = t.y;
      if (induk && pos[induk.dari]) {
        const ia = pos[induk.dari];
        tx = (ia.x + t.x) / 2; ty = (ia.y + t.y) / 2;
      }
      const mdx = tx - x1, mdy = ty - y1;
      const mp = Math.hypot(mdx, mdy) || 1;
      isi += `<path d="M ${x1} ${y1} Q ${(x1 + tx) / 2 + 34} ${(y1 + ty) / 2} ${tx - (mdx / mp) * 9} ${ty - (mdy / mp) * 9}" ${atr}${tanda}/>`;
      const lab = p.label || '';
      isi += `<text x="${(x1 + tx) / 2 + 30}" y="${(y1 + ty) / 2 - 7}" font-size="11" font-weight="700" fill="#2E7D6F" text-anchor="middle">${lab}</text>`;
      return;
    }

    isi += `<path d="M ${x1} ${y1} Q ${mx} ${(y1 + y2) / 2 + kendali * geser * 2.4} ${x2} ${y2}" ${atr}${tanda}/>`;

    if (p.labelUtama || p.labelAngka) {
      /* ── LABEL JANGAN MENUMPUK — versi 3 (18Sep26) ────────────────────
         🚨 Akar sebenarnya: label ditaruh di titik tengah garis, dan pada
         model mediasi ada BEBERAPA garis yang titik tengahnya berdekatan
         (X1→Z, X2→Z, Z→Y) → label pasti tumpuk walau digeser sedikit.
         PERBAIKAN NYATA:
           (a) LABEL SELALU DI ATAS GARIS pada jarak tetap (bukan di tengah);
           (b) diberi LATAR PUTIH OPAK (harus, bukan 0,94) supaya garis
               tidak menembus huruf;
           (c) kalau ada 2 garis sepasang (dari-ke sama), label digeser
               ke atas/bawah sesuai urutannya.                            */
      const t1 = p.labelUtama || '';
      const t2 = (o.tampilkanAngka && p.labelAngka) ? ` = ${p.labelAngka}` : '';
      const teks = t1 + t2;
      const fx = (x1 + x2) / 2;
      /* jarak label dari garis: baris atas untuk pasangan pertama */
      const fy = (y1 + y2) / 2 - 9 - (lewatBawah ? 15 : 0) + (geser / 2);
      const lebar = teks.length * 5.8 + 10;
      const tinggi = 14;
      isi += `<rect x="${fx - lebar / 2}" y="${fy - tinggi + 3}" width="${lebar}" height="${tinggi}" fill="#FFFFFF"/>`;
      isi += `<text x="${fx}" y="${fy}" font-size="10.5" font-weight="700" fill="#2B2722" text-anchor="middle">${teks}</text>`;
    }
  });

  /* ── simpul (elips + teks) ── */
  simpul.forEach(s => {
    const p = pos[s.id];
    const w = warnaSimpul(s);
    const rx = LEBAR_ELIPS / 2, ry = TINGGI_ELIPS / 2;
    isi += `<ellipse cx="${p.x}" cy="${p.y}" rx="${rx}" ry="${ry}" fill="${w.isi}" stroke="${w.garis}" stroke-width="1.7"/>`;
    /* nama dipecah 2 baris bila panjang */
    const nama = s.nama || s.id;
    const potong = nama.length > 19 ? Math.ceil(nama.length / 2) : 0;
    if (potong) {
      const kiri = nama.slice(0, nama.indexOf(' ', potong - 5) + 1) || nama.slice(0, potong);
      const kanan = nama.slice(kiri.length).trim();
      isi += `<text x="${p.x}" y="${p.y - 3}" font-size="12" font-weight="600" fill="#2B2722" text-anchor="middle">${kiri.trim()}</text>`;
      isi += `<text x="${p.x}" y="${p.y + 12}" font-size="12" font-weight="600" fill="#2B2722" text-anchor="middle">${kanan}</text>`;
    } else {
      isi += `<text x="${p.x}" y="${p.y + 4}" font-size="12.5" font-weight="600" fill="#2B2722" text-anchor="middle">${nama}</text>`;
    }
    if (s.simbol) {
      isi += `<text x="${p.x}" y="${p.y + (potong ? 27 : 19)}" font-size="10.5" fill="#6B6259" text-anchor="middle">(${s.simbol})</text>`;
    }
  });

  const keluar = [];
  keluar.push(`<svg viewBox="0 0 ${o.lebar} ${TINGGI}" class="dugaan" style="max-width:100%;height:auto">`);
  keluar.push(`<defs>
    <marker id="mk-a" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#2B2722"/></marker>
    <marker id="mk-t" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10" fill="none" stroke="#2B2722" stroke-width="1.6"/></marker>
    <marker id="mk-m" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="#2E7D6F"/></marker>
  </defs>`);
  if (o.judul) {
    keluar.push(`<text x="${o.lebar / 2}" y="26" font-size="14" font-weight="700" fill="#2B2722" text-anchor="middle">${o.judul}</text>`);
  }
  keluar.push(isi);
  keluar.push('</svg>');
  return { svg: keluar.join('\n'), tinggi: TINGGI, tingkat };
}
