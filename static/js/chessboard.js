
let socket = io(location.host)

import {INPUT_EVENT_TYPE, COLOR, Chessboard, MARKER_TYPE} from "../cm-chessboard/src/cm-chessboard/Chessboard.js"
import {Chess} from "./Chess.js"

$(document).ready(function() {
    let fen = $('#fen').text()
    let chess = new Chess(fen)

    const board = new Chessboard(document.getElementById("board"), {
        position: chess.fen(),
        orientation: $('#current_player_color').text(),
        sprite: {url: "../static/cm-chessboard/assets/images/chessboard-sprite-staunty.svg"},
        style: {moveFromMarker: undefined, moveToMarker: undefined}, // disable standard markers
    })
    board.enableMoveInput(inputHandler)

    function inputHandler(event) {
        console.log("event", event)
        event.chessboard.removeMarkers(undefined, MARKER_TYPE.dot)
        event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)
        if (event.type === INPUT_EVENT_TYPE.moveStart) {
            const moves = chess.moves({square: event.square, verbose: true});
            console.log(moves)
            event.chessboard.addMarker(event.square, MARKER_TYPE.square)
            for (const move of moves) {
                event.chessboard.addMarker(move.to, MARKER_TYPE.dot)
            }
            return moves.length > 0
        } else if (event.type === INPUT_EVENT_TYPE.moveDone) {
            console.log(event)
            let promotion = ""
            const move = {from: event.squareFrom, to: event.squareTo, promotion: promotion}
            console.log(move)
            const result = chess.move(move)
            if (result) {
                send_fen(chess.fen(), promotion)
                event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)
            } else {
                console.warn("invalid move", move)
            }
            return result
        }
    }

    function send_fen(fen, promotion) {
        let fen_pos = fen.split(' ')[0]
        socket.emit('fen_pos', fen_pos, promotion)
    }

    socket.on("fen", function(data) {
        let move_status = data["status"]
        let fen = data["fen"]
        chess = Chess(fen)
        board.setPosition(fen)
        console.log("Status: ", move_status)
        console.log("Fen: ", fen)
    })
})
