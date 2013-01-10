$(document).ready(function(){
    seatmap_id = $('#seatmap_id').val();

	show_grid = false;
	GRID_INC = 15;
	preview_container = '#preview';
    create_canvas('#seatmap-container'); // height and width are dependent on the parent element

    init_canvas({
		canvas_id : 'seatmap-canvas',
		zoom_out_selector: '#zoom-out-button',
		zoom_in_selector: '#zoom-in-button',
		select_seat_selector: '#select-seat-button',
		pan_selector: '#pan-button',
	});
    populate_canvas(seatmap_id);
    $('#seatmap-message').hide();
    $('#seatmap-toolbar').show();
	$('#select-seat-button').click();
	$('button').button();
});
