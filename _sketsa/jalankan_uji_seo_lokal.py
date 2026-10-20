"""Jalankan uji_seo.py terhadap SERVER UJI LOKAL (:8122), bukan kontainer.

uji_seo.py bawaan menembak kontainer (yang belum di-deploy). Untuk verifikasi
SEBELUM deploy, arahkan ke :8122 lewat variabel BASE_UJI.
"""
import os
import runpy
import sys

os.environ['BASE_UJI'] = 'http://127.0.0.1:8122'
sys.argv = ['uji_seo.py']
runpy.run_path('uji_seo.py', run_name='__main__')
