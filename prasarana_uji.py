"""PRASARANA UJI — satu tempat untuk memeriksa Chrome CDP :9333.

AKAR (terukur 21Sep26, dua kejadian):
  1. Chrome CDP :9333 MATI → 7 grup gerbang dilaporkan "GAGAL" padahal
     mesin sama sekali tidak tersentuh. Wulan lalu mengejar bug aplikasi
     yang tidak ada. Itu MEMBUANG WAKTU dan MENYESATKAN.
  2. Chrome hidup HANYA kalau dijalankan lewat Hermes
     (`terminal(background=true)`) → PPID = Hermes gateway (160), bukan 1.
     Segala usaha melepasnya GAGAL, terukur:
       · `Popen` biasa                     → Chrome tidak nyala
       · `Popen(start_new_session=True)`   → nyala, tapi PPID = skrip
                                             pemanggil → mati saat skrip usai
       · double-fork (fork→fork→keluar)    → tidak nyala (galat dbus)
       · double-fork + setsid              → tidak nyala (galat dbus)
     ⇒ Chrome TIDAK BISA dilepas dari gateway. PPID 160 itu SYARAT HIDUP,
       bukan kelemahan. Jadi JANGAN coba-coba menyalakannya sendiri.

ATURAN (diputuskan Bos 21Sep26, Opsi A):
  Kalau Chrome mati → uji keluar dengan `KODE_LEWAT` (77) + pesan JELAS
  berisi perintah menyalakannya. Gerbang memahami 77 = LEWAT karena
  prasarana, BUKAN GAGAL.

Pakai di berkas uji:
    from prasarana_uji import pastikan_chrome, KODE_LEWAT
    kode = pastikan_chrome(9333)
    if kode is not None:
        return kode            # 77 = lewat, gerbang tidak bilang GAGAL
"""
from __future__ import annotations

import urllib.request

# Satu sumber untuk semua berkas uji & gerbang.
KODE_LEWAT = 77

CHROME = ('/opt/data/home/.cloakbrowser/'
          'chromium-151.0.7922.108.6-pro/chrome')
BENDERA = ('--headless=new --no-sandbox --disable-gpu '
           '--remote-allow-origins=* --window-size=390,900 --hide-scrollbars')


def cdp_hidup(port: int = 9333) -> bool:
    """Chrome CDP di `port` benar-benar menjawab? (bukan cuma 'ada proses')."""
    try:
        with urllib.request.urlopen(
                f'http://127.0.0.1:{port}/json/version', timeout=4) as r:
            return r.status == 200
    except Exception:                                       # noqa: BLE001
        return False


def pesan_chrome(port: int = 9333) -> None:
    """Pesan JELAS + perintah siap-tempel (Bos akses dari HP)."""
    print(f'\n  ⏭️  LEWAT — Chrome CDP di :{port} belum menyala.')
    print('     Uji ini butuh Chrome. Mesin TIDAK salah — yang kurang')
    print('     cuma prasarana, jadi gerbang tidak menghitungnya GAGAL.')
    print('\n     Nyalakan sekali (tempel apa adanya, lewat terminal background):')
    print(f'       {CHROME} {BENDERA} \\')
    print(f'         --remote-debugging-port={port}')
    print('\n     ⚠️ JANGAN coba menyalakan lewat shell/Python biasa —')
    print('        Chrome akan langsung keluar (galat dbus). Terukur 21Sep26:')
    print('        4 cara dicoba, SEMUA gagal. Harus lewat Hermes background.')
    print(f'\n     Cek sudah hidup belum:')
    print(f'       curl -s -o /dev/null -w "%{{http_code}}\\n" \\')
    print(f'         http://127.0.0.1:{port}/json/version      # harus 200')


def pastikan_chrome(port: int = 9333) -> int | None:
    """None kalau Chrome siap; KODE_LEWAT kalau tidak (beserta pesannya)."""
    if cdp_hidup(port):
        return None
    pesan_chrome(port)
    return KODE_LEWAT
