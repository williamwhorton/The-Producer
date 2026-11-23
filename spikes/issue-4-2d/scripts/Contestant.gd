extends CharacterBody2D

const SPEED = 80.0
const TILE_SIZE = 64.0

var target_position : Vector2

func _ready():
    position = Vector2(4 * TILE_SIZE, TILE_SIZE)
	
func _physics_process(delta):
	if target_position:
		position.move_toward(target_position, SPEED * delta)
