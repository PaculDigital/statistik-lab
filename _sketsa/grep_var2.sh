#!/usr/bin/env bash
cd /opt/data/services/statistik-lab
echo "=== DAFTAR VARIABEL CSS yang ADA (cari yang hijau/merah/amber) ==="
grep -o -- "--[a-z0-9-]*:" app/static/gaya.css | sort -u | grep -E "hijau|merah|amber|teal|kuning" 
echo
echo "=== kelas catatan-* yang ADA ==="
grep -o "\.catatan[a-z-]*" app/static/gaya.css | sort -u
echo
echo "=== ikon 'gauge'/'shield' di sprite ==="
ls app/static/ikon/
