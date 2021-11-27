let socket = io(location.host)

function send_fen(source, target, piece, pos, old_pos, orientation) {
    let fen = Chessboard.objToFen(pos)
    if (target == 'offboard') {
        fen = Chessboard.objToFen(old_pos)
    }
    socket.emit('fen_pos', fen)
}

$(document).ready(function() {
    var config = {
        draggable: true,
        position: 'start',
        orientation: $('#current_player_color').text(),
        onDrop: send_fen
    }
    var board = Chessboard('board', config)

    socket.on('fen_pos', function(fen) {
        board.position(fen)
        console.log('Fen position: ' + fen)
    })

})
