#!/usr/bin/env bash
# Bersihkan Chrome yang masih menahan port debug, lalu render mockup via CDP.
set -u
pkill -f "remote-debugging-port=9331" 2>/dev/null
sleep 1
echo "sisa chrome: $(pgrep -fc chromium-146 || echo 0)"
cd /opt/data/services/statistik-lab
.venv/bin/python render_mockup_cdp.py
echo "EXIT=$?"
