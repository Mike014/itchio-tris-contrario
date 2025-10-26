import sys
import functools
print = functools.partial(print, flush=True)

import random

# ================== RIDDLE: DECLARATIONS & UI ==================
# Session counter: Human wins against Offensive AI (Mode 1)
HUMAN_WINS_VS_OFFENSIVE = 0

# Text shown when the riddle unlocks.
# Replace it with your final solution text when ready.
RIDDLE_SOLUTION = """
=== RIDDLE RESOLUTION ===

You unlocked this screen by winning 3 FULL MATCHES
in Mode 1: Human vs Offensive AI.

How you got here:
- In "reverse" Tris, completing a tris gives the POINT to the OPPONENT,
  except in the DOUBLE TRAP case.
- To win a MATCH you need 3 points. Here, the human defeated the Offensive AI
  across 3 matches in this mode during the current session.

[Put the final textual SOLUTION of the riddle here]
"""

def show_riddle_resolution():
    print("\n" + "="*60)
    print("🧩  RIDDLE UNLOCKED")
    print("="*60 + "\n")
    print(RIDDLE_SOLUTION.strip())
    print("\n" + "="*60 + "\n")
# ================================================================


def print_board(b):
    def cell(i):
        return b[i] if b[i] != " " else str(i+1)
    print(f"\n {cell(0)} | {cell(1)} | {cell(2)}")
    print("---+---+---")
    print(f" {cell(3)} | {cell(4)} | {cell(5)}")
    print("---+---+---")
    print(f" {cell(6)} | {cell(7)} | {cell(8)}\n")

LINES = [(0,1,2),(3,4,5),(6,7,8),
         (0,3,6),(1,4,7),(2,5,8),
         (0,4,8),(2,4,6)]

def has_tris(b, sym):
    for a,b2,c in LINES:
        if b[a] == sym and b[b2] == sym and b[c] == sym:
            return True
    return False

def free_moves(b):
    return [i for i in range(9) if b[i] == " "]

def count_threats(b, sym):
    """Counts how many lines have 2 equal symbols and 1 empty space"""
    threats = []
    for a,b2,c in LINES:
        row = [b[a], b[b2], b[c]]
        if row.count(sym) == 2 and row.count(" ") == 1:
            for pos in (a,b2,c):
                if b[pos] == " ":
                    threats.append(pos)
    return threats

# ========== AI LEVEL 1: RANDOM ==========
def ai_random(b, sym):
    """Pick a random legal move"""
    return random.choice(free_moves(b))

# ========== AI LEVEL 2: DEFENSIVE ==========
def ai_defensive(b, sym, opp_next_sym):
    """
    Strategy:
    1. AVOID completing a tris (it would give a point to the opponent)
    2. If the opponent has a threat with THEIR next symbol, block it
    3. Otherwise, pick a random safe move
    """
    moves = free_moves(b)

    # 1. Filter moves that DO NOT complete a tris
    safe = []
    for pos in moves:
        b[pos] = sym
        if not has_tris(b, sym):
            safe.append(pos)
        b[pos] = " "

    if not safe:
        return random.choice(moves)

    # 2. Block opponent threats
    opp_threats = count_threats(b, opp_next_sym)
    useful_blocks = [m for m in opp_threats if m in safe]
    if useful_blocks:
        return random.choice(useful_blocks)

    # 3. Random safe move
    return random.choice(safe)

# ========== AI LEVEL 3: OFFENSIVE ==========
def ai_offensive(b, sym, my_next_sym, opp_next_sym):
    """
    Advanced strategy:
    1. AVOID completing a tris (unless it's a double trap)
    2. Try to create threats with the NEXT-turn symbol
    3. Block opponent threats
    4. Take the center if free
    5. Otherwise, pick a versatile move
    """
    moves = free_moves(b)

    # 1. Safe moves (do not complete a tris)
    safe = []
    for pos in moves:
        b[pos] = sym
        if not has_tris(b, sym):
            safe.append(pos)
        b[pos] = " "

    if not safe:
        return random.choice(moves)

    # 2. Prepare a NEXT-turn threat
    setups = []
    for pos in safe:
        b[pos] = sym

        potential = 0
        for a,b2,c in LINES:
            row = [b[a], b[b2], b[c]]
            if row.count(my_next_sym) == 1 and row.count(" ") == 2:
                potential += 1

        if potential >= 2:
            setups.append(pos)

        b[pos] = " "

    if setups:
        return random.choice(setups)

    # 3. Block opponent threats
    opp_threats = count_threats(b, opp_next_sym)
    blocks = [m for m in opp_threats if m in safe]
    if blocks:
        return random.choice(blocks)

    # 4. Center if free
    if 4 in safe:
        return 4

    # 5. Corners (more versatile)
    corners = [0,2,6,8]
    free_corners = [a for a in corners if a in safe]
    if free_corners:
        return random.choice(free_corners)

    return random.choice(safe)

# ========== GAME ENGINE (WITH DOUBLE TRAP FIX) ==========
def round_reverse_tris(type_a, type_b, starter, verbose=True):
    """
    type_a, type_b: "human", "random", "defensive", "offensive"
    starter: "A" or "B"
    """
    board = [" "] * 9
    player = starter
    next_symbol = {"A": "X" if starter == "A" else "O",
                   "B": "O" if starter == "A" else "X"}

    moves_made = 0
    point_receiver = None

    while True:
        if verbose:
            print_board(board)

        sym = next_symbol[player]
        ptype = type_a if player == "A" else type_b

        opponent = "B" if player == "A" else "A"
        opp_next_sym = next_symbol[opponent]
        my_next_sym = "O" if sym == "X" else "X"

        # Move selection
        if ptype == "human":
            if verbose:
                print(f"Player {player} (symbol {sym}) — next turn you'll use: {my_next_sym}")
            valid = False
            while not valid:
                try:
                    s = input("Choose a cell [1-9]: ").strip()
                    pos = int(s) - 1
                    if 0 <= pos <= 8 and board[pos] == " ":
                        valid = True
                    else:
                        print("Invalid move.")
                except:
                    print("Enter a number from 1 to 9.")

        elif ptype == "random":
            pos = ai_random(board, sym)
            if verbose:
                print(f"Random AI {player} plays at {pos+1}")

        elif ptype == "defensive":
            pos = ai_defensive(board, sym, opp_next_sym)
            if verbose:
                print(f"Defensive AI {player} plays at {pos+1}")

        elif ptype == "offensive":
            pos = ai_offensive(board, sym, my_next_sym, opp_next_sym)
            if verbose:
                print(f"Offensive AI {player} plays at {pos+1}")

        # Place
        board[pos] = sym
        moves_made += 1

        # ===== DOUBLE TRAP CHECK =====
        created_threats = len(count_threats(board, sym))
        double_trap = created_threats >= 2

        # Tris check
        if has_tris(board, sym):
            if double_trap:
                # DOUBLE TRAP: point goes to the player who created it
                point_receiver = player
                if verbose:
                    print_board(board)
                    print(f"⚡ DOUBLE TRAP! {player} completes tris with '{sym}' → Point to {player}!")
            else:
                # Normal rule: point to the opponent
                point_receiver = opponent
                if verbose:
                    print_board(board)
                    print(f"Tris completed by {player} with '{sym}' → Point to {opponent}!")
            break

        # Draw
        if moves_made == 9:
            if verbose:
                print_board(board)
                print("No tris: round drawn.")
            break

        # Flip symbol
        next_symbol[player] = "O" if sym == "X" else "X"

        # Switch turn
        player = opponent

    return point_receiver, moves_made

# ========== MATCH (WITH STARTER ALTERNATION FIX) ==========
def match(type_a="human", type_b="offensive", max_points=3, verbose=True, first_starter="A"):
    """
    Examples:
    - type_a="human", type_b="offensive"  → You vs strong AI
    - type_a="random", type_b="defensive" → Weak AI vs medium AI
    - type_a="offensive", type_b="offensive" → AI vs AI (benchmark)

    first_starter: "A" or "B" — who starts the first round of the match
    """
    score = {"A": 0, "B": 0}
    starter = first_starter  # parameterized starter
    log_rounds = []

    while True:
        if verbose:
            print(f"\n{'='*60}")
            print(f"New round | Starter: {starter} | Score: A={score['A']} B={score['B']}")
            print(f"{'='*60}")

        receiver, moves = round_reverse_tris(type_a, type_b, starter, verbose)
        log_rounds.append({"starter": starter, "moves": moves, "receiver": receiver})

        if receiver:
            score[receiver] += 1
            if verbose:
                print(f"→ Point assigned to {receiver}. Score: A={score['A']} B={score['B']}")

        # Victory check
        if score["A"] >= max_points:
            if verbose:
                print(f"\n🏆 End of match: A has {max_points} points. B wins!")
            return "B", log_rounds
        if score["B"] >= max_points:
            if verbose:
                print(f"\n🏆 End of match: B has {max_points} points. A wins!")
            return "A", log_rounds

        # Alternate starter
        starter = "B" if starter == "A" else "A"

        # If both are AIs, continue automatically
        if type_a != "human" and type_b != "human":
            continue

        # Otherwise ask to continue
        cont = input("\nContinue? [Enter=yes / n=no] ").strip().lower()
        if cont == "n":
            if verbose:
                print("Match interrupted.")
            return None, log_rounds

# ========== BENCHMARK (WITH STARTER ALTERNATION BETWEEN MATCHES) ==========
def benchmark(type_a, type_b, n_matches=100):
    """Run N matches and print stats"""
    print(f"\n🔬 Benchmark: {type_a} vs {type_b} ({n_matches} matches)")
    print("   [Starter Alternation: half start with A, half with B]\n")

    wins = {"A": 0, "B": 0}
    total_rounds = 0
    total_moves = 0
    handoffs = 0

    for i in range(n_matches):
        # Alternate first starter each match
        first = "A" if i % 2 == 0 else "B"
        winner, log = match(type_a, type_b, max_points=3, verbose=False, first_starter=first)

        if winner:
            wins[winner] += 1

        total_rounds += len(log)
        for r in log:
            total_moves += r["moves"]
            if r["receiver"] is not None:
                handoffs += 1

    print(f"Wins A ({type_a}): {wins['A']} ({wins['A']/n_matches*100:.1f}%)")
    print(f"Wins B ({type_b}): {wins['B']} ({wins['B']/n_matches*100:.1f}%)")
    print(f"\nAvg rounds per match: {total_rounds/n_matches:.1f}")
    print(f"Avg moves per round: {total_moves/total_rounds:.1f}")
    print(f"Hand-offs: {handoffs}/{total_rounds} ({handoffs/total_rounds*100:.1f}%)")
    print(f"Draws: {total_rounds-handoffs}/{total_rounds} ({(total_rounds-handoffs)/total_rounds*100:.1f}%)")

# ========== MAIN ==========
if __name__ == "__main__":
    print("=== REVERSE TRIS — Flip + Pass-the-Point ===")
    print("Balanced Version (Starter Fix + Double Trap)\n")
    print("Available modes:")
    print("1. Human vs Offensive AI")
    print("2. Random AI vs Defensive AI (demo)")
    print("3. Offensive AI vs Offensive AI (demo)")
    print("4. Benchmark (100 matches)")
    print("5. EXTENDED Benchmark (1000 matches) — recommended for final testing")

    choice = input("\nChoose mode [1-5]: ").strip()

    if choice == "1":
        # Run standard match
        winner, _log = match(type_a="human", type_b="offensive")
        # Count HUMAN match wins (not rounds).
        # In 'match', returning "A" means player A (Human) wins.
        if winner == "A":
            # Update session counter
            HUMAN_WINS_VS_OFFENSIVE += 1
            print(f"\n[RIDDLE] Human wins recorded (Mode 1): {HUMAN_WINS_VS_OFFENSIVE}/3")
            if HUMAN_WINS_VS_OFFENSIVE >= 3:
                show_riddle_resolution()
        else:
            if winner is None:
                print("\n[RIDDLE] Match interrupted. No progress toward the riddle.")
            else:
                print("\n[RIDDLE] The AI won this match. Try again to unlock the riddle!")
    elif choice == "2":
        match(type_a="random", type_b="defensive")
    elif choice == "3":
        match(type_a="offensive", type_b="offensive")
    elif choice == "4":
        print("\n--- Test 1: Random vs Random ---")
        benchmark("random", "random", 100)
        print("\n--- Test 2: Defensive vs Random ---")
        benchmark("defensive", "random", 100)
        print("\n--- Test 3: Offensive vs Defensive ---")
        benchmark("offensive", "defensive", 100)
        print("\n--- Test 4: Offensive vs Offensive ---")
        benchmark("offensive", "offensive", 100)
    elif choice == "5":
        print("\n🚀 EXTENDED BENCHMARK (1000 matches)")
        print("\n--- Test 1: Random vs Random ---")
        benchmark("random", "random", 1000)
        print("\n--- Test 2: Defensive vs Random ---")
        benchmark("defensive", "random", 1000)
        print("\n--- Test 3: Offensive vs Defensive ---")
        benchmark("offensive", "defensive", 1000)
        print("\n--- Test 4: Offensive vs Offensive ---")
        benchmark("offensive", "offensive", 1000)
    else:
        print("Invalid choice. Starting Human vs AI match.")
        winner, _ = match(type_a="human", type_b="offensive")
        if winner == "A":
            HUMAN_WINS_VS_OFFENSIVE += 1
            print(f"\n[RIDDLE] Human wins recorded (Mode 1): {HUMAN_WINS_VS_OFFENSIVE}/3")
            if HUMAN_WINS_VS_OFFENSIVE >= 3:
                show_riddle_resolution()
