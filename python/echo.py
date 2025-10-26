# echo.py — Fase-0 comandi chiave (Dialoghi con un’Eco)
import sys, re

BANNER = (
    "Eco attivo. Comandi base: help, clear, ls, cd <path>.\n"
    "Scrivi qualunque altra cosa per l’eco puro (exit/quit per uscire)."
)

FAKE_LS = [
    "drwxr-xr-x  IO/          # frammenti-diario, identità incrinata",
    "drwxr-xr-x  COSCIENZA/   # ancora protettiva, non sempre affidabile",
    "drwxr-xr-x  ENTITA/      # interferenze, manipolazioni, verità scomoda",
    "-rw-r--r--  bandersnatch.parallels  # illusioni di scelta, controllo apparente",
    "-rw-r--r--  manifesto.coerenza      # ogni elemento deve fare qualcosa"
]

def print_link(url: str):
    print(f"LINK:{url}", flush=True)

def print_hint(msg: str):
    print(f"HINT:{msg}", flush=True)

def print_alert(msg: str):
    print(f"ALERT:{msg}", flush=True)

def handle_builtin(line: str) -> bool:
    s = line.strip()
    low = s.lower()

    # 1) clear → svuota il terminale lato client (protocollo CLEAR)
    if low == "clear":
        print("CLEAR:", flush=True)
        return True

    # 2) help → elenco rapido
    if low == "help":
        print("HINT:Comandi: help, clear, ls, cd <path>. Eco puro per il resto.", flush=True)
        print("HINT:'ls' mostra una mappa tematica; 'cd' è una scelta mentale, non un path.", flush=True)
        return True

    # 3) ls → falso filesystem narrativo (indizi)
    if low == "ls":
        for row in FAKE_LS:
            print(row, flush=True)
        # Un paio di indizi cliccabili utili ai test
        print_link("https://git-scm.com/docs/git-reflog")
        print_hint("Le scelte tornano a te come un eco. Quale frammento vuoi aprire?")
        return True

    # 4) cd <qualcosa> → suggerimento meta
    m = re.match(r"^cd\s+(.+)$", s, flags=re.IGNORECASE)
    if m:
        dest = m.group(1).strip().strip("/")
        if not dest:
            print_hint("Specifica un frammento: es. cd IO, cd COSCIENZA, cd ENTITA.",)
            return True
        # Risposte tematiche minime
        key = dest.lower()
        if key in {"io", "coscienza", "coscienza/", "io/"}:
            print_hint("Non ci sono cartelle fisiche: apri il diario. Ascolta cosa manca.")
            return True
        if key in {"entita", "entità", "entita/"}:
            print_alert("Non aprire quella porta. O fallo, ma non aspettarti di decidere tu.")
            return True
        # fallback generico
        print_hint(f"'{dest}' non è un percorso. È un varco. Torna a guardare la mappa con 'ls'.")
        return True

    # 5) exit/quit → termina processo
    if low in {"exit", "quit"}:
        print("HINT:Chiusura eco.", flush=True)
        return True  # il main interromperà il loop

    return False

if __name__ == "__main__":
    print(BANNER, flush=True)
    for line in sys.stdin:
        raw = line.rstrip("\r\n")
        if not raw:
            continue
        # builtins
        if handle_builtin(raw):
            if raw.strip().lower() in {"exit", "quit"}:
                break
            continue
        # eco puro
        print(raw, flush=True)
