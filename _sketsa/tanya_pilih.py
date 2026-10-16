import json, subprocess, time, urllib.request, sys
from pathlib import Path
import websocket
CH = '/opt/data/home/.cloakbrowser/chromium-151.0.7922.108.6-pro/chrome'
P = 9342
subprocess.run(['pkill','-f',f'remote-debugging-port={P}'],capture_output=True); time.sleep(1)
c = subprocess.Popen([CH,'--headless=new','--no-sandbox','--disable-gpu',
  f'--remote-debugging-port={P}','--remote-allow-origins=*','--window-size=390,900'],
  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(40):
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{P}/json/version',timeout=2); break
    except Exception: time.sleep(0.5)
req = urllib.request.Request(f'http://127.0.0.1:{P}/json/new', method='PUT')
d = json.loads(urllib.request.urlopen(req,timeout=20).read())
ws = websocket.create_connection(d['webSocketDebuggerUrl'],timeout=30)
n=[0]
def js(e):
    n[0]+=1; mid=n[0]
    ws.send(json.dumps({'id':mid,'method':'Runtime.evaluate','params':{'expression':e,'returnByValue':True,'awaitPromise':True}}))
    while True:
        m=json.loads(ws.recv())
        if m.get('id')==mid:
            r=m.get('result',{})
            if 'exceptionDetails' in r: return {'__err__':str(r['exceptionDetails'])[:400]}
            return r.get('result',{}).get('value')
js("1")
js("Page.enable")
# tangkap galat sebelum navigasi
js("window.__e=[];window.addEventListener('error',e=>window.__e.push(String(e.message)));")
urllib.request.urlopen(f'http://127.0.0.1:{P}/json/close/{d["id"]}') if False else None
ws.close()
# tab asli dengan penangkap galat terpasang lewat evaluate di dokumen baru
req2 = urllib.request.Request(f'http://127.0.0.1:{P}/json/new?http://127.0.0.1:8122/belajar', method='PUT')
d2 = json.loads(urllib.request.urlopen(req2,timeout=20).read())
ws2 = websocket.create_connection(d2['webSocketDebuggerUrl'],timeout=30)
n2=[0]
def js2(e):
    n2[0]+=1; mid=n2[0]
    ws2.send(json.dumps({'id':mid,'method':'Runtime.evaluate','params':{'expression':e,'returnByValue':True,'awaitPromise':True}}))
    while True:
        m=json.loads(ws2.recv())
        if m.get('id')==mid:
            r=m.get('result',{})
            if 'exceptionDetails' in r: return {'__err__':str(r['exceptionDetails'])[:400]}
            return r.get('result',{}).get('value')
time.sleep(4)
print('1. KAMUS ada? ', js2("typeof KAMUS"))
print('2. kunci KAMUS : ', js2("Object.keys(KAMUS).join(',')"))
print('3. typeof pilih : ', js2("typeof pilih"))
print('4. PIKIR LANGSUNG pilih(normalitas):')
print('   hasil ->', js2("(()=>{try{pilih('normalitas');return 'OK'}catch(e){return 'GALAT: '+e.message}})()"))
print('5. setelah itu: judul=', js2("document.getElementById('judul').textContent"))
print('   slider min=', js2("document.getElementById('slider').min"))
print('   batang    =', js2("document.getElementById('grafik').querySelectorAll('rect').length"))
print('6. galat yang tidak tertangkap:')
print('   ', js2("(window.__e||[]).join(' | ')"))
c.terminate()
