extends CharacterBody2D

class_name PlayerMarker

# Demo marker behavior for Issue #13 prototype
const SPEED = 80.0
const TILE_SIZE = 64.0

var target_position : Vector2

func _ready():
    # Hardcoded demo position in Room B (Cell)
    position = Vector2(4 * TILE_SIZE, TILE_SIZE)
	
func _physics_process(delta):
	if target_position:
		position.move_toward(target_position, SPEED * delta)
