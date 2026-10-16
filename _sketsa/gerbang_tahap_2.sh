#!/usr/bin/env bash
# Jalankan SEMUA gerbang yang terdampak Tahap 2.1 (grafik hidup).
# EXIT 0 = semua bersih. Tiap gerbang dinilai dari EXIT CODE, bukan grep teks.
set -u
cd /opt/data/services/statistik-lab || exit 1

GAGAL=0

jalankan() {
  nama="$1"; shift
  out="/tmp/gate_$(echo "$nama" | tr -c 'a-zA-Z0-9' '_').txt"
  "$@" > "$out" 2>&1
  kode=$?
  ringkas=$(grep -oE 'LULUS SEMUA: [0-9]+|LULUS / [0-9]+ GAGAL|SEMUA TEMPLATE SEHAT|0 pelanggaran' "$out" | tail -1)
  if [ "$kode" -eq 0 ]; then
    printf '  ✅ %-24s EXIT 0   %s\n' "$nama" "$ringkas"
  else
    printf '  ❌ %-24s EXIT %s  %s\n' "$nama" "$kode" "$ringkas"
    GAGAL=$((GAGAL + 1))
  fi
}

echo "═══ GERBANG TAHAP 2.1 ═══"
jalankan "sintaks_js"      .venv/bin/python gerbang_sintaks_js.py
jalankan "tag_skrip"       .venv/bin/python gerbang_tag_skrip.py
jalankan "jinja"           .venv/bin/python gerbang_jinja.py
jalankan "bahan_gambar"    .venv/bin/python uji_bahan_gambar.py
jalankan "grafik_hidup"    node uji_grafik_hidup.js

echo
if [ "$GAGAL" -eq 0 ]; then
  echo "  ✅ SEMUA GERBANG LULUS (EXIT 0)"
  exit 0
fi
echo "  ❌ $GAGAL gerbang GAGAL"
exit 1
