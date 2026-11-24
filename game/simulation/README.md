# Simulation boundary

This module will own private world state and game rules. Keep it runnable
without the world renderer, HUD, or persistence; do not pass private state
to either player-facing view.

#27 has no simulation. The launch scene runs on a static floor plan without
a game clock, actors, or randomness. Add domain code when a simulation issue
needs it rather than creating an unused interface here.
