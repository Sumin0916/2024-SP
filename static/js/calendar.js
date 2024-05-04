select: function(start, end) {
    var time_slot = prompt('Enter Time Slot (e.g., "13:00-15:00"):');
    if (time_slot) {
        var eventData = {
            title: time_slot,
            start: start.format(),
            end: end.format()
        };
        $('#calendar').fullCalendar('renderEvent', eventData, true);

        // AJAX 호출
        $.ajax({
            url: '/add_reservation',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                date: start.format('YYYY-MM-DD'),
                time_slot: time_slot
            }),
            success: function(response) {
                alert(response.message);
            },
            error: function(xhr, status, error) {
                alert('Error adding reservation: ' + error);
            }
        });
    }
    $('#calendar').fullCalendar('unselect');
},
