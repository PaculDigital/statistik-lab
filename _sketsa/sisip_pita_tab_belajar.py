#!/usr/bin/env python3
"""Sisipkan PITA TAB + kotak TAB 2 ke app/templates/belajar.html.

⚠️ ATURAN (pelajaran 19Sep26): JANGAN patch buta. Skrip penanda + cadangan +
   verifikasi ({ } seimbang, {% block %} seimbang, tag div berpasangan).

STRUKTUR SESUDAH (keputusan Bos 19Sep26: ①A · ③A):
  /belajar
  ├── pita tab  (Materi & Kamus | Ruang Uji)
  ├── TAB 1 — MATERI & KAMUS   = isi yang SEKARANG (tidak diubah isinya)
  └── TAB 2 — RUANG UJI        = 2 kartu (Rusak Data + Kuis Pilih Alat)

TAB 2 isinya SENGAJA masih "sedang disiapkan" — jujur, tidak menjanjikan palsu.
Isi asli Ruang Uji dikerjakan langkah berikutnya.

⚠️ JUDUL H1 DIUBAH: dulu "Kamus istilah, dengan slider" — terlalu sempit kalau
   halaman ini sekarang punya 2 tab. Diganti jadi lebih umum, TAPI teks tab 1
   tetap menyebut "Kamus" supaya user tahu tempatnya.
"""
import pathlib
import shutil

BERKAS = pathlib.Path('/opt/data/services/statistik-lab/app/templates/belajar.html')
CADANGAN = pathlib.Path('/tmp/belajar_html_cadangan.html')

TANDA = '<!-- ══════ PITA TAB (19Sep26) ══════ -->'

# ── 1. PITA TAB, disisipkan setelah header (sebelum .kamus-kisi) ──
PITA = TANDA + """
<div class="pita-tab" role="tablist">
  <a href="#tab-1" class="aktif" id="pa-1" role="tab" onclick="bukaTab(1);return false">
    {{ ikon('book-open', 15) }} Materi &amp; Kamus <span class="biji">9</span>
  </a>
  <a href="#tab-2" id="pa-2" role="tab" onclick="bukaTab(2);return false">
    {{ ikon('flask-conical', 15) }} Ruang Uji <span class="biji">2</span>
  </a>
</div>

<div id="tab-1" role="tabpanel">
"""

# ── 2. Penutup TAB 1 + TAB 2 ──
TAB2 = """</div><!-- /tab-1 -->

<div id="tab-2" role="tabpanel" hidden>
  <span class="eyebrow">{{ ikon('flask-conical', 13) }} RUANG UJI</span>
  <h1>Belajar dari yang rusak</h1>
  <p class="besar">
    Di sini kamu <strong>sengaja membuat data bermasalah</strong>, lalu menebak
    apa yang salah. Cara ini lebih melatih daripada melihat data yang selalu bagus.
  </p>

  <a class="kartu-alat" href="/klinik">
    <span class="ikon-alat">{{ ikon('flask-conical', 26) }}</span>
    <span class="isi-alat">
      <b>Rusak Data</b>
      <span>Geser satu tuas — lihat grafiknya rusak, lalu tebak apa yang salah
        dan bagaimana membetulkannya.</span>
    </span>
    <span class="panah">&rsaquo;</span>
  </a>

  <a class="kartu-alat" href="#">
    <span class="ikon-alat">{{ ikon('target', 26) }}</span>
    <span class="isi-alat">
      <b>Kuis Pilih Alat</b>
      <span>8 soal — pilih SPSS atau SmartPLS, dan pilih cara mengujinya.
        Skormu tersimpan di peramban ini.</span>
    </span>
    <span class="panah">&rsaquo;</span>
  </a>

  <p class="samar" style="font-size:12.5px;margin:18px 0 0">
    Kedua latihan ini sedang disiapkan. Sementara itu, kamu bisa
    <a href="/diagnosis">memeriksa datamu sendiri</a> lebih dulu.
  </p>
</div><!-- /tab-2 -->
"""

# ── 3. Skrip bukaTab ──
SKRIP_TAB = """
/* ══════ PITA TAB (19Sep26) ══════
   Tab MANDIRI — tidak mengambil dari skrip lain, menghindari jebakan urutan
   pemuatan yang sudah pernah menggigit (pelajaran 19Sep26:
   <script src> sebelum </body> jatuh SETELAH {% block skrip %}).
   State disimpan di location.hash supaya tombol mundur peramban bekerja. */
function bukaTab(n) {
  [1, 2].forEach(function (i) {
    const panel = document.getElementById('tab-' + i);
    const pa = document.getElementById('pa-' + i);
    if (!panel || !pa) return;
    panel.hidden = (i !== n);
    pa.classList.toggle('aktif', i === n);
  });
  try { history.replaceState(null, '', '#' + 'tab-' + n); } catch (e) {}
}
(() => {
  const m = (location.hash || '').match(/tab-([12])/);
  if (m) bukaTab(parseInt(m[1], 10));
})();
"""


def utama():
    s = BERKAS.read_text(encoding='utf-8')
    asli = len(s)
    CADANGAN.write_text(s, encoding='utf-8')
    print(f'cadangan → {CADANGAN} ({asli} byte)')

    if TANDA in s:
        print('⚠️  SUDAH ADA — berhenti (mencegah dobel)')
        return

    # ── A. pita tab: sisip SEBELUM .kamus-kisi ──
    penanda1 = '<div class="kamus-kisi renggang-b">'
    if penanda1 not in s:
        print('❌ penanda .kamus-kisi TIDAK KETEMU — berhenti')
        return
    s = s.replace(penanda1, PITA + penanda1, 1)

    # ── B. TAB 2: sisip SETELAH </section> di dalam blok isi ──
    penanda2 = '</section>\n\n{% endblock %}'
    if penanda2 not in s:
        print('❌ penanda </section>+endblock TIDAK KETEMU — berhenti')
        BERKAS.write_text(CADANGAN.read_text(encoding='utf-8'), encoding='utf-8')
        print('   berkas DIPULIHKAN')
        return
    s = s.replace(penanda2, '</section>\n' + TAB2 + '\n{% endblock %}', 1)

    # ── C. skrip bukaTab: sisip di awal blok skrip ──
    penanda3 = '{% block skrip %}'
    s = s.replace(penanda3, penanda3 + SKRIP_TAB, 1)

    # ── D. judul H1: lebih umum karena sekarang 2 tab ──
    s = s.replace('<h1>Kamus istilah, dengan slider</h1>',
                  '<h1>Materi, kamus, dan ruang uji</h1>', 1)

    BERKAS.write_text(s, encoding='utf-8')

    # ── VERIFIKASI ──
    print('\n── VERIFIKASI ──')
    print(f'  ukuran: {asli} → {len(s)} byte')
    for k in ['pita-tab', 'id="tab-1"', 'id="tab-2"', 'function bukaTab',
              'Rusak Data', 'Kuis Pilih Alat', 'Materi, kamus, dan ruang uji']:
        print(f'  {"✅" if k in s else "❌"} {k}')
    print(f'  {{% block isi %}}: {s.count("{% block isi %}")} · '
          f'{{% endblock %}}: {s.count("{% endblock %}")} (harus 2 & 2)')
    print(f'  <div>: {s.count("<div")} · </div>: {s.count("</div>")}')
    print(f'  <a>: {s.count("<a ")} · </a>: {s.count("</a>")}')
    print(f'  <span>: {s.count("<span")} · </span>: {s.count("</span>")}')


if __name__ == '__main__':
    utama()
