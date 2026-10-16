"""UJI MANOVA LEWAT HALAMAN SUNGGUHAN (Chrome CDP :9333).

═══════════════════════════════════════════════════════════════════════════
MENGAPA UJI INI ADA — pelajaran K-18 (21Sep26)
  Uji moderasi Wulan dulu lewat API langsung → SEMUA LULUS, padahal
  HALAMANNYA tidak pernah mengirim data yang diperlukan, jadi mahasiswa
  TIDAK PERNAH dapat hasil. Uji yang memanggil API langsung MENYEMBUNYIKAN
  cacat jalur halaman.

  ⇒ Karena itu MANOVA diuji dengan cara yang SAMA seperti mahasiswa
    memakainya: buka halaman → isi → klik tombol → periksa hasilnya
    benar-benar TAMPIL.

⚠️ PRASARANA (pelajaran K-21): Chrome :9333 & server :8122 WAJIB hidup.
   Kalau mati → keluar KODE_LEWAT 77, BUKAN gagal (itu bukan cacat aplikasi).
"""
from __future__ import annotations

import json
import sys
import urllib.request

sys.path.insert(0, '/opt/data/services/statistik-lab')

PORT_CDP = 9333
PORT_APP = 8122
KODE_LEWAT = 77
URL = f'http://127.0.0.1:{PORT_APP}/buat-data?model=banding-kelompok'

lulus = gagal = 0
pesan: list[str] = []


def catat(ok: bool, teks: str, tambahan: str = '') -> None:
    global lulus, gagal
    if ok:
        lulus += 1
        pesan.append(f'  ✅ {teks}' + (f'   {tambahan}' if tambahan else ''))
    else:
        gagal += 1
        pesan.append(f'  ❌ {teks}' + (f'   {tambahan}' if tambahan else ''))


def hidup(url: str, kode_ok=(200,)) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=5) as f:
            return f.status in kode_ok
    except Exception:                                    # noqa: BLE001
        return False


def main() -> int:
    # ── PRASARANA dulu (jangan menuduh aplikasi kalau prasarananya mati) ──
    if not hidup(f'http://127.0.0.1:{PORT_CDP}/json/version'):
        print('⏭️  LEWAT: Chrome CDP :9333 mati — ini PRASARANA, bukan cacat app')
        return KODE_LEWAT
    if not hidup(f'http://127.0.0.1:{PORT_APP}/health'):
        print(f'⏭️  LEWAT: server uji :{PORT_APP} mati — ini PRASARANA')
        return KODE_LEWAT

    import websocket                                  # noqa: PLC0415

    # buka tab baru lewat CDP
    # ⚠️ Chrome baru butuh METHOD PUT untuk /json/new (GET → HTTP 405).
    #    Buka 'about:blank' dulu, baru navigate (pola uji_moderasi_halaman.py).
    with urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{PORT_CDP}/json/new?about:blank',
            method='PUT'), timeout=20) as f:
        tab = json.load(f)
    ws = websocket.create_connection(tab['webSocketDebuggerUrl'], timeout=40)
    try:
        ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
        ws.send(json.dumps({'id': 2, 'method': 'Runtime.enable'}))
        ws.send(json.dumps({'id': 3, 'method': 'Page.navigate',
                            'params': {'url': URL}}))
        # tunggu halaman siap
        import time
        for _ in range(30):
            time.sleep(0.4)
            ws.send(json.dumps({'id': 99, 'method': 'Runtime.evaluate',
                                'params': {'expression':
                                           "document.readyState",
                                           'returnByValue': True}}))
            for _ in range(6):
                r = json.loads(ws.recv())
                if r.get('id') == 99:
                    if r.get('result', {}).get('result', {}).get('value') == \
                            'complete':
                        break
            else:
                continue
            break
        time.sleep(1.2)

        def js(expr: str, tid: int = 500):
            ws.send(json.dumps({'id': tid, 'method': 'Runtime.evaluate',
                                'params': {'expression': expr,
                                           'returnByValue': True,
                                           'awaitPromise': True}}))
            for _ in range(400):
                r = json.loads(ws.recv())
                if r.get('id') == tid:
                    hasil = r.get('result', {})
                    if hasil.get('exceptionDetails'):
                        return {'__err': str(hasil['exceptionDetails']
                                             .get('text'))}
                    return hasil.get('result', {}).get('value')
            return {'__err': 'tidak ada balasan'}

        # ── [1] halaman termuat & panel MANOVA MUNCUL ─────────────────
        judul = js('document.title')
        catat(isinstance(judul, str) and judul != '', 'halaman /buat-data termuat',
              str(judul)[:40])
        panel = js("(() => { const p = el('panel-manova');"
                   " return p ? !p.classList.contains('sembunyi') : false; })()")
        catat(panel is True, 'panel MANOVA MUNCUL (pintu ?model=banding-kelompok)')

        # ── [2] form regresi DISEMBUNYIKAN (jangan dua form tampil bareng) ──
        tersembunyi = js("(() => { const q = document.querySelector("
                         "'.pilih-kisi');"
                         " return q ? q.classList.contains('sembunyi') : false;"
                         " })()")
        catat(tersembunyi is True, 'form Regresi disembunyikan saat MANOVA')

        # ── [3] rentang beda ditulis dari SATU SUMBER (window, bukan HTML) ─
        rentang = js("(() => { const r = el('mn-rentang');"
                     " return r ? r.textContent.trim() : ''; })()")
        catat('0.30' in str(rentang) or '0,30' in str(rentang),
              'rentang beda TAMPIL di halaman (dari server)', str(rentang)[:30])

        # ── [4] tombol ada & bisa diklik ──────────────────────────────
        ada_tombol = js("!!el('mn-tombol')")
        catat(ada_tombol is True, 'tombol "Buatkan & ujikan" ada')

        # ── [5] PAGAR halaman: Y cuma 1 → pesan ramah, bukan dihitung ─
        js("el('mn-nama-y').value = 'Minat'")
        js("el('mn-tombol').click()")
        time.sleep(2.5)
        pesan_y1 = js("el('mn-hasil').textContent")
        catat('minimal 2 variabel hasil' in str(pesan_y1),
              'Y cuma 1 → halaman menolak dengan penjelasan',
              str(pesan_y1)[:45])

        # ── [6] JALAN SUNGGUHAN: klik → hasil MANOVA TAMPIL ───────────
        js("el('mn-nama-y').value = 'Minat, Nilai'")
        js("el('mn-beda').value = '0.90, 0.54'")
        js("el('mn-isi').value = '60'")
        js("el('mn-tombol').click()")
        # tunggu mesin selesai (maks ~40 detik)
        import time as _t
        isi = ''
        for _ in range(40):
            _t.sleep(1.0)
            isi = str(js("el('mn-hasil').textContent") or '')
            if 'Pillai' in isi or 'Belum bisa' in isi:
                break
        catat('Pillai' in isi, 'KLIK → hasil MANOVA TAMPIL di halaman',
              f'{len(isi)} karakter')
        catat('Kesimpulan' in isi, 'kesimpulan berbahasa manusia tampil')
        catat('Signifikan' in isi or 'NYATA' in isi,
              'putusan signifikan disebut')
        catat('Box' in isi, "syarat (Box's M) ikut ditampilkan — jangan disembunyikan")
        catat('Rerata tiap kelompok' in isi, 'rerata tiap kelompok tampil')

        # ── [6a] KOLOM 'n' HARUS ANGKA, BUKAN '—' (terbukti bisa gagal) ──
        # ⚠️ Ditemukan 21Sep26: uji Wulan sebelumnya HANYA memeriksa
        #    "tulisan Rerata tiap kelompok ada" — jadi saat rute /uji sengaja
        #    TIDAK mengirim 'isi_kelompok', kolom n jatuh ke '—' dan uji
        #    TETAP HIJAU. Uji yang tak bisa gagal = tidak menjaga apa pun.
        #    Sekarang: ambil n dari sel tabel dan wajib berupa angka > 0.
        n_sel = js("(() => { const t = el('mn-hasil')"
                   ".querySelectorAll('table');"
                   " for (const tb of t) {"
                   "   const h = tb.querySelector('thead').textContent;"
                   "   if (h.includes('Kelompok') && h.includes('n')) {"
                   "     const td = tb.querySelector('tbody tr td:nth-child(2)');"
                   "     return td ? td.textContent.trim() : null; } }"
                   " return null; })()")
        bisa_angka = False
        try:
            bisa_angka = int(str(n_sel)) > 0
        except (TypeError, ValueError):
            bisa_angka = False
        catat(bisa_angka, "kolom 'n' tiap kelompok berupa ANGKA (bukan '—')",
              f'n = {n_sel!r}')

        catat('Catatan kejujuran' in isi,
              'catatan kejujuran (setelan vs terbaca) tampil')

        # ── [6d] KOLOM "Nilai" HARUS NILAI STATISTIK, BUKAN F ────────────
        # ⚠️ BUG NYATA 21Sep26 (KETEMU MATA): kolom "Nilai" diisi `q.F` →
        #    halaman menampilkan Wilks = 28,369 dan Pillai = 57,224 (mustahil
        #    > 1). Uji teks Wulan LOLOS karena hanya memeriksa "ada angka".
        #    Pelajaran: untuk yang DILIHAT user, periksa NILAI-NYA, bukan
        #    sekadar keberadaan tulisan.
        cell = js("(() => { const t = [...el('mn-hasil')"
                  ".querySelectorAll('table')].find(tb => tb.textContent"
                  ".includes(\"Pillai's Trace\"));"
                  " if (!t) return null;"
                  " const td = [...t.querySelectorAll('tbody tr')].map(tr =>"
                  "   [...tr.querySelectorAll('td')].map(c => c.textContent"
                  ".trim()));"
                  " return JSON.stringify(td); })()")
        baris = []
        try:
            baris = json.loads(cell) if cell else []
        except (TypeError, ValueError):
            baris = []

        def angka(t: str):
            try:
                return float(str(t).replace(',', '.'))
            except (TypeError, ValueError):
                return None

        pil = next((b for b in baris if b and 'Pillai' in b[0]), None)
        wil = next((b for b in baris if b and 'Wilks' in b[0]), None)
        nilai_pil = angka(pil[1]) if pil and len(pil) > 1 else None
        nilai_wil = angka(wil[1]) if wil and len(wil) > 1 else None
        catat(nilai_pil is not None and 0 <= nilai_pil <= 1,
              'kolom "Nilai" Pillai masuk akal (0..1) — bukan F',
              f'Pillai = {nilai_pil}')
        catat(nilai_wil is not None and 0 <= nilai_wil <= 1,
              'kolom "Nilai" Wilks masuk akal (0..1)',
              f'Wilks = {nilai_wil}')
        catat(pil is not None and nilai_pil is not None and
              pil[2] != pil[1],
              'kolom "Nilai" BERBEDA dari kolom "F" (tidak tertukar)',
              f'Nilai={pil[1] if pil else "?"} F={pil[2] if pil else "?"}')
        # F harus ada isinya (bukan '—' di semua baris)
        f_ada = [b[2] for b in baris if len(b) > 2 and b[2] not in ('—', '')]
        catat(len(f_ada) >= 4, 'kolom F terisi untuk keempat ukuran',
              f'{len(f_ada)} baris')

        # ── [6b] ISI HASIL HARUS MASUK AKAL (bukan cuma "ada") ──────────
        # ⚠️ PELAJARAN 21Sep26: uji yang hanya memeriksa "ada tulisan" TIDAK
        #    BISA GAGAL saat mesinnya rusak — scandainya angka salah, tulisan
        #    tetap muncul. Jadi periksa: (a) tidak ada 'undefined'/'NaN',
        #    (b) angka p benar-benar terbaca dari tabel yang tampil.
        catat('undefined' not in isi and 'NaN' not in isi,
              'tidak ada nilai kosong (undefined/NaN) di hasil',
              isi[:35] if ('undefined' in isi or 'NaN' in isi) else '')
        p_tampil = js("(() => { const m = el('mn-hasil').textContent"
                      ".match(/([0-9]+[.,][0-9]{4,})/g);"
                      " return m ? m.length : 0; })()")
        catat(isinstance(p_tampil, int) and p_tampil >= 3,
              'angka p benar-benar tertulis di hasil',
              f'{p_tampil} angka desimal panjang')

        # ── [6c] TOMBOL kembali bisa dipakai (tidak nyangkut 'Menghitung…') ─
        t_tombol = str(js("el('mn-tombol').textContent") or '')
        catat('Menghitung' not in t_tombol,
              'tombol kembali normal setelah selesai', t_tombol.strip()[:30])

        # ── [7] PAGAR beda di luar rentang → pesan ramah + jalan keluar ─
        js("el('mn-beda').value = '2.50, 2.50'")
        js("el('mn-tombol').click()")
        _t.sleep(4.0)
        pesan_pagar = str(js("el('mn-hasil').textContent") or '')
        catat('Belum bisa dibuat' in pesan_pagar,
              'beda 2,50 → ditolak dengan pesan RAMAH (bukan galat)',
              pesan_pagar[:40])
        catat('sengaja dibuat sama' in pesan_pagar,
              'penolakan memberi JALAN KELUAR (aturan Bos)')
    finally:
        try:
            ws.close()
        except Exception:                                # noqa: BLE001
            pass
        try:
            urllib.request.urlopen(
                f'http://127.0.0.1:{PORT_CDP}/json/close/{tab["id"]}',
                timeout=5).read()
        except Exception:                                # noqa: BLE001
            pass

    print('=' * 74)
    print(' UJI MANOVA LEWAT HALAMAN SUNGGUHAN (Chrome CDP)')
    print('=' * 74)
    for p in pesan:
        print(p)
    print()
    print('=' * 74)
    if gagal:
        print(f' ❌ ADA GAGAL: {gagal}  (lulus {lulus})')
        return 1
    print(f' ✅ {lulus} LULUS / 0 GAGAL — mahasiswa benar-benar dapat hasilnya')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
