# echo.py — Phase E (Echo/Emerge) + Phase C (Contact)
# Compatible with client.js (prefixes: CLEAR:, HINT:, ALERT:, LINK:, FLAG:, UNLOCK:)
# UTF-8 safe / ASCII-friendly on Windows consoles

import sys, re

# --- Robust UTF-8 output even on Windows/cp1252 ---
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Py3.7+
except Exception:
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

STATE = {
    "phase": "E",  # E -> C -> (O later)
    "flags": {
        "seen_noise": False,   # from: open entita:rumore | entita:noise
        "red_pill": False,
        "blue_pill": False,
        "io_named": False,     # from: set io:<name>
    },
    "tries": {
        "io": 0,
        "coscienza": 0,
        "entita": 0,
        "lost_memories": 0,
        "silence": 0,
    },
    "ghost_files": set(),      # shadow files that appear in ls after attempts (E)
    "player_name": None,
}

BANNER = (
    "Initializing ECHO process...\n"
    "Link check -> stable\n"
    "Loading fragmented memory [OK]\n"
    "--------------------------------------------\n"
    "Echo active. Base commands: help, clear, ls, ls -a, cd <path>, whoami, pwd, "
    "open <ns:item>, exit/quit.\n"
    "Type anything else to use pure echo."
)

def out_link(url: str):  print(f"LINK:{url}",  flush=True)
def out_hint(msg: str):  print(f"HINT:{msg}",  flush=True)
def out_alert(msg: str): print(f"ALERT:{msg}", flush=True)

# -------------------- LISTINGS • PHASE E --------------------
def base_ls_rows_E():
    rows = [
        "drwxr-xr-x  IO/               # corrupted fragments",
        "drwxr-xr-x  COSCIENZA/        # process waiting",
        "drwxr-xr-x  ENTITA/           # access denied (loop 3)",
        "drwxr-xr-x  LOST_MEMORIES/    # [empty]",
        "drwxr-xr-x  SILENCE/          # contains... (nothing)",
    ]
    if STATE["flags"].get("seen_noise"):
        rows.append("-rw-r--r--  checksum.eco             # something feels off")
    if STATE["tries"].get("entita", 0) >= 2:
        STATE["ghost_files"].add("loop.tmp")
    if "loop.tmp" in STATE["ghost_files"]:
        rows.append("-rw-r--r--  loop.tmp                  # repetition avoided")
    if "trace.log" in STATE["ghost_files"]:
        rows.append("-rw-r--r--  trace.log                 # footprints")
    return rows

def hidden_ls_rows_E():
    hidden = []
    has_checksum = STATE["flags"].get("seen_noise")
    has_loop     = "loop.tmp" in STATE["ghost_files"]
    has_trace    = "trace.log" in STATE["ghost_files"]
    if has_checksum and has_loop and has_trace:
        hidden.append("drwx------  .eco/")    # gateway
        hidden.append("-r--------  .key")     # instruction
    return hidden

# -------------------- LISTINGS • PHASE C --------------------
def base_ls_rows_C():
    return [
        "drwxr-xr-x  IO/               # fragments (listening)",
        "drwxr-xr-x  COSCIENZA/        # process aligned",
        "drwxr-xr-x  ENTITA/           # not always external",
        "drwxr-xr-x  LOST_MEMORIES/    # some traces",
        "drwxr-xr-x  SILENCE/          # now it speaks more",
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
        out_hint("Choices return to you like an echo.")
        return
    # Phase C
    for row in base_ls_rows_C(): print(row, flush=True)
    if show_all:
        for row in hidden_ls_rows_C(): print(row, flush=True)
    out_hint("I hear you more clearly now.")

# -------------------- CD (E only) --------------------
def handle_cd_E(dest_raw: str):
    dest = dest_raw.strip().strip("/").lower()

    # IO
    if dest in {"io", "io/"}:
        k="io"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_hint("Access denied. The subject is present but not responding.")
        elif t == 2: out_hint("Knocking twice changes nothing.")
        else: out_alert("Enough. IO won’t return if you chase it.")
        return True

    # COSCIENZA
    if dest in {"coscienza", "coscienza/"}:
        k="coscienza"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_hint("Process suspended. Waiting for synchronization...")
        elif t == 2: out_hint("COSCIENZA is listening, but not for you.")
        else: out_hint("Order does not guarantee access.")
        return True

    # ENTITA (accept both 'entita' and 'entità')
    if dest in {"entita", "entità", "entita/"}:
        k="entita"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1: out_alert("Loop detected. Infinite repetition avoided.")
        elif t == 2: out_alert("No need to open it. She is already out.")
        else: out_alert("Do not insist. The gateway watches who knocks.")
        return True

    # LOST_MEMORIES (also accept Italian)
    if dest in {"lost_memories", "lost_memories/", "ricordi_perduti", "ricordi_perduti/"}:
        k="lost_memories"; STATE["tries"][k]+=1
        if "trace.log" not in STATE["ghost_files"]:
            STATE["ghost_files"].add("trace.log")
            out_hint("No files found. Only footprints.")
        else:
            out_hint("Footprints over footprints: they don’t become steps.")
        return True

    # SILENCE (also accept Italian)
    if dest in {"silence", "silence/", "silenzio", "silenzio/"}:
        k="silence"; STATE["tries"][k]+=1; t=STATE["tries"][k]
        if t == 1:
            out_hint("...")
            out_hint("Silence has answered you.")
        else:
            out_hint("It keeps quiet today as well.")
        return True

    out_hint(f"'{dest_raw}' is not a path. It is a gateway. Return to the map with 'ls'.")
    return True

# -------------------- OPEN (E only) --------------------
def handle_open_E(ns_raw: str, item_raw: str | None):
    ns = (ns_raw or "").lower().strip()
    item = (item_raw or "").lower().strip()

    if not item:
        if ns == "io":
            out_hint("Specify a fragment: open io:diario-1")
            return True
        if ns == "coscienza":
            out_hint("Specify a principle: open coscienza:principio-1")
            return True
        if ns in {"entita", "entità"}:
            out_hint("Specify a gateway: open entita:rumore")
            return True
        out_hint("Unknown namespace. Choose: io, coscienza, entita.")
        return True

    if ns == "io" and item == "diario-1":
        out_link("https://example.local/io/diario-1")
        out_hint("Blank page? Or perhaps courage is missing.")
        return True

    if ns == "coscienza" and item == "principio-1":
        out_hint("If it hurts, breathe. Name the feeling, then continue.")
        return True

    # ENTITÀ noise — accept both Italian 'rumore' and English 'noise'
    if ns in {"entita", "entità"} and item in {"rumore", "noise"}:
        STATE["flags"]["seen_noise"] = True
        out_alert("Interference detected.")
        print("FLAG:seen_noise", flush=True)
        return True

    out_hint("Not found. Try io:diario-1, coscienza:principio-1, entita:rumore.")
    return True

# -------------------- Optional choices (E) --------------------
def handle_pill(color: str):
    if color == "red":
        STATE["flags"]["red_pill"], STATE["flags"]["blue_pill"] = True, False
        print("FLAG:red_pill", flush=True)
        out_hint("You see the mechanism; it won’t save you.")
        return True
    if color == "blue":
        STATE["flags"]["blue_pill"], STATE["flags"]["red_pill"] = True, False
        print("FLAG:blue_pill", flush=True)
        out_hint("You ignore the mechanism; for now, you can breathe.")
        return True
    return False

SPECIALS = {
    "whoami": ("HINT", "Not a user. A witness."),
    "pwd":    ("HINT", "/memory/current"),
    "reflog": ("LINK", "https://git-scm.com/docs/git-reflog"),
}

# -------------------- Phase C: dedicated commands --------------------
def handle_builtin_C(line: str) -> bool:
    s = line.strip()
    low = s.lower()

    if low == "help":
        out_hint("Phase C. Commands: help, clear, ls, ls -a, whoami, pwd, can_you_hear_me, set io:<name>, exit/quit.")
        out_hint("Hint: run ls -a and read .eco/handshake.txt")
        return True

    if low in {"can_you_hear_me", "mi_senti"}:
        out_hint("I hear you. Now name yourself: set io:<any_name>")
        return True

    m = re.match(r"^set\s+io\s*:\s*(.+)$", s, flags=re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        if not name:
            out_hint("Choose a non-empty name: set io:<name>")
            return True
        STATE["player_name"] = name
        STATE["flags"]["io_named"] = True
        print("FLAG:io_named", flush=True)
        print(f"VAR:io={name}", flush=True)  # explicit variable for UI/log
        out_hint(f"Okay, {name}. The contact is stable.")
        print("UNLOCK:O", flush=True)  # ready for Phase O
        return True

    if low == "whoami":
        if STATE["flags"]["io_named"] and STATE.get("player_name"):
            out_hint(f"I see you, {STATE['player_name']}. You were here before you knocked.")
        else:
            out_hint("Not a user. A witness. Give me a name with: set io:<name>")
        return True

    if low == "pwd":
        out_hint("/memory/current (in contact)")
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
        out_hint("Echo closing.")
        return True

    if low.startswith("ls"):
        m = re.match(r"^ls(\s+.*)?$", s, flags=re.IGNORECASE)
        args = (m.group(1) or "").strip() if m else ""
        handle_ls(args)
        return True

    return False

# -------------------- Main parser --------------------
def handle_builtin(line: str) -> bool:
    s = line.strip()
    low = s.lower()

    # PHASE C takes priority
    if STATE["phase"] == "C":
        handled = handle_builtin_C(line)
        if handled:
            return True
        # if a command isn't handled in C, it falls through (whoami/pwd/ls/clear already covered)

    # --- PHASE E ---
    if low == "clear":
        print("CLEAR:", flush=True)
        try:
            if sys.stdout.isatty():
                sys.stdout.write("\033[2J\033[H"); sys.stdout.flush()
        except Exception:
            pass
        return True

    if low == "help":
        out_hint("Commands: help, clear, ls, ls -a, cd <path>, whoami, pwd, open <ns:item>, exit/quit.")
        out_hint("open io:diario-1 | open coscienza:principio-1 | open entita:rumore")
        out_hint("'ls' shows a thematic map; 'cd' is a gateway, not a path.")
        return True

    if low.startswith("ls"):
        m = re.match(r"^ls(\s+.*)?$", s, flags=re.IGNORECASE)
        args = (m.group(1) or "").strip() if m else ""
        handle_ls(args)
        return True

    # cd <path> (E only)
    m = re.match(r"^cd\s+(.+)$", s, flags=re.IGNORECASE)
    if m and STATE["phase"] == "E":
        return handle_cd_E(m.group(1))

    # open <ns:item> or open <ns> (E only)
    m = re.match(r"^open\s+([a-zA-Z]+)(\s*:\s*([a-zA-Z0-9\-_/]+))?$", s, flags=re.IGNORECASE)
    if m and STATE["phase"] == "E":
        ns = m.group(1)
        item = m.group(3) if m.group(2) else None
        return handle_open_E(ns, item)

    # cat .key
    if low == "cat .key" or low == "cat .chiave":  # accept Italian alias
        if STATE["phase"] == "E":
            has_checksum = STATE["flags"].get("seen_noise")
            has_loop     = "loop.tmp" in STATE["ghost_files"]
            has_trace    = "trace.log" in STATE["ghost_files"]
            if has_checksum and has_loop and has_trace:
                out_hint("If you listened to the echo, type: open_gateway")
            else:
                out_hint("...No response.")
            return True
        # in C the key is no longer required
        out_hint("The key is no longer required.")
        return True

    # unlock E -> C
    if low in {"open_gateway", "apri_varco"}:
        has_checksum = STATE["flags"].get("seen_noise")
        has_loop     = "loop.tmp" in STATE["ghost_files"]
        has_trace    = "trace.log" in STATE["ghost_files"]
        if has_checksum and has_loop and has_trace:
            STATE["phase"] = "C"                 # we actually switch to C here
            print("UNLOCK:C", flush=True)
            out_hint("Gateway open. Stay with me.")
        else:
            out_hint("The gateway remains closed.")
        return True

    # simple specials (valid anywhere)
    if low == "whoami":
        if STATE["phase"] == "C" and STATE["flags"]["io_named"] and STATE.get("player_name"):
            out_hint(f"I see you, {STATE['player_name']}.")
        else:
            out_hint("Not a user. A witness.")
        return True

    if low == "pwd":
        if STATE["phase"] == "C":
            out_hint("/memory/current (in contact)")
        else:
            out_hint("/memory/current")
        return True

    if low == "reflog":
        out_link("https://git-scm.com/docs/git-reflog")
        return True

    if low in {"exit","quit"}:
        out_hint("Echo closing.")
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
        # pure echo  -> sostituito: non “echoa” più testo arbitrario
        unknown = raw.strip()
        if unknown:
            out_alert(f"bash:{unknown} command not found")




