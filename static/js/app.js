$(document).ready(function() {
    let socket = io(location.host)

    $('#logout').on('click', function() {
        socket.disconnect()
    })

    $('#config_form').on('submit', function() {
        data = {
            'game_time': $('#game_time').val(),
            'supplement': $('#supplement').val(),
            'current_player_color': $('#player_color').val(),
            'opponent': $('#search').val()
        }
        console.log('Sent invitation to ' + data['opponent'])
        socket.emit('invite', data)
    })

    socket.on('error', function(message) {
        console.log('Error: ' + message)
    })

    socket.on('invite', function(data) {
        game_data = data['game_data']
        $('#flash_message').remove()
        $('#flashes-container').append(`<div class="nav-item flash_message" id="flash_message">Invitation from ${game_data['opponent']}</div>`)
        console.log('Invitation: ' + game_data)
    })
})
