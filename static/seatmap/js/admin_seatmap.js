$(document).ready(function(){
    seatmap_id = window.location.pathname.split('/')[4];

	//show_grid = false;
	GRID_INC = 15;
	preview_container = '#participant-preview';
    create_canvas('#seatmap-fieldset'); // height and width are dependent on the parent element

    init_canvas({
		canvas_id : 'seatmap-canvas',
		draw_chair_selector: '#chair-button',
		move_selector: '#move-button',
		admin_select_selector: '#select-button',
		zoom_out_selector: '#zoom-out-button',
		zoom_in_selector: '#zoom-in-button',
		save_selector: '#save-button',
		pan_selector: '#pan-button',
        draw_table_selector: '#aux-button',
        select_table_selector: '#s-table-button',
	});
    populate_canvas(seatmap_id);
    $('#seatmap-message').hide();
    $('#seatmap-toolbar').show();

    $('#seatmap-fieldset').mousemove(function(e) {
        $('#tooltip').css({
            'top': e.clientY + $(document).scrollTop() - 190,
            'left': e.clientX - 5
        });
    });
});