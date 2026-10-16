/* ==========================================================================
   GRAFIK HIDUP — Tahap 2 (ACC Bos 20Sep26)
   ──────────────────────────────────────────────────────────────────────────
   MENGAPA ADA: kartu di halaman ini dulu hanya menampilkan ANGKA. Mahasiswa
   bisa membaca "p = 0,044" tapi tidak melihat BENTUK masalahnya. Fungsi di
   sini menggambar grafik dari DATA YANG DIUNGGAH user — bukan contoh tetap.

   ATURAN INDUK:
     · Tanpa pustaka luar (Chart.js/D3). SVG tulisan sendiri — sudah terbukti
       di kamus /belajar dan diagram model.
     · Skala dihitung dari data, JANGAN dipaku. Kalau dipaku, grafik berbohong
       untuk data di luar jangkauan.
     · Titik dibatasi `BATAS_TITIK` supaya HP tidak berat; angka statistiknya
       tetap dihitung dari SEMUA baris (batas ini cuma soal MENGGAMBAR).

   ⚠️ JEBAKAN YANG SUDAH KENA (jangan ulang):
     · `innerHTML` + tag penutup HTML di dalam string JS WAJIB di-escape
       (`<\/text>`). Kalau tidak, parser HTML menutup blok <script> lebih awal
       → SELURUH skrip mati, halaman tetap HTTP 200, konsol cuma 404 favicon.
       Gerbang: `gerbang_tag_skrip.py`.
   ========================================================================== */

/* Batas titik DIGAMBAR. Alasan: 5.000 elemen SVG membuat HP lambat.
   Diambil MENYEBAR (bukan N pertama) supaya pola tidak menipu. */
const BATAS_TITIK = 500;

/* Ambil `maks` POSISI secara MENYEBAR dari panjang `n` → larik indeks.
   ⚠️ AKAR (20Sep26) — CACAT WULAN YANG DITUTUP SENDIRI: mula-mula `sebar()`
   dipanggil TERPISAH untuk zpred dan zresid. Itu SALAH BESAR: titik ke-7
   zpred jadi berpasangan dengan titik ke-7 zresid — padahal keduanya dari
   baris data yang BERBEDA. Gambar jadi omong kosong yang tetap "kelihatan
   masuk akal" (ini jenis cacat paling berbahaya: LOLOS dari mata).
   Benar: pilih INDEKS-nya sekali, lalu pakai indeks SAMA untuk semua sumbu.
   Fungsi ini mengembalikan INDEKS, bukan nilai. */
function indeksSebar(n, maks) {
  if (n <= maks) {
    const semua = [];
    for (let i = 0; i < n; i++) semua.push(i);
    return semua;
  }
  const out = [];
  const langkah = n / maks;
  for (let i = 0; i < maks; i++) out.push(Math.floor(i * langkah));
  return out;
}

/* Ambil nilai pada posisi terpilih — pakai indeks yang SAMA untuk tiap sumbu. */
function ambilPada(larik, idx) {
  const a = larik || [];
  const out = [];
  for (let i = 0; i < idx.length; i++) {
    if (idx[i] < a.length) out.push(a[idx[i]]);
  }
  return out;
}

/* Petakan NILAI DATA → KOORDINAT GAMBAR.
 *
 * ⚠️ AKAR (20Sep26) — CACAT WULAN YANG DITEMUKAN UJI, bukan tebakan:
 * versi lama bernama `skala(min, maks, dari, ke)` dan rumusnya
 *   `ke - ((dari - min) / (maks - min)) * (ke - dari)`
 * Dua kesalahan sekaligus:
 *   (1) NAMA MENYESATKAN — `dari` dipakai sebagai NILAI DATA, sedangkan `ke`
 *       dipakai sebagai KOORDINAT TUJUAN. Dua makna beda dalam satu nama itu
 *       yang membuat rumusnya kacau dan tidak ketahuan saat dibaca.
 *   (2) RUMUSNYA SALAH — pada data X bernilai 9…26,5 dengan bingkai 34…300,
 *       hasilnya 26,5 (titiknya TUMPAH KELUAR BINGKAI). Hanya "kelihatan
 *       benar" kalau nilai data kebetulan sama dengan koordinat bingkai.
 * Terukur sebelum diperbaiki: 200 titik semua jatuh di x = 9…26 padahal
 * bingkai 34…300 → grafik kosong walau datanya penuh.
 *
 * Sekarang: (nilai, nilaiMin, nilaiMaks) → (gambarMin, gambarMaks), LINIER.
 * Dipakai untuk KEDUA sumbu — perhatikan urutan `gambarMin/gambarMaks`:
 *   sumbu X: gambarMin = kiri, gambarMaks = kanan
 *   sumbu Y: gambarMin = BAWAH, gambarMaks = ATAS (SVG: y mengecil ke atas)
 */
function petakan(nilai, nilaiMin, nilaiMaks, gambarMin, gambarMaks) {
  if (nilaiMaks === nilaiMin) return (gambarMin + gambarMaks) / 2;
  const t = (nilai - nilaiMin) / (nilaiMaks - nilaiMin);
  return gambarMin + t * (gambarMaks - gambarMin);
}

/* Bingkai grafik: sumbu + label. Mengembalikan potongan SVG. */
function bingkaiSvg(p, judulX, judulY) {
  const { X0, Y0, X1, Y1 } = p;   /* X0=kiri, Y0=atas, X1=kanan, Y1=bawah */
  let s = '';
  s += '<line x1="' + X0 + '" y1="' + Y1 + '" x2="' + X1 + '" y2="' + Y1 +
       '" stroke="#E0D8C8" stroke-width="1"/>';
  s += '<line x1="' + X0 + '" y1="' + Y1 + '" x2="' + X0 + '" y2="' + Y0 +
       '" stroke="#E0D8C8" stroke-width="1"/>';
  if (judulX) {
    s += '<text x="' + ((X0 + X1) / 2) + '" y="' + (Y1 + 14) +
         '" font-size="8.5" fill="#9A9086" text-anchor="middle">' + judulX + '<\/text>';
  }
  if (judulY) {
    s += '<text x="' + (X0 - 6) + '" y="' + ((Y0 + Y1) / 2) +
         '" font-size="8.5" fill="#9A9086" text-anchor="middle" transform="rotate(-90 ' +
         (X0 - 6) + ' ' + ((Y0 + Y1) / 2) + ')">' + judulY + '<\/text>';
  }
  return s;
}

/* ──────────────────────────────────────────────────────────────────────────
   GRAFIK 1: SCATTER ZPRED × ZRESID — membaca HETEROSKEDASTISITAS
   Sama seperti SPSS: Analyze → Regression → Linear → Plots.
   Titik rata = aman. Titik melebar ke kanan = corong (bermasalah).
   ────────────────────────────────────────────────────────────────────────── */
function svgHetero(titik, aman) {
  const zpA = (titik && titik.zpred) || [];
  const zrA = (titik && titik.zresid) || [];
  const nAsli = Math.min(zpA.length, zrA.length);
  if (!nAsli) return '<p class="samar">Grafik belum bisa digambar — data sisa tidak tersedia.<\/p>';
  /* ⚠️ INDEKS dipilih SEKALI, dipakai untuk KEDUA sumbu — supaya pasangan
     (zpred, zresid) tetap dari baris data yang SAMA. */
  const idx = indeksSebar(nAsli, BATAS_TITIK);
  const zp = ambilPada(zpA, idx);
  const zr = ambilPada(zrA, idx);
  /* ⚠️ n = panjang INDEKS TERPILIH, bukan nAsli. Kalau nAsli > BATAS_TITIK,
     `indeksSebar` hanya mengembalikan BATAS_TITIK indeks — memakai nAsli
     membuat loop membaca indeks di luar larik `zp`/`zr` → titik NaN (hilang
     tanpa galat) DAN jumlahnya bisa melampaui batas jaga.
     Terukur dari uji lama: nAsli 5000 → 5000 lingkaran padahal batas 500. */
  const n = idx.length;

  const P = { X0: 34, Y0: 12, X1: 300, Y1: 104 };
  /* Skala dari data, dengan sedikit ruang di tepi supaya titik tidak menempel garis. */
  const semua = zp.concat(zr);
  const lo = Math.min.apply(null, semua) * 1.08;
  const hi = Math.max.apply(null, semua) * 1.08;
  const warna = aman ? '#2E7D6F' : '#A85A5A';

  let s = bingkaiSvg(P, 'nilai prediksi (ZPRED)', 'sisa (ZRESID)');
  /* garis nol: titik seharusnya tersebar rata di sekitarnya */
  const y0 = petakan(0, lo, hi, P.Y1, P.Y0);
  s += '<line x1="' + P.X0 + '" y1="' + y0 + '" x2="' + P.X1 + '" y2="' + y0 +
       '" stroke="#EDE6D8" stroke-width="1" stroke-dasharray="3 3"/>';
  for (let i = 0; i < n; i++) {
    const x = petakan(zp[i], lo, hi, P.X0, P.X1);
    const y = petakan(zr[i], lo, hi, P.Y1, P.Y0);
    s += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) +
         '" r="2.2" fill="' + warna + '" opacity=".5"/>';
  }
  return s;
}

/* ──────────────────────────────────────────────────────────────────────────
   GRAFIK 2: NORMAL P-P PLOT — membaca NORMALITAS SISA
   Titik MENEMPEL garis 45° = normal. Titik membelok di ujung = bermasalah.
   ────────────────────────────────────────────────────────────────────────── */
function svgPP(titik, normal) {
  const pp = (titik && titik.pp) || {};
  const thA = pp.teori || [], amA = pp.amati || [];
  const nAsli = Math.min(thA.length, amA.length);
  if (!nAsli) return '<p class="samar">Grafik belum bisa digambar — data sisa tidak tersedia.<\/p>';
  /* Indeks dipilih SEKALI, dipakai untuk kedua sumbu (pasangan tetap asli). */
  const idx = indeksSebar(nAsli, BATAS_TITIK);
  const th = ambilPada(thA, idx);
  const am = ambilPada(amA, idx);
  /* n = panjang INDEKS terpilih (bukan nAsli) — lihat catatan di svgHetero. */
  const n = idx.length;

  const P = { X0: 34, Y0: 10, X1: 300, Y1: 106 };
  const loT = Math.min.apply(null, th), hiT = Math.max.apply(null, th);
  const warna = normal ? '#2E7D6F' : '#A85A5A';

  let s = bingkaiSvg(P, 'peluang yang diharapkan', 'peluang teramati');
  /* garis acuan 45°: sumbu X (peluang 0…1) ↔ sumbu Y (peluang 0…1) */
  s += '<line x1="' + petakan(0, loT, hiT, P.X0, P.X1) + '" y1="' + P.Y1 +
       '" x2="' + petakan(1, loT, hiT, P.X0, P.X1) + '" y2="' + P.Y0 +
       '" stroke="#4E8A5A" stroke-width="1.4" stroke-dasharray="4 3"/>';
  for (let i = 0; i < n; i++) {
    const x = petakan(th[i], loT, hiT, P.X0, P.X1);
    const y = petakan(am[i], 0, 1, P.Y1, P.Y0);
    s += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) +
         '" r="2.2" fill="' + warna + '" opacity=".55"/>';
  }
  return s;
}

/* ──────────────────────────────────────────────────────────────────────────
   GRAFIK 3: HISTOGRAM SISA — melihat bentuk sebaran
   Lonceng = normal. Miring berat / berekor panjang = bermasalah.
   ────────────────────────────────────────────────────────────────────────── */
function svgHistogram(hist, normal) {
  const h = hist || {};
  const t = h.tinggi || [];
  if (!t.length) return '<p class="samar">Grafik belum bisa digambar — data sisa tidak tersedia.<\/p>';

  const P = { X0: 30, Y0: 10, X1: 300, Y1: 100 };
  const tinggiMaks = Math.max.apply(null, t) || 1;
  const lebar = (P.X1 - P.X0) / t.length;
  const warna = normal ? '#2E7D6F' : '#A85A5A';

  let s = bingkaiSvg(P, 'nilai sisa', 'jumlah');
  for (let i = 0; i < t.length; i++) {
    const th = (t[i] / tinggiMaks) * (P.Y1 - P.Y0 - 4);
    s += '<rect x="' + (P.X0 + i * lebar + 1).toFixed(1) + '" y="' + (P.Y1 - th).toFixed(1) +
         '" width="' + (lebar - 2).toFixed(1) + '" height="' + th.toFixed(1) +
         '" rx="1.5" fill="' + warna + '" opacity=".75"/>';
  }
  return s;
}

/* ──────────────────────────────────────────────────────────────────────────
   GRAFIK 4: SCATTER X × Y — membaca LINEARITAS
   Titik mengikuti satu garis lurus = linear. Melengkung = tidak.
   ────────────────────────────────────────────────────────────────────────── */
function svgLinear(tt, kolomX, kolomY, lurus) {
  const xA = (tt && tt.x) || [], yA = (tt && tt.y) || [];
  const nAsli = Math.min(xA.length, yA.length);
  if (!nAsli) return '<p class="samar">Grafik belum bisa digambar — data tidak tersedia.<\/p>';
  /* Indeks dipilih SEKALI, dipakai untuk kedua sumbu (pasangan tetap asli). */
  const idx = indeksSebar(nAsli, BATAS_TITIK);
  const x = ambilPada(xA, idx);
  const y = ambilPada(yA, idx);
  const n = idx.length;   /* lihat catatan di svgHetero & svgPP */

  const P = { X0: 38, Y0: 10, X1: 300, Y1: 104 };
  const loX = Math.min.apply(null, x), hiX = Math.max.apply(null, x);
  const loY = Math.min.apply(null, y), hiY = Math.max.apply(null, y);
  const warna = lurus ? '#2E7D6F' : '#A85A5A';

  let s = bingkaiSvg(P, kolomX || 'X', kolomY || 'Y');
  for (let i = 0; i < n; i++) {
    const px = petakan(x[i], loX, hiX, P.X0, P.X1);
    const py = petakan(y[i], loY, hiY, P.Y1, P.Y0);
    s += '<circle cx="' + px.toFixed(1) + '" cy="' + py.toFixed(1) +
         '" r="2.2" fill="' + warna + '" opacity=".5"/>';
  }
  return s;
}

/* Kotak gambar + keterangan kecil di bawahnya.
   `kunci` dipakai supaya tiap kotak punya id unik (untuk uji otomatis). */
function kotakGrafik(isiSvg, keterangan, kunci) {
  return '<div class="kotak-gambar" data-grafik="' + kunci + '" ' +
         'style="background:#FBF7F0;border:1px solid #E7DECF;border-radius:11px;' +
         'padding:8px 10px;margin:10px 0 6px">' +
    '<svg viewBox="0 0 336 118" style="width:100%;height:118px;display:block">' +
      isiSvg + '<\/svg><\/div>' +
    (keterangan ? '<p style="margin:0 0 4px;font-size:12px;color:#9A9086">' +
      keterangan + '<\/p>' : '');
}

/* Keterangan jujur tentang batas titik (dipakai kalau data > BATAS_TITIK). */
function catatanTitik(n) {
  if (!n || n <= BATAS_TITIK) return '';
  return 'Digambar ' + BATAS_TITIK + ' dari ' + n +
         ' titik (diambil menyebar — polanya tetap sama). Angka di atas dihitung dari SEMUA data.';
}
