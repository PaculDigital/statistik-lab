#!/usr/bin/env bash
# Uji E2E dari DALAM kontainer (aturan: 127.0.0.1 di host = loopback container).
set -uo pipefail
N=simulasi-olah-data
LULUS=0; GAGAL=0
cek() { # nama  harapan  dapat
  if [ "$2" = "$3" ]; then echo "  ✅ $1 ($3)"; LULUS=$((LULUS+1));
  else echo "  ❌ $1 — harap '$2', dapat '$3'"; GAGAL=$((GAGAL+1)); fi
}
py() { docker exec "$N" python -c "$1"; }

echo "═══ 1. HALAMAN ═══"
for u in / /belajar /buat-data /pengaturan /segera/klinik; do
  k=$(py "import urllib.request
print(urllib.request.urlopen('http://127.0.0.1:8000$u',timeout=10).status)")
  cek "GET $u" "200" "$k"
done

echo
echo "═══ 2. SPRITE IKON ═══"
sym=$(py "import urllib.request
h=urllib.request.urlopen('http://127.0.0.1:8000/belajar',timeout=10).read().decode()
print(h.count('<symbol id='))")
cek "symbol dalam sprite" "87" "$sym"
ikon=$(py "import urllib.request
h=urllib.request.urlopen('http://127.0.0.1:8000/belajar',timeout=10).read().decode()
print(1 if h.count('class=\"ik\"')>0 else 0)")
cek "ikon terpakai di halaman" "1" "$ikon"

echo
echo "═══ 3. API BUAT-DATA (3 mode) ═══"
docker cp /opt/data/services/statistik-lab/uji_web_data.py "$N":/tmp/u.py >/dev/null
docker exec "$N" python /tmp/u.py
[ $? -eq 0 ] && LULUS=$((LULUS+4)) || GAGAL=$((GAGAL+4))

echo
echo "═══ 4. UNDUHAN (buat data DULU) ═══"
py "import json, urllib.request
d=json.dumps({'n':100,'x':2,'beta':[0.30,0.20],'skala':5,'alpha':0.85,'mode':'presisi'}).encode()
r=urllib.request.Request('http://127.0.0.1:8000/api/buat-data',data=d,headers={'Content-Type':'application/json'})
urllib.request.urlopen(r,timeout=180).read()
print('  data dibuat untuk bahan unduhan')" >/dev/null
for b in csv xlsx; do
  k=$(py "import urllib.request
print(urllib.request.urlopen('http://127.0.0.1:8000/api/unduh?bentuk=$b',timeout=30).status)")
  cek "unduh $b" "200" "$k"
done

echo
echo "═══ 5. TAHAN RESTART ═══"
docker restart "$N" >/dev/null
for i in $(seq 1 30); do
  py "import urllib.request,sys
try: sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=3).status==200 else 1)
except Exception: sys.exit(1)" 2>/dev/null && break
  sleep 1
done
k=$(py "import urllib.request
print(urllib.request.urlopen('http://127.0.0.1:8000/api/unduh?bentuk=csv',timeout=30).status)")
cek "unduh csv sesudah restart" "200" "$k"

echo
echo "═══ 6. SAKLAR AI ═══"
on=$(py "import json,urllib.request
d=json.dumps({'aktif':True}).encode()
r=urllib.request.Request('http://127.0.0.1:8000/api/ai',data=d,headers={'Content-Type':'application/json'})
print(json.loads(urllib.request.urlopen(r,timeout=10).read())['ai_aktif'])")
cek "nyalakan AI" "True" "$on"
off=$(py "import json,urllib.request
d=json.dumps({'aktif':False}).encode()
r=urllib.request.Request('http://127.0.0.1:8000/api/ai',data=d,headers={'Content-Type':'application/json'})
print(json.loads(urllib.request.urlopen(r,timeout=10).read())['ai_aktif'])")
cek "matikan AI" "False" "$off"

echo
echo "════════════════════════════════════════"
echo " TOTAL: $LULUS LULUS / $GAGAL GAGAL"
echo "════════════════════════════════════════"
[ "$GAGAL" -eq 0 ] && exit 0 || exit 1
