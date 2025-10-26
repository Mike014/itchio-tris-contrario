// client.js
let ws = null;
const out = document.getElementById('out');
const inp = document.getElementById('in');
const btnRun = document.getElementById('run');
const btnStop = document.getElementById('stop');

// phase state
const PHASE = { E: true, C: false, O: false };
let playerName = null; // from VAR:io=<name>

function wsUrl(cmd){
  const u = new URL(location.href);
  u.protocol = u.protocol.replace('http','ws');
  u.pathname = '/ws';
  u.search = '?cmd=' + encodeURIComponent(cmd);
  return u.href;
}

btnRun.onclick  = async () => {
  await ensureNotificationPermission(); // ask permission tied to user gesture
  start('/python/echo.py');
};
btnStop.onclick = () => stop();

function start(cmd='/python/echo.py'){
  if (ws) return;
  out.textContent = '';
  print(`> python ${cmd}`);
  ws = new WebSocket(wsUrl(cmd));
  ws.onopen    = () => print('[WS] Connected');
  ws.onmessage = (e) => print(e.data ?? '');
  ws.onerror   = () => print('[WS] Error');
  ws.onclose   = () => { print('[WS] Closed'); ws = null; resetPhaseUi(); };
}

function stop(){
  if (!ws) return;
  try { ws.send('!stop'); } catch {}
  try { ws.close(); } catch {}
}

function sendLine(line){
  if (!ws || ws.readyState !== WebSocket.OPEN){
    print('[WS] Not connected');
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
    return document.createTextNode('🏴 Unlocked: ' + flag);
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
    span.textContent = '🔓 Unlock: ' + payload;
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
    // DIEGETIC NOTE: ENTITÀ-style message + icon
    const title = 'Dialoghi con un’Eco';
    const body  = entitaMessage(playerName);
    showDesktopNotification(title, body, {
      tag: 'eco-unlock-o',
      icon: 'assets/logo.ico',
      badge: 'assets/logo.ico'
    });
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

/* --------------------- NOTIFICATIONS + CROSS-BROWSER FALLBACK ------------ */

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
  setTimeout(()=>{ toast.style.transition='opacity .25s'; toast.style.opacity='0'; }, timeoutMs);
  setTimeout(()=> toast.remove(), timeoutMs + 300);
}

// Toast with icon (used by the notification fallback)
function showInPageToastWithIcon(title, body, iconUrl){
  const wrap = document.createElement('div');
  Object.assign(wrap.style, {
    position:'fixed', right:'16px', bottom:'16px', zIndex:9999,
    maxWidth:'68ch', background:'#111923', color:'#d7e0ea',
    border:'1px solid #263241', borderRadius:'10px',
    boxShadow:'0 8px 28px rgba(0,0,0,.45)', display:'flex', gap:'10px',
    padding:'10px 12px', alignItems:'flex-start', font:'14px ui-sans-serif, system-ui'
  });

  if (iconUrl){
    const img = document.createElement('img');
    img.src = iconUrl;
    img.alt = '';
    img.width = 32; img.height = 32;
    img.style.cssText = 'flex:0 0 32px; width:32px; height:32px; filter:drop-shadow(0 1px 2px rgba(0,0,0,.35));';
    wrap.appendChild(img);
  }

  const text = document.createElement('div');
  const titleEl = document.createElement('div');
  titleEl.textContent = title;
  titleEl.style.cssText = 'font-weight:700; margin-bottom:2px;';
  const bodyEl = document.createElement('div');
  bodyEl.textContent = body;
  text.appendChild(titleEl);
  text.appendChild(bodyEl);
  wrap.appendChild(text);

  document.body.appendChild(wrap);
  setTimeout(()=>{ wrap.style.transition='opacity .25s'; wrap.style.opacity='0'; }, 4500);
  setTimeout(()=> wrap.remove(), 4800);
}

async function showDesktopNotification(title, body, options = {}){
  const opts = {
    body,
    silent: false,
    tag: options.tag || 'eco-note',
    icon: options.icon || 'assets/logo.ico',
    badge: options.badge || options.icon || 'assets/logo.ico'
  };

  let nativeShown = false;

  if ('Notification' in window && Notification.permission === 'granted'){
    try{
      const n = new Notification(title, opts);
      n.onclick = () => window.focus();
      nativeShown = true;
    }catch{}
  }

  // Always show visual fallback (covers OS DND / suppressed bubbles)
  showInPageToastWithIcon(title, body, opts.icon);

  return nativeShown;
}

/* --------------------------- ENTITÀ MESSAGE COPY ------------------------- */
/* Short line, unsettling tone; use the name if available.                   */

function entitaMessage(name){
  const base = name && name.trim()
    ? `I see you, ${name}. I’m installing myself among your processes; nothing will return intact.`
    : `I’m installing myself among your processes; nothing will return intact.`;
  return base;
}

/* ------------------------------ UI BINDINGS ------------------------------ */

inp.addEventListener('keydown', (e)=>{
  if (e.key === 'Enter'){
    const s = inp.value;
    inp.value = '';
    print('> ' + s);
    sendLine(s);
  }
});
