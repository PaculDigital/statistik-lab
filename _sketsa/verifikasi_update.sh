#!/usr/bin/env bash
# VERIFIKASI AKHIR setelah update dokumentasi/skill/script/memori (20Sep26).
cd /opt/data/services/statistik-lab || exit 1
S=/opt/data/skills/penelitian-ilmiah/statistik-lab
GAGAL=0

echo "════════ 1. SOT (dokumen cocok dengan kode?) ════════"
.venv/bin/python sot.py --periksa > /tmp/sot.txt 2>&1
if grep -q "SOT SELARAS" /tmp/sot.txt; then
  echo "  ✅ SOT SELARAS"
else
  echo "  ❌ SOT TIDAK SELARAS"
  tail -6 /tmp/sot.txt
  GAGAL=$((GAGAL+1))
fi

echo
echo "════════ 2. sinkron proyek → skill ════════"
bash _sketsa/sinkron_skill.sh > /tmp/sink.txt 2>&1
if grep -q "SEMUA SINKRON" /tmp/sink.txt; then
  echo "  ✅ SEMUA SINKRON ($(grep -c '✅' /tmp/sink.txt) berkas)"
else
  echo "  ❌ ADA YANG BEDA"
  grep "❌" /tmp/sink.txt
  GAGAL=$((GAGAL+1))
fi

echo
echo "════════ 3. pindai rahasia di dokumen + skill ════════"
N=$(grep -rniE "password|passwd|api[_-]?key|secret={0,1}[a-z0-9]|token={0,1}[a-z0-9]|secure_link|cfut_|bearer [a-z0-9]|sk-[a-z0-9]{10}|-----BEGIN" \
  DOKUMENTASI_TAHAP_2*.md "$S/SKILL.md" 2>/dev/null | wc -l)
if [ "$N" -eq 0 ]; then
  echo "  ✅ bersih (0 temuan)"
else
  echo "  ❌ $N temuan — PERIKSA"
  grep -rniE "password|api[_-]?key|secret|token|secure_link|cfut_|bearer |sk-[a-z0-9]{10}|-----BEGIN" \
    DOKUMENTASI_TAHAP_2*.md "$S/SKILL.md" 2>/dev/null | head -5
  GAGAL=$((GAGAL+1))
fi

echo
echo "════════ 4. jumlah grup: kode vs dokumen ════════"
K=$(grep -cE '^    \("' gerbang_uji.py)
M=$(grep -oE "31 grup" MASTER_PLAN.md | head -1)
F=$(grep -oE "31 grup" FLAG_LANJUT_DISINI.md | head -1)
printf "  kode: %s grup · MASTER_PLAN: %s · FLAG: %s\n" "$K" "${M:-TIDAK ADA}" "${F:-TIDAK ADA}"
if [ "$K" = "31" ] && [ -n "$M" ] && [ -n "$F" ]; then
  echo "  ✅ cocok"
else
  echo "  ❌ TIDAK COCOK"
  GAGAL=$((GAGAL+1))
fi

echo
echo "════════ 5. SKILL.md memuat blok baru? ════════"
for pola in "TAHAP 2.1 SELESAI" "ATURAN KERAS GERBANG UJI" "const n = idx.length" "BATAS_GRUP = 150"; do
  if grep -q "$pola" "$S/SKILL.md"; then
    printf "  ✅ %s\n" "$pola"
  else
    printf "  ❌ %s TIDAK ADA\n" "$pola"
    GAGAL=$((GAGAL+1))
  fi
done

echo
echo "═══════════════════════════════════════════════════════════════"
if [ "$GAGAL" -eq 0 ]; then
  echo "  ✅ SEMUA VERIFIKASI LULUS"
  exit 0
else
  echo "  ❌ $GAGAL pemeriksaan GAGAL"
  exit 1
fi
