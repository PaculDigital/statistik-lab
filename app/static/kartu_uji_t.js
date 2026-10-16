/* ══════════════════════════════════════════════════════════════
   DATA KARTU UJI t — dibangkitkan dari _sketsa/data_uji_t.py
   JANGAN diubah manual: ubah sumbernya lalu jalankan ulang.
   ACC Bos 18Sep26 (3 lapis). Alasan dipisah dari belajar.html:
   datanya besar, supaya berkas templat tetap mudah dirawat.
   ══════════════════════════════════════════════════════════ */
const UJI_T = {
"hasil": [
{
"kunci": "sig-plus",
"nama": "Ada pengaruh, searah dugaan",
"nilai": "Sig. 0,008 · B +0,368",
"kelas": "hijau",
"label": "DITERIMA",
"naik": true,
"kabar": "Hasilmu sesuai dugaan.",
"arti": "Angka Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>, bukan kebetulan. Tanda plus artinya arahnya <b>sama</b> dengan yang kamu duga.",
"benar": "Promosi berpengaruh positif dan signifikan terhadap kepuasan (B&nbsp;=&nbsp;0,368; Sig.&nbsp;=&nbsp;0,008). Artinya, semakin gencar promosi, semakin tinggi kepuasan konsumen. Hipotesis diterima.",
"salah": null,
"sebab": [
[
"Hasilnya memang seperti dugaan",
"Tidak ada yang perlu diperbaiki.",
"Lanjutkan ke pembahasan dan kesimpulan.",
"sah"
]
],
"cek": [
"Sudah membaca ulang kalimat satu item kuisioner — nadanya sudah sesuai nama variabelnya?",
"Nilai Alpha Cronbach sudah di atas 0,70?",
"Jumlah responden sudah memenuhi rumus sampel di BAB III?"
]
},
{
"kunci": "sig-minus",
"nama": "Ada pengaruh, arah berlawanan",
"nilai": "Sig. 0,003 · B −0,412",
"kelas": "merah",
"label": "ADA TEMUAN",
"naik": false,
"kabar": "Jangan panik — ini temuan, bukan kesalahan.",
"arti": "Sig. di bawah 0,05 artinya pengaruhnya <b>nyata</b>. Tanda minus hanya menunjukkan <b>arahnya berlawanan</b> dengan dugaanmu. Dua hal ini terpisah: <i>\"ada tidaknya\"</i> dijawab Sig., <i>\"arahnya\"</i> dijawab tanda.",
"benar": "Harga berpengaruh signifikan negatif terhadap kepuasan (B&nbsp;=&nbsp;−0,412; Sig.&nbsp;=&nbsp;0,003). Artinya, semakin tinggi persepsi harga, semakin rendah kepuasan konsumen. Hasil ini berlawanan dengan hipotesis awal, dan diduga karena konsumen lebih peka terhadap harga pada produk sejenis.",
"salah": "Harga tidak berpengaruh terhadap kepuasan.",
"sebab": [
[
"Skala kuisioner terbalik",
"Item <i>\"harga produk ini mahal\"</i> diskor 5 = sangat setuju. Skor tinggi justru berarti kepuasan RENDAH.",
"Reverse coding (5→1, 4→2, 3→3), lalu hitung ulang. <b>Ini membetulkan yang memang salah sejak awal</b> — bukan mengubah hasil.",
"sah"
],
[
"Salah menentukan Y",
"Memakai <i>\"Ketidakpuasan\"</i> padahal seharusnya <i>\"Kepuasan\"</i>.",
"Perbaiki nama dan konsep variabel sesuai teori aslinya di BAB II.",
"sah"
],
[
"Multikolinearitas (VIF &gt; 10)",
"Dua X saling berkaitan sangat erat, sehingga X2 \"mencuri\" pengaruh X1 dan tandanya berputar.",
"Gabung atau sisihkan salah satu X — <b>dengan alasan teori yang kamu tulis di skripsi</b>, bukan karena hasilnya.",
"hati"
],
[
"Ada pencilan (data ekstrem)",
"Beberapa responden dengan pola jawaban jauh berbeda dari lainnya.",
"Buang <b>hanya kalau terbukti salah input atau jawaban asal</b> (lihat Box-Plot). Membuang data yang wajar hanya supaya tanda jadi plus — itu mencari-cari.",
"hati"
],
[
"Hipotesisnya memang berlawanan",
"Hubungan di lapangan memang berkebalikan, dan itu wajar.",
"<b>Tidak perlu diperbaiki.</b> Laporkan apa adanya lalu bahas sebabnya — penguji justru menghargai temuan seperti ini.",
"sah"
],
[
"Menghapus data sampai tandanya jadi plus",
"Membuang responden berulang kali sampai arahnya sesuai dugaan.",
"<b>Jangan.</b> Itu bukan memperbaiki, tapi membuat hasil — dan hasil seperti itu tidak bisa dipertanggungjawabkan.",
"curang"
]
],
"cek": [
"Baca ulang <b>kalimat setiap item</b> — ada yang bernada negatif (\"mahal\", \"lambat\", \"sulit\", \"sering mengeluh\")?",
"Cek <b>VIF</b> di tabel Coefficients — kalau di atas 10, tanda tidak bisa ditafsirkan dulu.",
"Buat <b>Box-Plot</b> — ada data ekstrem yang bukan wajar?",
"Pastikan Y sudah variabel yang benar (bukan kebalikannya).",
"Bicarakan dengan pembimbing <b>sebelum</b> mengubah apa pun."
]
},
{
"kunci": "marginal",
"nama": "Cenderung berpengaruh (marginal)",
"nilai": "Sig. 0,062 · B −0,380",
"kelas": "amber",
"label": "HATI-HATI",
"naik": false,
"kabar": "Hasilnya di batas — perlu dibahas, jangan dipaksa.",
"arti": "Sig. 0,062 berada <b>di atas 0,05</b> tapi belum jauh. Sebagian dosen menerima sampai 0,10, sebagian tidak. <b>Jangan menaikkan batas jadi 0,10 hanya supaya \"jadi signifikan\".</b>",
"benar": "Harga berpengaruh negatif terhadap kepuasan, namun belum mencapai signifikansi pada α&nbsp;=&nbsp;0,05 (B&nbsp;=&nbsp;−0,380; Sig.&nbsp;=&nbsp;0,062). Arah pengaruhnya sejalan dengan dugaan dan cenderung berpengaruh; disarankan menambah jumlah responden untuk memastikan.",
"salah": "Harga berpengaruh negatif signifikan terhadap kepuasan.",
"sebab": [
[
"Responden kurang",
"Dengan bukti yang sedikit, pengaruh yang sebenarnya ada pun bisa tampak tidak meyakinkan.",
"Tambah responden mengikuti <b>rumus sampel</b> yang sudah kamu tetapkan di BAB III.",
"sah"
],
[
"Alat ukur kurang tajam",
"Nilai Alpha Cronbach rendah, sehingga jawaban beragam tidak menggambarkan satu hal.",
"Rapikan kalimat item kuisioner, lalu ambil ulang data.",
"sah"
],
[
"Pengaruhnya memang kecil",
"Hubungannya lemah di lapangan, bukan soal jumlah data.",
"<b>Terima hasilnya.</b> Tulis apa adanya — itu jujur dan tetap dihargai penguji.",
"sah"
],
[
"Menaikkan batas α jadi 0,10 setelah melihat hasil",
"Menggeser batas <b>sesudah</b> tahu hasilnya, supaya lolos.",
"<b>Jangan.</b> Batas α harus ditetapkan di BAB III <i>sebelum</i> data dikumpulkan.",
"curang"
]
],
"cek": [
"Berapa <b>jumlah responden</b>mu, dan sudah memenuhi rumus sampel?",
"Berapa <b>Alpha Cronbach</b> tiap variabel?",
"Apakah <b>α = 0,05 sudah ditulis di BAB III sebelum</b> data dikumpulkan?",
"Yang kamu lakukan mengambil <b>data baru</b>, atau hanya menggeser batas?",
"Sudah minta pendapat pembimbing?"
]
},
{
"kunci": "tidaksig-plus",
"nama": "Tidak ada pengaruh (tanda plus)",
"nilai": "Sig. 0,142 · B +0,204",
"kelas": "abu",
"label": "TIDAK TERBUKTI",
"naik": true,
"kabar": "Tidak apa-apa — bukan berarti gagal.",
"arti": "Sig. di atas 0,05 artinya buktinya <b>belum cukup</b> untuk bilang ada pengaruh. <b>Penting:</b> kalau tidak signifikan, tandanya <b>tidak boleh ditafsirkan</b> — angka +0,204 itu bisa saja kebetulan.",
"benar": "Kualitas tidak terbukti berpengaruh nyata terhadap kepuasan (B&nbsp;=&nbsp;0,204; Sig.&nbsp;=&nbsp;0,142). Dengan demikian hipotesis tidak terbukti pada penelitian ini.",
"salah": "Kualitas berpengaruh positif tapi lemah terhadap kepuasan.",
"sebab": [
[
"Responden kurang",
"Bukti yang terkumpul belum cukup kuat untuk menyimpulkan ada pengaruh.",
"Tambah responden sesuai <b>rumus sampel</b>, dikumpulkan menurut sasaran yang sudah direncanakan.",
"sah"
],
[
"Pertanyaannya kurang menggigit",
"Item kuisioner terlalu umum, sehingga jawaban tidak menangkap pengaruh yang sebenarnya.",
"Perbaiki kalimat item, lalu ambil ulang data.",
"sah"
],
[
"Variabelnya memang tidak berpengaruh",
"Bisa jadi di objek penelitianmu, variabel itu memang bukan penentu.",
"<b>Laporkan apa adanya.</b> Ini tetap temuan yang sah dan bisa jadi bahan pembahasan.",
"sah"
],
[
"Menghapus data sampai Sig. &lt; 0,05",
"Membuang responden atau mengubah cara hitung berkali-kali sampai hasilnya lolos.",
"<b>Jangan.</b> Dalam penelitian ini disebut <i>p-hacking</i> — hasilnya jadi tidak bisa dipercaya.",
"curang"
],
[
"Mencoba banyak model, melaporkan yang lolos saja",
"Ganti-ganti susunan X sampai ada yang signifikan, lalu hanya yang lolos ditulis.",
"<b>Jangan.</b> Model ditentukan dari teori di BAB II, bukan dari hasil.",
"curang"
]
],
"cek": [
"Jumlah responden sudah memenuhi rumus sampel?",
"Alpha Cronbach tiap variabel di atas 0,70?",
"Susunan X dan Y mengikuti teori di BAB II, atau diubah setelah melihat hasil?",
"Kamu mengambil <b>data baru</b>, atau hanya menyortir data lama berulang kali?",
"Sudah dibahas dengan pembimbing?"
]
},
{
"kunci": "tidaksig-minus",
"nama": "Tidak ada pengaruh (tanda minus)",
"nilai": "Sig. 0,310 · B −0,115",
"kelas": "abu",
"label": "TIDAK TERBUKTI",
"naik": false,
"kabar": "Tandanya juga belum bisa dipakai.",
"arti": "Sig. di atas 0,05 = buktinya belum cukup. Tanda minusnya <b>juga tidak bisa ditafsirkan</b> — jangan menulis \"cenderung menurunkan\" kalau belum signifikan.",
"benar": "Tidak ada bukti yang cukup bahwa variabel ini berpengaruh terhadap kepuasan (B&nbsp;=&nbsp;−0,115; Sig.&nbsp;=&nbsp;0,310). Hipotesis tidak terbukti pada penelitian ini.",
"salah": "Variabel ini cenderung menurunkan kepuasan.",
"sebab": [
[
"Responden kurang",
"Bukti belum cukup kuat.",
"Tambah responden sesuai rumus sampel di BAB III.",
"sah"
],
[
"Memang tidak ada pengaruh",
"Di objek penelitian ini variabel tersebut bukan penentu.",
"Laporkan apa adanya dan bahas di pembahasan.",
"sah"
],
[
"Menyortir data sampai tandanya berubah",
"Mengubah susunan data supaya arahnya sesuai dugaan.",
"<b>Jangan.</b> Tanda tidak boleh \"dibuat\" — hanya boleh dilaporkan.",
"curang"
]
],
"cek": [
"Jumlah responden memenuhi rumus sampel?",
"Alpha Cronbach di atas 0,70?",
"Tidak ada data yang diubah atau dibuang setelah melihat hasil?",
"Sudah dibahas dengan pembimbing?"
]
}
],
"hack": [
[
"p-hacking",
"Membuang data atau mengubah cara hitung sampai Sig. &lt; 0,05"
],
[
"Menggeser batas α",
"Batas α diubah 0,05 → 0,10 <b>setelah</b> melihat hasil"
],
[
"Fishing",
"Mencoba banyak model, hanya yang lolos dilaporkan"
],
[
"HARKing",
"Hipotesis diubah <b>setelah</b> tahu hasilnya"
],
[
"Buang pencilan tanpa dasar",
"Membuang responden \"aneh\" hanya karena mengganggu hasil"
]
]
};
