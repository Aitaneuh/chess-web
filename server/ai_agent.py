from math import inf
import random
import time
import chess
import chess.polyglot

class AIAgent:
    def __init__(self):
        self.simulated_moves = 0

    PIECE_VALUES = {
        chess.PAWN: 10,
        chess.KNIGHT: 30,
        chess.BISHOP: 30,
        chess.ROOK: 50,
        chess.QUEEN: 90,
        chess.KING: 900
    }

    def play(self, board: chess.Board, depth: int) -> str:
        start = time.time()
        

        # Opening book
        try:
            with chess.polyglot.open_reader("Titans.bin") as book:
                entry = book.find(board)
                print("Book move")
                return entry.move.uci()
        except:
            pass

        best_score = -inf
        best_move = None

        analysis_board = board.copy()
        for move in analysis_board.legal_moves:
            analysis_board.push(move)
            score = -self.negamax(analysis_board, depth - 1, -inf, inf, 1 if analysis_board.turn else -1)
            analysis_board.pop()

            if score > best_score or (score == best_score and random.random() < 0.2):
                best_score = score
                best_move = move

        execTime = time.time() - start
        print(f"AI simulated {self.simulated_moves} moves in {execTime:.3f}s")
        self.simulated_moves = 0

        return best_move.uci() if best_move else ""

    def negamax(self, board: chess.Board, depth: int, alpha: float, beta: float, color: int) -> float:
        if depth == 0:
            return color * self.evaluate(board)

        if board.is_checkmate():
            return color * (-1_000_000 + (5 - depth))
        if board.is_stalemate():
            return 0

        best_value = -inf

        for move in board.legal_moves:
            self.simulated_moves += 1

            board.push(move)
            score = -self.negamax(board, depth - 1, -beta, -alpha, -color)
            board.pop()

            if score > best_value:
                best_value = score

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_value
        
    def evaluate(self, board: chess.Board) -> int:
        score = 0
        for piece_type in self.PIECE_VALUES:
            value = self.PIECE_VALUES[piece_type]
            score += value * len(board.pieces(piece_type, chess.WHITE))
            score -= value * len(board.pieces(piece_type, chess.BLACK))
        return score
