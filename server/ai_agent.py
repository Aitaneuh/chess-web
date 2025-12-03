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
        ordered_moves = self.order_moves(analysis_board, list(analysis_board.legal_moves))
        for move in ordered_moves:

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
            return -1_000_000 + (5 - depth)
        if board.is_stalemate():
            return 0

        best_value = -inf

        ordered_moves = self.order_moves(board, list(board.legal_moves))
        for move in ordered_moves:
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
    
    def order_moves(self, board: chess.Board, moves):
        scored = []

        for move in moves:
            score = 0

            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)

                if victim and attacker:
                    score += 10_000 + (self.PIECE_VALUES[victim.piece_type] -
                                    self.PIECE_VALUES[attacker.piece_type])

            else:
                to = move.to_square
                file = chess.square_file(to)
                rank = chess.square_rank(to)
                # bonus for central squares (e4 e5 d4 d5)
                score += 1_000 - abs(file - 3.5) - abs(rank - 3.5)

            scored.append((score, move))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]

