from math import inf
import time
import chess
import chess.polyglot
from typing import Optional, Tuple, List

# --- PIECE-SQUARE TABLES (PST) ---
# These replace complex evaluation logic. They define where pieces "like" to be.
# (Values are for White; the code mirrors them for Black automatically)
PST = {
    chess.PAWN: [
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
    ],
    chess.KNIGHT: [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ],
    chess.BISHOP: [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ],
    chess.ROOK: [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0
    ],
    chess.QUEEN: [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ],
    chess.KING: [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20
    ]
}

class AIAgent:
    def __init__(self):
        self.simulated_moves = 0
        self.tt = {}
        self.killer_moves = [[None, None] for _ in range(128)]  # max ply
        self.history = {}

        self.PIECE_VALUES = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }

    def play(self, origin_board: chess.Board, depth: int):
        board = origin_board.copy()
        
        # 1. Opening Book
        try:
            with chess.polyglot.open_reader("Titans.bin") as book:
                entry = book.find(board)
                return entry.move.uci(), "book", [], depth
        except:
            pass

        # Adjust depth (search deeper in endgames)
        new_depth = self.adjusted_depth(board, depth)
        
        start = time.time()
        self.simulated_moves = 0
        
        best_score = -inf
        best_move = None
        best_top_moves = []

        # 2. Iterative Deepening
        for current_depth in range(1, new_depth + 1):
            
            # Aspiration Window
            if current_depth > 1:
                alpha = best_score - 50
                beta  = best_score + 50
            else:
                alpha, beta = -inf, inf

            score, move, top_moves = self.negamax_root(
                board, current_depth, alpha, beta
            )

            # If score fell outside window, research with full window
            if score <= alpha or score >= beta:
                score, move, top_moves = self.negamax_root(
                    board, current_depth, -inf, inf
                )

            best_score = score
            best_move = move
            best_top_moves = top_moves

        exec_time = time.time() - start
        print(
            f"AI simulated {self.simulated_moves} moves in "
            f"{exec_time:.3f}s (best score {best_score}, depth {new_depth})"
        )

        if best_move is None:
            return None, self.simulated_moves, best_top_moves, new_depth
        
        return best_move.uci(), self.simulated_moves, best_top_moves, new_depth

    def negamax(self, board, depth, alpha, beta, ply):
        self.simulated_moves += 1
        alpha_orig = alpha

        # 1. Transposition Table Lookup
        key = board._transposition_key()
        if key in self.tt:
            entry = self.tt[key]
            if entry["depth"] >= depth:
                if entry["flag"] == "EXACT":
                    return entry["value"]
                elif entry["flag"] == "LOWER":
                    alpha = max(alpha, entry["value"])
                elif entry["flag"] == "UPPER":
                    beta = min(beta, entry["value"])
                if alpha >= beta:
                    return entry["value"]
        
        # 2. Check for game over or Quiescence
        if depth <= 0:
            return self.quiescence(board, alpha, beta)

        # --- OPTIMIZATION: SINGLE MOVE GENERATION ---
        moves = list(board.legal_moves)

        if not moves:
            # If no moves, it's either checkmate or stalemate
            if board.is_check():
                return -100000 + ply  # Mated
            else:
                return 0  # Stalemate

        # 3. Search
        # Order moves to search best ones first
        ordered_moves = self.order_moves(board, moves, ply)
        best_value = -inf

        for move in ordered_moves:
            board.push(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha, ply + 1)
            board.pop()

            if score > best_value:
                best_value = score
            
            alpha = max(alpha, score)

            if alpha >= beta:
                # Alpha-Beta Cutoff
                # Killer Move Heuristic
                killers = self.killer_moves[ply]
                if move != killers[0]:
                    killers[1] = killers[0]
                    killers[0] = move
                
                # History Heuristic
                self.history[(move.from_square, move.to_square)] = \
                    self.history.get((move.from_square, move.to_square), 0) + depth * depth
                break

        # 4. Store in Transposition Table
        flag = "EXACT"
        if best_value <= alpha_orig:
            flag = "UPPER"
        elif best_value >= beta:
            flag = "LOWER"

        self.tt[key] = {
            "value": best_value,
            "depth": depth,
            "flag": flag
        }

        return best_value

    def negamax_root(self, board, depth, alpha, beta):
        best_score = -inf
        best_move = None
        move_scores = []

        # 1. Get moves (sorted by your order_moves function)
        moves = self.order_moves(board, list(board.legal_moves), ply=0)
        
        # 2. Settings
        full_depth_count = 3  # How many moves to search at 100% depth
        reduction = 2         # How many levels of depth to "cut" for the others

        for i, move in enumerate(moves):
            board.push(move)
            
            if board.is_checkmate():
                board.pop()
                return 100000, move, [(move.uci(), 100000)]

            # --- HYBRID DEPTH LOGIC ---
            if i < full_depth_count:
                # Search the best moves fully to get exact scores
                score = -self.negamax(board, depth - 1, -inf, inf, ply=1)
            else:
                # Search the rest at a lower depth to get a "fast estimate"
                # We use max(1, ...) to ensure depth doesn't go below 1
                estimate_depth = max(1, depth - 1 - reduction)
                score = -self.negamax(board, estimate_depth, -inf, inf, ply=1)
            
            board.pop()
            move_scores.append((move, score))

            if score > best_score:
                best_score = score
                best_move = move

        # Sort results for the UI
        move_scores.sort(key=lambda x: x[1], reverse=True)
        top_moves = [(m.uci(), s) for m, s in move_scores[:10]]
        
        return best_score, best_move, top_moves

    def evaluate(self, board: chess.Board) -> int:
        """
        Fast evaluation using Piece-Square Tables (PST).
        """
        score = 0
        # Iterate over the piece map directly (fastest method in python-chess)
        for square, piece in board.piece_map().items():
            val = self.PIECE_VALUES[piece.piece_type]
            
            if piece.color == chess.WHITE:
                # Add material + positional bonus
                score += val + PST[piece.piece_type][chess.square_mirror(square)]
            else:
                # Subtract material + positional bonus (using mirrored square for black)
                score -= val + PST[piece.piece_type][square]

        return score if board.turn == chess.WHITE else -score

    def quiescence(self, board, alpha, beta):
        """
        Search until the position is 'quiet' (no captures) to avoid horizon effect.
        """
        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Generate only captures (Optimization)
        captures = board.generate_legal_moves(
            chess.BB_ALL, 
            board.occupied_co[not board.turn]
        )

        # MVV-LVA Sort for captures
        ordered_captures = []
        for m in captures:
            victim = board.piece_at(m.to_square)
            val = self.PIECE_VALUES[victim.piece_type] if victim else 0
            ordered_captures.append((val, m))
        
        ordered_captures.sort(key=lambda x: x[0], reverse=True)

        for _, move in ordered_captures:
            board.push(move)
            score = -self.quiescence(board, -beta, -alpha)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def order_moves(self, board, moves, ply):
        scored = []
        
        if ply >= 128: ply = 127
        killers = self.killer_moves[ply]

        for move in moves:
            score = 0
            
            # 1. MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                if victim:
                    attacker = board.piece_at(move.from_square)
                    score += 10000 + self.PIECE_VALUES[victim.piece_type] - (self.PIECE_VALUES[attacker.piece_type] // 10)
                elif board.is_en_passant(move):
                    score += 10100

            # 2. Killer Moves
            if move == killers[0]:
                score += 9000
            elif move == killers[1]:
                score += 8000

            # 3. History Heuristic
            score += self.history.get((move.from_square, move.to_square), 0)

            scored.append((score, move))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]

    def adjusted_depth(self, board, base_depth):
        # Calculate non-pawn material
        material = 0
        for piece in board.piece_map().values():
            if piece.piece_type != chess.KING and piece.piece_type != chess.PAWN:
                material += self.PIECE_VALUES[piece.piece_type]
        
        # Increase depth in endgame
        if material <= 2500:
            return base_depth + 2
        elif material <= 4000:
            return base_depth + 1
            
        return base_depth