#!/usr/bin/env bash
set -euo pipefail

expected_version=4.7.2.stable.official.ed1daf0bf
version=$(godot --version)
printf 'Godot %s\n' "$version"
if [[ "$version" != "$expected_version" ]]; then
    printf 'Expected Godot %s on PATH.\n' "$expected_version" >&2
    exit 1
fi

log=$(mktemp)
trap 'rm -f -- "$log"' EXIT

check() {
    printf '\n> godot --headless --path game %s\n' "$*"
    timeout --kill-after=5s 60s godot --headless --path game "$@" 2>&1 | tee "$log"
    # Godot can log an import or script error without returning a nonzero status.
    if grep -Eq '^(SCRIPT ERROR|ERROR):' "$log"; then
        printf 'Godot reported errors; see the output above.\n' >&2
        return 1
    fi
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
