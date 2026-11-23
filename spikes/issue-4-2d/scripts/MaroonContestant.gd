extends CharacterBody2D

const SPEED = 100.0
const TILE_SIZE = 64.0

var target_position : Vector2
var current_index : int = 0

func _ready():
    position = Vector2(1 * TILE_SIZE, TILE_SIZE)
	
func _physics_process(delta):
	# Demo movement: move between two connected cells automatically
	if target_position and position.distance_to(target_position) < SPEED * delta * 60:
		current_index = (current_index + 1) % 2
		target_position = [
			Vector2(1 * TILE_SIZE, TILE_SIZE),   # Cell in Room A
			Vector2(4 * TILE_SIZE, TILE_SIZE)    # Cell in Room B (connected through doorway)
		][current_index]
		position = target_position
	else:
		position.move_toward(target_position, SPEED * delta)
