// client.js
let ws = null;
const out = document.getElementById('out');
const inp = document.getElementById('in');
const btnRun = document.getElementById('run');
const btnStop = document.getElementById('stop');

// stato semplice per sblocchi
const PHASE = { E: true, C: false, O: false }; // E parte attiva per default
let playerName = null; // da VAR:io=<nome>

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
  ws.onopen    = () => print('[WS] Connesso');
  ws.onmessage = (e) => print(e.data ?? '');
  ws.onerror   = () => print('[WS] Errore');
  ws.onclose   = () => { print('[WS] Chiuso'); ws = null; resetPhaseUi(); };
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
      // segnale CLEAR
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
  const raw = String(line);
  const L = raw.trim();
  if (!L) return document.createTextNode('');

  // CLEAR:
  if (L.startsWith('CLEAR:')) return null;

  // LINK:
  if (L.startsWith('LINK:')){
    const url = L.slice(5).trim();
    const span = document.createElement('span');
    const a = document.createElement('a');
    a.href = url; a.target = '_blank'; a.rel = 'noreferrer';
    a.textContent = url;
    span.appendChild(document.createTextNode('🔗 '));
    span.appendChild(a);
    return span;
  }

  // HINT:
  if (L.startsWith('HINT:')){
    return document.createTextNode('💡 ' + L.slice(5).trim());
  }

  // ALERT:
  if (L.startsWith('ALERT:')){
    return document.createTextNode('‼ ' + L.slice(6).trim());
  }

  // FLAG:
  if (L.startsWith('FLAG:')){
    const flag = L.slice(5).trim();
    return document.createTextNode('🏴 Sbloccato: ' + flag);
  }

  // VAR: (es. VAR:io=<nome>)
  if (L.startsWith('VAR:')){
    const payload = L.slice(4).trim();
    const m = /^io\s*=\s*(.+)$/.exec(payload);
    if (m) {
      playerName = m[1].trim();
    }
    return document.createTextNode('[VAR] ' + payload);
  }

  // UNLOCK:
  if (L.startsWith('UNLOCK:')){
    const payload = L.slice(7).trim(); // C | O | ecc.
    onUnlock(payload);
    const span = document.createElement('span');
    span.textContent = '🔓 Sblocco: ' + payload;
    span.dataset.unlock = payload;
    return span;
  }

  // default: testo grezzo
  return document.createTextNode(raw);
}

/* ------------------------------ PHASE UI -------------------------------- */

function onUnlock(tag){
  if (tag === 'C'){
    PHASE.C = true; PHASE.E = false;
    // nessun cambio font qui — avviene solo su O
    return;
  }
  if (tag === 'O'){
    PHASE.O = true; PHASE.C = true; PHASE.E = false;
    // cambia font quando la fase O è sbloccata (cioè dopo aver superato E e C)
    setEntitaFont(true);
    return;
  }
}

function setEntitaFont(on){
  out.classList.toggle('entita-voice', !!on);
}

function resetPhaseUi(){
  // quando chiudiamo la WS, torniamo allo stato base
  PHASE.E = true; PHASE.C = false; PHASE.O = false;
  setEntitaFont(false);
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
