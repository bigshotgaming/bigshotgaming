$(document).ready(function(){
    seatmap_id = $('#seatmap_id').val();
    user = $('#user_username').val();

	show_grid = false;
	GRID_INC = 15;
	preview_container = '#preview';
    create_canvas('#seatmap-container'); // height and width are dependent on the parent element

    var canvas_options = {
        canvas_id : 'seatmap-canvas',
        zoom_out_selector: '#zoom-out-button',
        zoom_in_selector: '#zoom-in-button',
        pan_selector: '#pan-button'
    }

    if(user != "") {
        canvas_options.select_seat_selector = "#select-seat-button";
    } else {
        $('#select-seat-button').hide();

    }

    init_canvas(canvas_options);
    populate_canvas(seatmap_id, user);
    $('#seatmap-message').hide();
    $('#seatmap-toolbar').show();
	$('button').button();

    if (user != "") {
        $('#select-seat-button').click();
    }


    /* testing... create a div to follow the cursor around */
    $('#seatmap-container').mousemove(function(e) {
        $('#tooltip').css({
            'top': e.clientY + $(document).scrollTop() + 20,
            'left': e.clientX + 20
        });
    });


});
