#!/usr/bin/env python3
"""Gambar diagram model penelitian pakai GRAPHVIZ.

KENAPA GRAPHVIZ: Wulan tidak menebak koordinat. Wulan cuma menulis
`X1 -> Z [label="H1"]` dan Graphviz yang MENGHITUNG posisi elips + panah.
Akar semua kegagalan lama = Wulan menghitung posisi sendiri (menebak).

Pakai: python diagram_graphviz.py <berkas.dot> <keluaran.png>
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

DOT = '/opt/data/bin/gv/usr/bin/dot'
LIB = '/opt/data/bin/gv/usr/lib/x86_64-linux-gnu'

# ── Palet sama dengan tema terang-warm aplikasi ──────────────────────
KERTAS = '#FBF8F3'
GARIS = '#6B6259'
TEAL = '#2E7D6F'
AMBER = '#B5762A'


def gambar_dot(isi_dot: str, keluar: Path, fmt: str = 'png') -> tuple[bool, str]:
    """Render DOT → berkas. Kembalikan (berhasil, pesan)."""
    tmp = Path('/tmp/_diagram.dot')
    tmp.write_text(isi_dot, encoding='utf-8')

    proses = subprocess.run(
        [DOT, f'-T{fmt}', '-o', str(keluar), str(tmp)],
        capture_output=True, text=True,
        env={'PATH': '/usr/bin:/bin', 'LD_LIBRARY_PATH': LIB},
    )
    if proses.returncode != 0:
        return False, proses.stderr.strip()
    if not keluar.exists() or keluar.stat().st_size < 1000:
        return False, f'berkas keluaran kosong/terlalu kecil ({keluar})'
    return True, f'{keluar} ({keluar.stat().st_size} byte)'


# ══════════════════════════════════════════════════════════════════════
# MODEL CONTOH BOS — 9 konstruk, 12 hipotesis, 1 NH
# "Model of Goal-Directed Student Decision Quality in Choosing a University"
# ══════════════════════════════════════════════════════════════════════
DOT_BOS = f'''
digraph model {{
  rankdir=LR;              /* kiri ke kanan = arah pengaruh */
  bgcolor="{KERTAS}";
  fontname="Helvetica";
  nodesep=0.55;            /* jarak antar kotak dalam satu kolom */
  ranksep=1.5;             /* jarak antar kolom */
  splines=false;           /* PANAH LURUS — bukan melengkung */

  node [
    shape=ellipse,         /* ELIPS — seperti contoh Bos */
    style="filled",
    fillcolor="white",
    color="{GARIS}",
    fontname="Helvetica",
    fontsize=11,
    penwidth=1.4,
    margin="0.14,0.06"
  ];
  edge [
    color="{GARIS}",
    fontname="Helvetica",
    fontsize=10,
    fontcolor="{GARIS}",
    penwidth=1.3,
    arrowsize=0.8
  ];

  /* ── KOLOM 1: anteseden ── */
  SE [label="Self-efficacy\\n(X1)"];

  /* ── KOLOM 2: goal orientation (3 sejajar) ── */
  MG [label="Mastery Goals\\n(M1)"];
  PG [label="Performance-Approach\\nGoals (M2)"];
  AG [label="Performance-Avoidance\\nGoals (M3)"];

  /* ── KOLOM 3: afektif & kognitif ── */
  PA [label="Positive Affect\\n(M4)"];
  DC [label="Decision Confidence\\n(M5)"];

  /* ── KOLOM 4: kepuasan ── */
  DS [label="Decision Satisfaction\\n(M6)"];

  /* ── KOLOM 5: dua keluaran ── */
  AL [label="Attitudinal Loyalty\\nIntention (Y1)"];
  SL [label="Switching\\nLikelihood (Y2)"];

  /* ── PENGARUH LANGSUNG (H1 … H12) ── */
  SE -> MG [label="H1"];
  SE -> PG [label="H2"];
  SE -> AG [label="NH"];              /* tidak dihipotesiskan */
  MG -> PA [label="H3"];
  PG -> PA [label="H4"];
  AG -> PA [label="H5"];
  MG -> DC [label="H6"];
  PG -> DC [label="H7"];
  AG -> DC [label="H8"];
  PA -> DS [label="H9"];
  DC -> DS [label="H10"];
  DS -> AL [label="H11"];
  DS -> SL [label="H12"];

  /* catatan kaki */
  catatan [
    shape=plaintext, fillcolor="none", color="none",
    label="Note: NH = Not hypothesized", fontsize=9,
    fontcolor="{GARIS}"
  ];
  {{ rank=sink; catatan; }}
}}
'''


def main() -> int:
    keluar = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/model_bos.png')
    ok, pesan = gambar_dot(DOT_BOS, keluar)
    print(('OK   ' if ok else 'GAGAL ') + pesan)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
