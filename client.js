let ws = null;
const out = document.getElementById('out');
const inp = document.getElementById('in');
const btnRun = document.getElementById('run');
const btnStop = document.getElementById('stop');

function wsUrl(cmd){
  const u = new URL(location.href);
  u.protocol = u.protocol.replace('http','ws');
  u.pathname = '/ws';
  u.search = '?cmd=' + encodeURIComponent(cmd);
  return u.href;
}

function start(cmd='/python/echo.py'){
  if (ws) return;
  out.textContent = '';
  print(`> python ${cmd}`);
  ws = new WebSocket(wsUrl(cmd));
  ws.onopen   = () => print('[WS] Connesso');
  ws.onmessage= (e) => print(e.data ?? '');
  ws.onerror  = () => print('[WS] Errore');
  ws.onclose  = () => { print('[WS] Chiuso'); ws = null; };
}

function stop(){
  if (!ws) return;
  try { ws.send('!stop'); } catch {}
  try { ws.close(); } catch {}
}

function sendLine(line){
  if (!ws || ws.readyState !== WebSocket.OPEN){
    print('[WS] Non connesso');
    return;
  }
  ws.send(line);
}

/* --------------------------- OUTPUT RENDERING --------------------------- */

function print(s){
  if (s == null) return;
  const lines = String(s).split(/\r?\n/);
  for (const line of lines){
    const node = renderLine(line);
    if (node === null){
      // segnale di CLEAR
      out.textContent = '';
      continue;
    }
    if (node instanceof Node){
      out.appendChild(node);
    } else {
      out.appendChild(document.createTextNode(String(node)));
    }
    out.appendChild(document.createTextNode('\n'));
  }
  out.scrollTop = out.scrollHeight;
}

function renderLine(line){
  const L = String(line).trim();

  if (!L) return document.createTextNode('');

  // Protocollo semplice KIND:payload
  if (L.startsWith('CLEAR:')){
    return null; // handled by print()
  }

  if (L.startsWith('LINK:')){
    const url = L.slice(5).trim();
    const span = document.createElement('span');
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noreferrer';
    a.textContent = url;
    span.appendChild(document.createTextNode('🔗 '));
    span.appendChild(a);
    return span;
  }

  if (L.startsWith('HINT:')){
    const msg = L.slice(5).trim();
    return document.createTextNode('💡 ' + msg);
  }

  if (L.startsWith('ALERT:')){
    const msg = L.slice(6).trim();
    return document.createTextNode('‼ ' + msg);
  }

  // Default: testo grezzo come prima
  return document.createTextNode(line);
}

/* ------------------------------ UI BINDINGS ----------------------------- */

btnRun.onclick  = () => start('/python/echo.py');
btnStop.onclick = () => stop();

inp.addEventListener('keydown', (e)=>{
  if (e.key === 'Enter'){
    const s = inp.value;
    inp.value = '';
    print('> ' + s);
    sendLine(s);
  }
});
