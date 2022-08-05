let socket = io(location.host)

import {INPUT_EVENT_TYPE, COLOR, Chessboard, MARKER_TYPE, PIECE} from "../cm-chessboard/src/cm-chessboard/Chessboard.js"
import {Chess} from "./Chess.js"

$(document).ready(function() {
    let fen = $('#fen').text()
    let chess = new Chess(fen)
    const promoion_modal = document.querySelector('.promotion_modal')
    const overlay = document.getElementById('overlay')

    const board = new Chessboard(document.getElementById("board"), {
        position: chess.fen(),
        orientation: $('#current_player_color').text(),
        sprite: {url: "../static/cm-chessboard/assets/images/chessboard-sprite-staunty.svg"},
        style: {moveFromMarker: undefined, moveToMarker: undefined}, // disable standard markers
    })

    // move processing
    board.enableMoveInput(inputHandler)

    function inputHandler(event) {
        event.chessboard.removeMarkers(undefined, MARKER_TYPE.dot)
        event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)

        if (event.type === INPUT_EVENT_TYPE.moveStart) {
            const moves = chess.moves({square: event.square, verbose: true});
            event.chessboard.addMarker(event.square, MARKER_TYPE.square)
            for (const move of moves) {
                event.chessboard.addMarker(move.to, MARKER_TYPE.dot)
            }
            return true// moves.length > 0

        } else if (event.type === INPUT_EVENT_TYPE.moveDone) {
            let promotion = ''
            let target = event.squareTo
            let orientation = event.chessboard.getOrientation()

            const moves = chess.moves({square: event.squareFrom, verbose: true});
            const squares = []
            moves.forEach(move => {
                squares.push(move.to)
            })

            if (squares.includes(event.squareTo)) {
                if (target[1] == 8 && orientation == 'w' || target[1] == 1 && orientation == 'b') {
                    const modal = document.getElementById('modal')
                    openModal(modal, target)
                    return false
                }
            } else return false

            const move = {from: event.squareFrom, to: event.squareTo, promotion: promotion}
            const result = chess.move(move)
            // if (result) {
                send_fen(chess.fen(), promotion)
                // event.chessboard.removeMarkers(undefined, MARKER_TYPE.square)
            // } else {
                // console.warn("invalid move", move)
            // }
            return true //result
        }
    }

    // server communication
    function send_fen(fen, promotion) {
        let fen_pos = fen.split(' ')[0]
        socket.emit('fen_pos', fen_pos, promotion)
    }

    socket.on("fen", function(data) {
        let move_status = data["status"]
        let fen = data["fen"]
        chess = Chess(fen)
        board.setPosition(fen)
    })

    // modal logic
    function openModal(modal, target) {
        if (modal == null || target == null) return

        let multiplier = 'abcdefgh'.indexOf(target[0])
        modal.style.left = String(12.5 * multiplier) + '%'
        modal.classList.add('active')

        overlay.classList.add('active')
        overlay.removeEventListener('click', overlay_click_event)
        console.log("remove event listener")
        setTimeout(() => {
            console.log("timeout. add overlay event listener")
            overlay.addEventListener('click', overlay_click_event)
        }, 100)

        console.log("modal opened")
    }

    function closeModal(modal) {
        if (modal == null) return
        modal.classList.remove('active')
        overlay.classList.remove('active')
        console.log("modal closed")
    }

    promoion_modal.addEventListener('click', () => {
        console.log("modal clicked")
        closeModal(promoion_modal)
    })

    overlay.addEventListener('click', overlay_click_event)
    function overlay_click_event() {
        console.log("overlay clicked")
        const modals = document.querySelectorAll('.promotion_modal.active')
        modals.forEach(modal => {
            closeModal(modal)
        })
    }

    // modal gifs activation and deactivation
    const buttons = document.querySelectorAll('.promotion-button')
    buttons.forEach(button => {
        button.addEventListener('mouseover', () => {
            const img = button.getElementsByTagName('img')['0']
            const filename = img.getAttribute('src').split('.').slice(0, -1).join('.') + '.gif'
            img.setAttribute('src', filename)
        }, false)
        button.addEventListener('mouseout', () => {
            const img = button.getElementsByTagName('img')['0']
            const filename = img.getAttribute('src').split('.').slice(0, -1).join('.') + '.jpg'
            img.setAttribute('src', filename)
        }, false)
    })
})
