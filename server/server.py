from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import chess
import chess.pgn

app = Flask(__name__)
CORS(app)

# Global game state (simple version)
board = chess.Board()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/state")
def get_state():
    """Return full board state as FEN + turn + legal moves."""
    legal_moves = [move.uci() for move in board.legal_moves]
    return jsonify({
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "legal_moves": legal_moves,
        "is_check": board.is_check(),
        "is_game_over": board.is_game_over(),
        "result": board.result() if board.is_game_over() else None
    })

@app.route("/api/move", methods=["POST"])
def play_move():
    global board
    data = request.json
    uci = data.get("move") # type: ignore

    try:
        move = chess.Move.from_uci(uci)
        if move in board.legal_moves:
            board.push(move)
            return jsonify({"success": True, "fen": board.fen()})
        else:
            return jsonify({"success": False, "error": "Illegal move"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/restart", methods=["POST"])
def restart():
    global board
    board = chess.Board()
    return jsonify({"success": True, "fen": board.fen()})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
