#!/usr/bin/env bash
# GERBANG UJI — Penelitian STATISTIK Lab. (pembungkus tipis)
#
# Pakai:
#   cd /opt/data/services/statistik-lab && bash gerbang_uji.sh
#
# LULUS/GAGAL dinilai dari EXIT CODE. 0 = aman.
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -x ".venv/bin/python3" ]; then
  echo "❌ venv tidak ada di $DIR/.venv"
  echo "   Buat: uv venv .venv && uv pip install numpy scipy pandas"
  exit 2
fi

exec .venv/bin/python3 gerbang_uji.py
