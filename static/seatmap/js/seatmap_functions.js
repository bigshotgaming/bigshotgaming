var stage;
var tool_mode = "draw_chair";
var GRID_INC = 25;
var ZOOM_PERCENT = 0.1;
var PAN_STRENGTH = 1.0 // Percentage the stage will move while panning
var TABLE_LABEL_FONT_SIZE = 16;
var COLORS = {
	USER_SEAT_STROKE: '#B2B200',
	USER_SEAT_FILL: '#FFFF00',
	USER_SEAT_STROKE_OVER: '#B2B200',
	USER_SEAT_FILL_OVER: '#FFFF99',
	OPEN_SEAT_STROKE: '#008A20',
	OPEN_SEAT_FILL: '#16C940',
	OPEN_SEAT_STROKE_OVER: '#008A20',
	OPEN_SEAT_FILL_OVER: '#4FDB70',
	CLOSED_SEAT_STROKE: '#800000',
	CLOSED_SEAT_FILL: '#BA1414',
	CLOSED_SEAT_STROKE_OVER: '#800000',
	CLOSED_SEAT_FILL_OVER: '#E85454',
	TAKEN_SEAT_STROKE: '#800000',
	TAKEN_SEAT_FILL: '#BA1414',
	TAKEN_SEAT_STROKE_OVER: '#800000',
	TAKEN_SEAT_FILL_OVER: '#E85454',
	ADMIN_SEAT_STROKE: '#7891E3',
	ADMIN_SEAT_FILL: '#2247BF',
	ADMIN_SEAT_STROKE_OVER: '#7891E3',
	ADMIN_SEAT_FILL_OVER: '#748EE3',
	DEFAULT_STROKE: '#A8A8A8',
	DEFAULT_FILL: '#A8A8A8',
	GRID_COLOR: '#D4D4D4',
    TABLE_COLOR: '#292929',
    TABLE_TEXT_COLOR: '#FFFFFF',
}
var grid;
var chairs;
var tables;
var table_names;
var cur_table = null;
var mouse_down = false;
var seatmap_id;
var selected_seat = null;
update = false;
var show_grid = true;
var preview_container;

function populate_canvas(seatmap_id, user) {
    if ($('#seat_data').length > 0) {
        var e = eval($('#seat_data').val());
        for (var i = 0; i < e.length; i++) {
            addSeat(e[i].fields.x * GRID_INC, e[i].fields.y * GRID_INC, e[i].fields.participant, e[i].fields.status, user);
        }
        e = eval($('#table_data').val());
        for (var i = 0; i < e.length; i++) {
            addTable(e[i].fields.x * GRID_INC, e[i].fields.y * GRID_INC, e[i].fields.w, e[i].fields.h, e[i].fields.name);
        }
        stage.update();
    } else {
        $.ajax({
            url: '/seatmap/admin/data/?object_type=seat',
            data: 'seatmap_id=' + seatmap_id,
            type: 'GET',
        }).done(function(e) {
            for (var i = 0; i < e.length; i++) {
                addSeat(e[i].fields.x * GRID_INC, e[i].fields.y * GRID_INC, e[i].fields.participant, e[i].fields.status, user);
            }
        }).fail(function(e) {
            console.log('fail');
        });
        
        $.ajax({
            url: '/seatmap/admin/data/?object_type=table',
            data: 'seatmap_id=' + seatmap_id,
            type: 'GET',
        }).done(function(e) {
            for (var i = 0; i < e.length; i++) {
                addTable(e[i].fields.x * GRID_INC, e[i].fields.y * GRID_INC, e[i].fields.w, e[i].fields.h, e[i].fields.name);
            }
            stage.update();
        }).fail(function(e) {
            console.log('fail');
        });
    }
}

function create_canvas(parent_element) {
    var h = $(parent_element).height();
    if (h < 500) {
        h = 500;
    }
    var canvas = $('<canvas id="seatmap-canvas" width="' + ($(parent_element).width() - 20) + '" height="' + h + '">Please use a browser with canvas support.</canvas>');
    $(parent_element).append(canvas);
}

function init_canvas(options) {
    createjs.Ticker.setFPS(30);
    createjs.Ticker.addListener(stage);
	createjs.Ticker.addListener(window);

    stage = new createjs.Stage('seatmap-canvas');//options.canvas_id);
    createjs.Touch.enable(stage);
	stage.enableMouseOver();
    stage.panning = false;
    stage.drawing_table = false;
    stage.pan_origin = {x: 0, y:0};
    stage.pan_origin_loc = {x: 0, y:0};

    chairs = new createjs.Container();
    stage.addChild(chairs);
    
    tables = new createjs.Container();
    stage.addChild(tables);
    
    table_names = new createjs.Container();
    stage.addChild(table_names);
	init_grid();

    stage.update();

    if (options.select_table_selector != null) {
        $(options.select_table_selector).click(function() {
            stage.onMouseDown = function(e) {
				// get the seat that is being selected
				var x = e.stageX - stage.x;
				var y = e.stageY - stage.y;
				var objects = this.getObjectsUnderPoint(x, y);
				var selected_object = null;
				for (var i = 0; i < objects.length; i++) {
					if (objects[i].object_type == "table") {
						selected_object = objects[i];
						
					}
				}
				// show the dialog to select a user
				if (selected_object != null) {
                    if (selected_object.name != null) {
                        $('#table-text-box').val(selected_object.name);
                    }
					$('#table-dialog').dialog({
						title: "Edit a table",
						height:130,
                        buttons: {
                            "Remove Table": function() {
                                selected_object.text.text = '';
                                selected_object.text.visible = false;
                                table_names.removeChild(selected_object.text);
                                tables.removeChild(selected_object);
                                stage.update();
                                $( this ).dialog( "close" );
                            },
                            "Update": function() {
                                selected_object.name = $('#table-text-box').val();
                                selected_object.drawTable();
                                stage.update();
                                $( this ).dialog( "close" );
                            }
                        }
					});
				}
			}
			stage.onMouseUp = null;
        });
    }
    
    if (options.draw_table_selector != null) {
        $(options.draw_table_selector).click(function() {
            stage.onMouseDown = draw_table_mouse_down;
            stage.onMouseUp = draw_table_mouse_up;
        });
    }
    
	if (options.draw_chair_selector != null) {
		$(options.draw_chair_selector).click(function() {
			stage.onMouseDown = handle_draw_chair_click;
			stage.onMouseUp = null;
		});
	}
	if (options.move_selector != null) {
		$(options.move_selector).click(function() {
			stage.onMouseDown = handle_move_chair_mouse_down;
			stage.onMouseUp = handle_move_chair_mouse_up;
		});
	}
	if (options.admin_select_selector != null) {
		$(options.admin_select_selector).click(function() {
			stage.onMouseDown = function(e) {
				// get the seat that is being selected
				var x = e.stageX - stage.x;
				var y = e.stageY - stage.y;
				var objects = this.getObjectsUnderPoint(x, y);
				var selected_object = null;
				for (var i = 0; i < objects.length; i++) {
					if (objects[i].object_type == "seat") {
						selected_object = objects[i];
					}
				}
				// show the dialog to select a user
				if (selected_object != null) {
					selected_seat = selected_object;
					$('#participant-dialog').dialog({
						title: "Search for a User",
						height:260,
					});
				}
			}
			stage.onMouseUp = null;
		});
		
		function search_results() {
			$.ajax({
				url: '/seatmap/admin/seatmap/user/',
				data: 'q=' + $('#user-search-box').val(),
				type: 'GET',
			}).done(function(e) {
				$('#user-search-results ul')[0].innerHTML = '';
				for(var i = 0; i < e.length; i++) {
					var li = $('<li><a href="javascript:applyUserToCurrentSeat(\'' + e[i] + '\')">' + e[i] + '</a></li>');
					$('#user-search-results ul').append(li);
				}
			}).fail(function(e) {
				//console.log('failed');
			});
		}
		$('#user-search-box').keypress(function (e) {
		  if (e.which == 13) {
			search_results();
		  }
		});
		$('#user-search-button').click(search_results);
	}
	
	if (options.zoom_out_selector != null) {
		$(options.zoom_out_selector).click(function() {
			GRID_INC -= GRID_INC * ZOOM_PERCENT;
			if (show_grid) {
				grid.graphics.clear();
				init_grid();
			}
			for (var i = 0; i < chairs.children.length; i++) {
				var c = chairs.children[i];
				c.drawSeat();
				c.x = c.x - c.x * ZOOM_PERCENT;
				c.y = c.y - c.y * ZOOM_PERCENT;
			}
            
            for (var i = 0; i < tables.children.length; i++) {
				var t = tables.children[i];
				t.x = t.x - t.x * ZOOM_PERCENT;
				t.y = t.y - t.y * ZOOM_PERCENT;
                t.drawTable();
			}
            
			stage.update();
		});
	}
	if (options.zoom_in_selector != null) {
		$(options.zoom_in_selector).click(function() {
			GRID_INC += GRID_INC * ZOOM_PERCENT;
			if(show_grid) {
				grid.graphics.clear();
				init_grid();
			}
			for (var i = 0; i < chairs.children.length; i++) {
				var c = chairs.children[i];
				c.drawSeat();
				c.x = c.x + c.x * ZOOM_PERCENT;
				c.y = c.y + c.y * ZOOM_PERCENT;
			}
            
            for (var i = 0; i < tables.children.length; i++) {
				var t = tables.children[i];
				t.x = t.x + t.x * ZOOM_PERCENT;
				t.y = t.y + t.y * ZOOM_PERCENT;
                t.drawTable();
			}
            
			stage.update();
		});
	}
	if(options.pan_selector != null) { 
		$(options.pan_selector).click(function() {
			stage.onMouseDown = handle_pan_mouse_down;
			stage.onMouseUp = handle_pan_mouse_up;
		});
	}
	
	if (options.save_selector != null) {
		$(options.save_selector).click(function() {
			var seat_data = [];
			for (var i = 0; i < chairs.children.length; i++) {
				var c = chairs.children[i];
				var my_data = {
					x: Math.round(c.x / GRID_INC),
					y: Math.round(c.y / GRID_INC),
					status: c.status,
					seatmap_id: seatmap_id, // dont really need this
					type: 'seat',
					participant: c.participant
				};
				seat_data.push(my_data);
			}
            var table_data = [];
			for (var i = 0; i < tables.children.length; i++) {
				var t = tables.children[i];
				var my_data = {
					x: Math.round(t.x / GRID_INC),
					y: Math.round(t.y / GRID_INC),
                    w: t.width,
                    h: t.height,
					name: t.name,
					type: 'table',
				};
				table_data.push(my_data);
			}
			$.ajax({
				url: '/seatmap/admin/seatmap/save/',
				data: 'table_data=' + JSON.stringify(table_data) + '&seat_data=' + JSON.stringify(seat_data) + '&seatmap_id=' + seatmap_id,
				type: 'POST',
			}).done(function(e) {
				console.log('success');
			}).fail(function(e) {
				console.log('failure');
			});
			console.log(seat_data);
		});
	}
	
	if (options.select_seat_selector != null) {
		$(options.select_seat_selector).click(function() {
			stage.onMouseDown = function(e) {
				// get the seat that is being selected
				var x = e.stageX - stage.x;
				var y = e.stageY - stage.y;
				var objects = this.getObjectsUnderPoint(x, y);
				var selected_object = null;
				for (var i = 0; i < objects.length; i++) {
					if (objects[i].object_type == "seat" && objects[i].status == "O") {
						selected_object = objects[i];
						
					}
				}
				// show the dialog to select a user
				if (selected_object != null) {
					selected_seat = selected_object;
					$('#select-seat-dialog').dialog({
						title: "Confirm Seat",
						width:390,
						buttons: [
							{
								text: "Yes, reserve this seat.",
								click: function() {
									$.ajax({
										url: '/seatmap/admin/seatmap/sitdown/',
										data: 'seatmap_id=' + seatmap_id + '&x=' + Math.round(selected_seat.x / GRID_INC) + '&y=' + Math.round(selected_seat.y / GRID_INC),
										type: 'POST',
									}).done(function(e) {
										window.location.reload()
									}).fail(function(e) {
										console.log('fail');
									});
								}
							},
							{
								text: "No, pick a different seat.",
								click: function() {
									$('#select-seat-dialog').dialog("close");
								}
							}
						]
					});
				}
			}
			stage.onMouseUp = null;
		});
	}
}

function addTable(x, y, w, h, name) {
    var t = new createjs.Shape();
	
	t.mouseover = false;
    t.snapToGrid = function(x, y) {
        if (x < 0) {
            this.x = x - (GRID_INC - Math.abs(x) % GRID_INC);
        } else {
            this.x = x - x % GRID_INC;
        }
        if (y < 0) {
            this.y = y - (GRID_INC - Math.abs(y) % GRID_INC);
        } else {
            this.y = y - y % GRID_INC;
        }
    };
    t.snapToGrid(x, y);
    t.width = w;
    t.height = h;
    stage.draw_table_x = t.x;
    stage.draw_table_y = t.y;
    t.name = name;
    t.drawTable = function() {
        this.graphics.clear();
        this.graphics.setStrokeStyle(1);

        this.graphics.beginStroke(COLORS.TABLE_COLOR);
        this.graphics.beginFill(COLORS.TABLE_COLOR);
 
        this.graphics.drawRect(0, 0, GRID_INC * this.width, GRID_INC * this.height);
         
        if (this.text != null) {
            table_names.removeChild(this.text);
        }
        
        this.text = new createjs.Text(this.name, TABLE_LABEL_FONT_SIZE + "px Arial", COLORS.TABLE_TEXT_COLOR);
        this.text.x = this.x + (GRID_INC * this.width - this.text.getMeasuredWidth()) / 2;
        this.text.y = this.y + (GRID_INC * this.height - this.text.getMeasuredHeight()) / 2;
        table_names.addChild(this.text);
    };
    t.drawTable();
	
	t.object_type = "table";
	tables.addChild(t);
    return t;
}

function draw_table_mouse_down(e) {
    var x = e.stageX - stage.x;
    var y = e.stageY - stage.y;
    
    t = addTable(x, y, 1, 1, '');
    
    cur_table = t;
	
	stage.update();
    stage.drawing_table = true;
}

function draw_table_mouse_up(e) {
    var x = e.stageX - stage.x;
    var y = e.stageY - stage.y;
    
    stage.drawing_table = false;
}

function applyUserToCurrentSeat(username) {
	// Remove participant from any other seat first...
	selected_seat.participant = username;
	$("#participant-dialog").dialog("close");
}

function handle_pan_mouse_down(e) {
	stage.panning = true;
	stage.pan_origin = {x : stage.mouseX, y : stage.mouseY};
    stage.pan_origin_loc = {x : stage.x, y : stage.y};
}

function handle_pan_mouse_up(e) {
	stage.panning = false;
}

selected_object = null;
function handle_move_chair_mouse_down(e) {
	var x = e.stageX - stage.x;
    var y = e.stageY - stage.y;
	var objects = this.getObjectsUnderPoint(x, y);
	for (var i = 0; i < objects.length; i++) {
		if (objects[i].object_type == "seat") {
			selected_object = objects[i];
			selected_object.offset = {x : selected_object.x - e.stageX, y : selected_object.y - e.stageY};
			selected_object.origin = {x : selected_object.x, y : selected_object.y};
		}
	}
}

/*
    Still need to deal with whenever they mouseup over a gridline.  for now they can click the square again.
*/
function handle_move_chair_mouse_up(e) {
    var x = e.stageX - stage.x;
    var y = e.stageY - stage.y;
	var objects = this.getObjectsUnderPoint(x, y);
	for (var i = 0; i < objects.length; i++) {
		if (objects[i].object_type == "seat" && objects[i] != selected_object) {
			objects[i].x = selected_object.origin.x;
			objects[i].y = selected_object.origin.y;
	        
            selected_object.snapToGrid(x, y);	
			stage.update();
		}
	}
	if (objects.length == 1 && selected_object != null) {
        selected_object.snapToGrid(x, y);
		stage.update();
	}
	selected_object = null;
}

function handle_draw_chair_click(e) {
    var x = e.stageX - stage.x;
    var y = e.stageY - stage.y;
	var objects = this.getObjectsUnderPoint(x, y);
	for (var i = 0; i < objects.length; i++) {
		if (objects[i].object_type == "seat") {
			chairs.removeChild(objects[i]);
			stage.update();
		}
	}
	if (objects.length == 0) {
		addSeat(x, y, null, $('#chair-type-select').val());
	}
}

function addSeat(x, y, participant, status, user) {
	var s = new createjs.Shape();
	
	if (participant != null) {
		if (participant.length == 2) {
			s.participant = participant[0];
		} else {
			s.participant = participant
		}
	} else {
		s.participant = null;
	}
	
	s.status = status;
	s.mouseover = false;
    s.snapToGrid = function(x, y) {
        if (x < 0) {
            this.x = x - (GRID_INC - Math.abs(x) % GRID_INC);
        } else {
            this.x = x - x % GRID_INC;
        }
        if (y < 0) {
            this.y = y - (GRID_INC - Math.abs(y) % GRID_INC);
        } else {
            this.y = y - y % GRID_INC;
        }
    };
    s.snapToGrid(x, y);
    s.drawSeat = function() {
        this.graphics.clear();
        this.graphics.setStrokeStyle(1);

		if (s.participant === user) {
			if (this.mouseover == true) {
				this.graphics.beginStroke(COLORS.USER_SEAT_STROKE_OVER);
				this.graphics.beginFill(COLORS.USER_SEAT_FILL_OVER);
			} else {
				this.graphics.beginStroke(COLORS.USER_SEAT_STROKE);
				this.graphics.beginFill(COLORS.USER_SEAT_FILL);
			}
		} else if (this.status == "O") {
			if (this.mouseover == true) {
				this.graphics.beginStroke(COLORS.OPEN_SEAT_STROKE_OVER);
				this.graphics.beginFill(COLORS.OPEN_SEAT_FILL_OVER);
			} else {
				this.graphics.beginStroke(COLORS.OPEN_SEAT_STROKE);
				this.graphics.beginFill(COLORS.OPEN_SEAT_FILL);
			}
		} else if (this.status == "C") {
			if (this.mouseover == true) {
				this.graphics.beginStroke(COLORS.CLOSED_SEAT_STROKE_OVER);
				this.graphics.beginFill(COLORS.CLOSED_SEAT_FILL_OVER);
			} else {
				this.graphics.beginStroke(COLORS.CLOSED_SEAT_STROKE);
				this.graphics.beginFill(COLORS.CLOSED_SEAT_FILL);
			}
		} else if (this.status == "A") {
			if (this.mouseover == true) {
				this.graphics.beginStroke(COLORS.ADMIN_SEAT_STROKE_OVER);
				this.graphics.beginFill(COLORS.ADMIN_SEAT_FILL_OVER);
			} else {
				this.graphics.beginStroke(COLORS.ADMIN_SEAT_STROKE);
				this.graphics.beginFill(COLORS.ADMIN_SEAT_FILL);
			}
		} else if (this.status == "T") {
			if (this.mouseover == true) {
				this.graphics.beginStroke(COLORS.TAKEN_SEAT_STROKE_OVER);
				this.graphics.beginFill(COLORS.TAKEN_SEAT_FILL_OVER);
			} else {
				this.graphics.beginStroke(COLORS.TAKEN_SEAT_STROKE);
				this.graphics.beginFill(COLORS.TAKEN_SEAT_FILL);
			}
		} else {
			this.graphics.beginStroke(COLORS.DEFAULT_STROKE);
			this.graphics.beginFill(COLORS.DEFAULT_FILL);
		}
        this.graphics.drawRect(0, 0, GRID_INC, GRID_INC);
    };
    s.drawSeat();
    s.onMouseOver = function(e) {
		this.mouseover = true;
		if (this.participant == null) {
			$('#tooltip').hide();
		} else {
			$('#tooltip').show()
            $('#tooltip')[0].innerHTML = 'User: ' + this.participant;
		}
		this.drawSeat();
		stage.update();
    };
	s.onMouseOut = function(e) {
		$('#tooltip').hide();
		this.mouseover = false;
		this.drawSeat();
		stage.update();
	};
	
	s.object_type = "seat";
	chairs.addChild(s);
	
	stage.update();
}

// redo this because it sucks...
function init_grid() {
	if (show_grid) {
		var width = stage.canvas.width;
		var height = stage.canvas.height;
		
		grid = new createjs.Shape();
		grid.graphics.clear();
		grid.graphics.beginStroke(COLORS.GRID_COLOR);
		// I know there's a better way of doing this, but my maths are broken right now...
		// Vertical lines
		for (var liney = 0; liney <= width + Math.abs(stage.x); liney += GRID_INC) {
			grid.graphics.moveTo(liney, -Math.abs(stage.y));
			grid.graphics.lineTo(liney, height + Math.abs(stage.y));
		}
		// left of the stage
		for (var liney = -GRID_INC; liney > -Math.abs(stage.x); liney -= GRID_INC) {
			grid.graphics.moveTo(liney, -Math.abs(stage.y));
			grid.graphics.lineTo(liney, height + Math.abs(stage.y));
		}
		// Horizontal lines
		for (var linex = 0; linex <= height + Math.abs(stage.y); linex += GRID_INC) {
			grid.graphics.moveTo(-Math.abs(stage.x), linex);
			grid.graphics.lineTo(width + Math.abs(stage.x), linex);
		}
		// Above the stage
		for (var linex = -GRID_INC; linex > -Math.abs(stage.y); linex -= GRID_INC) {
			grid.graphics.moveTo(-Math.abs(stage.x), linex);
			grid.graphics.lineTo(width + Math.abs(stage.x), linex);
		}

		grid.graphics.closePath();
		stage.addChild(grid);
	}
}

function tick() {
	// this set makes it so the stage only re-renders when an event handler indicates a change has happened.
	if (selected_object != null) {
		selected_object.x = stage.mouseX + selected_object.offset.x;
		selected_object.y = stage.mouseY + selected_object.offset.y;
		stage.update();
	}

	if(stage.panning) {
        stage.x = stage.pan_origin_loc.x + (stage.pan_origin.x - stage.mouseX) * PAN_STRENGTH;
        stage.y = stage.pan_origin_loc.y + (stage.pan_origin.y - stage.mouseY) * PAN_STRENGTH;

        init_grid();

		stage.update();
	}
    
    if (stage.drawing_table) {
        if (cur_table != null) {
            cur_table.width = Math.ceil((stage.mouseX - stage.draw_table_x) / GRID_INC);
            cur_table.height = Math.ceil((stage.mouseY - stage.draw_table_y) / GRID_INC);
            cur_table.drawTable();
            stage.update();
        }
    }
}
