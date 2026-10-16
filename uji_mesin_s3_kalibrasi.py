"""UJI S3 versi KALIBRASI (cara yang sudah terbukti untuk mediasi/moderasi).

Alasan uji-1 meleset (terukur): bangun_berurutan TANPA kalibrasi → X1 yang
punya 2 peran (ke X2 DAN ke Y) terbaca 0,7354 padahal minta 0,55.
Mesin kalibrasi menggeser bobot 0,85x galat sampai hasil = permintaan.
"""
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))

from app.hitung.kalibrasi_jalur import kalibrasi_per_jalur   # noqa: E402


def jalur_s3(n_x, b_berg=None, b_rantai=0.55):
    """Bentuk jalur S3: rantai antar X + semua X ke Y."""
    Xs = [f"X{i+1}" for i in range(n_x)]
    if b_berg is None:
        b_berg = {x: round(0.30 - 0.04 * i, 3) for i, x in enumerate(Xs)}
    jalur = [{"target": Xs[i + 1], "dari": {Xs[i]: b_rantai}}
             for i in range(n_x - 1)]
    jalur.append({"target": "Y", "dari": dict(b_berg)})
    return jalur, b_berg


def uji(n_x):
    jalur, b_berg = jalur_s3(n_x)
    print(f"\n{'='*66}")
    print(f"S3 BERGANDA-BERANTAI ({n_x} X) — mesin KALIBRASI")
    print('='*66)
    print("permintaan berganda:", b_berg)
    print("permintaan rantai  : 0.55 tiap ruas")

    hasil = kalibrasi_per_jalur(jalur, n_resp=2000, item_per=4, skala=5,
                                toleransi=0.03, maks_putaran=40,
                                lapor=True, seed=42)

    print(f"\nputaran: {hasil['putaran']}   tercapai: {hasil['tercapai']}")
    print("\nHASIL TERUKUR vs PERMINTAAN:")
    terukur = hasil.get('hasil', {})
    print("  ", terukur)
    print("\n  galat: ", {k: round(v, 4) for k, v in
                          (hasil.get('galat') or {}).items()})
    return hasil


if __name__ == '__main__':
    uji(3)
    uji(5)
