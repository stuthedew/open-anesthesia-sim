---
id: PL-ZVG5
title: bin/docket release accepts a VERSION that is not a semantic version, so a typo such as 0.5.12x is carried into pyproject.toml's version field, the notes file name and every milestone stamp
priority: P2
effort: S
status: done
classes: defect
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1059
payoff: a mistyped release version is refused before it reaches pyproject.toml, the notes file name and every milestone stamp, where Python packaging would reject it and the milestone check would go quiet
verify: grep -q 'def test_a_version_that_is_not_semantic_is_refused' subprojects/docket/tests/test_release.py
---

**Problem.** bin/docket release accepts a VERSION that is not a semantic version, so a typo such as 0.5.12x is carried into pyproject.toml's version field, the notes file name and every milestone stamp

**Observed 2026-09-25 under `PL-3DN1`.** `bin/docket release 0.5.12x --dry-run
--no-fetch` on a tree at 0.5.11 prints `0.5.11 -> 0.5.12x` and the notes, and
refuses only because the branch holds no release-train claim - a branch that
held one would cut it. `PL-3DN1`'s `release.below_current` compares only
numbers `SEMVER_RE` parses, deliberately, because an unparsable one is not
"below" anything; nothing else between `cmd_release` and `prepare_bump`
checks the grammar, and `prepare_bump` substitutes whatever string it is
given. `version_key` reads an unparsable name as `(0, 0, 0)`, so a notes file
named `v0.5.12x.md` would also sort below every real release.

**Reproduced 2026-09-26 against 78b1a02b.** `bin/docket release 0.5.12x --dry-run --no-fetch` refuses only because "this branch holds no claim on the release train", and its advice files "Cut v0.5.12x from the 46 items finished since v0.5.11"; the version itself is never questioned. Python's `packaging` rejects it: `Version('0.5.12x')` raises `InvalidVersion`.

**Why it matters.** A cut writes the string into `pyproject.toml`, where Python packaging refuses it. It also silences what would catch it. `checks.py`'s stamped-milestone rule returns early on a current version `SEMVER_RE` cannot parse, and `suggest_version` hands that version back unchanged, so the next release inherits it. `version_key` sorts its notes file below every real release.

**Done when.** `bin/docket release` refuses a `VERSION` that `SEMVER_RE` does not match before it writes anything, in a dry run too, and says what grammar it wants. A test in `subprojects/docket/tests/test_release.py` holds it.

**Generator check.** One-off sibling of `PL-3DN1` (closed 2026-09-25), which compared only numbers that parse and filed this rather than widen its scope. The fact, which strings are release versions, is already one regex, `SEMVER_RE`, which `cmd_release` never asks. No head's `misread:` states it.
