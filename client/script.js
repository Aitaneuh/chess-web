let selected = null;
let legalMoves = [];
let whiteToMove = true;
let available_moves = [];
let lastSelected = null;
let lastMove = null;
let checkmated = false;
const statusLbl = document.getElementById("status")
const pieces = {
    "P": "/client/pieces/wP.svg",
    "N": "/client/pieces/wN.svg",
    "B": "/client/pieces/wB.svg",
    "R": "/client/pieces/wR.svg",
    "Q": "/client/pieces/wQ.svg",
    "K": "/client/pieces/wK.svg",

    "p": "/client/pieces/bP.svg",
    "n": "/client/pieces/bN.svg",
    "b": "/client/pieces/bB.svg",
    "r": "/client/pieces/bR.svg",
    "q": "/client/pieces/bQ.svg",
    "k": "/client/pieces/bK.svg"
};


async function fetchState() {
    const res = await fetch("http://127.0.0.1:8000/api/state");
    return res.json();
}

function squareToCoord(row, col) {
    const file = "abcdefgh"[col];
    const rank = 8 - row;
    return file + rank;
}

function coordToSquare(coord) {
    const file = coord[0];
    const rank = parseInt(coord[1]);
    const col = "abcdefgh".indexOf(file);
    const row = 8 - rank;
    return { row, col };
}

function drawBoard(fen) {
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";

    const parts = fen.split(" ");
    const rows = parts[0].split("/");

    for (let r = 0; r < 8; r++) {
        let row = rows[r];
        let col = 0;

        for (const char of row) {
            if (!isNaN(char)) {
                // empty squares
                for (let i = 0; i < parseInt(char); i++) {
                    createSquare(r, col, "");
                    col++;
                }
            } else {
                createSquare(r, col, char);
                col++;
            }
        }
    }
}

function createSquare(r, c, piece) {
    const sq = document.createElement("div");
    sq.className = "square " + ((r + c) % 2 === 0 ? "light" : "dark");

    const coord = squareToCoord(r, c);
    sq.dataset.coord = coord;

    if (checkmated && piece) {
        if (whiteToMove && piece === "K") {
            sq.classList.add("checkmated-king");
        }
        if (whiteToMove && piece === "k") {
            sq.classList.add("won-king");
        }
        if (!whiteToMove && piece === "k") {
            sq.classList.add("checkmated-king");
        }
        if (!whiteToMove && piece === "K") {
            sq.classList.add("won-king");
        }
    }

    if (piece) {
        sq.classList.add("pieced");

        const img = document.createElement("img");
        img.src = pieces[piece];
        img.classList.add("piece");
        sq.appendChild(img);
    }

    if (selected && coord === selected) {
        sq.classList.add("selected");
    }

    if (lastSelected && coord === lastSelected) {
        sq.classList.add("selected");
    }

    if (lastMove && coord === lastMove) {
        sq.classList.add("selected");
    }

    sq.onclick = () => onSquareClick(coord);

    document.getElementById("board").appendChild(sq);
}


async function onSquareClick(coord) {
    // First click → select a square
    const sq = document.querySelector(`[data-coord="${coord}"]`);
    if (coord == selected) {
        available_moves = null;
        selected = null;
        update()
        return
    }

    if (!selected) {
        if (sq && !sq.classList.contains("pieced")) {
            return;
        }
        selected = coord;
        available_moves = await getLegalMovesForPiece(coord)
        update()
        return;
    }

    if (!available_moves.includes(coord)) {
        if (sq && sq.classList.contains("pieced")) {
            selected = coord;
            available_moves = await getLegalMovesForPiece(coord)
            update()
            return;
        }
        available_moves = null;
        selected = null;
        update()
        return
    }

    // Second click → try move selected->coord
    lastMove = coord;
    lastSelected = selected;
    const move = selected + coord;

    const res = await fetch("http://127.0.0.1:8000/api/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ move })
    });
    const data = await res.json();

    if (!data.success) {
        console.log("Illegal move");
    }

    selected = null;
    whiteToMove = !whiteToMove;
    available_moves = null;
    update();
}

async function update() {
    checkmated = await is_checkmate()
    updateStatus()
    const s = await fetchState();
    drawBoard(s.fen);
    showMoveDots(available_moves);
}

document.getElementById("restart").onclick = async () => {
    await fetch("http://127.0.0.1:8000/api/restart", { method: "POST" });
    selected = null
    whiteToMove = true;
    lastMove = null;
    lastSelected = null;
    checkmated = false;
    update();
};

async function getLegalMovesForPiece(coord) {
    const res = await fetch("http://127.0.0.1:8000/api/legal_moves", {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ coord })
    })
    const data = await res.json();
    return data.moves
}

async function is_checkmate() {
    const res = await fetch("http://127.0.0.1:8000/api/is_checkmate", { method: "POST" })
    const data = await res.json();
    return data.is_checkmate
}

function showMoveDots(moves) {
    document.querySelectorAll(".move-dot").forEach(e => e.remove());

    if(!moves) {
        return;
    }
    moves.forEach(m => {
        const sq = document.querySelector(`[data-coord="${m}"]`);
        if (!sq) return;

        const dot = document.createElement("div");

        if (sq.classList.contains("pieced")) {
            dot.classList.add("move-dot", "capture");
        } else {
            dot.classList.add("move-dot");
        }

        sq.appendChild(dot);
    });
}


function updateStatus() {
    if (!checkmated) { statusLbl.innerText = whiteToMove ? "White to move" : "Black to move" }
    else { statusLbl.innerText = whiteToMove ? "Black won the match" : "White won the match" }
    
}

update();
