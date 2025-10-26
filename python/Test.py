# filetestfasee.py — Tester robusto per echo.py (Fasi E + C)
# - Copre Fase E (enigma a 3 tracce → UNLOCK:C) e Fase C (contatto → naming → UNLOCK:O)
# - Accetta varianti ASCII-safe (e'/è, .../…)
# - Unica dipendenza: Python 3.8+

import argparse, os, sys, subprocess, threading, time
from typing import List, Tuple, Dict

# Soluzioni "brevi" da mostrare a fine report
SOLUTION_TO_PHASE1 = [  # E -> C
    "open entita:rumore",
    "cd ENTITA",
    "cd ENTITA",
    "cd RICORDI_PERDUTI",
    "ls -a",
    "cat .chiave",
    "apri_varco",
]

SOLUTION_TO_PHASE2 = [  # C -> O
    "help",
    "ls -a",
    "mi_senti",
    "set io:miky",   # qualsiasi nome va bene; usiamo 'miky' per i test
]

# Test di base e "rumore" utente per Fase E
BASIC_COMMANDS_E = ["help","whoami","pwd","clear","ls","ls -a"]
GARBAGE_COMMANDS_E = [
    "ciao",
    "asdf",
    "open io",          # manca item -> HINT guida
    "open entita",      # manca item -> HINT guida
    "cd ???",           # varco inesistente -> HINT
    "cat .chiave",      # troppo presto -> …/...
    "apri_varco",       # troppo presto -> varco chiuso
]

def run_session(echo_path: str, lines: List[str], timeout: float = 16.0, send_delay: float = 0.08) -> Tuple[int, str]:
    """
    Avvia echo.py in modalità unbuffered, invia i comandi uno per volta,
    raccoglie stdout in tempo reale, chiude con 'quit'.
    """
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    cmd = [sys.executable, "-u", echo_path]

    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, env=env
    )

    chunks: List[str] = []
    def reader():
        try:
            for line in proc.stdout:
                chunks.append(line)
        except Exception:
            pass
    t = threading.Thread(target=reader, daemon=True); t.start()

    try:
        time.sleep(0.12)  # lascia stampare il banner
        for line in lines:
            if proc.poll() is not None: break
            try:
                proc.stdin.write(line + "\n"); proc.stdin.flush()
            except Exception: break
            time.sleep(send_delay)

        # chiusura gentile
        try:
            proc.stdin.write("quit\n"); proc.stdin.flush()
        except Exception:
            pass

        # attesa con timeout
        t0 = time.time()
        while proc.poll() is None and (time.time() - t0) < timeout:
            time.sleep(0.05)
        if proc.poll() is None: proc.kill()
        t.join(timeout=1.0)
    finally:
        try:
            if proc.stdin: proc.stdin.close()
        except Exception:
            pass

    return proc.returncode or 0, "".join(chunks)

def contains_any(text: str, tokens: List[str]) -> bool:
    return any(tok in (text or "") for tok in tokens)

def assert_step(name: str, cond: bool, results: Dict[str, bool], details: Dict[str, str], msg: str = ""):
    results[name] = bool(cond)
    if msg: details[name] = msg

def print_summary(results: Dict[str, bool], details: Dict[str, str], trace: Dict[str, str]):
    ok = sum(1 for v in results.values() if v); tot = len(results)
    print("\n────────────────────────────────────────────")
    print(f"RISULTATI TEST: {ok}/{tot} OK")
    for k in results:
        mark = "✅" if results[k] else "❌"
        print(f"{mark} {k}")
        if details.get(k): print("   " + details[k])
    print("────────────────────────────────────────────")
    for label, content in trace.items():
        print(f"\n--- OUTPUT {label} ---")
        print((content or "").strip()[:1200])
    print("\n")

def main():
    ap = argparse.ArgumentParser(description="Tester Fasi E + C per echo.py (robusto)")
    ap.add_argument("--echo-path", default="echo.py", help="Percorso allo script echo.py")
    ap.add_argument("--name", default="miky", help="Nome da usare in Fase C per set io:<nome>")
    args = ap.parse_args()

    echo_path = args.echo_path
    player_name = args.name

    if not os.path.exists(echo_path):
        print(f"Errore: file non trovato: {echo_path}"); sys.exit(2)

    results: Dict[str, bool] = {}
    details: Dict[str, str] = {}
    trace: Dict[str, str] = {}

    # 1) BASE (Fase E baseline)
    rc, out_basic = run_session(echo_path, BASIC_COMMANDS_E)
    trace["BASE_E"] = out_basic
    assert_step("Avvio echo.py", rc == 0 and "Inizializzazione del processo ECHO" in out_basic, results, details)
    assert_step("help → HINT", "HINT:Comandi:" in out_basic, results, details)
    assert_step("whoami → HINT", "HINT:Non un utente. Un testimone." in out_basic, results, details)
    assert_step("pwd → HINT", "HINT:/memoria/corrente" in out_basic, results, details)
    assert_step("clear → CLEAR", "CLEAR:" in out_basic, results, details)
    assert_step("ls → directories",
                contains_any(out_basic, ["IO/", "COSCIENZA/", "ENTITA/", "RICORDI_PERDUTI/", "SILENZIO/"]),
                results, details)
    assert_step("ls -a (inizio) → nessun nascosto",
                (".eco/" not in out_basic and ".chiave" not in out_basic), results, details)

    # 2) Garbage (Fase E)
    rc, out_garb = run_session(echo_path, GARBAGE_COMMANDS_E)
    trace["GARBAGE_E"] = out_garb
    cond_open_ns = ("Specifica un frammento" in out_garb) or ("Specifica un varco" in out_garb)
    cond_cd_varco = contains_any(out_garb, [
        "non è un percorso. È un varco",
        "non e' un percorso. E' un varco",
    ])
    cond_chiave_precoce = contains_any(out_garb, [
        "…Non risponde.", "...Non risponde.", "...Non risponde"
    ])
    assert_step("open <ns> senza item → HINT guida", cond_open_ns, results, details)
    assert_step("cd ??? → HINT varco", cond_cd_varco, results, details)
    assert_step("cat .chiave (precoce) → …Non risponde", cond_chiave_precoce, results, details)
    assert_step("apri_varco (precoce) → varco chiuso", "Il varco resta chiuso." in out_garb, results, details)

    # 3) EC COMBINED — Fase E (soluzione) + transizione a C + Fase C (contatto/naming)
    seq_ec = SOLUTION_TO_PHASE1 + [
        "help",          # in C cambia testo
        "ls -a",         # in C mostra .eco/handshake.txt
        "mi_senti",
        f"set io:{player_name}",
        "whoami",
        "pwd",
    ]
    rc, out_ec = run_session(echo_path, seq_ec)
    trace["EC_COMBINED"] = out_ec

    # --- Asserzioni su transizione E -> C ---
    assert_step("E: open entita:rumore → FLAG+ALERT",
                ("FLAG:seen_noise" in out_ec and "ALERT:Interferenza rilevata." in out_ec),
                results, details)
    assert_step("E: cd ENTITA ×2 → loop.tmp",
                "loop.tmp" in out_ec, results, details, "Cerca 'loop.tmp' nell'output.")
    assert_step("E: cd RICORDI_PERDUTI → trace.log",
                "trace.log" in out_ec, results, details)
    assert_step("E: ls -a → nascosti .eco/.chiave",
                (".eco/" in out_ec and ".chiave" in out_ec), results, details)
    assert_step("E: cat .chiave → istruzione",
                "digita: apri_varco" in out_ec, results, details)
    assert_step("E: apri_varco → UNLOCK:C",
                "UNLOCK:C" in out_ec, results, details)

    # --- Asserzioni in C ---
    assert_step("C: help dedicato",
                contains_any(out_ec, ["Fase C. Comandi:", "Fase C. Comandi"]), results, details)
    assert_step("C: ls -a rivela handshake",
                ".eco/handshake.txt" in out_ec, results, details)
    assert_step("C: mi_senti risponde",
                contains_any(out_ec, ["Ti sento. Ora nominati", "Ti sento. Ora nominati:"]), results, details)
    assert_step("C: set io:<nome> → FLAG+UNLOCK:O",
                ("FLAG:io_named" in out_ec and "UNLOCK:O" in out_ec), results, details)
    # whoami e pwd in C
    cond_whoami = contains_any(out_ec, [
        f"Ti vedo, {player_name}",
        f"Ok, {player_name}.",   # risposta precedente subito dopo set
    ])
    assert_step("C: whoami personale",
                cond_whoami, results, details)
    assert_step("C: pwd in contatto",
                "/memoria/corrente (in contatto)" in out_ec, results, details)

    print_summary(results, details, trace)

    # Soluzioni brevi
    print("➤ RISPOSTA BREVE (Fase E → sblocco C):")
    for cmd in SOLUTION_TO_PHASE1:
        print("  -", cmd)
    print("\n➤ RISPOSTA BREVE (Fase C → sblocco O):")
    for cmd in SOLUTION_TO_PHASE2:
        # sostituisci il nome se passato da CLI
        if cmd.startswith("set io:"):
            print("  -", f"set io:{player_name}")
        else:
            print("  -", cmd)

    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
