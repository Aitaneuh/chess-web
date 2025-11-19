let selected = null;
let legalMoves = [];

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
    return {row, col};
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

    if (piece) {
        sq.textContent = piece;
    }

    sq.onclick = () => onSquareClick(coord);

    document.getElementById("board").appendChild(sq);
}

async function onSquareClick(coord) {
    // First click → select a square
    if (!selected) {
        selected = coord;
        return;
    }

    // Second click → try move selected->coord
    const move = selected + coord;

    const res = await fetch("http://127.0.0.1:8000/api/move", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({move})
    });
    const data = await res.json();

    if (!data.success) {
        console.log("Illegal move");
    }

    selected = null;
    update();
}

async function update() {
    const s = await fetchState();
    drawBoard(s.fen);
}

document.getElementById("restart").onclick = async () => {
    await fetch("http://127.0.0.1:8000/api/restart", {method: "POST"});
    update();
};

update();
