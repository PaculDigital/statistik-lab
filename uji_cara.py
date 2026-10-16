#!/usr/bin/env python3
"""UJI: cara menguji (sederhana / berganda / keduanya) — ACC Bos 18Sep26.

YANG DIUJI (harus TERUKUR, bukan dugaan):
  1. `cara='sederhana'`  → ada 3 hasil TERPISAH, tiap uji 1 prediktor.
  2. `cara='berganda'`   → ada 1 uji BERSAMA, 3 koefisien.
  3. `cara='keduanya'`   → server mengirim DUA blok sekaligus.
  4. Syarat yang HARUS benar: koefisien "bersama" BERBEDA dari "terpisah"
     kalau antar-X saling berkorelasi. Kalau sama, berarti regresi berganda
     tidak benar-benar memperhitungkan X lain → mesin SALAH.
  5. 1 prediktor → cara dipaksa 'sederhana' (tidak ada gunanya dua pilihan).
  6. Bahwa jumlah X TIDAK lagi mengunci jenis analisis (bug yang ditutup).

Jalankan: .venv/bin/python uji_cara.py
"""
import sys

sys.path.insert(0, '.')

from app.berkas_kerja import buat_data  # noqa: E402

LULUS = GAGAL = 0


def cek(nama: str, syarat: bool, bukti: str = ''):
    global LULUS, GAGAL
    if syarat:
        LULUS += 1
        print(f'  ✅ {nama}' + (f' — {bukti}' if bukti else ''))
    else:
        GAGAL += 1
        print(f'  ❌ {nama}' + (f' — {bukti}' if bukti else ''))


def main() -> int:
    print('═══ UJI CARA MENGUJI: sederhana vs berganda ═══')

    # ── 1. SEDERHANA: 3 uji terpisah ────────────────────────────────────
    d = buat_data(n=400, x=3, beta=[0.35, 0.25, 0.15], mode='presisi',
                  cara='sederhana', seed=11)
    cek('cara sederhana → 3 hasil terpisah', len(d['terpisah']) == 3,
        f'{len(d["terpisah"])} baris')
    cek('cara sederhana → cara_label benar',
        'SENDIRI-SENDIRI' in d['cara_label'], d['cara_label'][:45])
    terp = [j['terbaca'] for j in d['terpisah']]
    print(f'     β terpisah: {[round(v,3) for v in terp]}')

    # ── 2. BERGANDA: 1 uji bersama ──────────────────────────────────────
    d2 = buat_data(n=400, x=3, beta=[0.35, 0.25, 0.15], mode='presisi',
                   cara='berganda', seed=11)
    bers = [j['terbaca'] for j in d2['bersama']]
    cek('cara berganda → 1 uji berisi 3 koefisien', len(d2['bersama']) == 3,
        f'{len(d2["bersama"])} baris')
    # ⚠️ DIPERBARUI 21Sep26 (ACC Bos, keputusan N1): label "bersama-sama"
    #    DIGANTI "parsial + simultan" — sebab kata "bersama-sama" ambigu
    #    (orang menyimpulkan hanya X terakhir → Y). Uji ini ikut diselaraskan;
    #    yang diuji tetap SEMANGATnya: label harus menyebut DUA uji itu.
    cek('cara berganda → cara_label benar',
        'parsial + simultan' in d2['cara_label'].lower(),
        d2['cara_label'][:60])
    print(f'     β bersama : {[round(v,3) for v in bers]}')

    # ── 3. DUA-DUANYA: server kirim kedua blok ──────────────────────────
    d3 = buat_data(n=400, x=3, beta=[0.35, 0.25, 0.15], mode='presisi',
                   cara='keduanya', seed=11)
    cek('cara keduanya → kirim DUA blok',
        len(d3['terpisah']) == 3 and len(d3['bersama']) == 3)
    cek('cara keduanya → label menyebut dua-duanya',
        'Dua-duanya' in d3['cara_label'], d3['cara_label'][:45])

    # ── 4. BUKTI PENTING: angkanya HARUS berbeda ────────────────────────
    # Kalau X saling berkorelasi (biasanya begitu di kuesioner), maka
    # koefisien berganda ≠ sederhana. Kalau sama → mesin tidak benar.
    beda = [abs(a - b) for a, b in zip(terp, bers)]
    cek('koefisien berganda BERBEDA dari sederhana (bukti mesin benar)',
        max(beda) > 0.005,
        f'bintang terbesar {max(beda):.4f} '
        f'(X1 {terp[0]:.3f}→{bers[0]:.3f}, X3 {terp[2]:.3f}→{bers[2]:.3f})')

    # ── 5. R² kedua cara ────────────────────────────────────────────────
    # R² berganda HARUS >= R² sederhana terbesar (menambah prediktor tidak
    # pernah menurunkan R²) — ini hukum statistik, bukan selera.
    r2_terp = max(j['r2'] for j in d['terpisah'])
    r2_bers = d2['r2']
    cek('R² berganda >= R² sederhana terbesar (hukum statistik)',
        r2_bers >= r2_terp - 1e-9,
        f'bersama {r2_bers:.4f} vs sederhana terbesar {r2_terp:.4f}')

    # ── 6. 1 prediktor → dipaksa sederhana ──────────────────────────────
    d4 = buat_data(n=200, x=1, beta=[0.35], cara='berganda', seed=11)
    cek('1 prediktor → cara dipaksa sederhana (tidak bingungkan user)',
        d4['cara'] == 'sederhana', f'cara={d4["cara"]}')

    # ── 7. JUMLAH X tidak lagi mengunci jenis analisis ──────────────────
    # 3 X dengan cara sederhana HARUS menghasilkan 3 uji terpisah,
    # bukan otomatis jadi "berganda" seperti bug lama.
    cek('3 X + cara sederhana TIDAK otomatis jadi berganda (bug ditutup)',
        d['cara'] == 'sederhana' and len(d['terpisah']) == 3,
        f'cara={d["cara"]}, {len(d["terpisah"])} uji terpisah')

    # ── 8. Presisi tetap terjaga di kedua cara ──────────────────────────
    cek('presisi terjaga (cara sederhana)',
        d['galat_maks'] <= 0.05, f"galat maks {d['galat_maks']:.4f}")
    cek('presisi terjaga (cara berganda)',
        d2['galat_maks'] <= 0.05, f"galat maks {d2['galat_maks']:.4f}")

    print(f'\n  HASIL: {LULUS} LULUS / {GAGAL} GAGAL')
    return 1 if GAGAL else 0


if __name__ == '__main__':
    sys.exit(main())
