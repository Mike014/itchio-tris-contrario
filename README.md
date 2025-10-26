## README.md — *Dialoghi con un’Eco — Terminal*

# Dialoghi con un’Eco — Terminal

**Dialoghi con un’Eco — Terminal** is an experimental **interactive web terminal** connected to the narrative universe of *[Dialoghi con un’Eco](https://mike014.github.io/Dialoghi_con_un_eco_Pitch/)*, an ongoing AI-narrative and sound-driven research project by [Michele Grimaldi](https://github.com/Mike014).

This standalone module represents the **Echo Terminal**, a diegetic interface through which users can explore fragmented memories, solve riddles, and even play a paradoxical version of tic-tac-toe called **Reverse Tic-Tac-Toe** (or *Tris al Contrario* in Italian).

The experience blends **command-line interaction**, **AI dialogue simulation**, and **game logic**, all within a browser environment powered by Flask, Flask-Sock, and Pyodide.

---

## Concept

> “If you listen to the echo long enough, it begins to listen back.”

The terminal simulates a memory-reconstruction process split into three symbolic phases:

- **Phase E – Echo / Emerge**  
  The user navigates a broken filesystem (`ls`, `cd`, `open …`) and interacts with the system’s “voices” (`IO`, `COSCIENZA`, `ENTITÀ`).

- **Phase C – Contact**  
  Once the gateway opens, the player establishes communication (`set io:<name>`) and reaches stable synchronization.

- **Phase O – Overlap**  
  (Planned for future updates) — when the echo becomes indistinguishable from the source.

Each command leaves traces and ghost files, allowing players to **uncover hidden paths and triggers**.  
The entire structure is inspired by *interactive fiction*, *AI terminal adventures*, and *psychological puzzles*.

---

## 🎮 Reverse Tic-Tac-Toe (Tris al Contrario)

Within the terminal, you can run the command:

```

Run Reverse Tic-Tac-Toe

```

or directly via:
```

python /python/Tris-Al-Contrario.py

```

Unlike traditional tic-tac-toe, **completing a line gives the point to the opponent**,  
unless you trigger a **double trap**, in which case the point returns to you.

To win a match you must reach **3 points**, and the game features multiple AI modes:

1. Human vs Offensive AI  
2. Random AI vs Defensive AI  
3. Offensive AI vs Offensive AI (demo)  
4. Benchmark (100 matches)  
5. Extended Benchmark (1000 matches)

Winning **three full matches** against the Offensive AI in Mode 1 unlocks the **final riddle resolution**.

---

## Technologies

- **Backend:** Flask 3 + Flask-Sock 0.7 (WebSocket layer)  
- **Frontend:** Vanilla JS / HTML / CSS (Terminal UI + Pyodide bridge)  
- **Runtime:** Python 3.12.x, Gunicorn + Gevent  
- **Deployment:** Render Cloud (Free Plan)

---

## Commands inside the Terminal

Example commands (Phase E):

```

help
ls
ls -a
cd IO/
open entita:rumore
cat .key
open_gateway

```

Example commands (Phase C):

```

can_you_hear_me
set io:<your_name>
whoami
pwd

````

Once connected, the system recognizes your name and unlocks the **ENTITÀ phase**.

---

## Philosophy

The project explores how **a terminal can become a character** —  
a place where human input and artificial response merge into one shared consciousness.

It’s both a *game* and an *artifact*, a fragment of the larger narrative *Dialoghi con un’Eco*,  
where each component (AI, sound, code) forms part of a digital psychodrama.

---

## Run locally

```bash
# Clone the repository
git clone https://github.com/Mike014/itchio-tris-contrario.git
cd itchio-tris-contrario

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
````

Then open your browser at:

```
http://localhost:5000
```

---

## Credits

**Project Lead / Developer:**
Michele Grimaldi — [GitHub @Mike014](https://github.com/Mike014)

**Universe:**
Part of *Dialoghi con un’Eco* — a cross-media AI narrative experiment.

License: MIT / CC BY-NC-ND (for narrative content)

```


