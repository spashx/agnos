#!/usr/bin/env bash
# The delivered skills' suites on a copy of a repository's tree, on Linux (RQ-PLG-008, RQ-PLG-010 / DEC-PLG-006).
# Usage: linux_suites.sh <repository>. The repository and the user's git configuration stay as they are. Exit code 1 if a suite fails.
set -u
[ $# -eq 1 ] || { echo 'usage: linux_suites.sh <repository>' >&2; exit 1; }
SKILLS=.github/skills
work=$(mktemp -d) || exit 1
trap 'rm -rf "$work"' EXIT
export GIT_CONFIG_GLOBAL="$work/gitconfig"
git config --file "$GIT_CONFIG_GLOBAL" user.name proof
git config --file "$GIT_CONFIG_GLOBAL" user.email proof@example.invalid
git config --file "$GIT_CONFIG_GLOBAL" --add safe.directory '*'
git config --file "$GIT_CONFIG_GLOBAL" init.defaultBranch main
mkdir "$work/repo"
(cd "$1" && git ls-files -co --exclude-standard -z | tar --null -T - -cf -) | tar -xf - -C "$work/repo" || exit 1
cd "$work/repo" || exit 1
git init -q . && git add -A && git commit -qm copy || exit 1

failed=0
python_suite() {   # <label> <skill> [pattern]
  echo "=== $1"
  python3 -m unittest discover -s "$SKILLS/$2/tests" ${3:+-p "$3"} > "$work/out.txt" 2>&1 || failed=1
  grep -E '^(FAIL|ERROR):|^Ran |^OK|^FAILED' "$work/out.txt" | cut -c1-160
}

echo "$(uname -sr), $(python3 --version), $(git --version)"
echo '=== index'
bash "$SKILLS/agnos-index/tests/test-build-index.sh" > "$work/out.txt" 2>&1 || failed=1
tail -n 1 "$work/out.txt"
python_suite init agnos-init
python_suite 'skill paths' agnos-meta-release test_skill_paths.py
python_suite 'perf center' agnos-perf-center
exit "$failed"
