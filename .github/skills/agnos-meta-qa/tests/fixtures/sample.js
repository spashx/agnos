// A fixture of the agnos-meta-qa tests with known findings (RQ-QLT-002, RQ-QLT-004).
function pick(a, b) {
  return a ? "first" : b ? "second" : "third";
}

function write(value) {
  let stored = value;
  // agnos-qa-exception: sonarjs/no-dead-store kept for the test
  stored = pick(stored, value);
  return value;
}

write(pick(1, 2));
