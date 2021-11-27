function send_fen(source, target, piece, pos, old_pos, orientation) {
    let socket = io(location.host)
    let fen = Chessboard.objToFen(pos)
    socket.emit('fen', fen)
}

$(document).ready(function() {
    var config = {
        draggable: true,
        position: 'start',
        orientation: $('#current_player_color').text(),
        onDrop: send_fen
    }
    var board = Chessboard('board', config)

    let socket = io(location.host)
    socket.on('fen', function(fen) {
        board.position(fen)
    })
})
