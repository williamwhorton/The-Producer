extends CharacterBody2D

const SPEED = 30.0
const TILE_SIZE = 64.0

# Simple wandering behavior
var wander_target : Vector2
var wander_timer : float = 0.0
var wander_interval : float = 2.0

func _ready():
    position = Vector2(5 * TILE_SIZE, -1 * TILE_SIZE)
	wander_target = position
	
func _physics_process(delta):
	# Simple wandering
	wander_timer -= delta
	
	if wander_timer <= 0:
		# Choose a new random target in nearby cells
		var dx = randi_range(-3, 3)
		var dy = randi_range(-1, 2)
		wander_target += Vector2(dx * TILE_SIZE, dy * TILE_SIZE)
		wander_timer = wander_interval
	
	if position.distance_to(wander_target) < SPEED * delta * 60:
		position = wander_target
	else:
		position.move_toward(wander_target, SPEED * delta)
