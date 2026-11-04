#!/usr/bin/env bash
# agnos-init (bash): adds AGNOS to a project, the block of its entry-point files, its guide and its process folders.
# RQ-INI-001 to RQ-INI-006, RQ-PLG-004, RQ-PLG-021 / ADR-INI-001 (DEC-INI-001 to DEC-INI-003), ADR-PLG-001 (DEC-PLG-003), ADR-PLG-003 (DEC-PLG-016).
# Usage: init.sh --target <project folder>
# Every entry-point file is checked before any write. Exit code 0 on success, 1 on error, with nothing
# written (message on the error stream). init.ps1 gives the same bytes.
set -u
export LC_ALL=C    # DEC-INI-002: files are handled as bytes

REPORT_PREFIX='agnos-init: '
BEGIN_PATTERN='^<!-- AGNOS:BEGIN'
END_MARKER='<!-- AGNOS:END -->'
CR=$(printf '\r')
END_PATTERN="^$END_MARKER$CR?\$"
ENTRY_FILES='CLAUDE.md AGENTS.md'
PROCESS_FOLDERS='process/1.requirements process/2.architecture process/3.plan process/_sessionstate'
README='readme.md'
GUIDE='AGNOS-GETTING-STARTED.md'
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

fail() {
  echo "$REPORT_PREFIX$1" >&2
  exit 1
}

target=''
while [ $# -gt 0 ]; do
  case "$1" in
    --target) target=${2-}; shift 2 ;;
    *) fail "unknown argument: $1" ;;
  esac
done
[ -n "$target" ] || fail 'usage: init.sh --target <folder>'
[ -d "$target" ] || fail "target folder not found: $target"

work=$(mktemp -d) || fail 'no temporary folder'
trap 'rm -rf "$work"' EXIT

# RQ-INI-006: writes the template, in the file's line ending, with a final one.
write_block() {   # <file> <crlf|lf> <output>
  tr -d '\r' < "$SCRIPT_DIR/../assets/templates/${1%.md}.block.md" > "$3.lf"
  if [ "$2" = crlf ]; then awk '{ printf "%s\r\n", $0 }' "$3.lf" > "$3"; else cp "$3.lf" "$3"; fi
}

# RQ-INI-002, RQ-INI-004: writes in $work what the file should hold, and its action.
plan_file() {   # <file>
  file=$1
  path=$target/$file
  result=$work/$file
  if [ ! -e "$path" ]; then
    write_block "$file" lf "$result"
    echo created > "$result.action"
    return
  fi
  begins=$(grep -c "$BEGIN_PATTERN" "$path")
  ends=$(grep -cE "$END_PATTERN" "$path")
  eol=lf
  [ "$(head -n 1 "$path" | tail -c 2 | od -An -tx1 | tr -d ' ')" = 0d0a ] && eol=crlf
  write_block "$file" "$eol" "$result.block"
  if [ "$begins" -eq 0 ] && [ "$ends" -eq 0 ]; then
    eol_text='\n'
    [ "$eol" = crlf ] && eol_text='\r\n'
    {
      if [ -s "$path" ]; then
        cat "$path"
        [ "$(tail -c 1 "$path" | od -An -tx1 | tr -d ' ')" = 0a ] || printf "$eol_text"
        printf "$eol_text"
      fi
      cat "$result.block"
    } > "$result"
    echo added > "$result.action"
    return
  fi
  begin_line=$(grep -n "$BEGIN_PATTERN" "$path" | head -n 1 | cut -d: -f1)
  end_line=$(grep -nE "$END_PATTERN" "$path" | head -n 1 | cut -d: -f1)
  if [ "$begins" -ne 1 ] || [ "$ends" -ne 1 ] || [ "$end_line" -lt "$begin_line" ]; then
    fail "$file holds a damaged AGNOS block: repair its BEGIN and END lines, then call agnos-init again"
  fi
  block_size=$(wc -c < "$result.block")
  eol_size=1
  [ "$eol" = crlf ] && eol_size=2
  {
    head -n $((begin_line - 1)) "$path"
    head -c $((block_size - eol_size)) "$result.block"
    tail -n +"$end_line" "$path" | tail -c +$((${#END_MARKER} + 1))
  } > "$result"
  echo updated > "$result.action"
}

for file in $ENTRY_FILES; do plan_file "$file"; done

for file in $ENTRY_FILES; do
  path=$target/$file
  if [ -e "$path" ] && cmp -s "$work/$file" "$path"; then    # RQ-INI-003
    echo "${REPORT_PREFIX}unchanged $file"
  else
    cat "$work/$file" > "$path" || fail "cannot write $file"
    echo "$REPORT_PREFIX$(cat "$work/$file.action") $file"
  fi
done

# RQ-PLG-021 / DEC-PLG-016: the guide is AGNOS's own file, rewritten whole from its template.
guide_template=$SCRIPT_DIR/../assets/templates/$GUIDE
if [ ! -e "$target/$GUIDE" ]; then
  guide_action=created
elif cmp -s "$guide_template" "$target/$GUIDE"; then
  guide_action=unchanged
else
  guide_action=updated
fi
if [ "$guide_action" != unchanged ]; then
  cat "$guide_template" > "$target/$GUIDE" || fail "cannot write $GUIDE"
fi
echo "$REPORT_PREFIX$guide_action $GUIDE"

for folder in $PROCESS_FOLDERS; do    # RQ-INI-005
  path=$target/$folder
  if [ ! -e "$path" ]; then
    mkdir -p "$path" && cat "$SCRIPT_DIR/../assets/templates/${folder##*/}.$README" > "$path/$README" || fail "cannot create $folder"
    echo "${REPORT_PREFIX}created $folder"
  fi
done
exit 0
