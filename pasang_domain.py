#!/usr/bin/env python3
"""Pasang domain statistik.bikinaja.id → kontainer simulasi-olah-data.

Urutan WAJIB (aturan skill cloudflare-api):
  0. BACKUP ingress + DNS record ke _arsip/ SEBELUM mengubah apa pun
  1. Cek DNS record existing (jangan bikin duplikat)
  2. Upsert CNAME → <tunnel>.cfargotunnel.com, proxied=True, ttl=1
  3. GET ingress → sisip route BARU sebelum catch-all 404 → PUT
  4. Set SSL full + Always HTTPS + auto-rewrites
  5. Verifikasi publik (curl dari luar)

Aman dijalankan berulang (idempotent).
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime

VAULT = '/opt/data/vault/cloudflare.json'
ZONE = 'da1822e6237bdf1bc34129e2b4ee5ef7'   # bikinaja.id
TUNNEL = '8ae633d2-4726-47e1-aa5d-1d90fe13ffb1'  # VPS EXA Cloud
HOSTNAME = 'statistik.bikinaja.id'
NAMA_KONTAINER = 'simulasi-olah-data'
PORT_KONTAINER = 8000
ARSIP = '/opt/data/services/statistik-lab/_arsip'

data = json.load(open(VAULT))
TOKEN = data['api_token']
ACC = data['account_id']
BASE = 'https://api.cloudflare.com/client/v4'
H = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}


def api(m, p, b=None, tout=30):
    d = json.dumps(b).encode() if b else None
    req = urllib.request.Request(BASE + p, data=d, method=m, headers=H)
    try:
        with urllib.request.urlopen(req, timeout=tout) as r:
            return True, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read().decode())
        except Exception:
            return False, {'err': f'HTTP {e.code}'}
    except Exception as e:
        return False, {'err': str(e)[:120]}


def ip_container(nama):
    out = subprocess.run(
        ['docker', 'inspect', '-f',
         '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', nama],
        capture_output=True, text=True).stdout.strip()
    return out


print('═' * 66)
print('  PASANG DOMAIN — statistik.bikinaja.id')
print('═' * 66)

# ── 0. BACKUP ──────────────────────────────────────────────────────────────
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
bak = f'{ARSIP}/ingress-pra-domain-{ts}'
os.makedirs(bak, exist_ok=True)

ok, cfg = api('GET', f'/accounts/{ACC}/cfd_tunnel/{TUNNEL}/configurations')
if not ok:
    raise SystemExit(f'❌ gagal baca ingress: {cfg}')
json.dump(cfg, open(f'{bak}/ingress_sebelum.json', 'w'), indent=2)

ok, dns0 = api('GET', f'/zones/{ZONE}/dns_records?name={HOSTNAME}')
json.dump(dns0, open(f'{bak}/dns_sebelum.json', 'w'), indent=2)
print(f'✅ 0/5  Backup: {bak}')

# ── 1. alamat kontainer ────────────────────────────────────────────────────
ip = ip_container(NAMA_KONTAINER)
if not ip:
    raise SystemExit('❌ kontainer tidak jalan')
service = f'http://{ip}:{PORT_KONTAINER}'
print(f'✅ 1/5  Kontainer {NAMA_KONTAINER} → {service}')

# ── 2. DNS CNAME ───────────────────────────────────────────────────────────
rek = [r for r in dns0.get('result', []) if r['name'] == HOSTNAME]
if rek:
    print(f'✅ 2/5  DNS sudah ada ({rek[0]["id"]}) — dilewati')
else:
    ok, res = api('POST', f'/zones/{ZONE}/dns_records', {
        'type': 'CNAME', 'name': HOSTNAME,
        'content': f'{TUNNEL}.cfargotunnel.com',
        'proxied': True, 'ttl': 1})
    if ok:
        print(f'✅ 2/5  DNS CNAME dibuat ({res["result"]["id"]})')
    else:
        raise SystemExit(f'❌ gagal buat DNS: {res}')

# ── 3. INGRESS ─────────────────────────────────────────────────────────────
ingress = cfg['result']['config']['ingress']
lama = [r for r in ingress if r.get('hostname') == HOSTNAME]
sisanya = [r for r in ingress if r.get('hostname') != HOSTNAME]

# pastikan catch-all 404 tetap paling akhir
if not sisanya or sisanya[-1].get('service') != 'http_status:404':
    sisanya.append({'service': 'http_status:404'})

sisanya.insert(-1, {'hostname': HOSTNAME, 'service': service})

ok, res = api('PUT', f'/accounts/{ACC}/cfd_tunnel/{TUNNEL}/configurations',
              {'config': {'ingress': sisanya,
                          'warp-routing': {'enabled': False}}})
if ok:
    aksi = 'diperbarui' if lama else 'ditambahkan'
    print(f'✅ 3/5  Ingress {aksi} → {service}')
else:
    raise SystemExit(f'❌ gagal update ingress: {res}')

# ── 4. Setelan zona ────────────────────────────────────────────────────────
for setelan, nilai in [('ssl', 'full'), ('always_use_https', 'on'),
                       ('automatic_https_rewrites', 'on')]:
    ok, res = api('PATCH', f'/zones/{ZONE}/settings/{setelan}', {'value': nilai})
    print(f'{"✅" if ok else "⚠️ "} 4/5  {setelan} = {nilai}')

json.dump({'hostname': HOSTNAME, 'service': service, 'ip': ip},
          open(f'{ARSIP}/domain_terpasang.json', 'w'), indent=2)

# ── 5. VERIFIKASI PUBLIK ───────────────────────────────────────────────────
print('⏳ 5/5  Verifikasi publik (DNS ~5-30 dtk)...')
kode = '000'
for i in range(1, 9):
    time.sleep(5)
    try:
        req = urllib.request.Request(f'https://{HOSTNAME}/health',
                                     headers={'User-Agent': 'uji/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            kode = str(r.status)
            isi = r.read().decode()[:120]
        print(f'   coba {i}: HTTP {kode} — {isi}')
        break
    except urllib.error.HTTPError as e:
        kode = str(e.code)
        print(f'   coba {i}: HTTP {kode}')
        if e.code in (502, 503, 522):
            time.sleep(5)
            continue
        break
    except Exception as e:
        print(f'   coba {i}: {str(e)[:70]}')

print()
if kode == '200':
    print(f'🎉 SELESAI — https://{HOSTNAME} LIVE')
else:
    print(f'⚠️  HTTP {kode} — DNS/ingress sudah dipasang; tunggu propagasi lalu uji ulang')
