"""JATAH HARIAN DETEKSI JUDUL — pengaman biaya (ACC Bos 18Sep26).

MENGAPA BERKAS INI ADA:
Aplikasi ini BELUM punya login (terukur 18Sep26: app/main.py nol cookie,
nol session, data/ hanya berisi contoh_model.json). Tanpa identitas user,
"batas per user" TIDAK BISA dihitung. Wulan hampir membuat kesalahan itu:
mengusulkan "batas 5x per sesi" padahal "sesi" tidak ada. Bos yang menemukan.

KEPUTUSAN BOS: penjaga = BROWSER (localStorage) + JATAH HARIAN SERVER.
  · Browser  → tahu judul mana yang sudah pernah dibaca (0 token AI)
  · Server   → jaminan biaya: 20 judul baru/hari
Kenapa "20 judul/hari" dan bukan "20x panggilan AI/hari": yang dihitung
adalah JUDUL BARU. Judul yang sama tidak dihitung ulang (jawabannya
disimpan di browser), jadi user yang mengulang tidak dipotong jatahnya.

⚠️ BATAS INI TIDAK BOLEH MEMBLOKIR USER:
Kalau jatah habis, aplikasi TETAP JALAN — hanya Lapis 1 (kata kunci, Rp 0)
dan kartu manual. User TIDAK pernah melihat pesan galat. Ini sejalan
dengan gaya bahasa EduAi: hangat, memberi jalan keluar, bukan menakutkan.

CATATAN JUJUR: jatah ini PER SERVER, bukan per orang. Kalau server yang
sama dipakai 100 mahasiswa, mereka berbagi 20 judul/hari. Ini memang
kompromi dari "belum ada login" — sudah disampaikan ke Bos.
"""
from __future__ import annotations

import json
import threading
from datetime import date
from pathlib import Path

# ── setelan (dari satu tempat, jangan tulis ulang di JS) ──────────────────
JATAH_HARIAN = 20          # judul BARU per hari (ACC Bos: "20 kali/hari")
BERKAS = Path(__file__).resolve().parent.parent / 'data' / 'jatah_judul.json'

_kunci = threading.Lock()


def _hari_ini() -> str:
    return date.today().isoformat()


def _baca() -> dict:
    """Baca catatan jatah. Tahan berkas rusak / belum ada."""
    try:
        isi = json.loads(BERKAS.read_text())
        if not isinstance(isi, dict):
            raise ValueError('bentuk salah')
        return isi
    except Exception:                                   # noqa: BLE001
        # berkas rusak/kosong → mulai dari nol, JANGAN matikan aplikasi
        return {'tanggal': _hari_ini(), 'terpakai': 0, 'riwayat': []}


def _tulis(d: dict) -> None:
    try:
        BERKAS.parent.mkdir(parents=True, exist_ok=True)
        BERKAS.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    except OSError:
        pass        # gagal menulis jatah JANGAN sampai menggagalkan permintaan


def cek() -> dict:
    """Lihat keadaan jatah hari ini tanpa memotong apa pun."""
    with _kunci:
        d = _baca()
        if d.get('tanggal') != _hari_ini():
            # hari berganti → reset (ACC Bos: "kembali lagi besok")
            d = {'tanggal': _hari_ini(), 'terpakai': 0, 'riwayat': []}
            _tulis(d)
        terpakai = int(d.get('terpakai', 0))
        return {
            'terpakai': terpakai,
            'batas': JATAH_HARIAN,
            'sisa': max(0, JATAH_HARIAN - terpakai),
            'penuh': terpakai >= JATAH_HARIAN,
        }


def pakai(judul: str) -> dict:
    """Catat satu judul BARU terpakai. Kembalikan keadaan jatah setelahnya.

    PENTING: fungsi ini TIDAK menolak. Kalau jatah habis, dia tetap
    mengembalikan penuh=True dan PEMANGGIL yang memutuskan (pakai Lapis 1
    saja). Ini disengaja: jatah adalah pengaman biaya, bukan pagar yang
    memblokir user.
    """
    with _kunci:
        d = _baca()
        if d.get('tanggal') != _hari_ini():
            d = {'tanggal': _hari_ini(), 'terpakai': 0, 'riwayat': []}

        j = (judul or '').strip()[:200]
        riwayat = d.setdefault('riwayat', [])
        # judul SAMA yang sudah pernah dibaca hari ini → TIDAK dipotong
        sudah = any(r.get('judul', '').lower() == j.lower() for r in riwayat)
        if not sudah:
            d['terpakai'] = int(d.get('terpakai', 0)) + 1
            riwayat.append({'judul': j, 'jam': _hari_ini()})
            d['riwayat'] = riwayat[-80:]        # simpan 80 terakhir saja
        _tulis(d)

        terpakai = int(d.get('terpakai', 0))
        return {
            'terpakai': terpakai,
            'batas': JATAH_HARIAN,
            'sisa': max(0, JATAH_HARIAN - terpakai),
            'penuh': terpakai >= JATAH_HARIAN,
            'sudah_pernah': sudah,
        }
