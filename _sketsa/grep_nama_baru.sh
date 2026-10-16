#!/usr/bin/env bash
# GREP DULU sebelum pakai nama apa pun (aturan Bos 19Sep26)
cd /opt/data/services/statistik-lab
echo "=== kelas yang mau dipakai — ADA atau TIDAK? ==="
for k in saklar-pintasan pintasan pokok kepala-pokok catatan hijau kenapa-kotak daftar-kenapa medan renggang pita-hijau pita-amber pita-merah pita-abu; do
  n=$(grep -c "\.$k" app/static/gaya.css)
  echo "  .$k -> $n"
done
echo
echo "=== variabel CSS yang mau dipakai ==="
for v in hijau-bg hijau merah-bg merah teal-terang garis kertas-2 tinta-2; do
  n=$(grep -c -- "--$v:" app/static/gaya.css)
  echo "  --$v -> $n"
done
echo
echo "=== ikon yang mau dipakai ==="
for i in bell activity trending-up percent bar-chart-3 boxes shield-check alert-circle info lightbulb help-circle book-open flask-conical; do
  n=$(grep -c "id=\"ik-$i\"" app/static/ikon/*.svg 2>/dev/null || echo 0)
  echo "  ik-$i -> $n"
done
