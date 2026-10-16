#!/usr/bin/env bash
# Perbarui catatan: MASTER_PLAN §9 sudah disamakan + SOT kini menjaga urutan tahap.
set -e
cd /opt/data/services/statistik-lab

echo "════════ 1. SOT ════════"
.venv/bin/python sot.py --periksa 2>&1 | tail -2

echo
echo "════════ 2. gerbang penuh (dari log gchk10) ════════"
tail -3 /opt/data/gchk10.txt

echo
echo "════════ 3. bukti penjaga urutan tahap bergigi ════════"
.venv/bin/python _sketsa/bukti_urutan_tahap.py 2>&1 | tail -4
