#!/usr/bin/env bash
# Bangun & jalankan kontainer UJI di port 8130 (produksi 8120 TIDAK disentuh).
# Tujuan: uji_normalitas.py butuh halaman nyata dari kode BARU.
set -euo pipefail
cd /opt/data/services/statistik-lab

NAMA=statlab-uji
TAG="uji-$(date +%H%M%S)"

echo "▶ 1/4 bangun image"
docker build -q -t "${NAMA}:${TAG}" . >/dev/null
docker tag "${NAMA}:${TAG}" "${NAMA}:terkini"
echo "   ✓ selesai"

echo "▶ 2/4 hentikan kontainer uji lama"
docker rm -f "$NAMA" >/dev/null 2>&1 || true

echo "▶ 3/4 jalankan di port 8130"
docker run -d --name "$NAMA" \
  -p "127.0.0.1:8130:8000" \
  -v "$(pwd)/data:/app/data" \
  "${NAMA}:terkini" >/dev/null

echo "▶ 4/4 tunggu sehat"
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:8130/health" >/dev/null 2>&1; then
    echo "   ✓ sehat setelah ${i}s"
    echo "   kode baru? normalitas=$(
      docker exec "$NAMA" grep -c 'normalitas' /app/app/templates/belajar.html
    )"
    exit 0
  fi
  sleep 1
done
echo "❌ kontainer uji tidak sehat"
docker logs --tail 30 "$NAMA"
exit 1
