"""Sisip 2 TOMBOL CONTOH (sehat & sakit) ke Langkah 2 di diagnosis.html.

⚠️ ATURAN SISIP (20Sep26): baca utuh · penanda memuat PEMBUKA + PENUTUP ·
cadangan dulu · buktikan sesudahnya dengan grep + ukuran berkas.

⚠️ NAMA YANG SUDAH DIBUKTIKAN ADA (grep 20Sep26, JANGAN tebak):
     · isiPilihan()          — baris 254, mengisi semua dropdown kolom
     · pilihKosong('kolom-y')— baris 267
     · tambahX()             — baris 289, menambah satu baris X (otomatis
                               memilih kolom pertama yang tersedia)
     · pesan(tempat, teks, jenis) — baris 206
     · namaKolom()           — baris 252
   NAMA YANG TIDAK ADA (jangan dipakai): isiPilihanKolom(), pilihOtomatis().
"""
from pathlib import Path
import shutil

F = Path('app/templates/diagnosis.html')
t = F.read_text(encoding='utf-8')
shutil.copy(F, F.with_suffix('.html.cadangan_contoh'))
sebelum = len(t)

# ── 1. TOMBOL CONTOH (sebelum kotak unggah) ────────────────────────────────
LAMA_TB = """  <label id="kotak-unggah" for="berkas" style="display:block;border:2px dashed #C9BFB2;border-radius:13px;padding:26px 16px;text-align:center;background:#FDFBF7;cursor:pointer">"""

BARU_TB = """  {# ── CONTOH SIAP-KLIK (Tahap 2.1d, ACC Bos 20Sep26) ──────────────────
     Mahasiswa awam sering belum punya data — halaman ini jadi kosong dan
     tak bisa dicoba. Dua tombol ini mengisi data contoh supaya SEMUA grafik
     langsung terlihat hidup, tanpa perlu menyiapkan berkas lebih dulu.
     "Sehat" = semua syarat terpenuhi (hijau). "Bermasalah" = sengaja
     melanggar (corong merah) supaya mahasiswa BELAJAR MENGENALI bentuknya.
     ⚠️ Data contoh ditandai jelas — jangan sampai dikira data mahasiswa. #}
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px">
    <button type="button" class="tb tb-sekunder" onclick="pakaiContoh('sehat')">
      {{ ikon('sparkles', 15) }} Coba contoh data yang sehat
    </button>
    <button type="button" class="tb tb-sekunder" onclick="pakaiContoh('sakit')">
      {{ ikon('activity', 15) }} Lihat contoh data bermasalah
    </button>
  </div>
  <p style="margin:0 0 14px;color:#6B6259;font-size:.9rem">
    Belum punya data? Pakai contoh dulu — nanti berkasmu sendiri tinggal
    diunggah seperti biasa.
  </p>

  <label id="kotak-unggah" for="berkas" style="display:block;border:2px dashed #C9BFB2;border-radius:13px;padding:26px 16px;text-align:center;background:#FDFBF7;cursor:pointer">"""

c = t.count(LAMA_TB)
if c != 1:
    raise SystemExit(f'  ❌ penanda tombol ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_TB, BARU_TB, 1)

# ── 2. KOTAK PENANDA "ini contoh" (di dalam ringkas-berkas) ────────────────
LAMA_CAT = """      <div id="bentuk-berkas" style="margin-top:5px;font-size:.9rem"></div>
    </div>
  </div>
</div>"""

BARU_CAT = """      <div id="bentuk-berkas" style="margin-top:5px;font-size:.9rem"></div>
    </div>
    {# Penanda jujur: berkas ini CONTOH, bukan data mahasiswa sendiri. #}
    <div id="catatan-contoh" class="catatan" hidden
         style="margin-top:9px;background:#FDF6E9;border-color:#E8D9B5"></div>
  </div>
</div>"""

c2 = t.count(LAMA_CAT)
if c2 != 1:
    raise SystemExit(f'  ❌ penanda catatan ketemu {c2}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_CAT, BARU_CAT, 1)

# ── 3. FUNGSI pakaiContoh() — di dalam <script>, sebelum penutupnya ────────
LAMA_JS = """  } finally { t.disabled = false; }
}
</script>"""

BARU_JS = """  } finally { t.disabled = false; }
}

/* ── CONTOH SIAP-KLIK (Tahap 2.1d, ACC Bos 20Sep26) ──────────────────────
   Data contoh DIBUAT DI BROWSER lalu diunggah lewat jalur yang SAMA seperti
   berkas mahasiswa. Jadi tidak ada berkas contoh yang perlu disimpan di
   server, dan halaman tidak punya "jalan rahasia" yang bisa berbeda dari
   jalur sungguhan.

   Dua rasa:
     · 'sehat'  — sisa tetap besarnya (semua uji seharusnya hijau)
     · 'sakit'  — sisa membesar mengikuti x1 (corong merah, Glejser menolak)

   ⚠️ KENAPA 'sakit' PAKAI exp() DAN BUKAN derau linear (terukur 20Sep26):
   Glejser menguji |sisa| lawan X SECARA LINEAR. Derau yang membesar linear
   (mis. 1+3|x1|) justru TIDAK tertangkap (p=0,31 — malah dianggap aman).
   Yang tertangkap adalah derau yang membesar mengikuti pangkat/eksponensial:
   exp(1,1·x1) → p≈0,000. Tombol "bermasalah" WAJIB memakai bentuk yang
   memang terdeteksi, kalau tidak tombolnya berbohong.

   ⚠️ Derau dihitung dari sin(i) — BUKAN Math.random(). Alasannya: hasilnya
   harus SAMA tiap kali diklik, supaya mahasiswa bisa membandingkan "sehat"
   dan "bermasalah" tanpa variasi acak yang membingungkan. #}
function buatContohData(rasa) {
  const n = 120;
  const baris = ['X1,X2,Y'];
  for (let i = 0; i < n; i++) {
    const x1 = (Math.sin(i * 1.7) + Math.cos(i * 0.9)) * 0.85;
    const x2 = (Math.cos(i * 1.3) + Math.sin(i * 2.1)) * 0.85;
    const dasar = 0.45 * x1 + 0.30 * x2;
    const sisa = (rasa === 'sakit')
      ? Math.sin(i * 5.7) * Math.exp(1.1 * x1)   /* membesar → corong */
      : Math.sin(i * 5.7) * 0.95;                /* tetap → rata */
    baris.push([x1.toFixed(4), x2.toFixed(4), (dasar + sisa).toFixed(4)].join(','));
  }
  return baris.join('\\n');
}

async function pakaiContoh(rasa) {
  pesan('pesan-unggah', rasa === 'sakit'
    ? 'Menyiapkan contoh data yang bermasalah…'
    : 'Menyiapkan contoh data yang sehat…');
  try {
    const csv = buatContohData(rasa);
    const nama = (rasa === 'sakit' ? 'contoh_bermasalah' : 'contoh_sehat') + '.csv';
    const fd = new FormData();
    fd.append('berkas', new Blob([csv], { type: 'text/csv' }), nama);
    const r = await fetch('/api/diagnosis/unggah', { method: 'POST', body: fd });
    const d = await r.json();
    if (!r.ok) {
      pesan('pesan-unggah', d.detail || 'Contohnya belum bisa dimuat.', 'galat');
      return;
    }
    /* Jalur penyiapan kolom — SAMA PERSIS seperti setelah unggah berkas
       sungguhan (baca fungsi unggah di atas), supaya tidak ada dua jalan
       berbeda yang bisa saling menyimpang. */
    KUNCI = d.kunci;
    KOLOM = d.kolom;
    document.getElementById('pesan-unggah').innerHTML = '';
    document.getElementById('nama-berkas').textContent = nama + ' — data contoh';
    document.getElementById('ukuran-berkas').textContent = '  ·  dibuat otomatis';
    document.getElementById('bentuk-berkas').textContent =
      d.n_baris + ' responden  ·  ' + d.n_kolom + ' kolom';
    document.getElementById('ringkas-berkas').hidden = false;
    document.getElementById('kartu-kolom').hidden = false;
    nX = 0;
    document.getElementById('baris-x').innerHTML = '';
    document.getElementById('baris-m').innerHTML = '';
    document.getElementById('daftar-konstruk').innerHTML = '';
    tambahX(); pilihKosong('kolom-y');
    if (ALAT === 'pls') { tambahKonstruk(); tambahKonstruk(); }
    document.getElementById('kartu-hasil').hidden = true;

    /* Susun kolomnya otomatis: X1 & X2 sebagai prediktor, Y sebagai yang
       dijelaskan — supaya mahasiswa tinggal tekan "Periksa sekarang". */
    const xPertama = document.querySelector('#baris-x .pilih-kolom');
    if (xPertama) xPertama.value = 'X1';
    tambahX();
    const xKedua = document.querySelectorAll('#baris-x .pilih-kolom')[1];
    if (xKedua) xKedua.value = 'X2';
    const ySel = document.getElementById('kolom-y');
    if (ySel) ySel.value = 'Y';

    const cat = document.getElementById('catatan-contoh');
    if (cat) {
      cat.hidden = false;
      cat.innerHTML = (rasa === 'sakit'
        ? '<strong>Ini contoh data yang SENGAJA bermasalah.</strong> Perhatikan ' +
          'grafik heteroskedastisitas: titiknya melebar ke kanan seperti corong. ' +
          'Di grafik normalitas, titiknya membelok menjauh dari garis. ' +
          'Datamu sendiri nanti bisa berbeda — inilah gunanya memeriksa.'
        : '<strong>Ini contoh data yang sehat.</strong> Semua syaratnya ' +
          'terpenuhi, jadi semua tanda berwarna hijau. Coba juga tombol ' +
          '"Lihat contoh data bermasalah" supaya kelihatan bedanya.');
    }
    pesan('pesan-unggah',
          'Contoh sudah siap. Tekan "Periksa sekarang" di bawah ya.', 'sukses');
    document.getElementById('kartu-kolom').scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (e) {
    pesan('pesan-unggah', 'Koneksi ke server terputus. Coba lagi ya.', 'galat');
  }
}
</script>"""

c3 = t.count(LAMA_JS)
if c3 != 1:
    raise SystemExit(f'  ❌ penanda skrip ketemu {c3}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_JS, BARU_JS, 1)

F.write_text(t, encoding='utf-8')
print('  ✅ tombol contoh + catatan-contoh + fungsi pakaiContoh() disisip')
print(f'  berkas: {sebelum} → {len(t)} karakter (+{len(t) - sebelum})')
print('  ✅ nama fungsi yang dipakai SUDAH dibuktikan ada: pesan, tambahX,')
print('     pilihKosong, KUNCI, KOLOM, ALAT, nX, kartu-kolom, ringkas-berkas')
