from math import inf
import random
import time
import chess
import chess.polyglot
import chess.syzygy
from typing import Optional, Tuple

SYZYGY_PATH = "/syzygy"

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

        # Final tables
        tb_move = self.choose_tablebase_move(board, tb_path=SYZYGY_PATH)
        if tb_move:
            print("Playing tablebase move:", tb_move)
            return tb_move.uci()

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

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                attackers = board.attackers(not piece.color, square)
                defenders = board.attackers(piece.color, square)

                if attackers and not defenders:
                    value = self.PIECE_VALUES[piece.piece_type]
                    if piece.color == chess.WHITE:
                        score -= value // 2
                    else:
                        score += value // 2
        return score
    
    def order_moves(self, board: chess.Board, moves):
        scored = []

        for move in moves:
            score = 0

            # 1. Prioritize captures (MVV-LVA like you do)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)

                if victim and attacker:
                    score += 10_000 + (
                        self.PIECE_VALUES[victim.piece_type] -
                        self.PIECE_VALUES[attacker.piece_type]
                    )

            else:
                # 2. Castling bonus
                if board.is_castling(move):
                    score += 6_000  # small but important priority

                # 3. Development bonus (only in early game)
                if board.fullmove_number <= 10:
                    piece = board.piece_at(move.from_square)
                    if piece and piece.piece_type in (chess.KNIGHT, chess.BISHOP):
                        score += 2_000

                # 4. Centralization (your original idea but stronger)
                to = move.to_square
                file = chess.square_file(to)
                rank = chess.square_rank(to)
                score += 1_000 - abs(file - 3.5) - abs(rank - 3.5)

            scored.append((score, move))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored]



    # DISCLAIMER : this syzygy function was not made by me
    def choose_tablebase_move(self, board: chess.Board, tb_path: str = SYZYGY_PATH) -> Optional[chess.Move]:
        """
        If the current position (or its next moves) is covered by syzygy tablebases,
        pick the best move according to WDL/DTZ probe.
        Returns a chess.Move or None if no tablebase info is available.
        """
        try:
            with chess.syzygy.open_tablebase(tb_path) as tb:
                best_win: Optional[Tuple[int, chess.Move]] = None   # (dtz, move) smallest dtz is best
                best_draw: Optional[chess.Move] = None
                best_loss: Optional[Tuple[int, chess.Move]] = None  # (dtz, move) largest dtz is best

                # iterate all legal moves and probe resulting position
                for mv in board.legal_moves:
                    board.push(mv)
                    try:
                        wdl = tb.probe_wdl(board)   # expected: 1 win, 0 draw, -1 loss (probe may raise if not covered)
                    except Exception:
                        # not covered by TB for this resulting position
                        board.pop()
                        continue

                    # try dtz if available (some tablebases / configs provide dtz)
                    try:
                        dtz = tb.probe_dtz(board)
                        if dtz is None:
                            dtz = 0
                    except Exception:
                        dtz = 0

                    board.pop()

                    if wdl == 1:
                        # winning move: prefer smallest dtz (fastest conversion)
                        if best_win is None or dtz < best_win[0]:
                            best_win = (dtz, mv)
                    elif wdl == 0:
                        # any draw is acceptable; keep first draw if no win
                        if best_draw is None:
                            best_draw = mv
                    else:  # wdl == -1
                        # losing move: prefer largest dtz (delay loss)
                        if best_loss is None or dtz > best_loss[0]:
                            best_loss = (dtz, mv)

                # choose priority: win > draw > loss
                if best_win:
                    return best_win[1]
                if best_draw:
                    return best_draw
                if best_loss:
                    return best_loss[1]

                return None
        except FileNotFoundError:
            # tablebase path doesn't exist
            return None
        except Exception:
            # any other TB error -> gracefully fallback
            return None