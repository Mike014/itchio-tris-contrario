let ws = null;
const out = document.getElementById('out');
const inp = document.getElementById('in');
const btnRun = document.getElementById('run');
const btnStop = document.getElementById('stop');

function print(s){ out.textContent += s + (s.endsWith('\n')?'':'\n'); out.scrollTop = out.scrollHeight; }
function wsUrl(cmd){ const u=new URL(location.href); u.protocol=u.protocol.replace('http','ws'); u.pathname='/ws'; u.search='?cmd='+encodeURIComponent(cmd); return u.href; }

function start(cmd='/python/echo.py'){
  if(ws) return;
  out.textContent = '';
  print(`> python ${cmd}`);
  ws = new WebSocket(wsUrl(cmd));
  ws.onopen = () => print('[WS] Connesso');
  ws.onmessage = (e) => print(e.data ?? '');
  ws.onerror = (e) => print('[WS] Errore');
  ws.onclose = () => { print('[WS] Chiuso'); ws = null; };
}
function stop(){
  if(!ws) return;
  try { ws.send('!stop'); } catch{}
  try { ws.close(); } catch{}
}
function sendLine(line){
  if(!ws || ws.readyState!==WebSocket.OPEN){ print('[WS] Non connesso'); return; }
  ws.send(line);
}

btnRun.onclick = () => start('/python/Tris-Al-Contrario.py');
btnStop.onclick = () => stop();

inp.addEventListener('keydown', (e)=>{
  if(e.key==='Enter'){
    const s = inp.value; inp.value='';
    print('> ' + s);
    sendLine(s);
  }
});
