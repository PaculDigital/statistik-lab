#!/usr/bin/env python3
"""Pindahkan <section kartu-ujit> KE DALAM .kamus-kisi (sejajar .papan).

⚠️ AKAR (19Sep26, keluhan Bos — VERBATIM):
   "kenapa di klik uji t, malah pindah ke bawah. Dia itu posisinya sama seperti
    tab tab disampingnya. Di klik muncul bukan jadi pindah ke bawah"

STRUKTUR (terukur dari berkas):
   baris  23: <div id="tab-1">
   baris  24: <div class="kamus-kisi renggang-b">
   baris  25:   <div class="kamus-daftar">   ← pita tombol istilah
   baris  35:   <div class="papan">          ← ISI KAMUS (berganti di tempat)
   baris  93:   </div>                       ← .papan DITUTUP
   baris  94: </div>                         ← .kamus-kisi DITUTUP
   baris 100: <section kartu-ujit>           ← DI LUAR ❌ (duduk di bawah)

⚠️ KESALAHAN WULAN SEBELUMNYA (jangan ulang):
   1. grep `class="kamus-kisi"` (persis) → TIDAK COCOK, karena kelasnya
      `kamus-kisi renggang-b` (dua kelas). Sampai Wulan salah simpul "kelasnya
      tidak ada" / "skrip menghapus pembukanya". GREP NAMA KELAS WAJIB PAKAI
      POLA LONGGAR: `kamus-kisi` tanpa `class="..."` penuh.
   2. Skrip versi pertama menebak titik sisip dari `"Di SPSS:"` → rapuh.

CARA BENAR (dipakai di sini): hitung KURUNG DIV dari titik <div id="tab-1">
   → cari </div> ke-2 (penutup .kamus-kisi) dengan penyeimbang.
"""
import pathlib

BERKAS = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CADANGAN = pathlib.Path('/tmp/belajar_cadangan6.html')


def utama():
    s = BERKAS.read_text(encoding='utf-8')
    CADANGAN.write_text(s, encoding='utf-8')
    print(f'cadangan → {CADANGAN} ({len(s)} byte)')

    # sanity: struktur awal
    for kata in ('kamus-kisi', 'kamus-daftar', 'kartu-ujit', 'tab-2'):
        n = s.count(kata)
        print(f'  {kata}: {n}×')
        if n == 0:
            print(f'❌ "{kata}" tidak ada — BATAL (jangan sentuh)')
            return

    # ── 1. potong blok <section kartu-ujit> … </section> beserta komentarnya ──
    awal_komentar = s.find('{# ⚠️ KARTU UJI t')
    if awal_komentar < 0:
        print('❌ tidak ketemu komentar penanda kartu uji t')
        return
    i0 = s.find('<section class="kartu-ujit"', awal_komentar)
    i1 = s.find('</section>', i0)
    if i0 < 0 or i1 < 0:
        print('❌ blok section tidak lengkap')
        return
    i1 += len('</section>')
    blok = s[awal_komentar:i1]
    print(f'blok dipotong: {len(blok)} byte (komentar+section)')

    sisa = s[:awal_komentar] + s[i1:]

    # ── 2. cari titik sisip dengan PENYEIMBANG DIV ──
    # dari <div id="tab-1">, hitung kedalaman div; sisip tepat SEBELUM </div>
    # yang menutup .kamus-kisi (yaitu </div> penutup pada kedalaman 2).
    t1 = sisa.find('<div id="tab-1"')
    if t1 < 0:
        print('❌ tidak ketemu <div id="tab-1">')
        return
    kedalaman = 0
    pos = t1
    titik_sisip = None
    while pos < len(sisa):
        buka = sisa.find('<div', pos)
        tutup = sisa.find('</div>', pos)
        if tutup < 0:
            break
        if buka >= 0 and buka < tutup:
            kedalaman += 1
            pos = buka + 4
        else:
            kedalaman -= 1
            if kedalaman == 1:          # baru menutup .kamus-kisi (anak ke-2 tab-1)
                titik_sisip = tutup
                break
            pos = tutup + 6
    if titik_sisip is None:
        print('❌ tidak ketemu titik sisip .kamus-kisi')
        return
    print(f'titik sisip: byte {titik_sisip} (sebelum </div> penutup .kamus-kisi)')

    # pastikan titik sisip memang di dalam .kamus-kisi (setelah kamus-daftar &
    # setelah .papan dibuka)
    before = sisa[:titik_sisip]
    if 'kamus-daftar' not in before or 'class="papan"' not in before:
        print('❌ titik sisip aneh — BATAL')
        return

    hasil = sisa[:titik_sisip] + '\n' + blok + '\n' + sisa[titik_sisip:]

    # ── 3. hapus gulir otomatis (tidak perlu lagi: kartu di tempat yang sama) ──
    hasil = hasil.replace('    bawaKeAtas(kartu);\n', '')
    hasil = hasil.replace('  bawaKeAtas(panelKamus);\n', '')
    hasil = hasil.replace('  const kotak = (elemen.closest', '  const kotak = (elemen.closest')

    BERKAS.write_text(hasil, encoding='utf-8')

    # ── VERIFIKASI ──
    print('\n── VERIFIKASI ──')
    print(f'  ukuran: {len(s)} → {len(hasil)} byte')
    print(f'  <script> {hasil.count("<script>")} / </script> {hasil.count("</script>")}')
    print(f'  <section {hasil.count("<section")} / </section> {hasil.count("</section>")}')
    print(f'  {{% block {hasil.count("{% block")} / {{% endblock {hasil.count("{% endblock")}')
    i_sec = hasil.find('<section class="kartu-ujit"')
    i_t2 = hasil.find('<div id="tab-2"')
    i_kisi = hasil.find('kamus-kisi')
    i_daftar = hasil.find('kamus-daftar')
    print(f'  posisi: kamus-kisi={i_kisi} · kamus-daftar={i_daftar} · '
          f'section={i_sec} · tab-2={i_t2}')
    print(f'  {"✅" if i_kisi < i_sec < i_t2 else "❌"} section SETELAH kamus-kisi '
          f'dan SEBELUM tab-2 (artinya DI DALAM tab-1)')


if __name__ == '__main__':
    utama()
