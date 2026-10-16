import json
import sys
sys.path.insert(0, '/opt/data/services/statistik-lab')
from app.hitung.kelompok import buat_data_kelompok
from app.hitung.manova import hitung_manova

d = buat_data_kelompok(n_per_kelompok=30, nama_kelompok=['Kelas A', 'Kelas B'],
                       nama_y=['Minat', 'Nilai'], beda=[0.9, 0.54], seed=7)
r = hitung_manova(d['Y'], d['kelompok'], d['nama_y'])
print('mardia   :', json.dumps(r['asumsi']['mardia'], ensure_ascii=False))
print('pencilan :', json.dumps(r['asumsi']['pencilan'], ensure_ascii=False)[:220])
print('box_m    :', json.dumps(r['asumsi']['box_m'], ensure_ascii=False)[:160])
print('levene[0]:', json.dumps(r['asumsi']['levene'][0], ensure_ascii=False)[:160])
print('statistik:', json.dumps(r['statistik'], ensure_ascii=False)[:200])
print('uji keys :', list(r['uji'].keys()))
print('uji.wilks:', json.dumps(r['uji']['wilks'], ensure_ascii=False))
print('ukur     :', json.dumps(r.get('ukur'), ensure_ascii=False)[:160])

for nm in ('wilks','pillai','hotelling','roy'):
    print(f'{nm:10}', r['uji'][nm])
