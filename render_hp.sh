#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# RENDER SCREENSHOT HP — lebar viewport yang BENAR.
#
# ⚠️ JEBAKAN BESAR (17Sep26): `chrome --window-size=390,1750 --screenshot=...`
# TIDAK memberi lebar 390! Chrome headless menolak jendela < ~500px dan tetap
# merender 500px. Terbukti: --window-size=390 → window.innerWidth 500.
#
# Akibatnya screenshot "HP" yang Wulan kirim ke Bos SELALU salah: yang
# dirender 500px, bukan 390px. Bug tampilan HP (tombol + dan preset 8 hilang)
# karena itu tidak pernah tertangkap.
#
# CARA BENAR: bungkus halaman dalam iframe selebar HP, dan sajikan pembungkus
# dari ORIGIN YANG SAMA (http kontainer). Media query di dalam iframe dihitung
# dari lebar iframe, jadi CSS HP benar-benar aktif.
#
# Pakai: bash render_hp.sh 390 [nama_keluaran]
# ═══════════════════════════════════════════════════════════════════════════
set -u
LEBAR="${1:-390}"
NAMA="${2:-hp_${LEBAR}}"
CHROME=/opt/data/home/.cloakbrowser/chromium-146.0.7680.177.5/chrome
KONT=simulasi-olah-data
OUT="$(dirname "$0")/_arsip/shot"
mkdir -p "$OUT"

IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$KONT")
if [ -z "$IP" ]; then echo "❌ kontainer tidak jalan"; exit 1; fi

BUNGKUS="_layar_${LEBAR}.html"
cat > "/tmp/$BUNGKUS" <<HTML
<!DOCTYPE html><meta charset="utf-8"><title>tampilan $LEBAR</title>
<style>
  html,body{margin:0;background:#e8e4dc}
  iframe{display:block;border:0;width:${LEBAR}px;height:1780px;background:#fff}
</style>
<iframe src="/buat-data?uji=x8"></iframe>
HTML
docker cp "/tmp/$BUNGKUS" "$KONT:/app/app/static/$BUNGKUS" >/dev/null

"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --window-size=$((LEBAR + 20)),1800 --force-device-scale-factor=1.4 \
  --virtual-time-budget=16000 \
  --screenshot="$OUT/$NAMA.png" \
  "http://$IP:8000/static/$BUNGKUS" >/dev/null 2>&1

if [ -s "$OUT/$NAMA.png" ]; then
  BYTE=$(wc -c < "$OUT/$NAMA.png")
  echo "  ✅ $NAMA.png  ($BYTE byte)  lebar viewport: ${LEBAR}px"
  .venv/bin/python - <<PY 2>/dev/null || true
import struct
d=open("$OUT/$NAMA.png","rb").read()
w,h=struct.unpack(">II", d[16:24])
print(f"     gambar {w}×{h}px (isi HP = {LEBAR}px + tepi)")
PY
else
  echo "  ❌ $NAMA.png GAGAL"
  exit 1
fi
