extends Node2D

# Isometric renderer for Issue #13 - Godot 4.7 prototype
# Coordinates are in Godot units; 1 unit = 64 pixels (isometric scale)
const TILE_SIZE : int = 64
const GRID_SIZE : int = 10

var upper_visible := true
var selected_room_index : int = 0
var room_markers : Dictionary = {}  # "RoomA", "RoomB", "RoomC" -> marker nodes
var marker_positions : Array[Vector2] = []

@onready var MarkerA: CharacterBody2D = null
@onready var MarkerB: CharacterBody2D = null

func _ready():
	set_process_input(true)
	# Initialize marker positions for demo (two connected cells in Room A and B)
	marker_positions.append(Vector2(1 * TILE_SIZE, TILE_SIZE))   # Cell in Room A - hardcoded demo position
	marker_positions.append(Vector2(4 * TILE_SIZE, TILE_SIZE))   # Cell in Room B - hardcoded demo position
	
	# Connect to markers to set their targets
	var maroon := MarkerA.get_node_or_null("MarkerA") as CharacterBody2D
	var contestant := MarkerB.get_node_or_null("MarkerB") as CharacterBody2D
	if maroon:
		maroon.target_position = marker_positions[0] if marker_positions.size() > 0 else position
	if contestant:
		contestant.target_position = marker_positions[1] if marker_positions.size() > 1 else position
	
	# No supernatural marker in this prototype (Issue #13 scope)
	
	update()

func _input(event):
	if event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
		# Pan camera by moving the node
		position -= event.relative * 0.01
	elif event is InputEventMouseButton and event.is_pressed() and event.button_index == MOUSE_BUTTON_WHEEL_UP:
		scale *= 1.1
	elif event is InputEventMouseButton and event.is_pressed() and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		scale /= 1.1
	elif event is InputEventKey:
		match event.keycode:
			KEY_R:
				# Toggle upper floor visibility
				upper_visible = not upper_visible
				var upper = get_node_or_null("UpperFloor") as Control
				if upper:
					upper.visible = upper_visible
			KEY_SPACE:
				# Cycle through rooms (highlighted by selection rect)
				selected_room_index = (selected_room_index + 1) % room_markers.size()
				var sel_name = ["RoomA", "RoomB", "RoomC"][selected_room_index]
				var sel_marker = get_node_or_null(sel_name) as Control
				if sel_marker:
					marker_positions[0] = Vector2(1 * TILE_SIZE, 1 * TILE_SIZE) + sel_marker.position
			KEY_LEFT:
				# Move marker left (debug control)
				if has_node("MarkerA") and marker_positions.size() > 0:
					var maroon = MarkerA.get_node_or_null("MarkerA") as CharacterBody2D
					if maroon:
						maroon.target_position.x -= TILE_SIZE
			KEY_RIGHT:
				# Move marker right (debug control)
				if has_node("MarkerA") and marker_positions.size() > 0:
					var maroon = MarkerA.get_node_or_null("MarkerA") as CharacterBody2D
					if maroon:
						maroon.target_position.x += TILE_SIZE

func update():
	# Update selection rect position
	var sel_rect = get_node_or_null("SelectionRect") as ColorRect
	if sel_rect:
		sel_rect.offset_left = marker_positions[selected_room_index].x - 64
		sel_rect.offset_top = marker_positions[selected_room_index].y - 64
		sel_rect.size.x = 128
		sel_rect.size.y = 128
