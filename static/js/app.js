$(document).ready(function() {
    let socket = io(location.host)

    $('#logout').on('click', function() {
        socket.disconnect()
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
})
