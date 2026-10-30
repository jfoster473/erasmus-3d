#!/bin/zsh
# The game's tests in one launch (round 26): `tools/run_tests.sh quick` (about 3 minutes: missions, stairs, the north,
# the Sagrat Cor, the debug menu) or `tools/run_tests.sh full` (everything, about 15 minutes). Silent. The log and the
# pictures go to workshop/test-runs/barcelona/<quick|full>/. Starts a fresh game (the test save is deleted first).
cd "$(dirname "$0")/.."
kind=${1:-quick}
out="$PWD/workshop/test-runs/barcelona/$kind"
rm -rf "$out"; mkdir -p "$out"
rm -f "$HOME/Library/Application Support/Godot/app_userdata/Flor de Lliri - Godot test/test_save.json"
if [[ $kind == quick ]]; then arg="--quick"; else arg="--full=$out"; fi
perl -e 'alarm 1500; exec @ARGV' /Applications/Godot.app/Contents/MacOS/Godot --audio-driver Dummy --path . -- $arg > "$out/log.txt" 2>&1
echo "exit $?"
grep -v "^$\|HAIRMASK\|SHROOMS\|Godot Engine\|Metal\|timeout waiting for fence" "$out/log.txt"
