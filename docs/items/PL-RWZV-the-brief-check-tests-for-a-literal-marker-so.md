---
id: PL-RWZV
title: The brief check tests for a literal marker, so an elaborated heading fails and an empty one passes
priority: P3
effort: S
status: ready
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_checks.py -k heading
---

**Problem.** The brief check tests for a literal marker, so an elaborated heading fails and an empty one passes

**Why it matters.**

**Where.**

**Done when.**

**Problem.** `checks.py` tests brief completeness with `marker not in
item.body` against the literal strings in `REQUIRED_BRIEF` plus
`**Done when.**`. Substring presence is the whole test, so it is wrong in both
directions:

- **An elaborated heading fails.** `PL-921W` was captured with `**Why it
  matters, and why it is not new.**`, which is a better heading than the bare
  one and reads as the required section to any human. `docket check` reported
  `brief is missing **Why it matters.**` and the heading had to be flattened
  to satisfy it (done 2026-08-31, during triage).
- **An empty heading passes.** The same file carried a stub block - `**Problem.**`
  echoing the title, then `**Why it matters.**`, `**Where.**` and `**Done
  when.**` with nothing under any of them - above its real brief. Had the stub
  been all there was, triaging the item to `ready` would have passed the check
  with three empty sections.

**Why it matters.** The check exists so that an item reaching `ready` can be
worked by someone who was not there when it was captured. Presence of a string
is a proxy for that, and it is a weak one in the direction that matters: it
rejects good briefs on wording while accepting empty ones on structure. The
first cost is paid in edits to prose that was already right; the second is
paid by whoever picks up an item with nothing under its headings.

**Where.** `subprojects/docket/src/docket/checks.py` - `REQUIRED_BRIEF` and
the loop at the top of `_check_item_fields`, and `test_checks.py` beside it.

**Approach.** Keep the marker literal and cheap; change what counts as
present. Match a heading at the start of a line by its opening words
(`**Why it matters`) rather than by the whole string, and require some
non-whitespace text between it and the next `**`-opened heading. That stays
decidable, needs no regex over prose, and is the `CLAUDE.md` line exactly: it
decides whether a section has content, never whether the content is any good.

**Not urgent, and worth saying why.** One elaborated heading has been rejected
and no empty-section item has reached `ready` - the stub above was caught by a
reader, not by the check. This is a small tax with a small hole beside it, not
a live failure.

**Done when.** A heading whose opening words match a required marker satisfies
the check however it continues; a required section with no text under it does
not; and tests cover both, including the two real cases above.

**Triaged 2026-08-31, in the session that found it.** P3, `infra`,
`dev-tooling`. The `verify:` command keys on `heading` rather than `brief`:
`-k brief` already selects a passing test today and would prove nothing.

**Admitted to v0.2.8's frozen list, 2026-09-01, under the scope test,**
reversing the "not urgent" reading above rather than disputing it. Urgency is
not the test; a misfire in machinery the goal names is, and this is a `docket
check` misfire like `PL-5YK8`, on the gate that decides whether an item may
reach `ready`. The empty-section half stopped being hypothetical on 2026-09-01:
`PL-K2ZK` and `PL-W1LN` were both captured with the four-heading stub above
their real briefs, and both would have passed this check at `ready` had the
stub been all they carried. The stubs were removed by hand during that triage.

**This file is itself the empty-section case, 2026-09-01.** The four headings
above the real brief - `**Problem.**` echoing the title, then `**Why it
matters.**`, `**Where.**` and `**Done when.**` with nothing under them - are
this item's own stub, and it is at `ready`. So the fix decides its own file's
fate, and the session doing it must delete the stub in the same commit or
`docket check` goes red on landing. It also forces the rule to be stated
precisely: whether a required section counts as present on its *first*
occurrence, on *all* of them, or on *any* one with text under it, is a choice
the three-marker scan cannot dodge here. Recommended: judge the first
occurrence, and delete the stub - "any occurrence with text" would let exactly
this shape pass, which is the hole the item exists to close. The other three
files carrying the stub (`PL-8MZN`, `PL-V5XM` dropped; `PL-WFJ9` done) are
outside `OPEN_STATUSES` and the check never reads them.
