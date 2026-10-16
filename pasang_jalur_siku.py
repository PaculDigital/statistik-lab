"""Pasang `_jalur_siku` menggantikan `_geser_ujung_sama`.

🚨 ACC BOS 18Sep26 + GAMBAR contoh (img_694de79f46b4.jpg):
"Garis rantai terakhir mulai dari ujung elips x3 sudut 90 derajat menuju
 panah ke elips tengah variabel Y"

BENTUK (terverifikasi vision atas gambar Bos):
  1. keluar sisi KANAN elips X-terakhir (agak ke bawah)
  2. jalan LURUS MENDATAR ke kanan
  3. BELOK 90° TAJAM (siku-siku) ke atas
  4. masuk sisi BAWAH elips Y

CARA BERSIH: `busur` pada geo boleh berupa STRING 'siku:bx,by' yang
artinya "gambar jalur M(sx,sy) L(bx,by) L(ex,ey)" — bukan kurva.
"""
from pathlib import Path

p = Path('/opt/data/services/statistik-lab/diagram_svg.py')
t = p.read_text(encoding='utf-8')

awal = t.find('    def _geser_ujung_sama(geo, i, j):')
akhir = t.find('    # 🚨 AKAR cacat terukur 18Sep26: label ditaruh di TITIK TENGAH panah.')
assert awal > 0 and akhir > awal, (awal, akhir)

BARU = '''    def _jalur_siku(geo, i, j):
        """Ubah pasangan (asal,tujuan SAMA) jadi: satu diagonal + satu siku.

        🚨 ACC BOS 18Sep26 (contoh gambar img_694de79f46b4.jpg):
          "Garis rantai terakhir mulai dari ujung elips x3 sudut 90
           derajat menuju panah ke elips tengah variabel Y"

        Pasangan yang labelnya H PALING BESAR diberi bentuk SIKU:
          keluar kanan elips X → mendatar ke kanan → belok 90 ke atas
          → masuk bawah elips Y.
        Yang labelnya lebih kecil tetap diagonal biasa (seperti H1/H2).
        Disimpan di geo[i] sebagai busur bertipe teks 'siku:bx,by'.
        """
        def _nomor(gg):
            lab = (gg[0]['label'] or '').upper()
            mm = __import__('re').search(r'H\\s*(\\d+)', lab)
            return int(mm.group(1)) if mm else -1

        # indeks mana yang jadi siku (H terbesar)
        idx_siku = j if _nomor(geo[j]) > _nomor(geo[i]) else i
        gg = geo[idx_siku]
        pp = gg[0]
        c_asal = pusat[pp['dari']]
        c_ke = pusat[pp['ke']]

        # titik keluar: sisi KANAN elips X, sedikit di bawah pusat
        ax = c_asal[0] + rx
        ay = c_asal[1] + ry * 0.45
        # titik belok: segaris mendatar, tepat di bawah titik masuk
        bx = c_ke[0]
        by = ay
        # titik masuk: sisi BAWAH elips Y
        exx = c_ke[0]
        eyy = c_ke[1] + ry
        geo[idx_siku] = (pp, ax, ay, exx, eyy, f'siku:{bx:.1f},{by:.1f}')

'''

t = t[:awal] + BARU + t[akhir:]
# panggilan: _geser_ujung_sama -> _jalur_siku
t = t.replace('_geser_ujung_sama(geo_awal, i, j)', '_jalur_siku(geo_awal, i, j)')
p.write_text(t, encoding='utf-8')
print('OK')
print('panggilan _jalur_siku:', t.count('_jalur_siku'))
