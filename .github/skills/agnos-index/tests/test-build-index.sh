#!/usr/bin/env bash
# Tests of build-index.sh against the shared fixtures and expected files.
# Covers RQ-IDX-001 to RQ-IDX-009, RQ-IDX-015, RQ-IDX-016 and RQ-IDX-018 (ADR-IDX-001, DEC-IDX-004).
# RQ-PLG-048, RQ-PLG-049 / DEC-PLG-039: the nominal fixture holds IDs in 0.facts/ and 4.knowledge/, absent from its expected index.
# The whole suite runs twice: default mode, then POSIX mode (POSIXLY_CORRECT=1).
# Usage: bash .github/skills/agnos-index/tests/test-build-index.sh
set -u

# RQ-PLG-036 / DEC-PLG-027: the folder and the index's name come from the skill's layout copy; the fixtures and expected
# files are written for a folder named FIXTURE_FOLDER, which each scenario renames to the layout's.
HERE=$(cd "$(dirname "$0")" && pwd)
SCRIPTS="$HERE/../scripts"
SCRIPT="$SCRIPTS/build-index.sh"
. "$SCRIPTS/agnos-layout.sh"
FIXTURE_FOLDER="process"
OTHER_FOLDER="other-folder"
OTHER_INDEX="other.idx.md"
OLD_TIME="200001010000"
DURATION_SUFFIX_ERE=' in [0-9]+\.[0-9]{3} s$'  # RQ-IDX-018
failures=0

# The expected strings and paths for a folder and an index name (RQ-PLG-036).
set_layout() {
  folder="$1"
  INDEX_REL="$1/$2"
  EXPECTED_NOMINAL_REPORT="agnos-index: 13 entries, 6 documents, $INDEX_REL"
  EXPECTED_DUPLICATE_REPORT="agnos-index: 3 entries, 1 documents, $INDEX_REL updated"
  EXPECTED_DUPLICATE_ERROR="agnos-index: DUPLICATE RQ-DUP-001 $1/1.requirements/FTR-DUP-001.md:5 (first: $1/1.requirements/FTR-DUP-001.md:3)"
  EXPECTED_MISSING_ERROR="agnos-index: '$1' folder not found - run from the repository root, or call agnos-init to add AGNOS to this project"
}

# An expected index with its document paths under the current folder (RQ-PLG-036).
expected() {
  sed "s#^@$FIXTURE_FOLDER/#@$folder/#" "$HERE/expected/$1.idx.md" >"$dir/.expected"
  echo "$dir/.expected"
}

new_scenario() {
  dir=$(mktemp -d)
  if [ -n "$1" ]; then cp -R "$HERE/fixtures/$1/$FIXTURE_FOLDER" "$dir/$folder"; fi
}

run_generator() {
  if [ "$mode" = "posix" ]; then
    (cd "$dir" && POSIXLY_CORRECT=1 bash "$SCRIPT" >"$dir/.out" 2>"$dir/.err")
  else
    (cd "$dir" && bash "$SCRIPT" >"$dir/.out" 2>"$dir/.err")
  fi
  code=$?
  out=$(cat "$dir/.out")
  report=$(printf %s "$out" | sed -E "s/$DURATION_SUFFIX_ERE//")  # report without its RQ-IDX-018 duration
  err=$(cat "$dir/.err")
}

check() {
  if [ "$2" = "0" ]; then echo "PASS [$mode] $1"; else echo "FAIL [$mode] $1"; failures=$((failures + 1)); fi
}

set_layout "$AGNOS_FOLDER" "$AGNOS_INDEX"
for mode in default posix; do
  # Scenario: nominal documents
  new_scenario nominal
  run_generator
  [ "$code" = 0 ]; check "Given nominal documents When indexing Then the exit code is 0 [RQ-IDX-009]" $?
  cmp -s "$dir/$INDEX_REL" "$(expected nominal)"
  check "Given nominal documents When indexing Then the index equals the expected bytes [RQ-IDX-001..006, RQ-IDX-015]" $?
  [ "$report" = "$EXPECTED_NOMINAL_REPORT updated" ]; check "Given nominal documents When indexing Then the report says updated [RQ-IDX-009]" $?
  printf %s "$out" | grep -Eq "$DURATION_SUFFIX_ERE" && [ "$(printf %s "$out" | wc -l)" -eq 0 ]
  check "Given nominal documents When indexing Then the single report line ends with the duration [RQ-IDX-018]" $?
  ! grep -Eq ' in [0-9]+\.[0-9]{3} s' "$dir/$INDEX_REL"; check "Given nominal documents When indexing Then the index holds no duration [RQ-IDX-018]" $?
  touch -t "$OLD_TIME" "$dir/$INDEX_REL" "$dir/.marker"
  run_generator
  [ "$report" = "$EXPECTED_NOMINAL_REPORT unchanged" ]; check "Given an up-to-date index When indexing again Then the report says unchanged [RQ-IDX-009]" $?
  ! [ "$dir/$INDEX_REL" -nt "$dir/.marker" ]; check "Given an up-to-date index When indexing again Then the file is not rewritten [RQ-IDX-009]" $?
  rm -rf "$dir"

  # Scenario: duplicate definitions
  new_scenario duplicate
  run_generator
  [ "$code" = 2 ]; check "Given a duplicate ID When indexing Then the exit code is 2 [RQ-IDX-007]" $?
  [ "$err" = "$EXPECTED_DUPLICATE_ERROR" ]; check "Given a duplicate ID When indexing Then the duplicate is reported [RQ-IDX-007]" $?
  cmp -s "$dir/$INDEX_REL" "$(expected duplicate)"
  check "Given a duplicate ID When indexing Then the index is still written [RQ-IDX-007, RQ-IDX-015]" $?
  [ "$report" = "$EXPECTED_DUPLICATE_REPORT" ]; check "Given a duplicate ID When indexing Then the report line is printed [RQ-IDX-009]" $?
  rm -rf "$dir"

  # Scenario: no process folder
  new_scenario ""
  run_generator
  [ "$code" = 1 ]; check "Given no process folder When indexing Then the exit code is 1 [RQ-IDX-008]" $?
  [ "$err" = "$EXPECTED_MISSING_ERROR" ]; check "Given no process folder When indexing Then the error is reported [RQ-IDX-008]" $?
  [ ! -e "$dir/$folder" ] && [ -z "$out" ]; check "Given no process folder When indexing Then nothing is written [RQ-IDX-008]" $?
  rm -rf "$dir"
done

# Scenario: a layout naming another folder and index (RQ-PLG-036, TASK-PLG-040)
skill=$(mktemp -d)
mkdir "$skill/scripts"
cp "$SCRIPT" "$skill/scripts/"
sed -e "s#^AGNOS_FOLDER=.*#AGNOS_FOLDER='$OTHER_FOLDER'#" -e "s#^AGNOS_INDEX=.*#AGNOS_INDEX='$OTHER_INDEX'#" \
  "$SCRIPTS/agnos-layout.sh" >"$skill/scripts/agnos-layout.sh"
SCRIPT="$skill/scripts/build-index.sh"
mode=default
set_layout "$OTHER_FOLDER" "$OTHER_INDEX"
new_scenario nominal
run_generator
[ "$code" = 0 ] && cmp -s "$dir/$INDEX_REL" "$(expected nominal)"
check "Given a layout naming another folder When indexing Then its index holds the same entries under that folder [RQ-PLG-036]" $?
[ "$report" = "$EXPECTED_NOMINAL_REPORT updated" ]; check "Given a layout naming another folder When indexing Then the report names its index [RQ-PLG-036]" $?
rm -rf "$dir" "$skill"

if [ "$failures" -gt 0 ]; then echo "$failures check(s) failed"; exit 1; fi
echo "All checks passed"
exit 0
