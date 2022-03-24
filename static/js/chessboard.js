let socket = io(location.host)
import {INPUT_EVENT_TYPE, COLOR, Chessboard, MARKER_TYPE} from "../cm-chessboard/src/cm-chessboard/Chessboard.js"

function send_fen(source, target, piece, pos, old_pos, orientation) {
    let fen = Chessboard.objToFen(pos)
    if (target == 'offboard') {
        fen = Chessboard.objToFen(old_pos)
    }
    socket.emit('fen_pos', fen)
}

$(document).ready(function() {
    // var config = {
    //     draggable: true,
    //     onDrop: send_fen
    // }

    const board = new Chessboard(document.getElementById("board"), {
        position: $('#fen_pos').text(),
        orientation: $('#current_player_color').text(),
        sprite: {url: "../static/cm-chessboard/assets/images/chessboard-sprite-staunty.svg"}
    })

    socket.on('fen_pos', function(fen) {
        board.position(fen)
        console.log('Fen position: ' + fen)
    })

})

const chess = new Chess()

function inputHandler(event) {
    console.log("event", event)
    event.chessboard.removeMarkers(undefined, MARKER_TYPE.dot)
    event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)
    if (event.type === INPUT_EVENT_TYPE.moveStart) {
        const moves = chess.moves({square: event.square, verbose: true});
        event.chessboard.addMarker(event.square, MARKER_TYPE.square)
        for (const move of moves) {
            event.chessboard.addMarker(move.to, MARKER_TYPE.dot)
        }
        return moves.length > 0
    } else if (event.type === INPUT_EVENT_TYPE.moveDone) {
        const move = {from: event.squareFrom, to: event.squareTo}
        const result = chess.move(move)
        if (result) {
            event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)
            event.chessboard.disableMoveInput()
            event.chessboard.setPosition(chess.fen())
            const possibleMoves = chess.moves({verbose: true})
            if (possibleMoves.length > 0) {
                const randomIndex = Math.floor(Math.random() * possibleMoves.length)
                const randomMove = possibleMoves[randomIndex]
                setTimeout(() => { // smoother with 500ms delay
                    chess.move({from: randomMove.from, to: randomMove.to})
                    event.chessboard.enableMoveInput(inputHandler, COLOR.white)
                    event.chessboard.setPosition(chess.fen())
                }, 500)
            }
        } else {
            console.warn("invalid move", move)
        }
        return result
    }
}

const board = new Chessboard(document.getElementById("board"), {
    position: chess.fen(),
    sprite: {url: "../assets/images/chessboard-sprite-staunty.svg"},
    style: {moveFromMarker: undefined, moveToMarker: undefined}, // disable standard markers
    orientation: COLOR.white
})
board.enableMoveInput(inputHandler, COLOR.white)