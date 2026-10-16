#!/usr/bin/env bash
cd /opt/data/services/statistik-lab
echo "=== UKURAN & HITUNG TAG belajar.html ==="
wc -l -c app/templates/belajar.html
echo "script buka : $(grep -c '<script' app/templates/belajar.html)"
echo "script tutup: $(grep -c '</script>' app/templates/belajar.html)"
echo "block jinja : $(grep -c '{% block' app/templates/belajar.html)"
echo "endblock    : $(grep -c '{% endblock' app/templates/belajar.html)"
echo "svg buka    : $(grep -o '<svg' app/templates/belajar.html | wc -l)"
echo "svg tutup   : $(grep -o '</svg>' app/templates/belajar.html | wc -l)"
echo "kartu-ujit  : $(grep -c 'kartu-ujit' app/templates/belajar.html)"
echo "pilih(      : $(grep -c 'pilih(' app/templates/belajar.html)"
