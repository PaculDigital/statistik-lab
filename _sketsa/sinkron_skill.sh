#!/usr/bin/env bash
# Bandingkan SEMUA berkas yang disalin ke skill: proyek vs skill.
S=/opt/data/skills/penelitian-ilmiah/statistik-lab
cd /opt/data/services/statistik-lab || exit 1

BERKAS="uji_bahan_gambar.py uji_alat_ukur_grafik.py uji_web_grafik.py \
uji_tombol_contoh.py uji_tab_baca_grafik.py uji_grafik_hidup.js gerbang_uji.py"

echo "════════ sinkron proyek → skill ════════"
beda=0
for f in $BERKAS; do
  p=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
  s=$(md5sum "$S/scripts/$f" 2>/dev/null | cut -d' ' -f1)
  if [ "$p" = "$s" ] && [ -n "$p" ]; then
    printf "  ✅ %-28s sama\n" "$f"
  else
    printf "  ❌ %-28s BEDA\n" "$f"
    beda=$((beda+1))
  fi
done

echo
d=$(md5sum DOKUMENTASI_TAHAP_2_GRAFIK_HIDUP_20SEP2026.md | cut -d' ' -f1)
e=$(md5sum "$S/references/DOKUMENTASI_TAHAP_2_GRAFIK_HIDUP_20SEP2026.md" | cut -d' ' -f1)
if [ "$d" = "$e" ]; then
  echo "  ✅ DOKUMENTASI_TAHAP_2_...md sama"
else
  echo "  ❌ DOKUMENTASI_TAHAP_2_...md BEDA"
  beda=$((beda+1))
fi

echo
if [ "$beda" -eq 0 ]; then
  echo "  ✅ SEMUA SINKRON"
  exit 0
else
  echo "  ❌ $beda berkas BEDA"
  exit 1
fi
