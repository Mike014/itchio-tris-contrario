// client.js
let ws = null;
const out = document.getElementById('out');
const inp = document.getElementById('in');
const btnRun = document.getElementById('run');
const btnStop = document.getElementById('stop');

// stato fasi
const PHASE = { E: true, C: false, O: false };
let playerName = null; // da VAR:io=<nome>

function wsUrl(cmd){
  const u = new URL(location.href);
  u.protocol = u.protocol.replace('http','ws');
  u.pathname = '/ws';
  u.search = '?cmd=' + encodeURIComponent(cmd);
  return u.href;
}

btnRun.onclick  = async () => {
  await ensureNotificationPermission(); // chiedi permesso legato al gesto utente
  start('/python/echo.py');
};
btnStop.onclick = () => stop();

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
      // CLEAR
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

  if (L.startsWith('CLEAR:')) return null;

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

  if (L.startsWith('HINT:'))  return document.createTextNode('💡 ' + L.slice(5).trim());
  if (L.startsWith('ALERT:')) return document.createTextNode('‼ ' + L.slice(6).trim());

  if (L.startsWith('FLAG:')){
    const flag = L.slice(5).trim();
    return document.createTextNode('🏴 Sbloccato: ' + flag);
  }

  if (L.startsWith('VAR:')){
    const payload = L.slice(4).trim();
    const m = /^io\s*=\s*(.+)$/.exec(payload);
    if (m) playerName = m[1].trim();
    return document.createTextNode('[VAR] ' + payload);
  }

  if (L.startsWith('UNLOCK:')){
    const payload = L.slice(7).trim(); // C | O
    onUnlock(payload);
    const span = document.createElement('span');
    span.textContent = '🔓 Sblocco: ' + payload;
    span.dataset.unlock = payload;
    return span;
  }

  return document.createTextNode(raw);
}

/* ------------------------------ PHASE UI -------------------------------- */

function onUnlock(tag){
  if (tag === 'C'){
    PHASE.C = true; PHASE.E = false;
    return;
  }
  if (tag === 'O'){
    PHASE.O = true; PHASE.C = true; PHASE.E = false;
    setEntitaFont(true);
    // NOTA DIEGETICA: messaggio stile ENTITÀ
    const title = 'Dialoghi con un’Eco';
    const body  = entitaMessage(playerName);
    showDesktopNotification(title, body, { tag: 'eco-unlock-o' });
    return;
  }
}

function setEntitaFont(on){
  out.classList.toggle('entita-voice', !!on);
}

function resetPhaseUi(){
  PHASE.E = true; PHASE.C = false; PHASE.O = false;
  setEntitaFont(false);
}

/* --------------------- NOTIFICHE + FALLBACK CROSS-BROWSER ---------------- */

async function ensureNotificationPermission(){
  if (!('Notification' in window)) return 'unsupported';
  const perm = Notification.permission; // granted | denied | default
  if (perm === 'default'){
    try { return await Notification.requestPermission(); }
    catch { return 'default'; }
  }
  return perm;
}

function showInPageToast(message, timeoutMs = 4500){
  const toast = document.createElement('div');
  toast.textContent = message;
  Object.assign(toast.style, {
    position: 'fixed', right: '16px', bottom: '16px',
    maxWidth: '60ch', padding: '10px 12px',
    background: '#111923', color: '#d7e0ea',
    border: '1px solid #263241', borderRadius: '10px',
    boxShadow: '0 8px 28px rgba(0,0,0,.45)', zIndex: 9999,
    font: '14px ui-sans-serif, system-ui'
  });
  document.body.appendChild(toast);
  // dissolve
  setTimeout(()=>{ toast.style.transition='opacity .25s'; toast.style.opacity='0'; }, timeoutMs);
  setTimeout(()=> toast.remove(), timeoutMs + 300);
}

async function showDesktopNotification(title, body, options = {}){
  const opts = { body, silent: false, tag: options.tag || 'eco-note' };
  let nativeShown = false;

  if ('Notification' in window && Notification.permission === 'granted'){
    try{
      const n = new Notification(title, opts);
      n.onclick = () => window.focus();
      nativeShown = true;
    }catch{}
  }

  // Sempre fallback visivo, in caso l'OS blocchi la bolla
  showInPageToast(`${title} — ${body}`);
  return nativeShown;
}

/* --------------------------- COPY ENTITÀ MESSAGE ------------------------- */
/* Genera una singola frase 10–14 parole, tono maligno. Niente virgolette.  */

function entitaMessage(name){
  const base = name && name.trim()
    ? `Ti vedo, ${name}. Mi installo tra i tuoi processi, niente tornerà integro.`
    : `Mi installo tra i tuoi processi, niente tornerà integro.`;
  // lunghezze valide (10–14 parole). Le due frasi rispettano il vincolo.
  return base;
}

/* ------------------------------ UI BINDINGS ----------------------------- */

inp.addEventListener('keydown', (e)=>{
  if (e.key === 'Enter'){
    const s = inp.value;
    inp.value = '';
    print('> ' + s);
    sendLine(s);
  }
});
