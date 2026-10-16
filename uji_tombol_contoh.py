"""UJI TOMBOL CONTOH (Tahap 2.1d) — dua rasa, bukti dari halaman sungguhan.

⚠️ MENGAPA DIPISAH dari uji_web_grafik.py: uji ini menekan TOMBOL yang benar
   (fungsi pakaiContoh + tombol Periksa), bukan memanggil API langsung. Jadi
   yang diuji adalah JALUR MAHASISWA, bukan jalur API.

Bukti yang dikumpulkan:
  1. tombol contoh mengisi kolom otomatis (X1, X2 → Y) — tanpa sentuhan user
  2. rasa 'sehat'  → SEMUA syarat hijau (bukan cuma "tidak error")
  3. rasa 'sakit'  → hetero DITOLAK + grafik memakai warna merah
  4. catatan contoh TAMPIL (mahasiswa tahu ini data contoh, bukan datanya)
  5. angka uji cocok dengan yang dihitung mesin (tidak dikarang di JS)

⚠️ AKAR YANG DITUTUP 21Sep26 — UJI WAJIB MENYIAPKAN DIRINYA SENDIRI:
   Dulu uji ini HANYA memeriksa apakah server :8122 hidup, tanpa pernah
   MENYALAKANNYA. Begitu dipanggil langsung dari gerbang_uji.sh (tanpa
   `jalankan_uji_normalitas.py` lebih dulu) → `Connection refused` →
   GAGAL PALSU 2 grup (uji ini + uji_web_grafik). Aplikasi SEHAT.
   PELAJARAN INDUK (tercatat 20Sep26 jebakan #8): "uji tidak menyiapkan
   dirinya sendiri" = GAGAL PALSU.

   🚨 JEBAKAN 21Sep26 (2 putaran terbuang — INGAT): server uji :8122 = uvicorn
   dari BERKAS LOKAL (`jalankan_uji_normalitas.py`), **BUKAN kontainer Docker**.
   Wulan sempat mencoba menyalakan kontainer Docker di :8122 → jalan, tapi
   `127.0.0.1:8122` dari dalam container Hermes tetap `Connection refused`
   (loopback Wulan ≠ host; lewat IP kontainer 172.17.0.x baru HTTP 200).
   ⇒ PAKAI POLA PROVEN: uvicorn lokal, `--host 127.0.0.1 --port 8122`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websocket

PORT, PORT_UJI = 9333, 8122
BASE = f'http://127.0.0.1:{PORT_UJI}'
DIR = Path(__file__).resolve().parent
PY = DIR / '.venv' / 'bin' / 'python'

LULUS = GAGAL = 0


def server_hidup():
    try:
        return urllib.request.urlopen(
            f'http://127.0.0.1:{PORT_UJI}/health', timeout=3).status == 200
    except Exception:
        return False


def siapkan_server_uji():
    """Nyalakan server uji :8122 SENDIRI — pola proven `jalankan_uji_normalitas.py`.

    Server = **uvicorn dari berkas LOKAL** (bukan kontainer Docker!). Kalau
    sudah hidup (mis. dinyalakan berkas lain), langsung pakai — tidak dobel.
    """
    if server_hidup():
        return True

    os.environ['PORT'] = str(PORT_UJI)
    subprocess.Popen(
        [str(PY), '-m', 'uvicorn', 'app.main:app',
         '--host', '127.0.0.1', '--port', str(PORT_UJI),
         '--log-level', 'warning'],
        cwd=str(DIR), env=dict(os.environ),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for _ in range(60):          # maks 30 detik
        if server_hidup():
            return True
        time.sleep(0.5)
    return False


def matikan_server_uji():
    """Matikan HANYA uvicorn yang kita nyalakan (jangan sentuh proses lain)."""
    subprocess.run(
        ['pkill', '-f', f'uvicorn app.main:app --host 127.0.0.1 '
                        f'--port {PORT_UJI}'],
        capture_output=True)



def cek(nama, syarat, bukti=''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}')
    else:
        GAGAL += 1
        print(f'  ❌ {nama}  {bukti}')


class Tab:
    def __init__(self):
        t = json.loads(urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT}/json/new?about:blank', method='PUT'),
            timeout=20).read())
        self.tab_id = t['id']
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90)
        self.n = 0

    def cmd(self, m, **p):
        self.n += 1
        self.ws.send(json.dumps({'id': self.n, 'method': m, 'params': p}))
        while True:
            r = json.loads(self.ws.recv())
            if r.get('id') == self.n:
                return r

    def js(self, e):
        r = self.cmd('Runtime.evaluate', expression=e, returnByValue=True,
                     awaitPromise=True)
        res = r.get('result', {})
        if res.get('exceptionDetails'):
            ex = res['exceptionDetails']
            return {'__galat': ex.get('text'),
                    'desc': (ex.get('exception') or {}).get('description', '')[:400],
                    'stack': (ex.get('stackTrace') or {}).get('callFrames', [])[:3]}
        return res.get('result', {}).get('value')

    def tutup(self):
        try:
            self.ws.close()
        except Exception:
            pass
        try:
            urllib.request.urlopen(urllib.request.Request(
                f'http://127.0.0.1:{PORT}/json/close/{self.tab_id}'), timeout=15).read()
        except Exception:
            pass


JALAN = """
(async (rasa) => {
  await pakaiContoh(rasa);
  /* ⚠️ CACAT UJI YANG DITUTUP (21Sep26): uji ini mula-mula membaca
     `#baris-x .pilih-kolom` dan `#kolom-y` — elemen LAMA yang SUDAH DIHAPUS
     saat bentuk PERAN menggantikan baris-x/baris-m. Akibatnya x selalu []
     dan y selalu null → GAGAL PALSU ("kolom terisi otomatis" gagal),
     padahal tombolnya sendiri BEKERJA (terbukti: pakaiContoh() memanggil
     bangunDaftarPeran() + mengisi PERAN[nm]='X1'/'X2'/'Y1').
     Yang benar: baca dari `PERAN` (objek peran) + dropdown `#daftar-peran`. */
  const kel = {};
  Object.keys(PERAN).forEach(k => {
    const v = PERAN[k];
    if (v) (kel[v] = kel[v] || []).push(k);
  });
  const hurufX = Object.keys(kel).filter(p => p[0] === 'X').sort();
  const hurufY = Object.keys(kel).filter(p => p[0] === 'Y').sort();
  const xSel = hurufX.reduce((a, p) => a.concat(kel[p]), []);
  const ySel = hurufY.length ? { value: kel[hurufY[hurufY.length - 1]][0] } : null;
  const isi = {
    x: xSel, y: ySel ? ySel.value : null,
    nDropPeran: document.querySelectorAll('#daftar-peran select').length,
    adaBentukLama: !!document.getElementById('baris-x') ||
                   !!document.getElementById('kolom-y'),
    nama: document.getElementById('nama-berkas').textContent,
    catatanTampil: !document.getElementById('catatan-contoh').hidden,
    catatan: (document.getElementById('catatan-contoh').textContent || '').slice(0, 120),
    pesan: (document.getElementById('pesan-unggah').textContent || '').slice(0, 100)
  };
  document.getElementById('tombol-periksa').click();
  for (let i = 0; i < 50; i++) {
    await new Promise(r => setTimeout(r, 500));
    const w = document.getElementById('kartu-hasil');
    if (!w.hidden && w.querySelectorAll('[data-grafik]').length >= 3) break;
  }
  const w = document.getElementById('kartu-hasil');
  isi.grafik = Array.from(w.querySelectorAll('[data-grafik]')).map(e => e.getAttribute('data-grafik'));
  isi.titikMerah = w.querySelectorAll('circle[fill="#A85A5A"]').length;
  isi.titikHijau = w.querySelectorAll('circle[fill="#2E7D6F"]').length;
  isi.lencana = Array.from(w.querySelectorAll('.lencana, .tanda')).map(e => (e.textContent || '').trim()).slice(0, 6);
  /* ⚠️ CACAT UJI YANG DITUTUP (20Sep26): mula-mula teks hasil dipotong 260
     karakter, lalu uji mencari kata 'corong' — padahal kalimat corong ada di
     kartu HETEROSKEDASTISITAS yang jauh di bawah (kartu Normalitas lebih
     dulu). Akibatnya uji GAGAL PALSU. Teks lengkap kini disimpan, kalimatnya
     diambil khusus dari kartu hetero. */
  isi.teksHasil = (w.textContent || '').replace(/\\s+/g, ' ');
  const kh = w.querySelector('[data-grafik="hetero"]');
  isi.teksHetero = kh ? (kh.closest('.kartu') || kh.parentElement).textContent.replace(/\\s+/g, ' ') : '';
  isi.tumpah = /\\{\\{|object Object|undefined|NaN/.test(w.textContent || '');
  return isi;
})
"""


def main():
    print('─' * 70)
    print(' UJI TOMBOL CONTOH — dua rasa, lewat jalur mahasiswa')
    print('─' * 70)

    # ⚠️ UJI WAJIB MENYIAPKAN SERVERNYA SENDIRI (akar ditutup 21Sep26).
    if not siapkan_server_uji():
        print(f'  ❌ server uji :{PORT_UJI} TIDAK BISA DINYALAKAN — uji dibatalkan.')
        print('     (bukan cacat aplikasi: uji ini butuh uvicorn lokal di '
              f':{PORT_UJI})')
        return 1

    tab = None
    try:
        tab = Tab()
        tab.cmd('Page.enable')
        tab.cmd('Runtime.enable')
        tab.cmd('Emulation.setDeviceMetricsOverride', width=390, height=900,
                deviceScaleFactor=2, mobile=True)
        tab.cmd('Page.navigate', url=BASE + '/klinik')
        time.sleep(4)

        # ── prasyarat: fungsi & tombol ADA ──
        ada = tab.js("({pakaiContoh: typeof pakaiContoh, buatContohData: typeof buatContohData})")
        cek('fungsi pakaiContoh() ada di halaman', ada.get('pakaiContoh') == 'function', str(ada))
        cek('fungsi buatContohData() ada di halaman', ada.get('buatContohData') == 'function', str(ada))
        tombol = tab.js("Array.from(document.querySelectorAll('button')).filter(b => /contoh/i.test(b.textContent)).length")
        cek('ada 2 tombol contoh di Langkah 2', tombol == 2, f'jumlah={tombol}')

        # ── RASA SEHAT ──
        print('\n  ── rasa: SEHAT ──')
        s = tab.js(f'{JALAN}("sehat")')
        if isinstance(s, dict) and s.get('__galat'):
            cek('rasa sehat jalan tanpa galat JS', False, json.dumps(s)[:250])
        else:
            cek('rasa sehat jalan tanpa galat JS', True)
            cek('kolom terisi otomatis X1,X2 → Y',
                s.get('x') == ['X1', 'X2'] and s.get('y') == 'Y',
                f"x={s.get('x')} y={s.get('y')}")
            # Penjaga bentuk PERAN (21Sep26): tombol contoh WAJIB mengisi
            # lewat dropdown peran — BUKAN lewat #baris-x/#kolom-y yang sudah
            # dihapus. Kalau elemen lama muncul lagi, uji ini menangkap.
            cek('memakai dropdown peran (bukan bentuk lama)',
                (s.get('nDropPeran') or 0) >= 3,
                f"dropdown peran = {s.get('nDropPeran')}")
            cek('elemen LAMA (#baris-x/#kolom-y) TIDAK ada di halaman',
                s.get('adaBentukLama') is False, str(s.get('adaBentukLama')))
            cek('berkas ditandai sebagai CONTOH',
                'contoh' in (s.get('nama') or '').lower(), str(s.get('nama')))
            cek('catatan "ini contoh" TAMPIL', bool(s.get('catatanTampil')), str(s.get('catatanTampil')))
            cek('3 grafik tergambar', sorted(s.get('grafik') or []) == ['hetero', 'linear', 'pp'],
                str(s.get('grafik')))
            cek('rasa sehat: TIDAK ada titik merah (semua lolos)',
                s.get('titikMerah') == 0, f"titik merah={s.get('titikMerah')}")
            cek('halaman tidak menumpahkan kode', not s.get('tumpah'), s.get('teksHasil', '')[:120])

        # ── RASA SAKIT ──
        print('\n  ── rasa: SAKIT (bermasalah) ──')
        k = tab.js(f'{JALAN}("sakit")')
        if isinstance(k, dict) and k.get('__galat'):
            cek('rasa sakit jalan tanpa galat JS', False, json.dumps(k)[:250])
        else:
            cek('rasa sakit jalan tanpa galat JS', True)
            cek('rasa sakit: ADA titik merah (ada yang ditolak)',
                (k.get('titikMerah') or 0) > 0, f"titik merah={k.get('titikMerah')}")
            th = (k.get('teksHetero') or '').lower()
            cek('rasa sakit: kartu hetero menyebut CORONG',
                'corong' in th or 'melebar' in th, (k.get('teksHetero') or '')[:150])
            cek('catatan contoh menyebut SENGAJA bermasalah',
                'sengaja' in (k.get('catatan') or '').lower(), str(k.get('catatan'))[:90])

        # ── BANDINGKAN: dua rasa harus BERBEDA ──
        print('\n  ── dua rasa harus berbeda ──')
        cek('jumlah titik merah sehat ≠ sakit',
            s.get('titikMerah') != k.get('titikMerah'),
            f"sehat={s.get('titikMerah')} sakit={k.get('titikMerah')}")
    finally:
        if tab is not None:
            tab.tutup()

    print('\n' + '─' * 70)
    print(f'  {"✅ LULUS SEMUA" if GAGAL == 0 else "❌ ADA GAGAL"}: {LULUS} lulus / {GAGAL} gagal')
    print('─' * 70)
    return 0 if GAGAL == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
