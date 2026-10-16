"""ALIHKAN /syarat → tab "Baca Grafik" di BELAJAR (ACC Bos 19Sep26 langkah 3A).

KEPUTUSAN BOS: halaman Syarat dijadikan ALAT saja (sudah selesai jadi
/diagnosis = /klinik). 7 kartu bacaannya dipindah ke BELAJAR (sudah
dikerjakan). Karena itu /syarat TIDAK dihapus — DIALIHKAN, supaya tautan
lama dari /belajar, /kuantitatif, /segera, dan bookmark mahasiswa tetap
hidup (aturan Bos: JANGAN matikan, alihkan).

YANG DIUBAH:
  1. Rute /syarat  → RedirectResponse ke /belajar#tab-3 (308, permanen)
  2. MODUL         → entri 'syarat' DIKELUARKAN (menu 8 → 7)
     Alasan: kalau tetap di menu, mahasiswa punya DUA pintu ke isi yang
     sama dan bingung mana yang dipakai (alasan yang sama seperti waktu
     menu 'klinik' dipakai ulang untuk DIAGNOSIS DATA, 19Sep26).
  3. template syarat.html TETAP ADA di disk (tidak dihapus) — kalau Bos
     mau kembali, tinggal hidupkan lagi rutenya.
"""
from pathlib import Path
import shutil

F = Path('app/main.py')
t = F.read_text(encoding='utf-8')
shutil.copy(F, F.with_name('main.py.cadangan_alih_syarat'))
sebelum = len(t)

# ══ 1. RUTE /syarat → pengalihan ═══════════════════════════════════════════
LAMA_RUTE = """@app.get('/syarat', response_class=HTMLResponse)
async def syarat(request: Request):
    return templates.TemplateResponse(request, 'syarat.html',
                                      _konteks(request, 'syarat', 'Periksa Syarat'))"""

BARU_RUTE = """@app.get('/syarat')
async def syarat():
    \"\"\"DIALIHKAN ke tab "Baca Grafik" di BELAJAR (ACC Bos 19Sep26 langkah 3A).

    ⚠️ MENGAPA DIALIHKAN, BUKAN DIHAPUS (20Sep26):
      (a) 7 kartu bacaannya sudah PINDAH ke BELAJAR tab ke-3 "Baca Grafik" —
          halaman ini jadi isi kembar;
      (b) BANYAK tautan lama menuju ke sini: /belajar, /kuantitatif, /segera,
          dan bookmark mahasiswa. Menghapus rutenya = tautan PATAH (404);
      (c) aturan Bos: "alihkan, jangan matikan".
    ⇒ 308 (PERMANENT REDIRECT): peramban & mesin pencari ikut memindahkan
      alamatnya, jadi tidak ada yang tersesat dan tidak ada isi kembar.

    template 'syarat.html' SENGAJA dibiarkan ada di disk — kalau Bos mau
    menghidupkan halamannya lagi, cukup kembalikan rutenya.
    \"\"\"
    return RedirectResponse('/belajar#tab-3', status_code=308)"""

c = t.count(LAMA_RUTE)
if c != 1:
    raise SystemExit(f'  ❌ penanda rute ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_RUTE, BARU_RUTE, 1)

# ══ 2. KELUARKAN 'syarat' dari MODUL (menu 8 → 7) ══════════════════════════
LAMA_MODUL = """    {'slug': 'syarat', 'nama': 'KAMUS GRAFIK', 'ikon': 'activity',
     'warna': '#4E8A5A', 'siap': True,
     'ringkas': 'Grafik uji asumsi (heteroskedastisitas, normalitas, VIF) dengan cara membacanya.'},
"""
c = t.count(LAMA_MODUL)
if c != 1:
    raise SystemExit(f'  ❌ penanda MODUL ketemu {c}× (harus 1) — DIBATALKAN')
t = t.replace(LAMA_MODUL, '', 1)

# ══ 3. pastikan RedirectResponse sudah diimpor ═════════════════════════════
if 'RedirectResponse' not in t.split('\n\n')[0] and 'from fastapi.responses' not in t:
    raise SystemExit('  ❌ RedirectResponse belum diimpor — DIBATALKAN')
print('  ✅ RedirectResponse sudah diimpor')

F.write_text(t, encoding='utf-8')
print(f'  ✅ main.py: {sebelum} → {len(t)} karakter ({len(t) - sebelum})')
sisa = t.count("{'slug':")
print(f'  ✅ menu sekarang: {sisa} entri (+ beranda bila ada)')
