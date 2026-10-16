"""NASIHAT — "cara membetulkan" untuk tiap masalah yang ditemukan diagnosis.

ACC Bos 19Sep26 (Opsi A): Wulan menulis sendiri, bahasa awam, gaya aplikasi.

⚠️ ATURAN BERKAS INI:
  · TIDAK mengimpor apa pun dari mesin. Murni teks.
  · Nada WAJIB mengingatkan, BUKAN menakutkan — DILARANG "PERINGATAN",
    "GAGAL", "BAHAYA". Mahasiswa sering salah paham statistik; yang
    dibutuhkan jalan keluar, bukan teguran.
  · Tiap nasihat WAJIB punya: (a) apa artinya dalam bahasa awam,
    (b) kenapa itu penting, (c) LANGKAH membetulkan (bernomor),
    (d) kapan boleh diabaikan.

KAMUS ISTILAH — pakai istilah baku berdampingan istilah ramah (aturan Bos):
  Heteroskedastisitas = sebaran sisa yang tidak rata
  Multikolinearitas   = X yang saling kembar
  Normalitas          = bentuk sebaran sisa
  Outlier             = data yang menyimpang jauh
  Autokorelasi        = sisa yang masih berhubungan dengan urutan
"""
from __future__ import annotations

# ══════════════════════════════════════════════════════════════════════════
# SPSS — 6 UJI
# ══════════════════════════════════════════════════════════════════════════

NORMALITAS = {
    'judul': 'Normalitas Sisa (bentuk sebaran sisa)',
    'arti': 'Sisa = selisih antara nilai asli dengan nilai yang diprediksi model. '
            'Normalitas artinya sisa-sisa itu menyebar merata di kedua sisi — '
            'tidak menumpuk di satu sisi saja.',
    'kenapa': 'Kalau sisa tidak normal, nilai p (tingkat signifikansi) bisa '
              'menyesatkan. Hipotesis yang sebenarnya berpengaruh bisa terlihat '
              'tidak berpengaruh, atau sebaliknya.',
    'boleh_abaikan': 'Pengujian tetap cukup tahan untuk sampel besar (n > 30 per '
                     'kelompok). Banyak pembimbing masih meminta, jadi lebih aman '
                     'tetap dilaporkan.',
    'langkah': [
        ('Cek dulu data yang menyimpang jauh (outlier).',
         'Outlier sering jadi penyebab utama sisa tidak normal. Periksa Box-Plot '
         'di menu Analisis Outlier, lalu putuskan: dibuang, atau tetap dipakai '
         'dengan alasan yang dicatat.'),
        ('Coba transformasi data.',
         'Kalau sebaran melenceng ke kanan, coba LG10 (log 10). Kalau melenceng '
         'ke kiri, coba akar kuadrat, atau balik dulu (1/x). Di SPSS: '
         'Transform → Compute Variable.'),
        ('Tambah jumlah responden kalau memungkinkan.',
         'Semakin banyak data, semakin normal bentuk sebarannya — ini efek '
         'teorema batas tengah, bukan trik.'),
        ('Kalau tetap tidak normal, laporkan apa adanya.',
         'Sebut di skripsi: "sisa tidak berdistribusi normal, namun jumlah '
         'sampel 120 memadai". Ini jujur dan diterima banyak pembimbing.'),
    ],
    'jangan': 'JANGAN menghapus data hanya supaya uji normalitas lolos. '
              'Itu mengubah kenyataan, bukan memperbaiki.',
}

HETERO = {
    'judul': 'Heteroskedastisitas (sebaran sisa yang tidak rata)',
    'arti': 'Disebut juga heteroskedastisitas. Bentuknya seperti corong: di nilai X '
            'kecil sisa-sisanya rapat, makin ke kanan makin melebar (atau sebaliknya).',
    'kenapa': 'Kalau sebaran sisa tidak rata, nilai p dan selang kepercayaan jadi '
              'tidak bisa dipegang. Kesimpulan hipotesis bisa berubah hanya karena '
              'beberapa titik yang sebarannya lebar.',
    'boleh_abaikan': 'Pada sampel besar, uji t masih cukup kuat walau ada '
                     'heteroskedastisitas ringan. Yang perlu diperhatikan justru '
                     'kalau corongnya sangat jelas — di situlah hasilnya mulai '
                     'bergantung pada sedikit titik.',
    'langkah': [
        ('Periksa datanya dulu, jangan langsung ditransformasi.',
         'Lihat menu Analisis Outlier. Satu-dua titik ekstrem sering jadi biang '
         'keroknya — membereskan itu lebih baik daripada mengubah semua data.'),
        ('Kalau sebaran miring, coba transformasi log.',
         'Transform → Compute Variable → LG10(namakolom). Cara paling umum dan '
         'paling diterima pembimbing.'),
        ('Kalau harus tetap pakai data asli, pakai galat baku tahan.',
         'Di SPSS: Analyze → Regression → Linear → Statistics → centang '
         '"Robust standard errors" (versi SPSS 27 ke atas). Cara ini TIDAK '
         'mengubah data, hanya cara menghitung nilai p-nya.'),
        ('Kalau memakai kuesioner, cek apakah butirnya bermasalah.',
         'Sering kali heteroskedastisitas muncul karena satu-dua butir '
         'pertanyaan jawabannya terlalu menumpuk di satu nilai.'),
    ],
    'jangan': 'JANGAN mengubah data lalu melaporkan angka aslinya. Kalau '
              'ditransformasi, tulis bahwa data ditransformasi.',
}

VIF = {
    'judul': 'Multikolinearitas (X yang saling kembar)',
    'arti': 'Multikolinearitas artinya beberapa variabel bebas (X) kamu saling '
            'berkaitan sangat erat. VIF mengukurnya: makin besar, makin kembar.',
    'kenapa': 'Kalau X saling kembar, model bingung menentukan mana yang '
              'berpengaruh. Koefisiennya bisa berpindah-pindah tanda — yang '
              'seharusnya positif malah jadi negatif.',
    'boleh_abaikan': 'VIF di bawah 5 umumnya aman. VIF 5–10 perlu diperhatikan. '
                     'Di atas 10 hampir selalu harus ditangani.',
    'langkah': [
        ('Lihat X mana yang VIF-nya paling besar.',
         'Tabel di atas sudah menunjukkan per variabel. Biasanya dua X yang '
         'nilainya mirip (misalnya "harga" dan "harga setelah diskon").'),
        ('Pilih SATU dari yang kembar, buang yang lain.',
         'Jangan pakai keduanya kalau memang mengukur hal yang sama. Ini '
         'keputusan berdasarkan teori, bukan angka — diskusikan dengan pembimbing.'),
        ('Kalau dua-duanya harus tetap ada, gabung jadi satu variabel.',
         'Misalnya jawaban responden untuk kedua variabel itu dijumlahkan lalu '
         'dirata-ratakan (di SPSS: Transform → Compute Variable → nilai rata-rata).'),
        ('Tambah jumlah responden.',
         'Multikolinearitas terasa lebih ringan pada sampel besar.'),
    ],
    'jangan': 'JANGAN membuang variabel hanya karena VIF tinggi, padahal menurut '
              'teori variabel itu penting. Multikolinearitas sering jadi temuan '
              'yang justru menarik untuk dibahas di skripsi.',
}

LINEARITAS = {
    'judul': 'Linearitas (hubungan X dan Y berbentuk garis lurus)',
    'arti': 'Model regresi mengandaikan hubungan X dan Y bisa digambar sebagai '
            'garis lurus. Kalau hubungannya melengkung, garis lurus tidak bisa '
            'mewakilinya dengan baik.',
    'kenapa': 'Kalau bentuknya melengkung tapi dipaksa garis lurus, model akan '
              'meleset di ujung-ujung, dan kesimpulan pengaruhnya jadi tidak akurat.',
    'boleh_abaikan': 'Kurang penting kalau titik-titiknya sudah menyebar acak di '
                     'sekitar garis. Pada data kuesioner (skala 1–5) penyimpangan '
                     'bentuk biasanya kecil.',
    'langkah': [
        ('Lihat dulu bentuk tebarannya.',
         'Buat Scatter Plot X dengan Y (Graphs → Legacy Dialogs → Scatter/Dot). '
         'Kalau titiknya membentuk lengkung yang jelas, linearitas bermasalah.'),
        ('Kalau lengkungnya melandai (melengkung lalu datar), tambahkan suku kuadrat.',
         'Uji dengan memasukkan X² sebagai variabel tambahan. Kalau X² signifikan, '
         'artinya bentuknya memang melengkung dan perlu dimodelkan begitu.'),
        ('Periksa apakah ada rentang nilai X yang terlalu menumpuk.',
         'Kalau hampir semua responden menjawab 4, tidak banyak bentuk yang bisa '
         'dibaca. Ini masalah rancangan kuesioner, bukan analisis.'),
        ('Pertimbangkan model lain kalau lengkungnya kuat.',
         'Untuk hubungan yang memang melengkung (misalnya kepuasan terhadap '
         'harga: naik sampai batas tertentu lalu turun), model kuadratik lebih tepat.'),
    ],
    'jangan': 'JANGAN melaporkan "hubungan linear" kalau tebarannya jelas melengkung.',
}

OUTLIER = {
    'judul': 'Data Menyimpang Jauh (outlier)',
    'arti': 'Outlier adalah jawaban responden yang jauh berbeda dari yang lain — '
            'misalnya semua orang menjawab 3–4, tapi satu orang menjawab 1 pada '
            'semua pertanyaan.',
    'kenapa': 'Satu-dua titik ekstrem bisa menarik garis regresi sehingga hasilnya '
              'berubah cukup banyak. Ini sering jadi penyebab heteroskedastisitas '
              'dan sisa yang tidak normal.',
    'boleh_abaikan': 'Kalau jumlahnya sedikit (di bawah 5%) dan tidak mengubah '
                     'kesimpulan, sering kali cukup dilaporkan saja.',
    'langkah': [
        ('Cari tahu SIAPA dan KENAPA, jangan langsung dibuang.',
         'Lihat nomor respondennya. Periksa jawabannya: apakah dia mengisi asal-asalan '
         '(semua nilai sama), atau memang punya pengalaman yang berbeda?'),
        ('Kalau pengisian jelas asal-asalan, buang dengan alasan tercatat.',
         'Contoh alasan yang sah: "responden menjawab nilai sama untuk seluruh '
         'butir". Tulis di skripsi berapa yang dibuang dan alasannya.'),
        ('Kalau jawabannya masuk akal, PERTAHANKAN.',
         'Responden yang tidak puas itu justru data berharga. Membuangnya membuat '
         'kesimpulanmu terlalu bagus dan tidak jujur.'),
        ('Coba analisis dua kali: dengan dan tanpa outlier.',
         'Kalau kesimpulannya sama, laporkan hasil dengan data lengkap. Kalau beda, '
         'bawa kedua hasilnya ke pembimbing.'),
    ],
    'jangan': 'JANGAN membuang outlier hanya supaya R² terlihat lebih bagus. '
              'Itu mengubah hasil penelitian, bukan memperbaikinya.',
}

DW = {
    'judul': 'Autokorelasi (sisa yang masih berhubungan dengan urutan)',
    'arti': 'Durbin-Watson mengukur apakah sisa dari satu responden berhubungan '
            'dengan responden berikutnya. Nilai sehatnya sekitar 2.',
    'kenapa': 'Autokorelasi terutama masalah pada data berurutan waktu (time series) '
              'atau data berkelompok. Pada kuesioner yang diisi bersamaan, '
              'autokorelasi jarang jadi masalah nyata.',
    'boleh_abaikan': 'Untuk data kuesioner lintas-responden (cross-section), '
                     'autokorelasi umumnya bisa diabaikan. Tetap laporkan nilainya '
                     'karena banyak pembimbing memintanya.',
    'langkah': [
        ('Pastikan dulu datanya memang berurutan waktu.',
         'Kalau data kuesioner biasa (tidak ada urutan waktu), autokorelasi '
         'bukan hal yang perlu dikhawatirkan. Sebutkan ini di skripsi.'),
        ('Kalau datanya memang deret waktu, periksa polanya.',
         'Buat plot sisa menurut urutan waktu. Kalau membentuk gelombang, '
         'autokorelasi memang ada.'),
        ('Pakai Cochrane-Orcutt atau bedakan data (differencing).',
         'Di SPSS: Analyze → Time Series → Create Models (versi 27 ke atas). '
         'Untuk skripsi sarjana, biasanya cukup dilaporkan dan dijelaskan.'),
        ('Tambah variabel yang mungkin terlewat.',
         'Autokorelasi sering muncul karena ada faktor penting yang belum masuk '
         'model — misalnya waktu, lokasi, atau kebijakan yang berubah.'),
    ],
    'jangan': 'JANGAN memaksa nilai Durbin-Watson masuk rentang 1,9–2,1 dengan '
              'cara mengubah urutan data. Itu memanipulasi hasil.',
}

# ══════════════════════════════════════════════════════════════════════════
# SmartPLS — 5 UJI
# ══════════════════════════════════════════════════════════════════════════

OUTER_LOADING = {
    'judul': 'Outer Loading (kekuatan tiap butir pertanyaan)',
    'arti': 'Outer loading mengukur seberapa kuat tiap butir pertanyaan mewakili '
            'variabel yang diukurnya. Kalau butirnya lemah, pertanyaan itu tidak '
            'benar-benar mengukur hal yang dimaksud.',
    'kenapa': 'Ini fondasi seluruh analisis PLS. Kalau butirnya lemah, semua angka '
              'di atasnya (AVE, jalur, hipotesis) ikut dipertanyakan.',
    'boleh_abaikan': 'Ambang yang umum: 0,7 (ketat) atau 0,6 (longgar, untuk '
                     'penelitian eksploratif). Di bawah 0,5 hampir selalu dibuang.',
    'langkah': [
        ('Lihat butir mana yang loadingnya di bawah ambang.',
         'Tabel di atas menampilkan per butir. Catat kode butirnya (misalnya KP3).'),
        ('Buang SATU butir dulu, hitung ulang.',
         'Jangan buang beberapa sekaligus — angkanya bisa berubah lagi setelah '
         'satu dibuang. Di SmartPLS: klik kanan butir → Delete.'),
        ('Periksa isi pertanyaannya, bukan cuma angkanya.',
         'Butir yang lemah biasanya kalimatnya bermakna ganda, atau sebenarnya '
         'mengukur hal lain. Perbaiki kalimatnya untuk penelitian berikutnya.'),
        ('Kalau butir yang lemah banyak, pertimbangkan model formatif.',
         'Kalau butir-butir memang mengukur DIMENSI berbeda (bukan hal yang sama), '
         'model reflektif tidak cocok — pakai formatif.'),
    ],
    'jangan': 'JANGAN membuang butir hanya karena angkanya rendah, tanpa memeriksa '
              'isinya. Butir yang penting secara teori wajib dipertahankan.',
}

AVE = {
    'judul': 'AVE — Validitas Konvergen',
    'arti': 'AVE mengukur seberapa banyak keragaman tiap butir yang bisa dijelaskan '
            'oleh variabelnya. Sederhananya: apakah butir-butirnya benar-benar '
            'mengumpul membentuk satu variabel.',
    'kenapa': 'Kalau AVE rendah, artinya butir-butirnya tidak kompak — variabel '
              'kamu sebenarnya mengukur lebih dari satu hal.',
    'boleh_abaikan': 'Ambang umum 0,5. Kalau Composite Reliability sudah di atas '
                     '0,7, AVE sedikit di bawah 0,5 masih sering diterima pembimbing.',
    'langkah': [
        ('Lihat butir dengan outer loading terendah dulu.',
         'AVE naik paling cepat dengan membuang butir yang loadingnya paling lemah. '
         'Satu butir biasanya cukup.'),
        ('Periksa apakah butir itu memang bermakna ganda.',
         'Misalnya pertanyaan "pelayanan cepat dan ramah" — itu dua hal dalam satu '
         'kalimat. Pecah jadi dua pertanyaan.'),
        ('Pertimbangkan memakai skor total kalau butirnya memang beragam.',
         'Kalau menurut teori butir-butirnya memang mengukur hal berbeda, '
         'model formatif lebih tepat daripada memaksa AVE naik.'),
    ],
    'jangan': 'JANGAN membuang butir sampai AVE naik, kalau yang tersisa tinggal '
              '2 butir. Variabel dengan 2 butir rawan bermasalah di tahap berikutnya.',
}

CR = {
    'judul': 'Composite Reliability (keandalan/konsistensi variabel)',
    'arti': 'Composite Reliability mengukur seberapa konsisten jawaban responden '
            'antar-butir dalam satu variabel. Mirip Cronbach Alpha, tapi lebih '
            'tepat untuk PLS.',
    'kenapa': 'Kalau keandalannya rendah, jawaban responden tidak bisa dipegang — '
              'variabel kamu tidak stabil mengukur apa yang dimaksud.',
    'boleh_abaikan': 'Ambang 0,7 untuk penelitian konfirmatori, 0,6 untuk '
                     'eksploratif. Di atas 0,95 justru dicurigai butirnya kembar.',
    'langkah': [
        ('Periksa dulu butir yang loadingnya rendah.',
         'Butir yang lemah menurunkan keandalan. Buang satu, hitung ulang.'),
        ('Periksa apakah ada butir yang kalimatnya hampir sama.',
         'Dua pertanyaan yang isinya sama persis membuat keandalan terlihat tinggi '
         'tapi palsu (butir kembar). Gabung jadi satu.'),
        ('Tambah jumlah butir kalau memang mengukur hal yang sama.',
         'Keandalan naik dengan jumlah butir yang setara, bukan dengan butir yang '
         'berbeda-beda.'),
    ],
    'jangan': 'JANGAN menambah butir hanya supaya angkanya naik, tanpa dasar teori.',
}

VIF_INNER = {
    'judul': 'VIF Inner (variabel yang saling berkaitan)',
    'arti': 'VIF Inner versi PLS dari multikolinearitas — mengukur apakah ada '
            'variabel yang saling berkaitan sangat erat di dalam model.',
    'kenapa': 'Kalau VIF tinggi, jalur pengaruh antar-variabel bisa berubah tanda '
              'atau tidak stabil — sama seperti masalah kembar di regresi.',
    'boleh_abaikan': 'Ambang 5. Di bawah 3 umumnya aman. Di antara 3–5 perlu '
                     'dilihat apakah modelnya masih masuk akal secara teori.',
    'langkah': [
        ('Lihat jalur mana yang VIF-nya paling besar.',
         'Tabel di atas menampilkan per variabel prediktor.'),
        ('Periksa apakah ada butir yang isinya tumpang tindih antar-variabel.',
         'Sering kali satu butir di variabel A isinya hampir sama dengan butir di '
         'variabel B. Pindahkan butir itu ke variabel yang paling tepat.'),
        ('Gabung variabel yang memang mengukur hal sama.',
         'Kalau dua variabel terbukti mengukur konsep yang sama, jadikan satu '
         'variabel — model jadi lebih sederhana dan kuat.'),
        ('Kurangi jumlah variabel prediktor.',
         'Terlalu banyak variabel yang saling berkaitan membuat model tidak stabil. '
         'Pilih yang paling penting menurut teori.'),
    ],
    'jangan': 'JANGAN menghapus variabel dari model tanpa dasar teori hanya karena '
              'angka VIF. Cek dulu isi butirnya.',
}

FORNELL = {
    'judul': 'Fornell-Larcker (variabel berbeda memang berbeda)',
    'arti': 'Uji ini memastikan tiap variabel lebih berkaitan dengan butirnya '
            'sendiri daripada dengan variabel lain. Kalau tidak, variabel-variabel '
            'kamu sebenarnya mengukur hal yang sama.',
    'kenapa': 'Ini penentu apakah model kamu layak ditafsirkan. Kalau variabelnya '
              'tumpang tindih, jalur pengaruh antar-variabel jadi tidak bermakna.',
    'boleh_abaikan': 'Dianggap lulus kalau akar(AVE) tiap variabel lebih besar dari '
                     'korelasi antar-variabel. Uji HTMT lebih ketat — dan '
                     'sudah tersedia di alat ini, lihat kartu HTMT di bawahnya.',
    'langkah': [
        ('Lihat pasangan variabel mana yang korelasinya terlalu tinggi.',
         'Umumnya di atas 0,85 antar-variabel sudah perlu diperiksa lebih teliti.'),
        ('Periksa isi butir pada PASANGAN yang bermasalah.',
         'Cari butir yang kalimatnya mirip antar-kedua variabel. Itu penyebab '
         'paling umum — bukan kesalahan hitung.'),
        ('Buang atau pindahkan butir yang tumpang tindih.',
         'Kalau butir lebih cocok mengukur variabel yang lain, pindahkan. '
         'Kalau memang berlebihan, buang.'),
        ('Kalau variabelnya memang satu konsep, gabung.',
         'Dua variabel yang saling berkorelasi di atas 0,9 sering kali sebenarnya '
         'satu variabel yang dipecah tanpa alasan kuat.'),
    ],
    'jangan': 'JANGAN melaporkan model sebagai "valid" hanya karena lulus '
              'Fornell-Larcker, padahal korelasinya sangat tinggi. Jelaskan.',
}

HTMT = {
    'judul': 'HTMT (dua variabel tidak boleh kembar)',
    'arti': 'HTMT mengukur seberapa mirip dua variabel. Kalau nilainya tinggi, '
            'dua variabel itu sebenarnya menanyakan hal yang hampir sama — '
            'responden menjawabnya nyaris sama.',
    'kenapa': 'Ini uji yang lebih ketat daripada Fornell-Larcker. Banyak skripsi '
              'lolos Fornell-Larcker tapi gagal HTMT, dan pembimbing yang teliti '
              'biasanya meminta angka ini. Tujuannya menjaga agar tiap variabel '
              'punya makna tersendiri.',
    'boleh_abaikan': 'Di bawah 0,85 sudah aman. Antara 0,85–0,90 masih diterima '
                     'dengan catatan (jelaskan di keterbatasan). Di atas 0,90 '
                     'sudah perlu diperbaiki. Kalau variabelmu memang dua sisi '
                     'dari satu konsep, gabung saja.',
    'langkah': [
        ('Lihat pasangan mana yang nilainya paling tinggi.',
         'Biasanya 1–2 pasangan saja yang bermasalah, tidak semua.'),
        ('Bandingkan kalimat butir pada pasangan itu.',
         'Cari dua butir dari variabel berbeda yang isinya hampir sama. '
         'Itu penyebab paling sering — bukan kesalahan hitung.'),
        ('Perbaiki kalimat butir yang tumpang tindih.',
         'Buat kalimatnya menanyakan hal yang jelas berbeda. Kalau butir itu '
         'lebih cocok mengukur variabel lain, pindahkan.'),
        ('Kalau memang satu konsep, gabungkan variabelnya.',
         'Dua variabel dengan HTMT di atas 0,95 hampir pasti satu konsep. '
         'Menggabung lebih jujur daripada memaksa memisah.'),
    ],
    'jangan': 'JANGAN menghapus butir hanya supaya angka HTMT turun. Itu '
              'menambal masalah, bukan membetulkan. Perbaiki kalimat butirnya '
              'atau gabung variabelnya.',
}

# ══════════════════════════════════════════════════════════════════════════
# PETA MASALAH → NASIHAT
# ══════════════════════════════════════════════════════════════════════════
SPSS = {
    'normalitas': NORMALITAS,
    'hetero': HETERO,
    'vif': VIF,
    'linearitas': LINEARITAS,
    'outlier': OUTLIER,
    'dw': DW,
}

PLS = {
    'outer_loading': OUTER_LOADING,
    'ave': AVE,
    'cr': CR,
    'vif_inner': VIF_INNER,
    'fornell': FORNELL,
    'htmt': HTMT,
}


def ambil(kode: str, mode: str = 'spss') -> dict | None:
    """Ambil nasihat berdasarkan kode masalah."""
    return (SPSS if mode == 'spss' else PLS).get(kode)


def semua(mode: str = 'spss') -> dict:
    return dict(SPSS if mode == 'spss' else PLS)


def daftar_kode(mode: str = 'spss') -> list[str]:
    return list((SPSS if mode == 'spss' else PLS).keys())
