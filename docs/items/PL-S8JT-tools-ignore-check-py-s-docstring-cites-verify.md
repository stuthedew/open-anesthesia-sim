---
id: PL-S8JT
title: tools/ignore_check.py's docstring cites verify.py's SUPPRESSIONS tuple as its worked example of a type: ignore that is not a directive, and PL-G21K removed it from that tuple - the file now holds the marker in comments, which is the one carrier the tool does count
priority: P3
effort: S
status: done
classes: defect
touches: tools/ignore_check.py, tests/unit/test_ignore_check.py
added: 2026-09-20
closed: 2026-09-21
payoff: stops the tokenize-over-grep argument citing an example the tree no longer holds
verify: ! grep -q 'a tuple of suppression markers' tools/ignore_check.py
---

**Problem.** tools/ignore_check.py's docstring cites verify.py's SUPPRESSIONS tuple as its worked example of a type: ignore that is not a directive, and PL-G21K removed it from that tuple - the file now holds the marker in comments, which is the one carrier the tool does count

**Why it matters.** `tools/ignore_check.py` is what stops an inert
`type: ignore` going unread in the two trees the mypy gate excludes, and the
docstring in question is the argument for why it tokenizes rather than greps -
the distinction the whole tool rests on. An example that no longer holds
invites the next reader to conclude the distinction was over-thought and
replace the tokenizer with a grep, which would count this same file's prose as
directives.

**Where it comes from.** `PL-G21K`'s close-out, 2026-09-20. `tools/ignore_check.py`'s
`directives()` docstring justifies tokenizing over grepping with three worked
examples: "`subprojects/docket/src/docket/verify.py` holds one in a tuple of
suppression markers, `test_release.py` names one in prose, and `test_verify.py`
writes one into a fixture file as a string literal."

`PL-G21K` dropped `# type: ignore` from `SUPPRESSIONS`, so the first example is
no longer true. The other two are untouched and the argument is unaffected -
but the file now carries the marker in comments explaining why it was dropped,
and a comment is the one carrier that tool *does* count as a directive. So the
stale example names the file's new shape as its counter-example.

**No behavior changes.** `verify.py` sits in `subprojects/docket/src`, outside
`TREES`, so `ignore_check.py` never scans it; and `strict = true`'s
`warn_unused_ignores` reads those comments as prose, which `make check` proves
each run. This is a docstring whose example needs replacing, not a defect in
the check.

**Done when** the example names a file that still holds a `type: ignore` in a
tuple or a string, or is replaced by one that does.

The `verify:` command asserts the phrase `a tuple of suppression markers` is
gone from `tools/ignore_check.py`, which is the clause that went stale. It is
a negative grep because the replacement wording cannot be predicted, and the
stale clause is the one thing the fix must remove.

**The same sentence had a second carrier, and `touches` now names it.**
`tests/unit/test_ignore_check.py`'s
`test_directives_finds_the_real_ones_in_this_repository` opens with the same
three examples and the same dead first one, so fixing only the tool would have
left the tokenize-over-grep argument citing `verify.py`'s tuple one file away.
Both were replaced in the same commit.

**What replaced it.** Every example now sits inside `TREES`, which the old set
did not: two of its three - `verify.py`'s tuple and `test_release.py`'s prose -
named files this function never scans, so they were illustrations rather than
evidence, and "a grep counts all three" overstated what a grep over the checked
directories would do. The new set is `test_release.py` in prose,
`test_verify.py` in prose and as a fixture string literal, and
`test_a_comment_directive_is_counted_and_a_string_is_not`'s fixture line,
which holds a string-literal marker and a real directive at once. Named by
test rather than by line, per `.claude/rules/citation-drift.md` - this brief
first cited it as `test_ignore_check.py:148`, which `doc_check` passed because
the line exists, while the docstring edit above had already moved the fixture
to 149. The failure this item is about, inside its own brief, in one sitting. Measured 2026-09-21: a grep over `TREES` returns 39
lines where 28 are directives, and `bin/docket`'s own check reports
`28 evaluated, 0 inert`. The claim is now pinned by
`test_directives_finds_the_real_ones_in_this_repository`, which already fails
if the trees stop carrying an occurrence a grep would over-count - the old
example went stale precisely because nothing held it.
