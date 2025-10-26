# Tris al Contrario — GDD (Bozza)

## 1) Visione
Un micro-gioco da 5–10 minuti che ribalta le attese: **evitare** il tris, sfruttare le **trappole doppie** e pensare “al contrario”.
Minimal, leggibile e con IA che espone tre stili diversi per allenare l’intuizione.

## 2) Pillars
- **Twist cognitivo**: il “vietato vincere” classico crea sorprese.
- **Chiarezza**: feedback testuali puliti e turni ben segnati.
- **Ritmo**: round brevi, alternanza starter, punteggio target.

## 3) Core Loop
Scegli modalità → gioca turni evitando tris → valuta minacce → punti assegnati → prossima manche → vittoria a `N` punti.

## 4) Regole Chiave
- Completare un tris **regala** il punto all’avversario.
- **Trappola Doppia**: se crei 2 minacce simultanee e poi chiudi, il punto è tuo.
- Alternanza dello starter tra i round.
- IA con tre livelli: Random / Difensiva / Offensiva.

## 5) Sistema IA (riassunto)
- **Random**: mossa casuale tra quelle libere.
- **Difensiva**: evita di chiudere tris, blocca minacce avversarie.
- **Offensiva**: crea setup di doppia minaccia, preferisce centro/angoli, blocca quando serve.

## 6) Scalabilità
- Skin grafiche a griglia (mobile-friendly).
- Modalità “best of N”.
- Log partita esportabile.

## 7) Audio
- Playlist jazz “focus” opzionale via Spotify (avvio manuale).

## 8) UX/Accessibilità
- Input numerici da tastiera (1–9).
- Messaggi espliciti per mosse non valide.

## 9) Licenze & Crediti
- Codice prototipo: © Michele Grimaldi (licenza da definire).
- Pagina web: © Michele Grimaldi — Bootstrap, Pyodide.
