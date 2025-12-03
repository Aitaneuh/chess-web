# Python Chess Engine (Negamax + Alpha-Beta + Opening Book)

<p align="center">
  <img src="image/logo.png" width="500" alt="Project Logo"/>
</p>

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![VanillaJS](https://img.shields.io/badge/Vanilla_JS-F0DB4F?style=for-the-badge&logo=javascript&logoColor=323330)
![AI](https://img.shields.io/badge/AI-Negamax-blueviolet?style=for-the-badge&logo=OpenAI&logoColor=white)

---

This project contains a lightweight chess engine written in Python using **python-chess**, featuring:

* ✔️ Full **Negamax search** implementation
* ✔️ **Alpha–Beta pruning**
* ✔️ **Basic evaluation** (material score)
* ✔️ **Transposition-ready architecture**
* ✔️ **opening book support (.bin Polyglot)**
* ✔️ Can be used as a standalone engine or embedded into any UI (CLI, WebSocket, GUI…)

---

## Features

### Search Algorithm

The engine uses **Negamax**, a simplified Minimax formulation that unifies evaluation for both players:

* Efficient and clean recursive structure
* Alpha–Beta pruning to skip irrelevant branches
* Move simulation via `board.push()` / `board.pop()`
* Search depth configurable

The algorithm is intentionally simple and educational, serving as a foundation for:

* Move ordering
* Quiescence search
* Transposition tables
* Aspiration windows
* Principal Variation Search (PVS)

All of these can be added incrementally.

---

## Evaluation Function

Currently the evaluation is **material-based only**:

| Piece  | Value (centipawns) |
| ------ | ------------------ |
| Pawn   | 10                 |
| Knight | 30                 |
| Bishop | 30                 |
| Rook   | 50                 |
| Queen  | 90                 |
| King   | 900  (symbolic)    |

This keeps the engine stable, predictable, and easy to debug.

---

## Opening Book (Optional)

You can enable an opening book using any Polyglot `.bin` file:

```python
with chess.polyglot.open_reader("Titans.bin") as book:
    entry = book.find(board)
    return entry.move.uci()
```

If no book move is available, the engine falls back to the search algorithm.

---

## Installation

## Example Usage

```python
import chess
from ai_agent import AIAgent

engine = AIAgent()
board = chess.Board()

# Get best move at depth 3
best_move = engine.play(board, depth=3)
print("Engine plays:", best_move)
```

---

## Roadmap

### Near-term improvements

* Move ordering (captures first, killer moves, history heuristic)
* Quiescence search (reduces horizon effect)
* Transposition table (Zobrist hashing)

### Mid-term

* Evaluation with:

  * Piece-square tables
  * King safety
  * Passed pawns
  * Mobility

### Long-term

* Iterative deepening
* Principal Variation Search (PVS)
* Opening book trainer
* Self-play mode for reinforcement learning

---

## Author

Project created by Aitaneuh — enthusiast developer building his first full chess engine from scratch.