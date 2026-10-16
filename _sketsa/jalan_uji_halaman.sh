#!/usr/bin/env bash
# Jalankan 3 uji halaman (grafik, tombol contoh, tab Baca Grafik).
# EXIT 0 = ketiganya lulus. Dinilai dari EXIT CODE, bukan grep teks.
cd /opt/data/services/statistik-lab
TOTAL=0
for u in uji_web_grafik.py uji_tombol_contoh.py uji_tab_baca_grafik.py; do
  printf "  %-26s " "$u"
  .venv/bin/python "$u" > /tmp/uji_$$.txt 2>&1
  rc=$?
  ringkas=$(grep -E "LULUS|GAGAL" /tmp/uji_$$.txt | tail -1 | tr -d '\r')
  echo "EXIT=$rc  $ringkas"
  TOTAL=$((TOTAL + rc))
done
rm -f /tmp/uji_$$.txt
echo
echo "  TOTAL_EXIT=$TOTAL"
exit $TOTAL
