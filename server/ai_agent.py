import chess
import chess.polyglot

class AIAgent:
    def __init__(self):
        self.simulated_moves = 0

    # Piece values (centipawns)
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    def play(self, board: chess.Board) -> str:
        try:
            with chess.polyglot.open_reader("Titans.bin") as book:
                entry = book.find(board)
                return entry.move.uci()
        except:
            pass

        return ""