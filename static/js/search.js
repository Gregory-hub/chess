$(document).ready(function() {
    $('#search').on('input', function() {
        query = this.value
        socket.emit('search', query)
    })
    
    socket.on('search_result', function(matched_users) {
        $('.dropdown-item').remove()
        for (let i = 0; i < matched_users.length; i++) {
            result_item = '<li class="dropdown-item list-group-item search-dropdown-item" id="search-dropdown-item-' + matched_users[i] + '">' + matched_users[i] + '</li>'
            $('#dropdown-results').append(result_item)

            $('#search-dropdown-item-' + matched_users[i]).on('click', function() {
                $('#search').val($('#search-dropdown-item-' + matched_users[i]).text())
                $('.dropdown-item').remove()
            })
        }
    })
})
