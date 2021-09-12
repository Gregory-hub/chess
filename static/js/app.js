let socket = io(location.host)

$('#logout').on('click', function() {
    socket.disconnect()
})

$('button.invite_button').on('click', function() {
    let username = this.id
    game_data = {
        '': '',
    }
    socket.emit('invite', username, game_data)
    console.log('invite')
})

socket.on('error', function(message) {
    $('#invitation_result').html(message)
})

socket.on('success', function(message) {
    $('#invitation_result').html(message)
})

socket.on('invite', function(data) {
    $('#invitation').html('Invitation from', inviting, game_data)
})
