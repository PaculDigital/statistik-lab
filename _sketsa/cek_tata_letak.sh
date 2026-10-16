#!/usr/bin/env bash
# Jalankan grup tata letak SENDIRIAN (tidak berbarengan dengan grup lain).
cd /opt/data/services/statistik-lab || exit 1
for i in 1 2; do
  printf "  percobaan %d: " "$i"
  timeout 250 .venv/bin/python gerbang_tata_letak.py > "/tmp/tl$i.txt" 2>&1
  rc=$?
  masalah=$(grep -c "❌" "/tmp/tl$i.txt" 2>/dev/null || echo "?")
  echo "EXIT=$rc  masalah=$masalah"
done
