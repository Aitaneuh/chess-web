from cmath import inf
import random
import time
import chess
import chess.polyglot

class AIAgent:
    def __init__(self):
        self.simulated_moves = 0

    # using chess programming wiki values
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
        try:
            with chess.polyglot.open_reader("Titans.bin") as book:
                entry = book.find(board)
                execTime = time.time() - start
                print("Execution time:", execTime, "s")
                return entry.move.uci()
        except:
            pass

        best_score = float("-inf")
        if not board.legal_moves:
            return ""
        best_move = random.choice(list(board.legal_moves))
        
        for move in board.legal_moves:
            analysis_board = board.copy()
            analysis_board.push(move)
            if analysis_board.is_checkmate():
                return move.uci()

            score = self.negamax(board, -inf, inf, depth, analysis_board.turn)
            if score > best_score or (score == best_score and random.random() < 0.3):
                best_score = score
                best_move = move

        execTime = time.time() - start
        print("Execution time:", execTime, "s")
        return best_move.uci()
    
    def negamax(self, board: chess.Board, alpha: float, beta: float, depth:int, player: chess.Color) -> float:
        return -inf