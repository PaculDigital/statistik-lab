/* UJI GRAFIK HIDUP — apakah gambar benar (bukan cuma "ada").
 *
 * Dijalankan dengan Node. Menguji FUNGSI SUNGGUHAN dari app/static/grafik_hidup.js
 * (disuntik lewat fs.readFileSync + eval), bukan salinan.
 *
 * Yang WAJIB dibuktikan:
 *   1. `indeksSebar` memilih MENYEBAR (bukan N pertama, bukan acak).
 *   2. ⭐ PASANGAN TITIK TETAP ASLI — ini cacat yang hampir lolos (20Sep26).
 *   3. Jumlah titik tidak pernah melebihi BATAS_TITIK.
 *   4. Setiap fungsi gambar menghasilkan SVG yang SAH (tag seimbang).
 *   5. Data sakit menghasilkan gambar yang BEDA dari data sehat.
 *
 * EXIT 0 = semua lulus.
 */
const fs = require('fs');
const path = require('path');

const berkas = path.join(__dirname, 'app', 'static', 'grafik_hidup.js');
/* ⚠️ JEBAKAN NODE (20Sep26): `eval(kode)` di dalam file CommonJS TIDAK
   membocorkan `const`/`function` ke scope modul — `BATAS_TITIK is not defined`.
   Yang JALAN: indirect eval `(0, eval)(kode)` → dijalankan di scope GLOBAL,
   sehingga `const BATAS_TITIK` dan tiap `function` bisa dipanggil dari sini.
   (Alternatif: `vm.runInThisContext` — sama-sama global.) */
const vm = require('vm');
vm.runInThisContext(fs.readFileSync(berkas, 'utf8') +
  '\n;globalThis.BATAS_TITIK = BATAS_TITIK;' +
  '\n;globalThis.indeksSebar = indeksSebar;' +
  '\n;globalThis.ambilPada = ambilPada;' +
  '\n;globalThis.svgHetero = svgHetero;' +
  '\n;globalThis.svgPP = svgPP;' +
  '\n;globalThis.svgHistogram = svgHistogram;' +
  '\n;globalThis.svgLinear = svgLinear;' +
  '\n;globalThis.petakan = petakan;');

let total = 0, gagal = 0;
function cek(nama, syarat, info) {
  total += 1;
  if (syarat) { console.log('  \u2705 ' + nama); }
  else { gagal += 1; console.log('  \u274c ' + nama + (info ? '  ' + info : '')); }
}

console.log('\n\u2500\u2500 1. indeksSebar: menyebar, bukan N pertama \u2500\u2500');
const kecil = indeksSebar(10, 500);
cek('n < maks \u2192 ambil SEMUA', kecil.length === 10 && kecil[9] === 9);
const besar = indeksSebar(1000, 500);
cek('n > maks \u2192 tepat maks', besar.length === 500, besar.length);
cek('menyebar sampai ujung (bukan 500 pertama)', besar[499] > 900, besar[499]);
cek('indeks menaik', besar.every((v, i) => i === 0 || v > besar[i - 1]));
cek('tidak ada indeks di luar jangkauan', besar.every(v => v >= 0 && v < 1000));

console.log('\n\u2500\u2500 2. \u2b50 PASANGAN TITIK TETAP ASLI (cacat yang hampir lolos) \u2500\u2500');
{
  // zpred[i] = i, zresid[i] = i * 100  \u2192 pasangan asli selalu (i, i*100)
  const n = 2000;
  const zpA = [], zrA = [];
  for (let i = 0; i < n; i++) { zpA.push(i); zrA.push(i * 100); }
  const idx = indeksSebar(Math.min(zpA.length, zrA.length), BATAS_TITIK);
  const zp = ambilPada(zpA, idx), zr = ambilPada(zrA, idx);
  let semuaBenar = true, contohSalah = '';
  for (let i = 0; i < zp.length; i++) {
    if (zr[i] !== zp[i] * 100) {
      semuaBenar = false;
      contohSalah = `titik ke-${i}: zpred=${zp[i]} tapi zresid=${zr[i]} (harusnya ${zp[i] * 100})`;
      break;
    }
  }
  cek('pasangan (zpred, zresid) tetap dari baris yang SAMA', semuaBenar, contohSalah);

  /* ⚠️ Uji "bisa gagal" yang BENAR (20Sep26).
     Percobaan pertama Wulan SALAH RANCANG: ia menyebar zpred & zresid lewat
     `indeksSebar` terpisah, tapi karena PANJANG keduanya sama, indeks yang
     dihasilkan juga sama → kebetulan tetap benar, ujinya tidak bisa gagal.
     Cara yang benar untuk membuktikan ujinya bergigi: buat DUA larik dengan
     panjang BERBEDA (seperti data yang punya baris kosong di salah satu
     kolom). Di situ penyebaran terpisah PASTI salah. */
  const zpPendek = zpA.slice(0, 1500);          /* 1500 */
  const zrPanjang = zrA.slice(0, 1800);         /* 1800 — beda panjang */
  const idxBenar = indeksSebar(Math.min(zpPendek.length, zrPanjang.length), BATAS_TITIK);
  const zpB = ambilPada(zpPendek, idxBenar), zrB = ambilPada(zrPanjang, idxBenar);
  let caraBenarOk = true;
  for (let i = 0; i < zpB.length; i++) if (zrB[i] !== zpB[i] * 100) { caraBenarOk = false; break; }
  cek('panjang beda: cara BENAR tetap mempertahankan pasangan', caraBenarOk);

  const idxSalah = indeksSebar(zpPendek.length, BATAS_TITIK);
  const idxSalah2 = indeksSebar(zrPanjang.length, BATAS_TITIK);
  const zpS = ambilPada(zpPendek, idxSalah), zrS = ambilPada(zrPanjang, idxSalah2);
  let caraSalahRusak = false;
  for (let i = 0; i < Math.min(zpS.length, zrS.length); i++) {
    if (zrS[i] !== zpS[i] * 100) { caraSalahRusak = true; break; }
  }
  cek('\u26a0\ufe0f uji ini BENAR-BENAR BISA GAGAL (cara salah terdeteksi rusak)', caraSalahRusak);
}

console.log('\n\u2500\u2500 3. Batas titik dipatuhi \u2500\u2500');
{
  const n = 5000;
  const zp = [], zr = [];
  for (let i = 0; i < n; i++) { zp.push(Math.sin(i)); zr.push(Math.cos(i)); }
  const svg = svgHetero({ zpred: zp, zresid: zr }, true);
  const jml = (svg.match(/<circle/g) || []).length;
  cek('svgHetero: titik \u2264 BATAS_TITIK', jml <= BATAS_TITIK, jml + ' lingkaran');
  cek('svgHetero: titik > 0', jml > 0, jml + ' lingkaran');
}

console.log('\n\u2500\u2500 4. SVG yang dihasilkan SAH \u2500\u2500');
{
  const zp = [], zr = [], th = [], am = [], yy = [], xx = [];
  for (let i = 0; i < 120; i++) {
    zp.push(Math.sin(i / 7)); zr.push(Math.cos(i / 5));
    th.push((i - 60) / 40); am.push((i + 1) / 121);
    xx.push(i); yy.push(i * 2 + Math.sin(i));
  }
  const kasus = [
    ['svgHetero', svgHetero({ zpred: zp, zresid: zr }, true)],
    ['svgPP', svgPP({ pp: { teori: th, amati: am } }, true)],
    ['svgHistogram', svgHistogram({ batas: [0, 1, 2, 3, 4, 5], tinggi: [2, 8, 15, 9, 3], n_bin: 5 }, true)],
    ['svgLinear', svgLinear({ x: xx, y: yy }, 'X1', 'Y', true)],
  ];
  for (const [nama, svg] of kasus) {
    const buka = (svg.match(/<(circle|rect|line|text|path)[\s>]/g) || []).length;
    const tutup = (svg.match(/<\/(circle|rect|line|text|path)>/g) || []).length;
    const mandiri = (svg.match(/<(circle|rect|line)[^>]*\/>/g) || []).length;
    cek(nama + ': tidak ada tag menggantung',
        buka === tutup + mandiri || tutup === 0,
        `buka=${buka} tutup=${tutup} mandiri=${mandiri}`);
    cek(nama + ': tidak ada </script> mentah (jebakan tag skrip)',
        !svg.includes('</script>'));
  }
  // data kosong TIDAK boleh meledak, harus kasih pesan
  cek('data kosong \u2192 pesan jujur, bukan meledak',
      svgHetero({ zpred: [], zresid: [] }, true).includes('belum bisa digambar'));
  cek('data kosong (pp) \u2192 pesan jujur',
      svgPP({ pp: { teori: [], amati: [] } }, true).includes('belum bisa digambar'));
}

console.log('\n\u2500\u2500 5. Data SAKIT harus BEDA dari data SEHAT \u2500\u2500');
{
  // sehat: sisa rata di semua nilai X. sakit: sisa melebar di kanan (corong).
  const zp = [], sehat = [], sakit = [];
  for (let i = 0; i < 200; i++) {
    const x = (i - 100) / 40;
    zp.push(x);
    sehat.push(Math.sin(i) * 0.6);
    sakit.push(Math.sin(i) * (0.3 + 1.6 * Math.abs(x)));
  }
  const sSehat = svgHetero({ zpred: zp, zresid: sehat }, true);
  const sSakit = svgHetero({ zpred: zp, zresid: sakit }, false);
  cek('gambar sehat \u2260 gambar sakit', sSehat !== sSakit);
  cek('warna berbeda (hijau vs merah)',
      sSehat.includes('#2E7D6F') && sSakit.includes('#A85A5A'));

  /* Ukur lebar sebaran di KANAN vs KIRI.
     ⚠️ AKAR (20Sep26) — versi pertama Wulan memakai ambang x>250 / x<100,
     angka bingkai yang DIPAKU. Setelah `petakan()` diperbaiki, skala barunya
     menaruh titik di posisi berbeda → ambang tetap itu jadi SALAH UKUR, bukan
     aplikasinya yang salah. ATURAN: uji geometri WAJIB pakai lebar RELATIF
     (bagian dari rentang bingkai), jangan angka piksel tetap. */
  function lebarKanan(svg) {
    const c = [...svg.matchAll(/<circle cx="([\d.]+)" cy="([\d.]+)"/g)]
      .map(m => ({ x: parseFloat(m[1]), y: parseFloat(m[2]) }));
    const xs = c.map(p => p.x);
    const xMin = Math.min(...xs), xMax = Math.max(...xs);
    const potong = xMin + (xMax - xMin) * 0.75;   /* 25% paling kanan */
    const kanan = c.filter(p => p.x > potong), kiri = c.filter(p => p.x <= potong);
    const sp = arr => {
      if (arr.length < 2) return 0;
      const m = arr.reduce((a, p) => a + p.y, 0) / arr.length;
      return Math.sqrt(arr.reduce((a, p) => a + (p.y - m) ** 2, 0) / arr.length);
    };
    return { kanan: sp(kanan), kiri: sp(kiri), n: c.length };
  }
  const L = lebarKanan(sSakit);
  cek('\u26a0\ufe0f corong TERLIHAT di gambar: sebaran KANAN lebih lebar dari KIRI',
      L.kanan > L.kiri * 1.3,
      `kanan=${L.kanan.toFixed(1)} kiri=${L.kiri.toFixed(1)} n=${L.n}`);
  /* pembanding: pada data SEHAT, kanan & kiri harus SEIMBANG */
  const LS = lebarKanan(sSehat);
  cek('data sehat: sebaran kanan & kiri SEIMBANG (tidak ada corong)',
      LS.kanan < LS.kiri * 1.6,
      `kanan=${LS.kanan.toFixed(1)} kiri=${LS.kiri.toFixed(1)}`);
}

console.log();
if (gagal) { console.log(`  \u274c GAGAL: ${gagal} dari ${total}`); process.exit(1); }
console.log(`  \u2705 LULUS SEMUA: ${total} pemeriksaan`);
