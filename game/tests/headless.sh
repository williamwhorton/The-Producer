#!/usr/bin/env bash
set -euo pipefail

expected_version=4.7.2.stable.official.ed1daf0bf
version=$(godot --version)
printf 'Godot %s\n' "$version"
if [[ "$version" != "$expected_version" ]]; then
    printf 'Expected Godot %s on PATH.\n' "$expected_version" >&2
    exit 1
fi

scratch=$(mktemp -d)
log="$scratch/godot.log"
player_pack="$scratch/player.zip"
trap 'rm -f -- "$log" "$player_pack"; rmdir -- "$scratch"' EXIT

run_godot() {
    printf '\n> godot --headless %s\n' "$*"
    timeout --kill-after=5s 60s godot --headless "$@" 2>&1 | tee "$log"
    # Godot can log an import or script error without returning a nonzero status.
    if grep -Eq '^(SCRIPT ERROR|ERROR):' "$log"; then
        printf 'Godot reported errors; see the output above.\n' >&2
        return 1
    fi
}

check() {
    run_godot --path game "$@"
}

check --editor --import
check --quit-after 2
check --script res://tests/smoke.gd
check --script res://tests/smoke.gd -- --show-navigation
check --script res://tests/scheduler.gd
check --script res://tests/house_navigation.gd
check --script res://tests/scenario_loading.gd
check --script res://tests/contestant_runtime.gd
check --script res://tests/contestant_perception.gd
check --script res://tests/contestant_sharing.gd
check --script res://tests/contestant_departure.gd
check --script res://tests/prepared_effects.gd
check --script res://tests/live_observations.gd
check --script res://tests/causal_trace.gd
check --export-pack 'Linux privacy check' "$player_pack"
check --script res://tests/causal_trace.gd -- --verify-pack "$player_pack"
# Launch from the isolated pack and try the diagnostic arguments at the
# actual player entry point. Only the explicit source test script honors them.
run_godot --main-pack "$player_pack" --quiet --quit-after 2 -- --print-trace --seed 21
if [[ -s "$log" ]]; then
    printf 'Expected no console output from the player entry point.\n' >&2
    exit 1
fi
printf 'PASS: player pack boots without diagnostic output\n'
