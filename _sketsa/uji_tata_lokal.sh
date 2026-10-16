#!/usr/bin/env bash
# Jalankan gerbang_tata_letak.py terhadap SERVER UJI (bukan kontainer produksi).
#
# ⚠️ MENGAPA (20Sep26): perubahan `app/static/ukur_tata.html` hanya terbaca
# setelah image dibangun ulang. Supaya bisa diuji SEBELUM deploy, gerbang
# diarahkan ke server uji :8140 lewat variabel TATA_IP.
#
# Pakai: bash _sketsa/uji_tata_lokal.sh
set -u
cd /opt/data/services/statistik-lab

# Gerbang membaca IP kontainer lewat `docker inspect`. Untuk server lokal,
# kita tipu dengan nama kontainer sementara? TIDAK — lebih bersih: jalankan
# langsung modulnya dengan IP ditimpa lewat env.
TATA_IP="127.0.0.1" TATA_PORT="8140" .venv/bin/python - "$@" <<'PYEOF'
import os, sys
sys.argv = ['gerbang_tata_letak.py']
os.environ['TATA_IP'] = '127.0.0.1'
os.environ['TATA_PORT'] = '8140'
import runpy
runpy.run_path('gerbang_tata_letak.py', run_name='__main__')
PYEOF
