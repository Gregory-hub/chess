let socket = io(location.host)

import {INPUT_EVENT_TYPE, COLOR, Chessboard, MARKER_TYPE, PIECE} from "../cm-chessboard/src/cm-chessboard/Chessboard.js"
import {Chess} from "./Chess.js"

$(document).ready(function() {
    let fen = $('#fen').text()
    let chess = new Chess(fen)
    let target
    let source
    const promoion_modal = document.querySelector('.promotion_modal')
    let modal_opened = false
    const sq_q = document.getElementById('sq-q')
    const sq_r = document.getElementById('sq-r')
    const sq_b = document.getElementById('sq-b')
    const sq_n = document.getElementById('sq-n')
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
            return true         // moves.length > 0

        } else if (event.type === INPUT_EVENT_TYPE.moveDone) {
            target = event.squareTo
            source = event.squareFrom
            let orientation = event.chessboard.getOrientation()
            let piece = chess.get(source)

            if (piece.type == 'p' && (target[1] == 8 && orientation == 'w' || target[1] == 1 && orientation == 'b')) {
                const moves = chess.moves({square: event.squareFrom, verbose: true});
                const squares = []
                moves.forEach(move => {
                    squares.push(move.to)
                })

                if (squares.includes(event.squareTo) ) {
                    const modal = document.getElementById('modal')
                    openModal(modal, target)
                } 
                return false
            }

            const move = {from: event.squareFrom, to: event.squareTo, promotion: ''}
            const result = chess.move(move)
            // if (result) {                                                    // FRONTENT MOVE CHECK
                send_fen(chess.fen(), '')
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
        if (modal == null  || target == null) return

        let multiplier = 'abcdefgh'.indexOf(target[0])
        if (target[1] == 8) {
            modal.style.left = String(12.5 * multiplier) + '%'
        } else {
            modal.style.left = String(87.5 - 12.5 * multiplier) + '%'
        }
        modal.classList.add('active')

        overlay.classList.add('active')
        overlay.removeEventListener('click', overlay_click_event)
        console.log("remove event listener")
        setTimeout(() => {
            console.log("timeout. add overlay event listener")
            overlay.addEventListener('click', overlay_click_event)
        }, 100)

        console.log("modal opened")
        modal.addEventListener('touchend', modalMouseUp)
        modal_opened = true
    }

    function modalMouseUp(modal)
    {
        modal.removeEventListener('touchend', modalMouseUp)
    }

    function closeModal(modal) {
        if (modal == null) return
        modal.classList.remove('active')
        overlay.classList.remove('active')
        console.log("modal closed")
        modal_opened = false
    }

    sq_q.addEventListener('click', () => {
        if (!modal_opened) return
        console.log("queen clicked")
        const move = {from: source, to: target, promotion: 'q'}
        chess.move(move)
        send_fen(chess.fen(), 'q')
        closeModal(promoion_modal)
    })

    sq_r.addEventListener('click', () => {
        if (!modal_opened) return
        console.log("rook clicked")
        const move = {from: source, to: target, promotion: 'r'}
        chess.move(move)
        send_fen(chess.fen(), 'r')
        closeModal(promoion_modal)
    })

    sq_b.addEventListener('click', () => {
        if (!modal_opened) return
        console.log("bishop clicked")
        const move = {from: source, to: target, promotion: 'b'}
        chess.move(move)
        send_fen(chess.fen(), 'b')
        closeModal(promoion_modal)
    })

    sq_n.addEventListener('click', () => {
        if (!modal_opened) return
        console.log("knight clicked")
        const move = {from: source, to: target, promotion: 'n'}
        chess.move(move)
        send_fen(chess.fen(), 'n')
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
