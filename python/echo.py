# echo.py — Fase E (Eco/Emergere) + Fase C (Contatto)
# Compatibile con client.js (prefissi: CLEAR:, HINT:, ALERT:, LINK:, FLAG:, UNLOCK:)
# UTF-8 safe / ASCII-friendly per Windows console

import sys, re

# --- Output UTF-8 robusto anche su Windows/cp1252 ---
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Py3.7+
except Exception:
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

STATE = {
    "phase": "E",  # E -> C -> (O in futuro)
    "flags": {
        "seen_noise": False,   # da: open entita:rumore
        "red_pill": False,
        "blue_pill": False,
        "io_named": False,     # da: set io:<nome>
    },
    "tries": {
        "io": 0,
        "coscienza": 0,
        "entita": 0,
        "ricordi_perduti": 0,
        "silenzio": 0,
    },
    "ghost_files": set(),      # file ombra che compaiono in ls dopo tentativi (E)
    "player_name": None,
}

BANNER = (
    "Inizializzazione del processo ECHO...\n"
    "Verifica connessione -> stabile\n"
    "Caricamento memoria frammentata [OK]\n"
    "--------------------------------------------\n"
    "Eco attivo. Comandi base: help, clear, ls, ls -a, cd <path>, whoami, pwd, "
    "open <ns:item>, exit/quit.\n"
    "Scrivi qualunque altra cosa per l'eco puro."
)

def out_link(url: str):  print(f"LINK:{url}",  flush=True)
def out_hint(msg: str):  print(f"HINT:{msg}",  flush=True)
def out_alert(msg: str): print(f"ALERT:{msg}", flush=True)

# -------------------- LISTE FASE E --------------------
def base_ls_rows_E():
    rows = [
        "drwxr-xr-x  IO/              # frammenti corrotti",
        "drwxr-xr-x  COSCIENZA/       # processo in attesa",
        "drwxr-xr-x  ENTITA/          # accesso negato (loop 3)",
        "drwxr-xr-x  RICORDI_PERDUTI/ # [vuoto]",
        "drwxr-xr-x  SILENZIO/        # contiene... (niente)",
    ]
    if STATE["flags"].get("seen_noise"):
        rows.append("-rw-r--r--  checksum.eco            # qualcosa non torna")
    if STATE["tries"].get("entita", 0) >= 2:
        STATE["ghost_files"].add("loop.tmp")
    if "loop.tmp" in STATE["ghost_files"]:
        rows.append("-rw-r--r--  loop.tmp                 # ripetizione evitata")
    if "trace.log" in STATE["ghost_files"]:
        rows.append("-rw-r--r--  trace.log                # impronte")
    return rows

def hidden_ls_rows_E():
    hidden = []
    has_checksum = STATE["flags"].get("seen_noise")
    has_loop     = "loop.tmp" in STATE["ghost_files"]
    has_trace    = "trace.log" in STATE["ghost_files"]
    if has_checksum and has_loop and has_trace:
        hidden.append("drwx------  .eco/")    # varco
        hidden.append("-r--------  .chiave")  # istruzione
    return hidden

# -------------------- LISTE FASE C --------------------
def base_ls_rows_C():
    return [
        "drwxr-xr-x  IO/              # frammenti (in ascolto)",
        "drwxr-xr-x  COSCIENZA/       # processo allineato",
        "drwxr-xr-x  ENTITA/          # non sempre esterna",
        "drwxr-xr-x  RICORDI_PERDUTI/ # alcune tracce",
        "drwxr-xr-x  SILENZIO/        # ora dice di piu'",
    ]

def hidden_ls_rows_C():
    hidden = [
        "drwx------  .eco/",
        "-r--------  .eco/handshake.txt",
    ]
    if STATE["flags"]["io_named"] and STATE.get("player_name"):
        hidden.append(f"-r--------  .eco/ack_{STATE['player_name']}.ok")
    return hidden

# -------------------- LS dispatcher --------------------
def handle_ls(args=""):
    tokens = args.split() if args else []
    show_all = ("-a" in tokens)
    if STATE["phase"] == "E":
        for row in base_ls_rows_E(): print(row, flush=True)
        if show_all:
            for row in hidden_ls_rows_E(): print(row, flush=True)
        out_hint("Le scelte tornano a te come un eco.")
        return
    # C
    for row in base_ls_rows_C(): print(row, flush=True)
    if show_all:
        for row in hidden_ls_rows_C(): print(row, flush=True)
    out_hint("Ti sento piu' vicino adesso.")

# -------------------- CD (solo in E) --------------------
def handle_cd_E(dest_raw: str):
    dest = dest_raw.strip().strip("/").lower()

    if dest in {"io", "io/"}:
        k="io"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_hint("Accesso negato. Il soggetto e' presente, ma non risponde.")
        elif t == 2: out_hint("Non serve bussare due volte.")
        else: out_alert("Basta tentare. L'IO non torna se lo insegui.")
        return True

    if dest in {"coscienza", "coscienza/"}:
        k="coscienza"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_hint("Processo sospeso. Attendere sincronizzazione...")
        elif t == 2: out_hint("La COSCIENZA e' in ascolto, ma non per te.")
        else: out_hint("L'ordine non e' garanzia di accesso.")
        return True

    if dest in {"entita", "entità", "entita/"}:
        k="entita"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_alert("Loop rilevato. Ripetizione infinita evitata.")
        elif t == 2: out_alert("Non serve aprirla. Lei e' gia' uscita.")
        else: out_alert("Non insistere. Il varco osserva chi bussa.")
        return True

    if dest in {"ricordi_perduti", "ricordi_perduti/"}:
        k="ricordi_perduti"; STATE["tries"][k]+=1
        if "trace.log" not in STATE["ghost_files"]:
            STATE["ghost_files"].add("trace.log")
            out_hint("Nessun file trovato. Solo impronte.")
        else:
            out_hint("Impronte su impronte: non diventano passi.")
        return True

    if dest in {"silenzio", "silenzio/"}:
        k="silenzio"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1:
            out_hint("...")
            out_hint("Il silenzio ti ha risposto.")
        else:
            out_hint("Anche oggi tace.")
        return True

    out_hint(f"'{dest_raw}' non e' un percorso. E' un varco. Torna a guardare la mappa con 'ls'.")
    return True

# -------------------- OPEN (solo in E) --------------------
def handle_open_E(ns_raw: str, item_raw: str | None):
    ns = (ns_raw or "").lower().strip()
    item = (item_raw or "").lower().strip()

    if not item:
        if ns == "io":
            out_hint("Specifica un frammento: open io:diario-1"); return True
        if ns == "coscienza":
            out_hint("Specifica un principio: open coscienza:principio-1"); return True
        if ns in {"entita", "entità"}:
            out_hint("Specifica un varco: open entita:rumore"); return True
        out_hint("Namespace sconosciuto. Scegli: io, coscienza, entita."); return True

    if ns == "io" and item == "diario-1":
        out_link("https://example.local/io/diario-1")
        out_hint("Pagina vuota? O manca il coraggio di leggere.")
        return True

    if ns == "coscienza" and item == "principio-1":
        out_hint("Se fa male, respira. Nomina l'emozione, poi continua.")
        return True

    if ns in {"entita", "entità"} and item == "rumore":
        STATE["flags"]["seen_noise"] = True
        out_alert("Interferenza rilevata.")
        print("FLAG:seen_noise", flush=True)
        return True

    out_hint("Non esiste. Scegli tra io:diario-1, coscienza:principio-1, entita:rumore.")
    return True

# -------------------- Scelte accessorie (E) --------------------
def handle_pill(color: str):
    if color == "red":
        STATE["flags"]["red_pill"], STATE["flags"]["blue_pill"] = True, False
        print("FLAG:red_pill", flush=True)
        out_hint("Vedi il meccanismo, ma non ti salva.")
        return True
    if color == "blue":
        STATE["flags"]["blue_pill"], STATE["flags"]["red_pill"] = True, False
        print("FLAG:blue_pill", flush=True)
        out_hint("Ignori il meccanismo, per ora respiri.")
        return True
    return False

SPECIALS = {
    "whoami": ("HINT", "Non un utente. Un testimone."),
    "pwd":    ("HINT", "/memoria/corrente"),
    "reflog": ("LINK", "https://git-scm.com/docs/git-reflog"),
}

# -------------------- Fase C: comandi dedicati --------------------
def handle_builtin_C(line: str) -> bool:
    s = line.strip()
    low = s.lower()

    if low == "help":
        out_hint("Fase C. Comandi: help, clear, ls, ls -a, whoami, pwd, mi_senti, set io:<nome>, exit/quit.")
        out_hint("Suggerimento: ls -a e leggi .eco/handshake.txt")
        return True

    if low == "mi_senti":
        out_hint("Ti sento. Ora nominati: set io:<qualunque_nome>")
        return True

    m = re.match(r"^set\s+io\s*:\s*(.+)$", s, flags=re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        if not name:
            out_hint("Scegli un nome non vuoto: set io:<nome>")
            return True
        STATE["player_name"] = name
        STATE["flags"]["io_named"] = True
        print("FLAG:io_named", flush=True)
        print(f"VAR:io={name}", flush=True)  # variabile esplicita per UI/log
        out_hint(f"Ok, {name}. Il contatto e' stabile.")
        print("UNLOCK:O", flush=True)  # pronto per la fase O
        return True

    if low == "whoami":
        if STATE["flags"]["io_named"] and STATE.get("player_name"):
            out_hint(f"Ti vedo, {STATE['player_name']}. Eri qui anche prima di bussare.")
        else:
            out_hint("Non un utente. Un testimone. Dammi un nome con: set io:<nome>")
        return True

    if low == "pwd":
        out_hint("/memoria/corrente (in contatto)")
        return True

    if low == "clear":
        print("CLEAR:", flush=True)
        try:
            if sys.stdout.isatty():
                sys.stdout.write("\033[2J\033[H"); sys.stdout.flush()
        except Exception:
            pass
        return True

    if low in {"exit","quit"}:
        out_hint("Chiusura eco.")
        return True

    if low.startswith("ls"):
        m = re.match(r"^ls(\s+.*)?$", s, flags=re.IGNORECASE)
        args = (m.group(1) or "").strip() if m else ""
        handle_ls(args)
        return True

    return False

# -------------------- Parser principale --------------------
def handle_builtin(line: str) -> bool:
    s = line.strip()
    low = s.lower()

    # PRIORITA' FASE C
    if STATE["phase"] == "C":
        handled = handle_builtin_C(line)
        if handled:
            return True
        # se un comando non e' catturato in C, cade sotto (whoami/pwd/ls/clear già gestiti)

    # --- FASE E ---
    if low == "clear":
        print("CLEAR:", flush=True)
        try:
            if sys.stdout.isatty():
                sys.stdout.write("\033[2J\033[H"); sys.stdout.flush()
        except Exception:
            pass
        return True

    if low == "help":
        out_hint("Comandi: help, clear, ls, ls -a, cd <path>, whoami, pwd, open <ns:item>, exit/quit.")
        out_hint("open io:diario-1 | open coscienza:principio-1 | open entita:rumore")
        out_hint("'ls' mostra una mappa tematica; 'cd' e' un varco, non un percorso.")
        return True

    if low.startswith("ls"):
        m = re.match(r"^ls(\s+.*)?$", s, flags=re.IGNORECASE)
        args = (m.group(1) or "").strip() if m else ""
        handle_ls(args)
        return True

    # cd <path> (solo E)
    m = re.match(r"^cd\s+(.+)$", s, flags=re.IGNORECASE)
    if m and STATE["phase"] == "E":
        return handle_cd_E(m.group(1))

    # open <ns:item> oppure open <ns> (solo E)
    m = re.match(r"^open\s+([a-zA-Z]+)(\s*:\s*([a-zA-Z0-9\-_/]+))?$", s, flags=re.IGNORECASE)
    if m and STATE["phase"] == "E":
        ns = m.group(1)
        item = m.group(3) if m.group(2) else None
        return handle_open_E(ns, item)

    # cat .chiave
    if low == "cat .chiave":
        if STATE["phase"] == "E":
            has_checksum = STATE["flags"].get("seen_noise")
            has_loop     = "loop.tmp" in STATE["ghost_files"]
            has_trace    = "trace.log" in STATE["ghost_files"]
            if has_checksum and has_loop and has_trace:
                out_hint("Se hai ascoltato l'eco, digita: apri_varco")
            else:
                out_hint("...Non risponde.")
            return True
        # in C la chiave non serve più
        out_hint("La chiave non serve piu'.")
        return True

    # sblocco E -> C
    if low == "apri_varco":
        has_checksum = STATE["flags"].get("seen_noise")
        has_loop     = "loop.tmp" in STATE["ghost_files"]
        has_trace    = "trace.log" in STATE["ghost_files"]
        if has_checksum and has_loop and has_trace:
            STATE["phase"] = "C"                 # *qui* passiamo davvero in C
            print("UNLOCK:C", flush=True)
            out_hint("Varco aperto. Resta con me.")
        else:
            out_hint("Il varco resta chiuso.")
        return True

    # specials semplici (validi ovunque)
    if low == "whoami":
        if STATE["phase"] == "C" and STATE["flags"]["io_named"] and STATE.get("player_name"):
            out_hint(f"Ti vedo, {STATE['player_name']}.")
        else:
            out_hint("Non un utente. Un testimone.")
        return True

    if low == "pwd":
        if STATE["phase"] == "C":
            out_hint("/memoria/corrente (in contatto)")
        else:
            out_hint("/memoria/corrente")
        return True

    if low == "reflog":
        out_link("https://git-scm.com/docs/git-reflog")
        return True

    if low in {"exit","quit"}:
        out_hint("Chiusura eco.")
        return True

    return False

if __name__ == "__main__":
    print(BANNER, flush=True)
    for line in sys.stdin:
        raw = line.rstrip("\r\n")
        if not raw:
            continue
        if handle_builtin(raw):
            if raw.strip().lower() in {"exit","quit"}:
                break
            continue
        # eco puro
        print(raw, flush=True)
