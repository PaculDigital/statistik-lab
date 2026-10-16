#!/usr/bin/env python3
"""
GERBANG UJI STATISTIK LAB — satu perintah, semua uji inti.

Pakai:
    cd /opt/data/services/statistik-lab
    bash gerbang_uji.sh          # atau: .venv/bin/python gerbang_uji.py

WAJIB dijalankan SEBELUM menyatakan mesin "aman".
LULUS/GAGAL ditentukan dari EXIT CODE (0 = aman) — JANGAN grep teks
(teks "GAGAL" juga muncul di ringkasan "0 GAGAL").
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent
PY = DIR / ".venv" / "bin" / "python3"

# ── BATAS KERAS WAKTU PER GRUP (Bos 20Sep26) ──────────────────────────────
# Sebelumnya TIDAK ADA batas → satu grup menggantung = gerbang menunggu
# selamanya (inilah akar gerbang terasa "lama banget"). 150 detik dipilih
# karena grup terberat (browser/grafik) terukur selesai < 105 detik.
BATAS_GRUP = 150

# ── KODE "LEWAT" — aku tidak bisa jalan, tapi MESIN tidak salah ───────────
# Dipakai uji yang bergantung PRASARANA (Chrome CDP :9333, dsb). Kalau
# prasarana mati, uji keluar dengan kode ini, BUKAN 1 — supaya gerbang
# TIDAK melaporkannya sebagai "GAGAL" (yang bikin Wulan mengejar bug
# aplikasi yang tidak ada). Kejadian nyata 21Sep26: Chrome mati → 7 grup
# dilaporkan GAGAL, padahal mesin sama sekali tidak tersentuh.
KODE_LEWAT = 77

# (nama, berkas, catatan) — urut dari yang paling penting
UJI = [
    # ⚠️ URUTAN PERTAMA = pemeriksa SOT. Kalau dokumen tidak cocok dengan kode,
    # uji lainnya tidak ada artinya — dokumen yang berbohong jadi sumber
    # kesalahan berikutnya (arahan Bos: "tetap prinsip SOT").
    ("SOT — dokumen selaras dengan kode", "sot.py",
     "--periksa"),
    ("INTI — semua model", "uji_kalibrasi_jalur.py",
     "regresi, mediasi, dual mediasi, berjenjang, model jurnal Bos"),
    ("MODEL JURNAL BOS", "uji_jurnal.py",
     "9 konstruk / 12 hipotesis / 4 tingkat / 1 jalur NH"),
    ("PENUTUP — 2 mode + sampel kecil", "uji_penutup.py",
     "Presisi vs Natural + n=50/100/150/200"),
    ("KELAYAKAN SETELAN", "uji_kelayakan.py",
     "R², VIF/multikolinearitas, saran β wajar, sampel kecil"),
    ("MODEL LANJUTAN", "uji_model_lanjutan.py",
     "multi-group, formatif, second-order (HOC), medmod 2 moderator"),
    ("WEB — 1-8 VARIABEL + NAMA + n=2000", "uji_variabel.py",
     "variabel 1-8, nama dari user, berkas unduhan, batas jaga"),
    ("TEMPLATE — semua template Jinja bisa di-compile", "gerbang_jinja.py",
     "template gagal compile = halaman HTTP 500; gerbang lain tak menyentuh Jinja"),
    ("TEMPLATE — tag penutup di dalam <script>", "gerbang_tag_skrip.py",
     "cegah skrip tumpah jadi teks (bug '<div>' mentah di dalam string JS)"),
    ("WEB — galat JavaScript di halaman", "gerbang_galat_js.py",
     "SyntaxError/TypeError mematikan skrip padahal HTTP 200 tetap hijau"),
    ("WEB — kode tumpah jadi teks (halaman nyata)", "gerbang_kode_tumpah.py",
     "buka halaman & baca teks yang TERLIHAT user — berkas benar != halaman benar"),
    ("WEB — tata letak kontrol (geometri)", "gerbang_tata_letak.py",
     "tombol −/+ sejajar, preset sebaris, tidak keluar layar"),
    ("WEB — lingkaran tak berujung antar-fungsi", "gerbang_lingkaran.py",
     "fungsi saling memanggil → tiap geseran slider membangun ulang tabel (HP macet)"),
    ("WEB — istilah tidak jelas di teks user", "gerbang_bahasa.py",
     "istilah karangan (pagar/ramalan) bikin user bertanya"),
    ("MESIN — 10 bentuk model (med.iasi, mode.rasi, gabungan)",
     "audit_mesin.py", ["10 LULUS / 0 GAGAL"]),
    ("MESIN — cara menguji: sederhana vs berganda", "uji_cara.py",
     "3 X diuji sendiri-sendiri ATAU bersama-sama; jumlah X tidak mengunci"),
    ("WEB — slider: kenop muat & keterangan tidak menempel", "gerbang_slider.py",
     "kenop meluber keluar kotak / teks menumpuk di garis slider"),
    ("WEB — teks terpotong di tengah kata & label slider melayang",
     "gerbang_teks_terpotong.py",
     "teks flex terpotong / label ujung slider loncat ke tengah"),
    # ⚠️ DITAMBAHKAN 19Sep26 (TAHAP 1.3) — MENGAPA ADA: gerbang di atas menguji
    # HALAMAN SATU-SATU, tapi tidak ada yang menguji JALUR KLIK kartu induk →
    # sub-pilihan → tautan model. Terukur 19Sep26: 46 uji (Regresi 3 sub +
    # Mediasi 4 sub + Moderasi 6 sub + geometri 346×224px di HP 390).
    ("WEB — sub-pilihan model (Regresi/Mediasi/Moderasi)",
     "uji_sub_regresi.py",
     "klik kartu induk → sub muncul → tautan benar → tombol kembali"),
    # ⚠️ DITAMBAHKAN 19Sep26 (TAHAP 1.4) — MENGAPA ADA: `ikon()` hanya
    # memvalidasi FORMAT nama, bukan keberadaannya di sprite. Ikon yang tidak
    # ada → <use href="#ik-..."> KOSONG tanpa galat apa pun (HTTP 200, konsol
    # bersih). Terukur 19Sep26: 8 ikon kosong sudah lama tersembunyi
    # (skull, clock×3, play-circle, calendar, history, message-square).
    ("WEB — nama ikon benar-benar ada di sprite", "gerbang_ikon.py",
     "ikon tak ada = elemen kosong tanpa galat (skull/clock/play-circle)"),

    # ⚠️ DITAMBAHKAN 20Sep26 (TAHAP 1.5) — MENGAPA ADA (akar terukur):
    # Sebuah `}` yang hilang di akhir entri KAMUS di belajar.html membuat
    # `SyntaxError: Unexpected identifier 'normalitas'`. Dampaknya BUKAN cuma
    # fitur baru mati — SELURUH 50.177 karakter skrip MATI, termasuk kamus
    # yang sudah jalan berbulan-bulan. Halaman tetap HTTP 200, konsol hanya
    # mencatat 404 favicon, dan TIDAK ADA gerbang lama yang menangkapnya:
    #   · gerbang_jinja.py       → template lolos (Jinja tak lihat JS)
    #   · gerbang_tag_skrip.py   → tag penutup HTML, bukan sintaks JS
    #   · gerbang_galat_js.py    → hanya berkas .js berdiri sendiri
    # Pelajaran lama terulang: "HTTP 200 + konsol bersih ≠ kode jalan".
    # Cara: RENDER template dulu (skrip inline berisi sintaks Jinja), baru
    # `node --check` tiap blok. Terbukti BISA GAGAL (dibuang 1 kurung →
    # EXIT 1).
    ("WEB — sintaks <script> inline setelah render Jinja",
     "gerbang_sintaks_js.py",
     "1 kurung hilang = SELURUH skrip mati walau HTTP 200 (20Sep26)"),

    # ⚠️ DITAMBAHKAN 20Sep26 (TAHAP 1.6) — MENGAPA ADA: entri kamus
    # `normalitas` punya RENTANG SENDIRI (−100…+100), sedangkan entri lain
    # 0…100. Kalau `pilih()` tidak menyetel min/max per-entri, normalitas
    # rusak ATAU entri lama ikut rusak. Uji ini menjaga DUA-DUANYA:
    # (a) normalitas dapat −100…+100, (b) 5 istilah lama TETAP 0…100.
    # Plus: tombol pintasan, kalimat penegas, kartu uji t, tidak meluber.
    ("WEB — normalitas (slider 2 arah) + pintasan hetero",
     "uji_normalitas.py",
     "rentang per-entri tidak merusak 5 istilah lama + kalimat penegas"),

    # ── 20-23. DIAGNOSIS DATA SPSS & PLS (19Sep26) ───────────────────────────
    # Alat "Diagnosis Data": unggah .sav/.csv/.xlsx → diagnosa → cara membetulkan.
    # 4 gerbang: (20) mesin, (21) nasihat, (22) jalur web, (23) alat ukur.
    ("DIAGNOSIS — mesin SPSS & PLS (6+5 uji)", "uji_diagnosis.py",
     "baca 3 format + 6 uji SPSS + 5 uji PLS + pagar berkas rusak"),
    ("DIAGNOSIS — teks 'cara membetulkan' 11 masalah", "uji_nasihat.py",
     "kelengkapan + bahasa HANGAT (larangan PERINGATAN/GAGAL/BAHAYA)"),
    ("DIAGNOSIS — jalur web (unggah → periksa → hasil)", "uji_web_diagnosis.py",
     "HTTP sungguhan: unggah csv/xlsx, SPSS bersih vs sakit, PLS, 5 pagar"),
    ("ALAT UKUR UJI — terbukti BISA GAGAL", "uji_alat_ukur.py",
     "suntik kerusakan (np.abs hilang, rng bersama) → HARUS tertangkap"),

    # ── 24-27. IDENTIFIKASI DATA: PERAN KOLOM → SKOR KONSTRUK (21Sep26) ──────
    # Mahasiswa menandai PERAN tiap kolom (X1=3 kolom) → digabung jadi SATU
    # skor sebelum dihitung. Aturan jawaban kosong = Opsi B (ACC Bos 21Sep26).
    ("PERAN — periksa penandaan + skor konstruk (murni)",
     "uji_peran_kolom.py",
     "5 cek mesin + skor_konstruk + penjaga tag mentah di string JS"),
    ("PERAN — skor konstruk: gabung kolom seperan", "uji_skor_konstruk.py",
     "X1=3 kolom → 1 skor · Opsi B (rata² terjawab × jumlah item)"),
    ("PERAN — rute web periksa-peran (HTTP sungguhan)",
     "uji_peran_web.py",
     "5 cek lewat HTTP + bentuk paralel/berjenjang + bukti bisa gagal"),
    ("PERAN — alur halaman: unggah → peran → Hasil", "uji_peran_alur.py",
     "Chrome CDP: 20 asersi, galat JS harus 0, hasil keluar"),
    ("PERAN — peran sampai ke MESIN sebagai skor konstruk",
     "uji_peran_skor_e2e.py",
     "unggah nyata: prediktor [X1,X2] BUKAN 5 kolom mentah · R² cocok"),
    # ⚠️ uji_tombol_contoh.py MASUK GERBANG 21Sep26 — sebelumnya TIDAK masuk,
    # dan itu menyembunyikan cacat uji usang (masih baca #baris-x/#kolom-y
    # yang sudah dihapus) selama berhari-hari → GAGAL PALSU tanpa ketahuan.
    ("PERAN — tombol Contoh (sehat/sakit) jalur mahasiswa",
     "uji_tombol_contoh.py",
     "klik tombol contoh → peran terisi, 3 grafik, penjaga bentuk lama"),
    # ⚠️ uji_mesin_s3.py MASUK GERBANG 21Sep26 — dulu TIDAK masuk DAN salah
    # ukur (memanggil fungsi internal dgn koreksi_atenuasi=False). Akibatnya
    # Wulan 1× SALAH LAPOR ke Bos bahwa mesin rantai cacat (lihat K-09).
    # Kini diukur dari PINTU PRODUKSI buat_data() → galat 0,0003–0,0083.
    ("MESIN — S3 berantai (rantai antar-X) dari pintu produksi",
     "uji_mesin_s3.py",
     "ukur lewat buat_data(): rantai X1->X2->X3 galat < 0,0083"),

    # ══════════════════════════════════════════════════════════════════════
    # MEDIASI & MODERASI (ACC Bos 21Sep26, putusan 1b+2a+3a)
    # ══════════════════════════════════════════════════════════════════════
    # MENGAPA 2 GRUP (bukan 1): dua lapisan yang rusaknya TIDAK saling
    # tertangkap — sudah terbukti 21Sep26:
    #   (a) MESIN (kaitan.py): kalau rumus mediasi/moderasi salah, uji pintu
    #       bisa lolos kalau datanya derau. Uji murni menanam koefisien yang
    #       DIKETAHUI (a=0,60 · b=0,50 · interaksi=0,35) → mesin wajib
    #       menemukan kebenaran itu.
    #   (b) PINTU (rute /klinik): dulu M dijejalkan jadi prediktor biasa dan
    #       Z DIBUANG TOTAL. Mesinnya benar, tapi halaman tidak pernah
    #       memanggilnya → mahasiswa dapat hasil kosong. Cacat ini LOLOS
    #       berhari-hari karena tak ada uji yang lewat pintu ini.
    #       Lihat TEMUAN_MEDIASI_MODERASI_21SEP2026.md + fact_store 108/109.
    ("KAITAN — mediasi & moderasi, mesin murni (koefisien ditanam)",
     "uji_kaitan.py",
     "bootstrap a×b · interaksi X×Z · penuh/parsial/tidak ada · bisa gagal"),
    ("KAITAN — mediasi & moderasi SAMPAI KE HASIL lewat pintu produksi",
     "uji_kaitan_web.py",
     "unggah .csv → peran → Hasil: jalur a, a×b, Z, interaksi keluar"),
    # ⚠️ MEDIASI BERJENJANG (X → M1 → M2 → Y) — ACC Bos 21Sep26.
    # Dua lapisan lagi, karena berjenjang punya cara rusak SENDIRI:
    #   (a) rumusnya beda (a1×b1 dan a1×d×b2, dua jalur tumpang-tindih),
    #   (b) bentuk 'berjenjang' harus SAMPAI dari halaman ke mesin —
    #       kalau hilang, mesin diam-diam jatuh ke paralel (terbukti:
    #       dibuang → 4 kegagalan ditangkap).
    ("KAITAN — mediasi BERJENJANG mesin murni (X→M1→M2→Y)",
     "uji_berjenjang.py",
     "tanam a1/d/b2 → mesin temukan · jalur terputus terbaca jujur"),
    ("KAITAN — mediasi berjenjang sampai ke HASIL lewat pintu produksi",
     "uji_berjenjang_web.py",
     "bentuk='berjenjang' dari halaman → 2 jalur tidak langsung keluar"),
    # ⚠️ RANTAI >2 PERANTARA — ACC Bos 21Sep26: "Rantai lebih 2 perantara
    # belum". Sebelum ini mediasi berjenjang HANYA menghitung 2 perantara
    # pertama (sisanya cuma diberi catatan "belum"). Sekarang mediasi_rantai()
    # menghitung SEMUA k perantara → k jalur tidak langsung.
    # Terbukti bisa gagal: cacat lama dikembalikan → 6 kegagalan ditangkap.
    ("KAITAN — rantai PANJANG >2 perantara mesin murni (3 & 4 perantara)",
     "uji_rantai.py",
     "jalur 3 = a1·d1·d2·b3 · rantai putus di tengah terbaca jujur"),
    ("KAITAN — rantai panjang >2 perantara sampai ke HASIL (pintu produksi)",
     "uji_rantai_web.py",
     "3 perantara → 3 jalur · 4 perantara → 4 jalur (dulu cuma 2)"),
    # ⚠️ BANYAK X — ACC Bos 21Sep26 ("Semua x masuk")
    ("KAITAN — banyak X masuk mediasi & moderasi (kovariat dikendalikan)",
     "uji_banyak_x.py",
     "X2..Xk dikendalikan · X1 bergeser saat X2 masuk (p signifikan→tidak)"),
    ("KAITAN — banyak X & banyak Y lewat PINTU PRODUKSI",
     "uji_ukur_xmy_banyak.py",
     "3X+2M+2Y lewat unggah→peran→Hasil (bukan fungsi internal)"),
    # ⚠️ BANYAK Z — OPSI A ACC Bos 21Sep26 (Z lain dikendalikan)
    ("KAITAN — moderasi banyak X & banyak Z (Opsi A: Z lain dikendalikan)",
     "uji_moderasi_banyak.py",
     "Z1 bergeser saat Z2 dikendalikan · Z1a/Z1b digabung jadi 1 moderator"),
    ("KAITAN — moderasi lewat HALAMAN SUNGGUHAN (jalur mahasiswa)",
     "uji_moderasi_halaman.py",
     "Chrome: unggah → tandai X/Z/Y → periksa → kartu moderasi muncul"),
    # ⚠️ MANOVA — ACC Bos 21Sep26: "Ok buka untuk manova". Ruang yang dipesan
    # 19Sep26 (RUANG_MANOVA.md) sudah dibuka. Kartu ke-5 = "Banding Kelompok".
    ("MANOVA — banding kelompok (mesin uji + pembangun data berkelompok)",
     "uji_manova.py",
     "SSCP · Wilks/Pillai/Hotelling/Roy · F&p · ANOVA per-Y · asumsi · pagar"),
    # ⚠️ KOMBINASI — jawab "bisa kombinasi apa saja?" dengan UKURAN, bukan klaim
    ("KOMBINASI — banyak X+M+Z+Y & campuran mediasi+moderasi",
     "uji_kombinasi.py",
     "9 kombinasi terukur lewat pintu produksi (peran, bukan kolom mentah)"),
    # ⚠️ MANOVA LEWAT HALAMAN — pelajaran K-18 (21Sep26): uji lewat API
    # langsung MENYEMBUNYIKAN cacat jalur halaman (dulu uji moderasi LULUS
    # padahal halaman tak pernah mengirim kolom_z). Karena itu MANOVA diuji
    # seperti mahasiswa memakainya: buka halaman → isi → klik → lihat hasil.
    # Terbukti BERGIGI: rute sengaja tidak mengirim 'isi_kelompok' → EXIT 1.
    ("MANOVA — lewat HALAMAN sungguhan (Chrome CDP)",
     "uji_manova_halaman.py",
     "panel muncul · klik → hasil tampil · n berupa angka · pagar ramah"),
    # ⚠️ BANYAK X — ACC Bos 21Sep26: "Semua x masuk". Sebelum ini mediasi &
    # moderasi memakai `kolom_x[0]` saja → X2, X3 DIBUANG DIAM-DIAM dan
    # hasilnya kelihatan sah. Terukur: kaitan.mediasi[0].x = "X1".
    # Sekarang X2..Xk masuk sebagai kovariat yang DIKENDALIKAN.
    # Bukti telak: p jalur a X1 bergeser 0,057 → 0,387 setelah X2 masuk.
    # Terbukti bisa gagal: `kolom_x[0]` dikembalikan → 6 kegagalan ditangkap.
    ("KAITAN — SEMUA X masuk (banyak X), mesin murni",
     "uji_banyak_x.py",
     "x_semua=['X1','X2','X3'] · 1 X tetap sama persis (tidak merusak lama)"),
    ("KAITAN — banyak X + banyak M + banyak Y (+Z) sampai ke HASIL",
     "uji_ukur_xmy_banyak.py",
     "3X+2M+1Y · 3X+1M+3Y · 3X+2M+2Y+Z — prediktor & kaitan utuh"),

    # ══════════════════════════════════════════════════════════════════════
    # 24-27. TAHAP 2 — GRAFIK HIDUP (20Sep26, ACC Bos)
    # ══════════════════════════════════════════════════════════════════════
    # MENGAPA 4 GRUP, BUKAN 1: Tahap 2 menyentuh EMPAT lapisan yang berbeda,
    # dan tiap lapisan punya cara rusak yang TIDAK tertangkap oleh lapisan
    # lain (semua sudah terukur nyata 20Sep26):
    #
    #   (24) MESIN — bahan gambar (titik.pp/hist/xy/zpred/zresid) dihitung
    #        dari angka yang sudah ada. Kalau bahan hilang, halaman
    #        kehilangan grafiknya TANPA galat apa pun (tidak ada yang
    #        error — grafiknya cuma tidak muncul).
    #   (25) FUNGSI GAMBAR — grafik_hidup.js (SVG dari data). Diuji lewat
    #        Node memakai FUNGSI SUNGGUHAN (fs.readFileSync), bukan salinan.
    #        ⚠️ JEBAKAN NODE: `(0, eval)` TIDAK membocorkan `const`
    #        (BATAS_TITIK → undefined) — yang jalan `vm.runInThisContext`
    #        + ekspor eksplisit ke globalThis.
    #   (26) HALAMAN — apakah grafiknya SAMPAI ke /klinik lewat jalur API
    #        (unggah → periksa), termasuk `kunci` sesi yang WAJIB dikirim.
    #   (27) JALUR MAHASISWA + TAB — menekan tombol contoh & tab seperti
    #        mahasiswa. Ini yang menangkap cacat NYATA 20Sep26:
    #        · bug LAMA `n is not defined` (halaman mati jadi "Koneksi
    #          terputus" setiap habis unggah — ada SEBELUM Tahap 2);
    #        · `#}` dipakai sebagai penutup komentar JS → 1 komentar tak
    #          tertutup → SELURUH 26.716 byte skrip MATI;
    #        · "/syarat duplikat" — 7 kartu pindah ke BELAJAR tab "Baca
    #          Grafik", /syarat DIALIHKAN (308) supaya tautan lama hidup.
    ("GRAFIK — bahan gambar dari mesin (P-P, histogram, scatter)",
     "uji_bahan_gambar.py",
     "bahan hilang = grafik hilang TANPA galat; corong eksponensial (p=0,0000)"),
    ("GRAFIK — fungsi SVG dari data (24 pemeriksaan)",
     "uji_grafik_hidup.js",
     "petakan/indeksSebar: titik menjebol bingkai & pasangan tertukar (20Sep26)"),
    ("GRAFIK — sampai ke halaman /klinik (jalur API)",
     "uji_web_grafik.py",
     "unggah → periksa; `kunci` sesi WAJIB dikirim (tanpa itu HTTP 400)"),
    ("GRAFIK — tombol contoh + tab Baca Grafik (jalur mahasiswa)",
     "uji_tab_baca_grafik.py",
     "KAMUS GRAFIK keluar dari menu · /syarat 308 → /belajar#tab-3 · 7 kartu"),
    ("PLS — Fornell-Larcker + HTMT (rumusnya, fungsi ASLI)",
     "uji_fornell_htmt.py",
     "data KEMBAR harus tertangkap (HTMT > 0,85); 1 konstruk & 1 butir tak meledak"),
    ("PLS — Fornell + HTMT sampai halaman /klinik (jalur API)",
     "uji_web_fornell_htmt.py",
     "unggah→periksa; `konstruk`=DICT {nama:[butir]} & `kolom_y_konstruk`=str"),

    # ⚠️ MENGAPA DIPISAH (aturan Bos 19Sep26: "GERBANG WAJIB DIUJI BISA GAGAL"):
    #    uji_alat_ukur.py menjaga MESIN statistik (np.abs hilang, rng bersama).
    #    Berkas ini menjaga BAHAN GAMBAR + FUNGSI GAMBAR — lapisan berbeda,
    #    cara rusak berbeda. Dijalankan PERTAMA kali, hasilnya 6 LULUS / 7
    #    GAGAL — SEMUANYA cacat uji Wulan (nama fungsi salah, tanda tangan
    #    salah, argumen ke-4 periksa_spss salah arti). Setelah dibetulkan:
    #    22 LULUS, dan TERBUKTI BERGIGI (4 kerusakan nyata → EXIT 1 semua).
    #    Uji yang tidak bisa gagal = tidak menjaga apa pun.
    ("GRAFIK — uji grafiknya sendiri terbukti BISA GAGAL",
     "uji_alat_ukur_grafik.py",
     "suntik: petakan dibalik · pasangan dipisah · batas jaga hilang · warna tertukar"),

    # ══════════════════════════════════════════════════════════════════════
    # 28-30. UJI F + TABEL ANOVA (21Sep26, ACC Bos Langkah 2 keputusan N1)
    # ══════════════════════════════════════════════════════════════════════
    # MENGAPA 3 GRUP: menyentuh 3 lapisan berbeda, cara rusaknya berbeda:
    #   (28) RUMUS  — uji_f() di mesin. Dibandingkan KEBENARAN LUAR (scipy).
    #   (29) GIGI   — uji (28) terbukti BISA GAGAL lewat suntikan kerusakan.
    #   (30) HALAMAN— tabel ANOVA benar-benar RENDER di /buat-data.
    #
    # ⚠️ PELAJARAN TERUKUR 21Sep26 (dua-duanya hampir lolos):
    #   (a) Versi PERTAMA uji (28) hanya memeriksa keajegan INTERNAL
    #       (SS_regresi+SS_residu=SS_total, MS=SS/df, F=MS/MS). Uji seperti
    #       itu BUTA: rumus dibalik & df salah TETAP konsisten internal →
    #       4 suntikan LOLOS semua. FIX: bandingkan dengan scipy.
    #   (b) `sys.path.insert(0, '/jalur/ABSOLUT')` membuat uji dari SALINAN
    #       tersuntik tetap membaca berkas ASLI → suntikan MUSTAHIL
    #       tertangkap. FIX: jalur dari Path(__file__).resolve().
    #   (c) `innerText` TIDAK memuat teks <th> → uji menuntut /SS/ & /MS/
    #       pada innerText = GAGAL PALSU. FIX: baca struktur (th + td).
    ("MESIN — uji F + tabel ANOVA (dibandingkan scipy, sumber LUAR)",
     "_sketsa/uji_uji_f.py",
     "F/p/SS/df/MS mesin == scipy; 1 X: F == t^2 (hukum statistik)"),
    ("MESIN — uji F terbukti BISA GAGAL (suntik 4 kerusakan rumus)",
     "_sketsa/bukti_uji_f_gagal.py",
     "df salah · F dibalik · SS salah · R2 kebalik → HARUS tertangkap"),
    ("HALAMAN — tabel ANOVA sampai ke /buat-data (jalur mahasiswa)",
     "uji_web_anova.py",
     "kartu ② = parsial (uji t) + simultan (uji F); kartu ① punya uji F per-X"),

    # ══════════════════════════════════════════════════════════════════════
    # 31. PINTU — KARTU REGRESI (21Sep26, ACC Bos Langkah 3 keputusan N1+R1)
    # ══════════════════════════════════════════════════════════════════════
    # ⚠️ MENGAPA GRUP TERSENDIRI: menyentuh HALAMAN PILIH (bukan mesin hitung).
    #    Cara rusaknya beda: kartu "berantai" hidup lagi, atau istilah
    #    Parsial/Simultan hilang dari judul — mesin tetap benar, gerbang mesin
    #    TIDAK menangkapnya.
    # ⚠️ TERBUKTI BERGIGI 5 ARAH setelah 3 PUTARAN perbaikan penjaga:
    #    (i)   cek "ada kata Parsial di berkas" → LOLOS (kata itu ada di komentar)
    #    (ii)  cek "ada di salah satu judul" → LOLOS (kartu ② juga memuat
    #          kata "Parsial" di "Berganda (Parsial + Simultan)")
    #    (iii) ukur JUDUL PER KARTU (data-cara=) → BARU tertangkap.
    #    ATURAN: ukur hal yang BENAR-BENAR dimaksud, jangan "ada kata".
    ("PINTU — penjaga kartu regresi terbukti BISA GAGAL",
     "_sketsa/bukti_penjaga_kartu.py",
     "5 suntikan: berantai hidup lagi/dihapus · mesin dibongkar · istilah hilang"),

    ("PINTU — kartu ①② terbukti di HALAMAN (jalur nyata user)",
     "uji_web_pintu.py",
     "⚠️ lewat ?model= (bukan /buat-data polos — halaman SENGAJA redirect)"),
]


def main() -> int:
    if not PY.exists():
        print(f'❌ Python venv tidak ada: {PY}')
        print('   Buat dulu: uv venv .venv && uv pip install numpy scipy pandas')
        return 2

    # Berkas uji .js dijalankan dengan node (bukan Python). Dicari lewat
    # shutil.which — sama seperti gerbang_sintaks_js.py, supaya tidak
    # mengarang jalur.
    node = shutil.which('node')

    print('=' * 74)
    print(' GERBANG UJI — Penelitian STATISTIK Lab.')
    print('=' * 74)
    print()

    hasil = []
    for nama, berkas, catatan in UJI:
        jalur = DIR / berkas
        if not jalur.exists():
            print(f'⚠️  LEWAT  {nama} — berkas {berkas} tidak ada')
            hasil.append((nama, None, 'tidak ada'))
            continue
        print(f'▶  {nama}')
        print(f'   ({catatan})')
        t0 = time.time()
        # Uji berakhiran .js dijalankan dengan NODE, sisanya dengan Python venv.
        # ⚠️ MENGAPA: uji_grafik_hidup.js menguji FUNGSI SUNGGUHAN dari
        # app/static/grafik_hidup.js (fs.readFileSync + vm.runInThisContext).
        # Dijalankan dengan Python akan gagal dengan galat sintaks Python yang
        # menyesatkan — bukan karena grafiknya rusak.
        if jalur.suffix == '.js':
            if not node:
                print(f'   ⚠️  LEWAT — node tidak ada, {berkas} tidak bisa dijalankan')
                hasil.append((nama, None, 'node tidak ada'))
                print()
                continue
            perintah = [node, str(jalur)]
        else:
            perintah = [str(PY), str(jalur)]
        # ── ATURAN KERAS: TIAP GRUP PUNYA BATAS WAKTU (Bos 20Sep26) ────────
        # ⚠️ AKAR cacat LAMA: `subprocess.run(...)` TANPA `timeout=` → kalau
        # satu grup menggantung, GERBANG MENUNGGU TANPA BATAS. Itu sebabnya
        # gerbang terasa "lama banget" dan Wulan mengulang-ulang.
        # Sekarang: grup yang lewat batas DIHENTIKAN dan dihitung GAGAL,
        # dengan pesan jujur — bukan menggantung selamanya.
        # Batas 150 dtk: grup terberat (browser/grafik) terukur < 105 dtk.
        try:
            p = subprocess.run(perintah, cwd=str(DIR), capture_output=True,
                               text=True, timeout=BATAS_GRUP)
            kode, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as e:
            dt = time.time() - t0
            print(f'   GAGAL  ({dt:.1f} detik)  ⏱️ LEWAT BATAS {BATAS_GRUP} detik')
            print(f'   --- grup ini MENGGANTUNG (tidak selesai dalam {BATAS_GRUP} detik) ---')
            ekor = (e.stdout or b'').decode('utf-8', 'replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
            for baris in ekor.splitlines()[-10:]:
                print('   ' + baris)
            print()
            hasil.append((nama, 124, 'TIMEOUT'))
            continue
        dt = time.time() - t0
        # ringkasan baris terakhir yang memuat LULUS/GAGAL
        ringkas = ''
        for baris in reversed(out.splitlines()):
            if 'LULUS' in baris and 'GAGAL' in baris:
                ringkas = baris.strip()
                break
        status = 'LULUS' if kode == 0 else 'GAGAL'
        print(f'   {status}  ({dt:.1f} detik)  {ringkas}')
        if kode != 0:
            print('   --- 20 baris terakhir keluaran ---')
            for baris in out.splitlines()[-20:]:
                print('   ' + baris)
            if err.strip():
                print('   --- galat ---')
                for baris in err.strip().splitlines()[-10:]:
                    print('   ' + baris)
        print()
        hasil.append((nama, kode, ringkas))

    print('=' * 74)
    print(' RINGKASAN')
    print('=' * 74)
    gagal = 0
    lewat = 0
    for nama, rc, ringkas in hasil:
        if rc is None:
            tanda = '⚠️  LEWAT'
            lewat += 1
        elif rc == 0:
            tanda = '✅ LULUS'
        elif rc == KODE_LEWAT:
            # Uji sendiri yang bilang "aku tidak bisa jalan" (mis. Chrome CDP
            # mati). Itu PRASARANA, bukan mesin — JANGAN dihitung GAGAL.
            # (Terukur 21Sep26: Chrome mati → 7 grup dihitung GAGAL → Wulan
            # mengejar bug aplikasi yang tidak ada.)
            tanda = '⏭️  LEWAT  (prasarana — lihat pesan di atas)'
            lewat += 1
        else:
            tanda = '❌ GAGAL'
            gagal += 1
        print(f'  {tanda}  {nama}  {ringkas}')
    print()
    if gagal == 0:
        print(f'  SEMUA LULUS — mesin aman ({len(hasil)} grup uji'
              + (f' · {lewat} lewat karena prasarana' if lewat else '') + ')')
    else:
        print(f'  {gagal} GRUP GAGAL — JANGAN deploy, perbaiki dulu')
        if lewat:
            print(f'  ({lewat} grup lain LEWAT karena prasarana, tidak dihitung gagal)')
    print()
    return 0 if gagal == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
