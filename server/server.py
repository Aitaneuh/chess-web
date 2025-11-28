import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import chess
import chess.pgn

from ai_agent import AIAgent

app = Flask(__name__)
ai_agent = AIAgent()
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
    uci = data["move"] # type: ignore

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

@app.route("/api/legal_moves", methods=["POST"])
def legal_moves():
    global board
    data = request.json
    coord = data.get("coord") # type: ignore
    square = chess.parse_square(coord)
    moves = []

    for move in board.legal_moves:
        if move.from_square == square:
            moves.append(chess.square_name(move.to_square))

    return jsonify({"moves": moves})

@app.route("/api/is_checkmate", methods=["POST"])
def is_checkmate():
    global board
    return jsonify({"is_checkmate": board.is_checkmate()})

@app.route("/api/ai_play", methods=["POST"])
def ai_play():
    global board
    move = "e7e5"
    time.sleep(0.5)
    return jsonify({"move": move})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
