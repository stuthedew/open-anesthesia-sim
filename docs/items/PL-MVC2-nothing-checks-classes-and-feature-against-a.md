---
id: PL-MVC2
title: "Nothing checks `classes:` and `feature:` against a declared vocabulary, so a misspelled class escapes the safety-class pin and a misspelled feature silently splits the group docket next ranks by"
priority: P2
effort: S
status: done
closed: 2026-09-02
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/checks.py, docket.toml, subprojects/docket/tests/test_checks.py
added: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_a_class_outside_the_declared_vocabulary_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** `checks.py` reads `classes` in exactly two places — the
safety-class pin in `_check_item` (`c in config.safety_classes`) and the
process-work test in `_groom` (`all(c in config.process_classes ...)`) — and
`feature` only as an opaque grouping key. Neither is validated against a
declared set, and `docket.toml` declares no vocabulary to validate against.
Any string is accepted in either field, silently.

Measured across the store on 2026-09-02: `classes` holds `bug` once
(`PL-T940`) against `defect` ninety-two times, and `feature` holds `docket`
once (`PL-3QGR`) against `dev-tooling` seventy-two times. Both are on closed
items, so nothing is wrong today; the mechanism that let them in is live.

**Why it matters.** Both fields fail *open*, and one of them is a
safety gate.

- `classes: safey` — or `bug` where `defect` was meant, or `saftey`, or
  `Safety` — is not in `safety_classes`, so the pin that refuses to seat
  safety-critical work below P1 does not fire, and `docket check` reports
  zero errors. The whole point of that rule is that the band means "a
  clinician could be misled"; a typo is enough to leave such an item at P3,
  and nothing anywhere says so. `CLAUDE.md`'s safety-critical standard asks
  for an obvious failure in place of a plausible-looking pass, which is
  exactly what this field does not give.
- A misspelled `feature` splits one group into two. `docket next` ranks work
  in a feature already underway, nearest-finishing first (`PL-B0YN`,
  `PL-G1MF`), so a split group makes that ranking wrong in a way that reads
  as a correct answer — the half nobody can see counts as unstarted work.

The set is small, closed and already written down in `docket.toml` for two of
the three uses, so this is the decidable half `CLAUDE.md` asks to be moved
into code rather than left to a session's memory. There is no judgment to
script: whether `bug` is a class is a question about a list, not about the
item.

**Where.** `subprojects/docket/src/docket/config.py` (where the vocabulary
would be declared, beside `safety_classes`, `process_classes` and
`debt_classes`, which are three overlapping subsets of the same set);
`subprojects/docket/src/docket/checks.py` (the per-item error block, next to
the `unknown_fields` rule that already refuses a misspelled *field* name for
this same reason); `docket.toml`; `subprojects/docket/tests/test_checks.py`.

**Worth deciding while there.** Whether `feature` gets the same treatment as
`classes`. A closed class vocabulary is clearly right — the set is fixed and
`docket.toml` half-declares it already. Features are coined as work is
grouped, so a closed list would have to be edited before each new feature
could be used, which is friction on the common path. The cheaper answer for
`feature` may be an *advisory* on a singleton — a feature carried by exactly
one item is usually a typo and occasionally a genuinely new group — rather
than an error against a declared list. `bug` and `docket` would both have
been caught by that advisory on the day they were written.

**Done when.** `bin/docket check` errors on a class outside the declared set,
naming the value and the set; `feature` is either validated the same way or
carries the singleton advisory instead, with the choice recorded; `bug` and
`docket` are corrected to `defect` and `dev-tooling` on the two closed items
that carry them; and a test pins that an unknown class is reported rather
than accepted.

**Closed 2026-09-02.** `docket.toml` declares `known_classes`;
`Config.vocabulary()` falls back to the union of `safety_classes`,
`process_classes`, `debt_classes`, `minor_classes` and `BRANCHED_ON` where a
project declares nothing, so the check is never comparing against an empty set
and silently passing everything - which would be this check carrying the defect
it exists to catch. `_check_item` errors before the safety pin reads the field.

`BRANCHED_ON` exists for `anticipated`, which the pin reads to let a concern
whose feature does not exist yet wait at its blocker's band, and which no
config list names.

**The feature half was scoped down, and the reasoning matters more than the
code.** Only mechanical variants are decided - case, and `_` or a space where
`-` was meant. Whether `docket` and `dev-tooling` name one group is the
judgment half, and a tool guessing at it would merge two features somebody
meant to keep apart. The measured instance was fixed by hand instead:
`PL-3QGR` and `PL-YNCW` moved to `dev-tooling`, and `bug` on `PL-T940` became
`defect`.

**Closed late, by its own new machinery.** The work landed several commits
before this line was written, and the item was caught still `ready` only
because its `verify:` named `test_a_class_outside_the_declared_vocabulary_is_an_error`
and the test had been written under a near-synonym. The test was renamed to the
commissioned name rather than the command rewritten to match what was built -
which is the distinction `PL-L9JS` exists to hold.

