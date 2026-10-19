#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# Penelitian STATISTIK Lab. — skrip deploy
#
# ATURAN: deploy produksi WAJIB lewat skrip ini (DILARANG `docker cp app/...`).
# Port host 8120 -> kontainer 8000. Bridge DEFAULT (cloudflared di host).
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

NAMA=simulasi-olah-data
PORT=8120
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TAG="$(date +%Y%m%d_%H%M%S)-statlab"

cd "$DIR"

echo "▶ 1/5  Gerbang uji mesin (WAJIB lulus sebelum deploy)"
if [ -f gerbang_uji.sh ]; then
  bash gerbang_uji.sh || { echo "❌ Gerbang uji GAGAL — deploy dibatalkan."; exit 1; }
  echo "   ✓ Gerbang uji LULUS"
else
  echo "   ⚠️  gerbang_uji.sh tidak ada — dilewati (Fase 1)"
fi

echo "▶ 2/5  Bangun image ${NAMA}:${TAG}"
docker build -q -t "${NAMA}:${TAG}" . >/dev/null
docker tag "${NAMA}:${TAG}" "${NAMA}:terkini"
echo "   ✓ Image siap"

echo "▶ 3/5  Hentikan kontainer lama (kalau ada)"
docker rm -f "$NAMA" >/dev/null 2>&1 || true
echo "   ✓ Bersih"

echo "▶ 4/5  Jalankan kontainer"
# ── Kunci AI (opsional) — dibaca dari .env di folder ini, JANGAN dari repo ──
# ⚠️ Tanpa kunci, modul AI mati dengan pesan jujur (503 + mode manual),
#    bukan error. Jadi deploy tetap jalan walau .env belum ada.
ENV_AI=()
if [ -f "${DIR}/.env" ]; then
  for VAR in ROUTER9_API_KEY ROUTER9_BASE ROUTER9_MODEL; do
    NILAI=$(grep -E "^${VAR}=" "${DIR}/.env" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
    if [ -n "${NILAI}" ]; then
      ENV_AI+=(-e "${VAR}=${NILAI}")
      echo "   ✓ ${VAR} disuntik dari .env"
    fi
  done
  [ ${#ENV_AI[@]} -eq 0 ] && echo "   ⚠️  .env ada tapi tidak memuat ROUTER9_* — AI akan mati (503 jujur)"
else
  echo "   ⚠️  ${DIR}/.env tidak ada — AI akan mati (503 jujur, mode manual tetap jalan)"
fi

docker run -d --name "$NAMA" \
  --restart unless-stopped \
  -p "127.0.0.1:${PORT}:8000" \
  -v "${DIR}/data:/app/data" \
  "${ENV_AI[@]}" \
  --health-cmd "python -c \"import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=4).status==200 else 1)\"" \
  --health-interval 30s --health-timeout 5s --health-retries 3 \
  "${NAMA}:${TAG}" >/dev/null
echo "   ✓ Kontainer jalan: ${NAMA} (port ${PORT})"

echo "▶ 5/5  Verifikasi"
# ⚠️ curl dari Wulan TIDAK BISA ke 127.0.0.1:PORT (loopback container Hermes,
#    bukan VPS). Karena itu verifikasi lewat `docker exec` ke dalam kontainer —
#    itu jalur yang benar dan tidak menipu.
LULUS=0
for i in $(seq 1 45); do
  if docker exec "${NAMA}" python -c "
import urllib.request, sys
try:
    r = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)
    sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)" >/dev/null 2>&1; then
    echo "   ✓ /health menjawab (dari dalam kontainer):"
    docker exec "${NAMA}" python -c "
import urllib.request
print('     ' + urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read().decode())"
    LULUS=1
    break
  fi
  sleep 2
done

if [ "$LULUS" = "1" ]; then
  echo
  echo "✅ SELESAI — ${NAMA} LIVE di port ${PORT}"
  echo "   Domain (setelah ingress dipasang): statistik.bikinaja.id"
  exit 0
fi

echo "❌ Kontainer tidak menjawab /health dalam 90 detik."
echo "   Periksa: docker logs ${NAMA}"
exit 1
