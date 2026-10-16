#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# UJI MOBILE FRIENDLY — ukur di lebar layar HP nyata.
#
# ⚠️ PELAJARAN PENTING (17Sep26): Chrome versi chromium-151.0.7922.108.6-pro
# RUSAK — gagal menyimpan screenshot TANPA pesan galat, sehingga Wulan
# mengira sudah mengambil gambar padahal tidak ada berkas. Versi yang
# TERBUKTI BEKERJA: chromium-146.0.7680.177.5.
# ATURAN: WAJIB periksa berkas benar-benar ada (ls) sesudah render.
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail

CHROME="${CHROME:-/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome}"
[ -x "$CHROME" ] || CHROME=/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.4-pro/chrome

IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' simulasi-olah-data)

HP="360x640 375x667 390x844 412x915 768x1024"
HAL="/:beranda /belajar:belajar /buat-data:buatdata /pengaturan:pengaturan"

TOTAL=0; GAGAL=0
echo "═══ UJI MOBILE FRIENDLY — SEMUA UKURAN HP ═══"
echo "   Chrome: $CHROME"
echo "   LULUS bila: GESER<=0, LEBAR=0, KECIL=0, SEMPIT=0"
echo

for u in $HP; do
  w=$(echo "$u" | cut -dx -f1); h=$(echo "$u" | cut -dx -f2)
  echo "── layar ${w}×${h} ──"
  for j in $HAL; do
    jalur="${j%%:*}"; nama="${j##*:}"
    T=$(timeout 150 "$CHROME" --headless --disable-gpu --no-sandbox \
        --window-size="${w},${h}" --virtual-time-budget=9000 --dump-dom \
        "http://$IP:8000/static/ukur.html?w=${w}&p=${jalur}" 2>/dev/null \
        | grep -oP '(?<=<title>)[^<]*' | head -1)

    g=$(echo "$T" | grep -oP '(?<=GESER=)-?\d+')
    l=$(echo "$T" | grep -oP '(?<=LEBAR=)\d+')
    k=$(echo "$T" | grep -oP '(?<=KECIL=)\d+')
    s=$(echo "$T" | grep -oP '(?<=SEMPIT=)\d+')

    TOTAL=$((TOTAL+1))
    if [ "${g:-99}" -le 0 ] && [ "${l:-99}" -eq 0 ] && [ "${k:-99}" -eq 0 ] && [ "${s:-99}" -eq 0 ]; then
      printf "  ✅ %-12s GESER=%s LEBAR=%s KECIL=%s SEMPIT=%s\n" "$nama" "$g" "$l" "$k" "$s"
    else
      GAGAL=$((GAGAL+1))
      printf "  ❌ %-12s GESER=%s LEBAR=%s KECIL=%s SEMPIT=%s\n" "$nama" "$g" "$l" "$k" "$s"
      echo "     → $T"
    fi
  done
  echo
done

echo "═══════════════════════════════════════════"
echo "  TOTAL: $TOTAL halaman-ukuran | LULUS: $((TOTAL-GAGAL)) | GAGAL: $GAGAL"
[ "$GAGAL" -eq 0 ] && echo "  ✅ SEMUA LULUS — mobile friendly" || echo "  ❌ MASIH ADA MASALAH"
exit $([ "$GAGAL" -eq 0 ] && echo 0 || echo 1)
