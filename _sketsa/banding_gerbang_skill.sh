#!/usr/bin/env bash
# Bandingkan gerbang_uji.py versi PROYEK vs versi SKILL.
S=/opt/data/skills/penelitian-ilmiah/statistik-lab
cd /opt/data/services/statistik-lab || exit 1

echo "════════ gerbang_uji.py: proyek vs skill ════════"
printf "  proyek: %s byte · %s grup · BATAS_GRUP=%s\n" \
  "$(stat -c%s gerbang_uji.py)" \
  "$(grep -cE '^    \("' gerbang_uji.py)" \
  "$(grep -c BATAS_GRUP gerbang_uji.py)"
printf "  skill : %s byte · %s grup · BATAS_GRUP=%s\n" \
  "$(stat -c%s $S/scripts/gerbang_uji.py)" \
  "$(grep -cE '^    \("' $S/scripts/gerbang_uji.py)" \
  "$(grep -c BATAS_GRUP $S/scripts/gerbang_uji.py)"
